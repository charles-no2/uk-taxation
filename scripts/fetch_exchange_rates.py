#!/usr/bin/env python3
"""Download HMRC monthly reference rates; these are not daily spot rates.

Rates are foreign currency units per GBP: divide a foreign amount by the rate.
Downloading these customs reference rates does not establish their suitability
for a particular Self Assessment entry. No taxpayer records are sent upstream.
"""
import argparse
import calendar
import csv
from datetime import date, datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen

ORIGIN = 'https://www.trade-tariff.service.gov.uk'
FIELDS = ['period', 'rate_type', 'currency', 'country', 'valid_from', 'valid_to',
          'currency_units_per_gbp', 'gbp_per_currency_unit', 'source_url',
          'retrieved_at_utc']


def periods(start, end):
    current = start.replace(day=1)
    while current <= end:
        yield current
        current = date(current.year + current.month // 12, current.month % 12 + 1, 1)


def extract_rates(payload, period, currencies, url, stamp):
    meta = payload['data']['attributes']
    if (int(meta['year']), int(meta['month']), meta['type']) != (
            period.year, period.month, 'monthly'):
        raise ValueError('Unexpected period or rate type in response')
    end = period.replace(day=calendar.monthrange(period.year, period.month)[1])
    rows = []
    for item in payload.get('included', []):
        if item['type'] != 'exchange_rate':
            continue
        entry = item['attributes']
        currency = entry['currency_code'].upper()
        if currency not in currencies:
            continue
        rate = Decimal(str(entry['rate']))
        if not rate.is_finite() or rate <= 0:
            raise ValueError(f'Invalid rate for {currency}')
        start_date = date.fromisoformat(entry['validity_start_date'])
        end_date = date.fromisoformat(entry['validity_end_date'])
        if start_date > period or end_date < end:
            raise ValueError(f'Rate does not cover the full month: {currency}')
        rows.append(dict(zip(FIELDS, [period.strftime('%Y-%m'), 'monthly', currency,
            entry['country'], start_date.isoformat(), end_date.isoformat(), str(rate),
            str((Decimal(1) / rate).quantize(Decimal('0.000000000001'))), url, stamp])))
    missing = currencies - {row['currency'] for row in rows}
    if missing:
        raise ValueError(f'Missing currencies: {sorted(missing)}')
    return sorted(rows, key=lambda row: (row['currency'], row['country']))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--start', type=date.fromisoformat, required=True)
    parser.add_argument('--end', type=date.fromisoformat, required=True)
    parser.add_argument('--currency', action='append', required=True,
                        help='Three-letter currency code; repeat for more currencies')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.end < args.start:
        parser.error('--end must not precede --start')
    currencies = {value.upper() for value in args.currency}
    if any(not re.fullmatch('[A-Z]{3}', value) for value in currencies):
        parser.error('Currency codes must have three letters')
    if args.output.exists():
        parser.error(f'Output already exists: {args.output}; choose another path')
    rows = []
    for period in periods(args.start, args.end):
        url = (f'{ORIGIN}/uk/api/exchange_rates/{period.year}-{period.month}'
               '?filter%5Btype%5D=monthly')
        request = Request(url, headers={'Accept': 'application/json',
                                       'User-Agent': 'TaxReferenceRates/1.0'})
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
        rows.extend(extract_rates(payload, period, currencies, url,
                                  datetime.now(timezone.utc).isoformat()))
    # Fetch and validate the complete range before creating the output.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f'Saved {len(rows)} monthly reference rates to {args.output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
