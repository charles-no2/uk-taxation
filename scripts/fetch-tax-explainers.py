"""Save selected public tax explainers in a separate, dated snapshot."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'sources', ROOT / 'scripts/fetch-self-assessment-sources.py')
sources = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sources)

# Guide roots preserve all parts, not merely the first screen.
PATHS = [
    '/income-tax', '/income-tax-rates', '/income-tax-reliefs',
    '/tax-on-dividends', '/apply-tax-free-interest-on-savings',
    '/expenses-if-youre-self-employed', '/capital-allowances',
    '/guidance/income-tax-when-you-rent-out-a-property-working-out-your-rental-income',
    '/capital-gains-tax', '/tax-on-your-private-pension',
    '/self-employed-national-insurance-rates', '/national-insurance',
    '/tax-foreign-income',
    '/guidance/check-if-you-can-claim-the-4-year-foreign-income-and-gains-regime',
    '/trusts-taxes', '/inheritance-tax', '/how-vat-works',
    '/stamp-duty-land-tax', '/understand-self-assessment-bill',
]


def main():
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    dest = ROOT / 'docs/tax-explainers' / stamp
    dest.mkdir(parents=True, exist_ok=False)
    sources.DEST = dest
    state = {'scope': 'Public explanations; mixed tax years; no taxpayer data',
             'started_at': stamp, 'status': 'in_progress', 'pages': [], 'errors': []}
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [(path, pool.submit(sources.page, ('guides', path))) for path in PATHS]
        for path, future in futures:
            try:
                record, children = future.result()
                record['unfollowed_children'] = children
                state['pages'].append(record)
                print(record['title'], flush=True)
            except Exception as error:
                state['errors'].append({'path': path, 'error': str(error)})
                print('ERROR', path, str(error), flush=True)
            sources.write(dest / 'manifest.json', json.dumps(state, indent=2) + '\n')
    state['status'] = 'partial' if state['errors'] or any(
        page['errors'] for page in state['pages']) else 'complete'
    state['finished_at'] = datetime.now(timezone.utc).isoformat()
    sources.write(dest / 'manifest.json', json.dumps(state, indent=2) + '\n')
    lines = ['# Saved public tax explainers', '',
             'Snapshot: ' + stamp + '. Status: ' + state['status'] + '.', '',
             'Each guide retains original content JSON, body HTML and readable text, including',
             'all guide parts returned by GOV.UK. This is not a recursive website mirror.',
             'Linked child publications are recorded but not followed. Attachment selection',
             'inherits the reference downloader’s 2026/undated filter; see the manifest for exclusions.',
             'These rolling pages may describe a later year than the 2025–26 return pack.', '',
             '| Explanation | Local copy |', '|---|---|']
    for page in state['pages']:
        relative = (ROOT / page['file']).relative_to(dest)
        lines.append(f"| [{page['title']}]({page['source']}) | [Text]({relative.as_posix()}) |")
    sources.write(dest / 'INDEX.md', '\n'.join(lines) + '\n')
    print(dest, state['status'], flush=True)
    return int(state['status'] != 'complete')


if __name__ == '__main__':
    raise SystemExit(main())
