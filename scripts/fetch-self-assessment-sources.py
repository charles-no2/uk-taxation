#!/usr/bin/env python3
"""Fetch the 2025–26 Self Assessment reference pack, not taxpayer records.

Uses GOV.UK content JSON; retains originals, readable text and a source manifest.
Run from any directory. Existing files are replaced only after successful fetching.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import time
from urllib.parse import urljoin, urlparse, unquote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'docs' / 'self-assessment'
ORIGIN = 'https://www.gov.uk'
spec = importlib.util.spec_from_file_location('manual_text', ROOT / 'scripts/fetch-hmrc-manuals.py')
manual_text = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manual_text)
SEEDS = {
    '2025-26/forms': ['/guidance/how-to-complete-your-self-assessment-tax-return-for-last-tax-year'],
    'completion-guidance': ['/government/collections/get-help-filling-in-your-self-assessment-tax-return'],
    '2025-26/helpsheets': [
        '/government/collections/self-assessment-helpsheets-employment',
        '/government/collections/self-assessment-helpsheets-self-employment-and-partnerships',
        '/government/collections/self-assessment-helpsheets-capital-gains',
        '/government/collections/self-assessment-helpsheets-foreign',
        '/government/collections/self-assessment-helpsheets-residence-and-remittance-basis',
        '/government/collections/self-assessment-helpsheets-trusts-and-estates',
    ],
    '2025-26/calculations': ['/government/publications/self-assessment-technical-specifications-2026-for-individual-returns'],
    'rates-and-allowances': [
        '/government/publications/rates-and-allowances-income-tax',
        '/government/publications/rates-and-allowances-national-insurance-contributions',
        '/government/publications/rates-and-allowances-capital-gains-tax',
        '/income-tax-rates', '/scottish-income-tax', '/welsh-income-tax',
        '/tax-on-dividends', '/apply-tax-free-interest-on-savings',
        '/guidance/tax-free-allowances-on-property-and-trading-income',
        '/tax-on-your-private-pension/pension-tax-relief',
        '/government/publications/student-loans-a-guide-to-terms-and-conditions',
    ],
    'filing-guidance': [
        '/self-assessment-tax-returns',
        '/self-assessment-tax-returns/who-must-send-a-tax-return',
        '/self-assessment-tax-returns/deadlines',
        '/self-assessment-tax-returns/keeping-records',
        '/self-assessment-tax-returns/corrections',
        '/self-assessment-tax-returns/sending-return',
        '/understand-self-assessment-bill/payments-on-account',
        '/guidance/check-if-youre-eligible-for-making-tax-digital-for-income-tax',
    ],
}


def fetch(url):
    for attempt in range(4):
        try:
            with urlopen(Request(url, headers={'User-Agent': 'SelfAssessmentReferenceDownloader/1.0'}), timeout=60) as r:
                return r.read(), r.geturl(), r.headers.get_content_type()
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_bytes(data if isinstance(data, bytes) else data.encode())
    tmp.replace(path)


def eligible(title):
    years = re.findall(r'(?<!\d)20\d{2}(?!\d)', title)
    return not years or '2026' in years


def page(job):
    category, path = job
    raw, _, _ = fetch(ORIGIN + '/api/content' + path)
    d = json.loads(raw)
    if d.get('document_type') == 'redirect':
        target = urlparse(urljoin(ORIGIN, d['redirects'][0]['destination']))
        if target.netloc != 'www.gov.uk':
            raise ValueError('External redirect: ' + target.geturl())
        raw, _, _ = fetch(ORIGIN + '/api/content' + target.path)
        d = json.loads(raw)
    source = ORIGIN + d['base_path']
    slug = path.strip('/').replace('/', '__')
    if len(slug) > 180:
        slug = slug[:160] + '--' + hashlib.sha256(path.encode()).hexdigest()[:12]
    folder = DEST / category / slug
    stamp = datetime.now(timezone.utc).isoformat()
    write(folder / 'source.json', raw)
    details = d.get('details', {})
    if path == SEEDS['2025-26/forms'][0] and not any(
        '2026' in a.get('title', '') and 'SA100' in a.get('title', '')
        for a in details.get('attachments', [])
    ):
        raise ValueError('The rolling main-return page no longer contains SA100 (2026); update the seed to its archived 2025–26 publication')
    bodies = [d.get('description', ''), details.get('body', '')]
    bodies += [f"<h2>{p.get('title', '')}</h2>" + p.get('body', '') for p in details.get('parts', [])]
    bodies += [g.get('body', '') for g in details.get('collection_groups', [])]
    bodies = [b for b in bodies if isinstance(b, str)]
    html = '\n'.join(bodies)
    write(folder / 'content.html', html)
    lines = [d['title'], 'Source: ' + source, 'Retrieved (UTC): ' + stamp,
             'Updated: ' + str(d.get('public_updated_at')), '', manual_text.plain_text(html, source)]
    children = []
    for item in d.get('links', {}).get('documents', []):
        if item.get('base_path') and eligible(item.get('title', '')):
            children.append((category, item['base_path']))
            lines.append(f"{item.get('title')}: {ORIGIN}{item['base_path']}")
    if category == '2025-26/forms':
        children += [(category, urlparse(urljoin(source, href)).path)
                     for href in re.findall(r'href=[\"\']([^\"\']+)', html)
                     if '/government/publications/self-assessment-' in href and
                     'sa100' not in href and 'earlier' not in href]
    if category in {'completion-guidance', '2025-26/helpsheets'}:
        for href in re.findall(r'href=[\"\']([^\"\']+)', html):
            link = urlparse(urljoin(source, href))
            if link.netloc == 'www.gov.uk' and link.path.startswith('/government/publications/') and (
                'helpsheet' in link.path or re.search(r'\bhs\d{3}\b', link.path)
            ) and eligible(link.path):
                children.append(('2025-26/helpsheets', link.path))
    attachments, skipped, errors = [], [], []
    for a in details.get('attachments', []):
        url = a.get('url')
        if not url:
            continue
        if not eligible(a.get('title', '') + ' ' + a.get('filename', '')):
            skipped.append({'title': a.get('title'), 'url': url, 'reason': 'Other tax year'})
            continue
        parsed = urlparse(url)
        if a.get('attachment_type') == 'html' or parsed.netloc == 'www.gov.uk':
            children.append((category, parsed.path))
            continue
        if parsed.netloc != 'assets.publishing.service.gov.uk':
            skipped.append({'title': a.get('title'), 'url': url, 'reason': 'External attachment'})
            continue
        try:
            data, resolved, content_type = fetch(url)
            name = Path(unquote(parsed.path)).name
            if not name or content_type == 'text/html':
                raise ValueError('Expected an attachment, received HTML or no filename')
            if name.lower().endswith('.pdf') and not data.startswith(b'%PDF-'):
                raise ValueError('Invalid PDF signature')
            file = folder / name
            write(file, data)
            record = {'title': a.get('title'), 'url': url, 'resolved_url': resolved,
                      'file': str(file.relative_to(ROOT)), 'bytes': len(data),
                      'sha256': hashlib.sha256(data).hexdigest(), 'content_type': content_type}
            if name.lower().endswith('.pdf') and shutil.which('pdftotext'):
                output = file.with_suffix('.txt')
                subprocess.run(['pdftotext', '-layout', str(file), str(output)], check=True, capture_output=True)
                record['text_file'] = str(output.relative_to(ROOT))
            attachments.append(record)
            lines.append(f"Attachment: {a.get('title')} ({url})")
        except Exception as e:
            errors.append({'url': url, 'error': str(e)})
    write(folder / 'index.txt', '\n'.join(lines) + '\n')
    return {'title': d['title'], 'source': source, 'requested_source': ORIGIN + path,
            'category': category, 'retrieved_at': stamp, 'updated_at': d.get('public_updated_at'),
            'file': str((folder / 'index.txt').relative_to(ROOT)),
            'attachments': attachments, 'skipped_attachments': skipped, 'errors': errors}, children


def main():
    state = {'scope': '2025–26 forms/helpsheets/calculations; current mixed-year public guidance',
             'started_at': datetime.now(timezone.utc).isoformat(), 'status': 'in_progress', 'pages': [], 'errors': []}
    queue = [(category, path) for category, paths in SEEDS.items() for path in paths]
    seen = set()
    with ThreadPoolExecutor(max_workers=4) as pool:
        while queue:
            batch = list(dict.fromkeys(job for job in queue if job not in seen))
            seen.update(batch)
            queue = []
            futures = [(job, pool.submit(page, job)) for job in batch]
            for job, future in futures:
                try:
                    record, children = future.result()
                    state['pages'].append(record)
                    queue.extend(children)
                    print(record['title'], len(record['attachments']), 'attachments', flush=True)
                except Exception as e:
                    state['errors'].append({'category': job[0], 'source': ORIGIN + job[1], 'error': str(e)})
                    print('ERROR', job, e, flush=True)
                write(DEST / 'manifest.json', json.dumps(state, indent=2) + '\n')
    state['finished_at'] = datetime.now(timezone.utc).isoformat()
    state['status'] = 'partial' if state['errors'] or any(p['errors'] for p in state['pages']) else 'complete'
    write(DEST / 'manifest.json', json.dumps(state, indent=2) + '\n')
    index = ['# Downloaded Self Assessment sources', '',
             'Generated by `scripts/fetch-self-assessment-sources.py`. See [data requirements](../data-sources.md).', '',
             'Original attachments are retained. PDF text copies preserve layout where possible; use the originals for box positions and tables.', '',
             '| Category | Source / refresh link | Local text | Attachments |',
             '|---|---|---|---|']
    for p in sorted(state['pages'], key=lambda p: (p['category'], p['title'])):
        local = Path(p['file']).relative_to('docs/self-assessment').as_posix()
        attachments = ', '.join(f"[{Path(a['file']).name}]({Path(a['file']).relative_to('docs/self-assessment').as_posix()})" for a in p['attachments']) or 'HTML guidance'
        index.append(f"| {p['category']} | [{p['title'].replace('|', '/').strip()}]({p['source']}) | [text]({local}) | {attachments} |")
    write(DEST / 'INDEX.md', '\n'.join(index) + '\n')
    print(state['status'], len(state['pages']), 'pages', flush=True)
    return int(state['status'] != 'complete')


if __name__ == '__main__':
    raise SystemExit(main())
