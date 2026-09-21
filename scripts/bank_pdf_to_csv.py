#!/usr/bin/env python3
"""Local extraction of text-based UK current-account statement tables."""

import argparse
import csv
from datetime import date
from decimal import Decimal
import json
from pathlib import Path
import re
import sys


class ConversionError(ValueError):
    pass


MONEY = re.compile(r"^(?:£)?(?:\d{1,3}(?:,\d{3})+|\d+)\.\d{2}$")
DATE = re.compile(r"^(\d{1,2})[ /-]([A-Za-z]{3,9}|\d{1,2})(?:[ /-](\d{2}|\d{4}))?$")
MONTHS = {name: n for n, name in enumerate(
    ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'], 1)}
FIELDS = ['date', 'merchant', 'money_in_gbp', 'money_out_gbp']


def lines(words):
    result = []
    for word in sorted(words, key=lambda w: (w['top'], w['x0'])):
        if not result or abs(word['top'] - result[-1][0]['top']) > 3:
            result.append([])
        result[-1].append(word)
    return [sorted(line, key=lambda w: w['x0']) for line in result]


def header(line):
    """Locate separate paid-in/out columns; never infer direction from order."""
    text = [w['text'].lower().strip(':') for w in line]
    found = {}
    for i, token in enumerate(text):
        if token == 'date':
            found['date'] = line[i]['x0']
        if token in ('details', 'description', 'transactions', 'payment', 'type'):
            found.setdefault('description', line[i]['x0'])
        if token in ('money', 'paid', 'payments') and i + 1 < len(text):
            direction = text[i + 1]
            if direction in ('in', 'out'):
                found[direction] = line[i + 1]['x1']
        if token == 'balance':
            found['balance'] = line[i]['x1']
    return found if all(k in found for k in ('date', 'description', 'in', 'out', 'balance')) else None


def parse_date(value, year):
    match = DATE.fullmatch(value.strip())
    if not match:
        raise ConversionError('Unrecognised transaction date.')
    day, month, explicit_year = match.groups()
    month = int(month) if month.isdigit() else MONTHS.get(month[:3].lower(), 0)
    if explicit_year:
        year = int(explicit_year) + (2000 if len(explicit_year) == 2 else 0)
    if year is None:
        raise ConversionError('Dates omit the year. Supply --year for the first transaction year.')
    try:
        return date(year, month, int(day))
    except ValueError:
        raise ConversionError('Invalid transaction date.') from None


def merchant_label(description, mapping):
    matches = {label for needle, label in mapping.items() if needle.casefold() in description.casefold()}
    if len(matches) > 1:
        raise ConversionError('A transaction matches conflicting merchant labels. Refine the mapping.')
    label = next(iter(matches), description)
    # Prevent a label being evaluated as a spreadsheet formula.
    return "'" + label if label.lstrip().startswith(('=', '+', '-', '@')) else label


def parse_pages(pages, year=None, mapping=None):
    rows = []
    current = None
    previous_date = None
    balance = None
    page_count = 0

    def finish():
        nonlocal current
        if current:
            rows.append({
                'date': current['date'].isoformat(),
                'merchant': merchant_label(' '.join(current['description']), mapping or {}),
                'money_in_gbp': format(current['in'], '.2f'),
                'money_out_gbp': format(current['out'], '.2f'),
            })
            current = None

    for page_number, words in enumerate(pages, 1):
        page_count += 1
        if not words:
            raise ConversionError(f'Page {page_number}: no readable text. Scanned PDFs are unsupported.')
        columns = None
        found_table = False
        page_rows = 0
        for line in lines(words):
            detected = header(line)
            if detected:
                finish()
                columns = detected
                found_table = True
                continue
            if columns is None:
                continue
            joined = ' '.join(w['text'] for w in line)
            lower = joined.lower()
            # Stop before non-transaction statement sections.
            if lower.startswith(('interest rates', 'your deposit', 'important information',
                                 'about your statement', 'credit interest rates')):
                finish()
                columns = None
                continue
            if re.search(r'\btotal(?:s)?\b', lower):
                raise ConversionError(f'Page {page_number}: summary row needs layout-specific handling.')
            anchors = sorted((columns[key], key) for key in ('in', 'out', 'balance'))
            first_money = min(columns['in'], columns['out']) - 65
            date_end = columns['description'] - 5
            date_text = ' '.join(w['text'] for w in line if w['x0'] < date_end)
            description = ' '.join(w['text'] for w in line
                                   if w['x0'] >= date_end and w['x1'] < first_money)
            amounts = {}
            for word in line:
                if word['x1'] < first_money:
                    continue
                token = word['text']
                if MONEY.fullmatch(token):
                    key = min(anchors, key=lambda pair: abs(pair[0] - word['x1']))[1]
                    if key in amounts:
                        raise ConversionError(f'Page {page_number}: ambiguous amount columns.')
                    amounts[key] = Decimal(token.replace(',', '').replace('£', ''))
                elif re.search(r'\d', token):
                    raise ConversionError(f'Page {page_number}: unsupported amount or table layout.')
            if any(phrase in lower for phrase in ('balance brought forward', 'balance carried forward',
                                                  'brought forward', 'carried forward',
                                                  'opening balance', 'closing balance')):
                finish()
                if 'in' in amounts or 'out' in amounts:
                    raise ConversionError(f'Page {page_number}: ambiguous balance row.')
                if 'balance' in amounts:
                    if balance is not None and balance != amounts['balance']:
                        raise ConversionError(f'Page {page_number}: balance does not reconcile.')
                    balance = amounts['balance']
                continue
            if date_text:
                if DATE.fullmatch(date_text):
                    transaction_date = parse_date(date_text, year)
                    if previous_date and transaction_date < previous_date:
                        # Only a December-to-January rollover is inferred.
                        if not DATE.fullmatch(date_text).group(3) and previous_date.month == 12 and transaction_date.month == 1:
                            transaction_date = transaction_date.replace(year=previous_date.year + 1)
                        else:
                            raise ConversionError(f'Page {page_number}: dates are not chronological.')
                    previous_date = transaction_date
                    year = transaction_date.year
                elif amounts:
                    raise ConversionError(f'Page {page_number}: amount has an unrecognised date.')
                else:
                    continue
            if 'in' in amounts or 'out' in amounts:
                if previous_date is None or ('in' in amounts and 'out' in amounts):
                    raise ConversionError(f'Page {page_number}: missing date or ambiguous payment direction.')
                finish()
                incoming, outgoing = amounts.get('in', Decimal(0)), amounts.get('out', Decimal(0))
                expected = balance + incoming - outgoing if balance is not None else None
                if 'balance' in amounts and expected is not None and amounts['balance'] != expected:
                    raise ConversionError(f'Page {page_number}: balance does not reconcile; conversion stopped.')
                balance = amounts.get('balance', expected)
                current = {'date': previous_date, 'description': [description], 'in': incoming, 'out': outgoing}
                page_rows += 1
            elif 'balance' in amounts:
                raise ConversionError(f'Page {page_number}: unexplained balance-only row.')
            elif current and description:
                current['description'].append(description)
            elif DATE.fullmatch(date_text):
                raise ConversionError(f'Page {page_number}: dated row has no payment amount.')
        finish()
        if not found_table or page_rows == 0:
            raise ConversionError(f'Page {page_number}: no supported transaction table. Use a bank CSV export or adapt the layout.')
    if not rows or not page_count:
        raise ConversionError('No transactions found.')
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path)
    parser.add_argument('-o', '--output', type=Path, required=True)
    parser.add_argument('--year', type=int, help='Year of first transaction, when omitted in the table')
    parser.add_argument('--merchant-map', type=Path, help='Local JSON object mapping description snippets to safe labels')
    args = parser.parse_args(argv)
    try:
        if not args.pdf.is_file():
            raise ConversionError('Input PDF not found or not a file. Replace the example PDF path with the actual statement path; quote paths containing spaces.')
        if args.output.exists():
            raise ConversionError('Output already exists. Choose a new --output filename.')
        if not args.output.parent.is_dir():
            raise ConversionError('Output folder does not exist. Create it first or choose an existing folder.')
        if args.merchant_map and not args.merchant_map.is_file():
            raise ConversionError('Merchant map file not found. Check --merchant-map or omit it.')
        import pdfplumber
        mapping = json.loads(args.merchant_map.read_text()) if args.merchant_map else {}
        if not isinstance(mapping, dict) or any(not isinstance(k, str) or not k.strip()
                or not isinstance(v, str) or not v.strip() or '\n' in v or '\r' in v
                for k, v in mapping.items()):
            raise ConversionError('Merchant map must contain nonempty text snippets and single-line labels.')
        with pdfplumber.open(args.pdf) as pdf:
            rows = parse_pages((page.extract_words() for page in pdf.pages), args.year, mapping)
        # Exclusive creation protects an existing export and the input PDF.
        with args.output.open('x', newline='', encoding='utf-8') as output:
            writer = csv.DictWriter(output, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        print(f'Wrote {len(rows)} rows. Transaction descriptions are preserved unless explicitly mapped.')
        return 0
    except ImportError:
        print('Install dependencies: python3 -m pip install -r scripts/bank-pdf-requirements.txt', file=sys.stderr)
    except ConversionError as error:
        print(f'Conversion stopped: {error}', file=sys.stderr)
    except Exception:
        # PDF library errors and paths can include private statement information.
        print('Conversion stopped: unable to read input/map or create output. Check the files locally, PDF encryption, and whether the output exists.', file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main())
