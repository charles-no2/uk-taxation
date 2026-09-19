#!/usr/bin/env python3
"""Download HMRC manuals through GOV.UK's public content API (Python 3.10+)."""

import argparse
from collections import deque
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


ORIGIN = "https://www.gov.uk"
MANUALS = (
    "employment-income-manual",
    "savings-and-investment-manual",
    "property-income-manual",
    "capital-gains-manual",
    "pensions-tax-manual",
    "inheritance-tax-manual",
    "national-insurance-manual",
)
ADDITIONAL_MANUALS = (
    "business-income-manual",
    "cryptoassets-manual",
    "self-assessment-manual",
    "residence-and-fig-regime-manual",
    "residence-domicile-and-remittance-basis",
    "trusts-settlements-and-estates-manual",
    "capital-allowances-manual",
)
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "docs" / "guidance"


class TextParser(HTMLParser):
    """Keep paragraph boundaries, list items, table cells and link destinations."""

    BLOCKS = {"p", "div", "section", "blockquote", "ul", "ol", "table",
              "h1", "h2", "h3", "h4", "h5", "h6", "pre"}

    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.source = source
        self.parts = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in self.BLOCKS:
            self.parts.append("\n\n")
        elif tag in {"br", "tr"}:
            self.parts.append("\n")
        elif tag == "li":
            self.parts.append("\n- ")
        elif tag == "a":
            self.links.append(urljoin(self.source, attrs["href"]) if attrs.get("href") else "")
        elif tag == "img" and attrs.get("alt"):
            self.parts.append(attrs["alt"])

    def handle_endtag(self, tag):
        if tag in self.BLOCKS:
            self.parts.append("\n\n")
        elif tag in {"li", "tr"}:
            self.parts.append("\n")
        elif tag in {"td", "th"}:
            self.parts.append(" | ")
        elif tag == "a" and self.links:
            link = self.links.pop()
            if link:
                self.parts.append(f" ({link})")

    def handle_data(self, data):
        self.parts.append(re.sub(r"\s+", " ", data))

    def text(self):
        lines = [line.strip() for line in "".join(self.parts).splitlines()]
        return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def plain_text(html, source):
    parser = TextParser(source)
    parser.feed(html)
    parser.close()
    return parser.text()


def children(document):
    for group in document["details"].get("child_section_groups", []):
        yield from group.get("child_sections", [])


def render(document, fetched):
    source = ORIGIN + document["base_path"]
    details = document["details"]
    lines = [
        document["title"],
        f"Identifier: {details.get('section_id', 'index')}",
        f"Source: {source}",
        f"Published: {document.get('first_published_at') or 'Not supplied'}",
        f"Updated: {document.get('public_updated_at') or 'Not supplied'}",
        f"Retrieved (UTC): {fetched}",
    ]
    if document.get("withdrawn_notice"):
        lines.extend(["", "WITHDRAWN", plain_text(
            document["withdrawn_notice"].get("explanation", ""), source)])
    for html in [document.get("description", ""), details.get("body", "")]:
        if html:
            lines.extend(["", plain_text(html, source)])
    sections = list(children(document))
    if sections:
        lines.extend(["", "Contents:"])
        lines.extend(f"- {s.get('section_id', '')}: {s['title']} ({ORIGIN}{s['base_path']})"
                     for s in sections)
    return "\n".join(lines).rstrip() + "\n"


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


class SourceGap(Exception):
    """A contents entry whose source no longer provides a guidance page."""

    def __init__(self, reason, **metadata):
        super().__init__(reason)
        self.record = {"reason": reason, **metadata}


def fetch(path, delay):
    for attempt in range(4):
        time.sleep(delay)
        try:
            request = Request(ORIGIN + "/api/content" + path,
                              headers={"User-Agent": "HMRCManualTextDownloader/1.0",
                                       "Accept": "application/json"})
            with urlopen(request, timeout=45) as response:
                document = json.load(response)
            if document.get("base_path") == path and document.get("document_type") == "redirect":
                destinations = [urljoin(ORIGIN, item["destination"])
                                for item in document.get("redirects", [])
                                if item.get("destination")]
                if not destinations:
                    raise ValueError(f"Redirect without a destination at {path}")
                raise SourceGap("redirect", destinations=destinations)
            if document.get("base_path") != path or document.get("document_type") not in {
                "hmrc_manual", "hmrc_manual_section"
            }:
                raise ValueError(f"Unexpected content at {path}")
            return document
        except HTTPError as error:
            if error.code in {404, 410}:
                error.close()
                raise SourceGap("missing", http_status=error.code) from error
            if error.code not in {429, 500, 502, 503, 504} or attempt == 3:
                raise
            retry_after = error.headers.get("Retry-After", "")
            time.sleep(min(float(retry_after), 120) if retry_after.isdigit() else 2 ** attempt)
        except (URLError, TimeoutError):
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)


