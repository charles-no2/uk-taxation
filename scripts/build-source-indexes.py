"""Build offline navigation indexes; never rewrite downloaded source files."""

import argparse
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
TOPICS = {
    "business-income-manual": "Self-employment, trading profits, expenses, losses, partnerships",
    "capital-allowances-manual": "Business equipment, capital expenditure, allowances",
    "capital-gains-manual": "Asset disposals, shares, property gains, losses, reliefs",
    "cryptoassets-manual": "Cryptoassets, tokens, trading and disposals",
    "employment-income-manual": "Employment pay, benefits, expenses, share schemes, pension income",
    "inheritance-tax-manual": "Inheritance, gifts, estates; usually outside the personal return",
    "national-insurance-manual": "National Insurance contributions, employment status, contribution classes",
    "pensions-tax-manual": "Pension contributions, relief, annual and other allowance charges",
    "property-income-manual": "Rental income, landlord expenses, property businesses, Rent a Room",
    "residence-and-fig-regime-manual": "Residence, foreign income and gains regime, overseas workday relief",
    "residence-domicile-and-remittance-basis": "Domicile, remittance basis, historical and transitional overseas cases",
    "savings-and-investment-manual": "Interest, dividends, savings, investment income",
    "self-assessment-manual": "Return administration, filing, payments, amendments, enquiries",
    "trusts-settlements-and-estates-manual": "Trusts, settlements, estate income, beneficiaries",
}


def cell(value):
    return str(value).replace("|", "&#124;").replace("\n", " ").strip()


def write(path, lines, check):
    content = "\n".join(lines) + "\n"
    if check:
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            raise ValueError(f"Index missing or stale: {path}")
    else:
        path.write_text(content, encoding="utf-8")


def guidance(root, check=False):
    folder = root / "docs/guidance"
    overview = [
        "# Guidance index", "",
        "For explanations of how the taxes work, read the [tax summary](SUMMARY.md) first.", "",
        "Start here to locate HM Revenue & Customs (HMRC) interpretations. These are not legislation.", "",
        "1. Select a topic below, then search that manual's page-title index.",
        "2. Open only the matching text files. For a known identifier, open its lowercase `.txt` file directly.",
        "3. Check the page's source, update/retrieval dates, withdrawal notices and tax-year applicability.",
        "   Check the manifest for gaps/errors; a completed crawl is not proof of complete tax coverage.", "",
        "For form boxes and annual completion notes, start at [Self Assessment sources](../self-assessment/INDEX.md).",
        "For statutory wording, use the [rules index](../rules/INDEX.md).", "",
        "## Choose a manual", "",
        "Page counts include the manual landing page. Status and gap counts come from saved manifests.", "",
        "| Topic / search terms | Page-title index | Indexed pages | Run status | Gaps / errors / missing files |",
        "|---|---|---:|---|---|",
    ]
    for manifest in sorted(folder.glob("*/manifest.json")):
        state = json.loads(manifest.read_text(encoding="utf-8"))
        manual = manifest.parent.name
        gaps, errors = state.get("gaps", {}), state.get("errors", {})
        rows, missing = [], []
        for source, record in sorted(state["pages"].items()):
            if source in gaps or source in errors:
                continue
            path = manifest.parent / record["file"]
            if not path.is_file():
                missing.append(source)
                continue
            with path.open(encoding="utf-8") as stream:
                title = stream.readline().strip()
            rows.append(f"| [{cell(path.stem.upper())}]({path.name}) | {cell(title)} | {cell(record.get('updated_at', 'unknown'))} |")
        problems = [f"- `{source}`: {cell(json.dumps(detail, sort_keys=True))}"
                    for group in (gaps, errors) for source, detail in sorted(group.items())]
        problems.extend(f"- `{source}`: manifest lists a missing local file" for source in missing)
        lines = [f"# {manual}: page-title index", "",
                 "Generated from saved manifest entries and source titles; not a summary of tax treatment.",
                 "Search this file rather than loading it all. Titles can describe historical or withdrawn material.",
                 "Pages with recorded gaps/errors are excluded even if an older file remains on disk.", "",
                 f"Run status: `{state.get('status', 'unknown')}`. Manifest checked: `{state.get('checked_at', 'unknown')}`.",
                 "See [manifest](manifest.json) for per-page retrieval dates and source paths,",
                 "[original contents](index.txt) for the published hierarchy, and [topic index](../INDEX.md) for other manuals.", "",
                 "## Known gaps and errors", "", *(problems or ["None recorded."]), "",
                 "## Pages", "", "| Identifier / local text | Source title | Source updated |",
                 "|---|---|---|", *rows]
        write(manifest.parent / "INDEX.md", lines, check)
        overview.append(f"| {TOPICS.get(manual, manual)} | [{manual}]({manual}/INDEX.md) | {len(rows)} | {state.get('status', 'unknown')} | {len(gaps)} / {len(errors)} / {len(missing)} |")
    overview.extend([
        "", "## Targeted lookup", "", "Run from the repository root:", "", "```sh",
        "rg -n -i 'rent a room|repairs' docs/guidance/property-income-manual/INDEX.md",
        "rg -n -i 'staking|airdrop' docs/guidance/cryptoassets-manual/INDEX.md",
        "# If the topic is unclear, search titles across all manuals, not every source body.",
        "rg -n -i 'foreign tax' docs/guidance/*/INDEX.md", "```", "",
        "A title search can miss a concept discussed only in the body. Follow the matching page's contents/links",
        "or search within the selected manual as a fallback. No match does not mean no applicable rule.", "",
        "## Refresh", "", "Generated offline with `python3 scripts/build-source-indexes.py`.",
        "Run it after downloading sources; `--check` detects stale indexes without writing.",
        "Only manifest-listed successful pages are indexed; unlisted leftover files are not treated as current.",
        "See [download instructions](README.md). Index generation does not refresh or verify official sources.",
    ])
    write(folder / "INDEX.md", overview, check)