def download(manual, args):
    root = "/hmrc-internal-manuals/" + manual
    folder = args.output / manual
    state_file = folder / "manifest.json"
    state = {"manual": manual, "source": ORIGIN + root, "pages": {}}
    if args.resume and state_file.exists():
        state = json.loads(state_file.read_text(encoding="utf-8"))
        if state.get("manual") != manual:
            raise ValueError(f"Wrong manual in {state_file}")
    state.update(status="in_progress", errors={})
    state.setdefault("gaps", {})
    queue, visited = deque([root]), set()
    failures = 0
    processed = 0

    def save():
        state["checked_at"] = datetime.now(timezone.utc).isoformat()
        atomic_write(state_file, json.dumps(state, indent=2) + "\n")

    save()
    while queue:
        path = queue.popleft()
        if path in visited:
            continue
        if args.max_pages and processed >= args.max_pages:
            queue.appendleft(path)
            break
        visited.add(path)
        if path != root and not re.fullmatch(re.escape(root) + r"/[a-zA-Z0-9_-]+", path):
            raise ValueError(f"Unexpected section path: {path}")
        filename = "index.txt" if path == root else path.rsplit("/", 1)[1] + ".txt"
        previous = state["pages"].get(path)
        try:
            if args.resume and previous and path not in state["gaps"] and (folder / filename).exists():
                section_paths = previous["children"]
            else:
                document = fetch(path, args.delay)
                fetched = datetime.now(timezone.utc).isoformat()
                section_paths = [section["base_path"] for section in children(document)]
                atomic_write(folder / filename, render(document, fetched))
                state["pages"][path] = {"file": filename, "children": section_paths,
                                        "retrieved_at": fetched,
                                        "updated_at": document.get("public_updated_at")}
            queue.extend(section_paths)
            state["gaps"].pop(path, None)
        except SourceGap as gap:
            if path == root:
                failures += 1
                state["errors"][path] = f"Manual index unavailable: {gap.record}"
                print(f"ERROR {path}: {state['errors'][path]}", file=sys.stderr, flush=True)
            else:
                state["gaps"][path] = {**gap.record,
                                       "checked_at": datetime.now(timezone.utc).isoformat()}
                print(f"GAP {path}: {gap.record}", file=sys.stderr, flush=True)
        except (HTTPError, URLError, TimeoutError, ValueError, KeyError) as error:
            failures += 1
            state["errors"][path] = str(error)
            print(f"ERROR {path}: {error}", file=sys.stderr, flush=True)
        processed += 1
        save()
        if processed % 100 == 0:
            print(f"{manual}: {processed} pages checked", flush=True)
    state["status"] = ("failed" if failures else "partial" if queue
                       else "completed_with_gaps" if state["gaps"] else "complete")
    state["pages_checked"] = processed
    save()
    print(f"{manual}: {state['status']}, {processed} pages checked, "
          f"{len(state['gaps'])} gaps, {failures} errors", flush=True)
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manual", action="append", choices=MANUALS + ADDITIONAL_MANUALS,
                        help="Download only this manual; repeat to select several (default: all seven)")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--resume", action="store_true",
                        help="Reuse downloaded pages and their saved contents links; omit to refresh")
    parser.add_argument("--max-pages", type=int, default=0,
                        help="Limit pages per manual for a sample run; 0 downloads everything")
    parser.add_argument("--delay", type=float, default=0.25,
                        help="Seconds before each request (default: 0.25)")
    args = parser.parse_args()
    if args.max_pages < 0 or args.delay < 0:
        parser.error("--max-pages and --delay must be non-negative")
    failures = sum(download(manual, args) for manual in dict.fromkeys(args.manual or MANUALS))
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted. Run again with --resume to continue.", file=sys.stderr)
        sys.exit(130)