def headings(text):
    """Extract standalone headings from the saved XSL text layout, not legal structure."""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        title = line.strip()
        if (index < 8 or not title or line[0].isspace() or
                lines[index - 1].strip() or len(title) > 250 or
                not re.match(r"[A-Za-z]", title)):
            continue
        following = ""
        for cursor in range(index + 1, len(lines)):
            if lines[cursor].strip():
                following = lines[cursor].strip()
                break
        number = re.match(r"^(\d+[A-Z]*)\.\s*(?:$|\()", following)
        if number:
            title = f"{number[1]}. {title}"
        elif re.fullmatch(r"(?:Part|Chapter|Schedule|SCHEDULE)\s+[0-9A-Z]+", title):
            if following and len(following) <= 250:
                title = f"{title}: {following}"
        yield index + 1, title


def rules(root, check=False):
    folder = root / "docs/rules"
    overview = [
        "# Rules index", "",
        "For explanations of how the tax rules work, read the [tax summary](SUMMARY.md) first.", "",
        "Use this index for statutory wording, after identifying the issue in the [guidance index](../guidance/INDEX.md).",
        "For return boxes and completion instructions, use [annual Self Assessment sources](../self-assessment/INDEX.md).", "",
        "These are saved revised-law snapshots, not a verified set of rules for a particular tax year.",
        "Check the official provision, commencement dates, amendments and territorial scope before applying it.",
        "Supporting regulations and case law are not included. Topic folders are routing hints, not limits on an Act's scope.", "",
        "## Choose an Act", "",
        "Each heading index lists local line numbers so you can read a small relevant passage.", "",
        "| Topic | Act / local text | Heading index | Source lines | Fetch time |",
        "|---|---|---|---:|---|",
    ]
    for path in sorted(folder.glob("*/*.txt")):
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        entries = list(headings(text))
        title = lines[0].strip()
        source = next(line.removeprefix("Official source: ") for line in lines if line.startswith("Official source: "))
        fetched = next(line.removeprefix("Fetched (UTC): ") for line in lines if line.startswith("Fetched (UTC): "))
        index_path = path.with_suffix(".index.md")
        warning = "No standalone headings detected: inspect source completeness before use."
        detail = [f"# {title}: heading index", "",
                  f"[Local text]({path.name}) · [Official source]({source})", "",
                  f"Fetched: `{fetched}`. Source lines: {len(lines)}.", "",
                  "Automatically extracted navigation headings, not an authoritative table of provisions.",
                  "The plain-text format loses structural information. Numbers may be schedule paragraphs",
                  "rather than Act sections; inspect surrounding headings before citing. Repeated headings are retained.",
                  "Line numbers refer to the saved text, not this index. Regenerate after source changes.", "",
                  "| Source line | Heading / provision hint |", "|---:|---|"]
        detail.extend(f"| {line} | {cell(heading)} |" for line, heading in entries)
        if not entries:
            detail.extend(["", f"WARNING: {warning}"])
        write(index_path, detail, check)
        link = index_path.relative_to(folder).as_posix()
        overview.append(f"| {path.parent.name} | [{cell(title)}]({path.relative_to(folder).as_posix()}) | [Headings]({link}){' — **CHECK: no headings found**' if not entries else ''} | {len(lines)} | {fetched} |")
    overview.extend([
        "", "## Targeted lookup", "", "Run from the repository root:", "", "```sh",
        "rg -n -i 'property business|rent.a.room' docs/rules/income-tax/*.index.md",
        "rg -n -i 'notice.*return|amendment' docs/rules/tax-administration/*.index.md",
        "# Use the source-line column, not rg's index-file line number.",
        "sed -n '40,95p' docs/rules/income-tax/income-tax-act-2007.txt", "```", "",
        "Search headings first; if necessary search the selected Act's text. Heading extraction is a navigation aid",
        "and may omit headings or include quoted provisions; it does not establish legal coverage.", "",
        "## Source limitations", "",
        "Any Act flagged above with no headings needs a completeness check before use. A file containing",
        "only introductory text is not a full Act; do not infer that a rule is absent.",
        "The filename `latest` is not a freshness guarantee. Consult the official source when needed.", "",
        "## Refresh", "", "Regenerate after source downloads with `python3 scripts/build-source-indexes.py`.",
        "Use `--check` to detect stale indexes without writing. This does not fetch or legally verify sources.",
        "See [download instructions](README.md) and [fetch record](FETCHED_AT.md).",
    ])
    write(folder / "INDEX.md", overview, check)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    guidance(ROOT, args.check)
    rules(ROOT, args.check)
    print("Source indexes checked." if args.check else "Source indexes generated.")
