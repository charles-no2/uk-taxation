#!/usr/bin/env python3
"""Offline, allowlisted CSV exports from supported bank statements and tax forms."""

import argparse
from collections import Counter
import csv
from datetime import date
from decimal import Decimal
import json
from pathlib import Path
import re
import sys

from bank_pdf_to_csv import ConversionError, lines, parse_date


AMOUNT = re.compile(r"^£?((?:\d{1,3}(?:,\d{3})+|\d+)\.\d{2})(DR)?$")
ROW_DATE = re.compile(r"^(\d{1,2}[ -][A-Za-z]{3}(?:[ -](?:20\d{2}|\d{2}))?)\b")
TRANSACTION_FIELDS = ['source_id', 'page', 'account_id', 'account_type', 'date',
                      'currency', 'merchant', 'transaction_type', 'money_in', 'money_out']
FORM_FIELDS = ['source_id', 'page', 'form', 'tax_year_end', 'field', 'value', 'currency']
REPORT_FIELDS = ['source_id', 'handler', 'status', 'rows', 'balance_checks', 'detail']
PROFILES = ('hsbc_uk', 'hsbc_hk_premier', 'hsbc_hk_savings', 'barclays', 'p60', 'p11d',
            'hsbc_investment_tax_certificate')
ZERO = Decimal('0.00')


def compact(text):
    return re.sub(r'\s+', '', text).lower()


def money(text):
    match = AMOUNT.fullmatch(text)
    if not match:
        raise ConversionError('Unsupported monetary value.')
    value = Decimal(match[1].replace(',', ''))
    return -value if match[2] else value


def safe_cell(text):
    return "'" + text if text.lstrip().startswith(('=', '+', '-', '@')) else text


def detect(text):
    t = compact(text)
    if 'hsbcukbankplc' in t and 'consolidatedtaxcertificate(dividendsandinterest)' in t:
        return 'hsbc_investment_tax_certificate'
    if 'p11d' in t and 'expensesandbenefits' in t:
        return 'p11d'
    if 'p60' in t and 'endofyearcertificate' in t:
        return 'p60'
    if 'barclays' in t and 'yourtransactions' in t:
        return 'barclays'
    if 'hongkongdollarstatementsavings' in t:
        return 'hsbc_hk_savings'
    if 'hsbcpremieraccounttransactionhistory' in t:
        return 'hsbc_hk_premier'
    if 'yourhsbcpremierstatement' in t:
        return 'hsbc_uk'
    raise ConversionError('Unrecognised document layout.')


def statement_end(text, filename):
    # Only use the conventional date suffix, never arbitrary digits in a name.
    match = re.search(r'_(20\d{6})\.pdf$', filename, re.I)
    if match:
        try:
            return date.fromisoformat(f'{match[1][:4]}-{match[1][4:6]}-{match[1][6:]}')
        except ValueError:
            raise ConversionError('Invalid statement date suffix.') from None
    dates = re.findall(r'\b\d{1,2}\s*[A-Za-z]{3,9}\s+20\d{2}\b', text)
    parsed = []
    for value in dates:
        try:
            parsed.append(parse_date(re.sub(r'^(\d+)([A-Za-z])', r'\1 \2', value), None))
        except ConversionError:
            pass
    if not parsed:
        raise ConversionError('Cannot determine statement end date; use a _YYYYMMDD.pdf suffix.')
    return max(parsed)


def account_key(text, profile):
    patterns = {
        'barclays': r'Account\s+no\.?\s*(\d{8})',
        'hsbc_uk': r'\b\d{2}-\d{2}-\d{2}\s+(\d{8})\b',
        'hsbc_hk_savings': r'\b(\d{3}-\d{6}-\d{3})\b',
        'hsbc_hk_premier': r'\b(\d{3}-\d{6}-\d{3})\b',
    }
    # Match the account on transaction pages; Barclays summary pages may list others.
    values = re.findall(patterns[profile], text, re.I)
    if not values or len(set(values)) != 1:
        raise ConversionError('Missing or ambiguous account identity.')
    return profile + ':' + values[0]


def clean_merchant(parts, kind, mapping):
    description = ' '.join(parts)
    matches = {label for needle, label in mapping.items() if needle.casefold() in description.casefold()}
    if len(matches) > 1:
        raise ConversionError('Conflicting merchant-map matches.')
    if matches:
        return safe_cell(next(iter(matches)))
    t = compact(description)
    if kind == 'interest':
        return 'Bank interest'
    if 'creditcardpayment' in t:
        return 'Credit card payment'
    if kind == 'fee':
        return 'Bank fee'
    if kind == 'cash':
        return 'Cash withdrawal'
    if kind != 'card':
        # Free-text transfers can contain names, addresses and payment references.
        return 'Transfer / other payment'
    name = parts[0] if parts else ''
    if re.match(r"INT['’]?L\b", name, re.I):
        name = parts[1] if len(parts) > 1 else 'Card payment'
    if name.lower().startswith('card payment to '):
        name = name[len('card payment to '):]
        # Barclays wraps long merchant names onto the next line.
        if len(parts) > 1 and not re.match(r'^(On\b|\d|Ref:)', parts[1], re.I):
            name += ' ' + parts[1]
    name = re.split(r'\b(?:On\s+\d|Ref(?:erence)?\s*:|Account\b|Sort\s*Code\b)', name, flags=re.I)[0]
    name = re.sub(r'\b[A-Z]{2}\d{2}[A-Z0-9 ]{10,}\b', '', name)
    name = re.sub(r'\b[A-Z]{2}\s*\d{2}\s*\d{2}\s*\d{2}\s*[A-D]\b', '', name, flags=re.I)
    name = re.sub(r'\b\d[\d -]{4,}\d\b|\S+@\S+', '', name)
    # Order/authorization references commonly follow a merchant and an asterisk.
    name = re.sub(r'\*[A-Z0-9]{6,}\b', '', name)
    return safe_cell(name.strip() or 'Card payment')


def transaction_kind(code, description):
    t = compact(description)
    if t.startswith(('creditinterest', 'grossinterest', 'interestearned', 'debitinterest')):
        return 'interest'
    if code == 'DR' or 'transactionfee' in t:
        return 'fee'
    if code == 'ATM' or t.startswith('cashmachine'):
        return 'cash'
    if code in ('VIS', ')))') or t.startswith('cardpaymentto'):
        return 'card'
    return 'transfer_or_other'


def table_header(line):
    text = compact(' '.join(w['text'] for w in line))
    if not (text.startswith(('date', 'ccydate')) and 'balance' in text):
        return None
    columns = {}
    for i, word in enumerate(line):
        token = word['text'].lower().lstrip('£')
        if token in ('deposit', 'withdrawal', 'balance'):
            columns[{'deposit': 'in', 'withdrawal': 'out', 'balance': 'balance'}[token]] = word['x1']
        if token in ('in', 'out') and i and line[i - 1]['text'].lower().lstrip('£') in ('paid', 'money'):
            columns[token] = word['x1']
        if token in ('description', 'payment', 'transaction', 'transactiondetails'):
            columns.setdefault('description', word['x0'])
        if token == 'date':
            columns['date'] = word['x0']
    if not all(key in columns for key in ('in', 'out', 'balance', 'description', 'date')):
        raise ConversionError('Unsupported transaction columns.')
    return columns


def parse_statement(pages, profile, end, mapping=None):
    rows, checks = [], 0
    balances = {}
    unchecked = set()
    previous_dates = {}
    currency = 'HKD' if profile.startswith('hsbc_hk') else 'GBP'
    current = None
    tables = 0

    def finish():
        nonlocal current
        if current is None:
            return
        if current['amounts'] is None:
            raise ConversionError('Transaction description has no payment amount.')
        kind = transaction_kind(current['code'], ' '.join(current['parts']))
        rows.append({'page': current['page'], 'date': current['date'].isoformat(),
                     'currency': current['currency'], 'merchant': clean_merchant(current['parts'], kind, mapping or {}),
                     'transaction_type': kind,
                     'money_in': format(current['amounts'].get('in', ZERO), '.2f'),
                     'money_out': format(current['amounts'].get('out', ZERO), '.2f')})
        current = None

    for page_number, words in enumerate(pages, 1):
        if not words:
            raise ConversionError('Page has no readable text; scanned PDFs require local OCR first.')
        columns = None
        for line in lines(words):
            joined = ' '.join(w['text'] for w in line)
            tight = compact(joined)
            detected = table_header(line)
            if detected:
                finish()
                columns = detected
                if profile.startswith('hsbc_hk') and not tight.startswith('ccy'):
                    currency = 'HKD'
                tables += 1
                continue
            if columns is None:
                continue
            if tight.startswith(('balancebrought', 'balancecarried')):
                pass
            elif tight.startswith(('creditinterestrates', 'interestrates', 'yourdeposit',
                                   'important', 'aboutyourstatement', 'totalrelationship',
                                   'hkdbest', 'messages', 'exchangerate', 'thehongkong',
                                   'barclaysbank', 'anythingwrong', 'uanythingwrong',
                                   'customerservice', 'continued', 'foreigncurrencysavings')):
                finish()
                columns = None
                continue
            first_money = min(columns['in'], columns['out']) - 55
            amounts = {}
            for word in line:
                if word['x0'] < first_money:
                    continue
                if AMOUNT.fullmatch(word['text']):
                    key = min(('in', 'out', 'balance'), key=lambda k: abs(columns[k] - word['x1']))
                    if abs(columns[key] - word['x1']) > 22 or key in amounts:
                        raise ConversionError('Ambiguous monetary columns.')
                    amounts[key] = money(word['text'])
                elif re.search(r'\d', word['text']) and not tight.startswith('(dr='):
                    raise ConversionError('Unsupported number in monetary columns.')
            left = [w for w in line if w['x0'] < first_money]
            date_boundary = columns['description'] - (6 if profile in ('hsbc_uk', 'hsbc_hk_premier') else 2)
            date_text = ' '.join(w['text'] for w in left if w['x0'] < date_boundary)
            ccy = re.match(r'^(GBP|HKD|USD|EUR|AUD|CAD|CHF|JPY|NZD|CNY)\b\s*', date_text)
            if ccy:
                finish()
                currency = ccy[1]
                date_text = date_text[ccy.end():]
            date_text = re.sub(r'^(\d{1,2}-[A-Za-z]{3})(20\d{2})$', r'\1 \2', date_text)
            date_match = ROW_DATE.match(date_text)
            description_words = [w for w in left if w['x0'] >= date_boundary]
            description = ' '.join(w['text'] for w in description_words)
            combined_row = re.fullmatch(r'(\d{1,2}-[A-Za-z]{3}(?:\s*20\d{2})?)\s*([A-Z].*)', date_text)
            if combined_row:
                date_text, prefix = combined_row.groups()
                description = (prefix + ' ' + description).strip()
                date_text = re.sub(r'^(\d{1,2}-[A-Za-z]{3})(20\d{2})$', r'\1 \2', date_text)
                date_match = ROW_DATE.match(date_text)
            # Hong Kong savings places the opening year in the description column.
            year_match = re.match(r'^(20\d{2})\s+', description)
            date_value = date_match[1] if date_match else None
            if year_match and date_value:
                date_value += ' ' + year_match[1]
                description = description[year_match.end():]
            if date_value:
                dt = parse_date(date_value, end.year)
                explicit = bool(re.search(r'[ -]\d{2,4}$', date_value))
                if not explicit and dt > end:
                    dt = dt.replace(year=end.year - 1)
                if dt > end or (currency in previous_dates and dt < previous_dates[currency]):
                    raise ConversionError('Transaction dates are outside the statement or out of order.')
                previous_dates[currency] = dt
            elif date_text and amounts:
                raise ConversionError('Unrecognised transaction date.')
            desc_compact = compact(description)
            boundary = any(s in desc_compact for s in ('balancebroughtforward', 'balancecarriedforward',
                           'b/fbalance', 'c/fbalance', 'startbalance', 'endbalance', 'accountopened'))
            if boundary:
                finish()
                if set(amounts) != {'balance'}:
                    raise ConversionError('Ambiguous opening or closing balance.')
                if currency in balances:
                    if balances[currency] != amounts['balance']:
                        raise ConversionError('Opening/closing balance does not reconcile.')
                    checks += 1
                    unchecked.discard(currency)
                balances[currency] = amounts['balance']
                if any(s in desc_compact for s in ('balancecarriedforward', 'c/fbalance', 'endbalance')):
                    columns = None
                continue
            code = ''
            if profile == 'hsbc_uk':
                code_words = [w['text'] for w in left if columns['description'] - 5 <= w['x0'] < columns['description'] + 20]
                code = ' '.join(code_words)
                description = ' '.join(w['text'] for w in left if columns['description'] + 20 <= w['x0'])
            payment = 'in' in amounts or 'out' in amounts
            start = bool(code or date_value or (payment and (current is None or current['amounts'] is not None)))
            if start:
                finish()
                if currency not in previous_dates:
                    raise ConversionError('Payment is missing its date.')
                current = {'page': page_number, 'date': previous_dates[currency], 'currency': currency,
                           'code': code, 'parts': [], 'amounts': None}
            if current and description:
                current['parts'].append(description)
            if payment:
                if current is None or current['amounts'] is not None or ('in' in amounts and 'out' in amounts):
                    raise ConversionError('Ambiguous payment direction or transaction boundary.')
                if any(amounts.get(key, ZERO) < ZERO for key in ('in', 'out')):
                    raise ConversionError('Negative payment column is unsupported.')
                if currency not in balances:
                    raise ConversionError('Payment has no opening balance.')
                expected = balances[currency] + amounts.get('in', ZERO) - amounts.get('out', ZERO)
                unchecked.add(currency)
                if 'balance' in amounts:
                    if expected != amounts['balance']:
                        raise ConversionError('Running balance does not reconcile.')
                    checks += 1
                    unchecked.discard(currency)
                balances[currency] = expected
                current['amounts'] = amounts
            elif amounts:
                raise ConversionError('Unexplained balance-only row.')
        finish()
    if unchecked:
        raise ConversionError('Final transactions have no reconciled closing/running balance.')
    if not tables or not checks:
        raise ConversionError('No reconciled transaction table found.')
    return rows, checks


def form_year(text):
    patterns = (r'Tax year to 5 April (20\d{2})', r'Expenses\s+and\s+benefits\s+20\d{2}\s+to\s+(20\d{2})')
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return match[1] + '-04-05'
    raise ConversionError('Cannot determine form tax year.')


def parse_p60(pages, text):
    year = form_year(text)
    all_lines = [(p, ' '.join(w['text'] for w in line))
                 for p, words in enumerate(pages, 1) for line in lines(words)]
    result = []
    labels = {'previous_employment': r'\bIn previous\s*$', 'this_employment': r'\bIn this\s*$', 'total': r'Total for year'}
    totals = [i for i, (_, line) in enumerate(all_lines) if re.search(labels['total'], line, re.I)]
    if len(totals) != 1:
        raise ConversionError('Unsupported P60 annual total layout.')
    for field, pattern in labels.items():
        hits = [i for i, (_, line) in enumerate(all_lines[:totals[0] + 1]) if re.search(pattern, line, re.I)]
        if len(hits) != 1:
            raise ConversionError('Unsupported P60 pay/tax layout.')
        i = hits[0]
        values = []
        for page, line in all_lines[i:i + 3]:
            values = re.findall(r'(?<![\w.])(?:\d{1,3}(?:,\d{3})+|\d+)\.\d{2}(?!\d)', line)
            if values:
                break
        if len(values) != 2:
            raise ConversionError('P60 pay/tax pair is missing or ambiguous.')
        refund = bool(re.search(r'\d\.\d{2}\s*R\b', line))
        for suffix, value in zip(('pay', 'tax_deducted'), values):
            amount = money(value) * (-1 if refund and suffix == 'tax_deducted' else 1)
            result.append({'page': page, 'form': 'P60', 'tax_year_end': year,
                           'field': field + '_' + suffix, 'value': format(amount, '.2f'), 'currency': 'GBP'})
    values = {r['field']: Decimal(r['value']) for r in result}
    for suffix in ('pay', 'tax_deducted'):
        if values['previous_employment_' + suffix] + values['this_employment_' + suffix] != values['total_' + suffix]:
            raise ConversionError('P60 totals do not reconcile.')
    # Export tax code only from its explicit label, never the employee header.
    match = re.search(r'Final tax code\s+([A-Z0-9]+)', text, re.I)
    if match:
        result.append({'page': 1, 'form': 'P60', 'tax_year_end': year, 'field': 'final_tax_code',
                       'value': match[1], 'currency': ''})
    for page, words in enumerate(pages, 1):
        page_lines = lines(words)
        for i, line in enumerate(page_lines):
            s = ' '.join(w['text'] for w in line)
            nic = re.fullmatch(r'([A-Z])\s+(\d[\d,]*)\s+(\d[\d,]*)\s+(\d[\d,]*)\s+([\d,]+\.\d{2})', s)
            if nic:
                for field, value in zip(('national_insurance_category', 'earnings_at_lower_limit',
                                         'earnings_lower_to_primary_threshold', 'earnings_primary_to_upper_limit',
                                         'employee_national_insurance'), nic.groups()):
                    result.append({'page': page, 'form': 'P60', 'tax_year_end': year, 'field': field,
                                   'value': value.replace(',', ''), 'currency': '' if field.endswith('category') else 'GBP'})
            for label, field in (('Student Loan deductions', 'student_loan_deductions'),
                                 ('Postgraduate Loan deductions', 'postgraduate_loan_deductions')):
                if label.lower() not in s.lower():
                    continue
                # The loan boxes occupy the left half; employer address is on the right.
                candidates = [w['text'] for row in page_lines[i:i + 3] for w in row
                              if w['x0'] < 300 and re.fullmatch(r'\d[\d,]*(?:\.\d{2})?', w['text'])]
                if len(candidates) != 1:
                    raise ConversionError('Unsupported P60 loan deduction layout.')
                result.append({'page': page, 'form': 'P60', 'tax_year_end': year, 'field': field,
                               'value': candidates[0].replace(',', ''), 'currency': 'GBP'})
    # Refuse a partial form if additional decimal monetary fields were populated.
    printed = Counter(abs(money(value)) for value in re.findall(
        r'(?<![\w.])(?:\d{1,3}(?:,\d{3})+|\d+)\.\d{2}(?!\d)', text))
    extracted = Counter(abs(Decimal(r['value'])) for r in result if r['currency'] == 'GBP')
    if printed - extracted:
        raise ConversionError('P60 has additional populated amounts requiring a layout-specific handler.')
    return result


P11D_SECTIONS = {
    'A': ('Assets transferred', 'assets_transferred'),
    'B': ('Payments made on behalf', 'payments_on_behalf'),
    'C': ('Vouchers and credit cards', 'vouchers_credit_cards'),
    'D': ('Living accommodation', 'living_accommodation'),
    'E': ('Mileage allowance', 'mileage_allowance'),
    'F': ('Cars and car fuel', 'cars_and_fuel'),
    'G': ('Vans and van fuel', 'vans_and_fuel'),
    'H': ('Interest-free and low interest loans', 'beneficial_loans'),
    'I': ('Private medical treatment', 'private_medical'),
    'J': ('Qualifying relocation', 'qualifying_relocation'),
    'K': ('Services supplied', 'services_supplied'),
    'L': ('Assets placed', 'assets_available'),
    'M': ('Other items', 'other_items'),
    'N': ('Expenses payments', 'expense_payments'),
}


def parse_p11d(pages, text):
    year = form_year(text)
    result, section = [], None
    supported = {'A', 'B', 'C', 'D', 'E', 'I', 'J', 'K', 'L', 'M', 'N'}
    occurrences = {}
    for page, words in enumerate(pages, 1):
        # Filled values can be a few points below the printed box labels.
        form_lines = []
        for word in sorted(words, key=lambda w: (w['top'], w['x0'])):
            if not form_lines or word['top'] - form_lines[-1][0]['top'] > 4:
                form_lines.append([])
            form_lines[-1].append(word)
        for line in (sorted(row, key=lambda w: w['x0']) for row in form_lines):
            s = ' '.join(w['text'] for w in line)
            for letter, (title, _) in P11D_SECTIONS.items():
                if (compact(s).startswith(compact(letter + title)) or
                        ('£' not in s and compact(s).startswith(compact(title)))):
                    section = letter
                    break
            # Only monetary boxes with a printed pound sign are candidates.
            pounds = [i for i, w in enumerate(line) if w['text'] == '£']
            populated = [(slot, Decimal(line[i + 1]['text'].replace(',', ''))) for slot, i in enumerate(pounds)
                         if i + 1 < len(line) and re.fullmatch(r'\d[\d,]*(?:\.\d{2})?', line[i + 1]['text'])]
            if not populated:
                # An amount outside a recognized box must not silently disappear.
                if any(AMOUNT.fullmatch(w['text']) for w in line):
                    raise ConversionError('P11D amount outside a supported monetary box.')
                continue
            if section not in supported:
                raise ConversionError('Populated P11D cars, vans or loans require a layout-specific handler.')
            if len(pounds) not in (1, 3):
                raise ConversionError('Unsupported P11D monetary columns.')
            occurrences[section] = occurrences.get(section, 0) + 1
            for slot, value in populated:
                column = ('cost', 'amount_made_good', 'cash_equivalent')[slot] if len(pounds) == 3 else 'reportable_amount'
                result.append({'page': page, 'form': 'P11D', 'tax_year_end': year,
                               'field': f'{P11D_SECTIONS[section][1]}_{occurrences[section]}_{column}',
                               'value': format(value, '.2f'), 'currency': 'GBP'})
    if not result:
        raise ConversionError('No supported populated P11D monetary boxes found.')
    return result


def parse_hsbc_investment_tax_certificate(pages, text):
    """Parse the GBP summary layout; reject unsupported populated sections."""
    periods = re.findall(r'From\s+6\s+Apr\s+(20\d{2})\s+to\s+5\s+Apr\s+(20\d{2})', text, re.I)
    if len(periods) != 1 or int(periods[0][1]) != int(periods[0][0]) + 1:
        raise ConversionError('Missing or unsupported investment certificate tax period.')
    year = periods[0][1] + '-04-05'
    summaries = [(page, compact('\n'.join(' '.join(w['text'] for w in line) for line in lines(words))))
                 for page, words in enumerate(pages, 1)
                 if 'consolidatedtaxcertificate(dividendsandinterest)' in compact(
                     ' '.join(w['text'] for w in words))]
    if len(summaries) != 1:
        raise ConversionError('Missing or ambiguous investment certificate summary.')
    page, summary = summaries[0]
    if 'currencyisgbp.' not in summary:
        raise ConversionError('Unsupported investment certificate currency.')
    amount = r'((?:\d{1,3}(?:,\d{3})+|\d+)\.\d{2})'
    empty_sections = (
        ('interestfromuksecurities', 'uk_interest'),
        ('overseasdividendincomereceived', 'overseas_dividends'),
        ('overseasinterestincomereceived', 'overseas_interest'),
        ('othertaxableincome', 'other_taxable_income'),
    )
    pattern = (r'dividendsfromuksecuritiesdividendpaidtaxcreditsequalisationunittrust/oeics'
               + amount * 3
               + ''.join(heading + 'noincomereceived' for heading, _ in empty_sections)
               + 'theoriginaltaxcreditcertificate')
    matches = list(re.finditer(pattern, summary))
    if len(matches) != 1:
        raise ConversionError('Unsupported investment certificate income sections or monetary columns.')
    values = [money(value) for value in matches[0].groups()]
    # Additional schedules or amounts must not be silently omitted.
    printed = Counter(money(value) for value in re.findall(
        r'(?<![\w.])(?:\d{1,3}(?:,\d{3})+|\d+)\.\d{2}(?!\d)', text))
    if printed != Counter(values):
        raise ConversionError('Investment certificate has additional or ambiguous monetary amounts.')
    fields = ['uk_unit_trust_oeic_dividend_paid', 'uk_unit_trust_oeic_tax_credits',
              'uk_unit_trust_oeic_equalisation']
    fields.extend(field for _, field in empty_sections)
    values.extend([ZERO] * len(empty_sections))
    return [dict(page=page, form='HSBC_INVESTMENT_TAX_CERTIFICATE', tax_year_end=year,
                 field=field, value=format(value, '.2f'), currency='GBP')
            for field, value in zip(fields, values)]


def write_csv(path, fields, rows):
    with path.open('x', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='PDF or directory of PDFs (not recursive)')
    parser.add_argument('--output', type=Path, required=True, help='New export directory; never overwritten')
    parser.add_argument('--handler', choices=PROFILES, help='Force a handler for a single-layout batch')
    parser.add_argument('--merchant-map', type=Path, help='Private JSON snippet-to-safe-label mapping')
    parser.add_argument('--source-index', type=Path, help='Optional PRIVATE JSON mapping source IDs to original filenames')
    args = parser.parse_args(argv)
    try:
        import pdfplumber
        paths = sorted(p for p in args.input.iterdir() if p.suffix.lower() == '.pdf') if args.input.is_dir() else [args.input]
        if not paths or any(not p.is_file() or p.suffix.lower() != '.pdf' for p in paths):
            raise ConversionError('Input must contain PDF files.')
        if args.output.exists() or (args.source_index and args.source_index.exists()):
            raise ConversionError('Output already exists; choose a new destination.')
        if args.source_index and args.output.resolve() in args.source_index.resolve().parents:
            raise ConversionError('Keep the private source index outside the export directory.')
        mapping = json.loads(args.merchant_map.read_text()) if args.merchant_map else {}
        if not isinstance(mapping, dict) or any(not isinstance(k, str) or not k.strip() or
                not isinstance(v, str) or not v.strip() or '\n' in v or '\r' in v for k, v in mapping.items()):
            raise ConversionError('Merchant map must contain nonempty single-line text labels.')
        args.output.mkdir(parents=True, mode=0o700)
        accounts, index, reports = {}, {}, []
        for number, path in enumerate(paths, 1):
            source = f'document_{number:03d}'
            index[source] = path.name
            profile = 'unknown'
            try:
                with pdfplumber.open(path) as pdf:
                    pages = [p.extract_words() for p in pdf.pages]
                if not pages or any(not p for p in pages):
                    raise ConversionError('Empty/scanned page; local OCR is required.')
                texts = ['\n'.join(' '.join(w['text'] for w in line) for line in lines(p)) for p in pages]
                text = '\n'.join(texts)
                profile = args.handler or detect(text)
                checks = 0
                form_parsers = {'p60': parse_p60, 'p11d': parse_p11d,
                                'hsbc_investment_tax_certificate': parse_hsbc_investment_tax_certificate}
                if profile in form_parsers:
                    rows = form_parsers[profile](pages, text)
                    fields = FORM_FIELDS
                else:
                    transaction_text = '\n'.join(t for t, words in zip(texts, pages)
                                                 if any(table_header(line) for line in lines(words)))
                    key = account_key(transaction_text, profile)
                    account = accounts.setdefault(key, f'account_{len(accounts) + 1:03d}')
                    rows, checks = parse_statement(pages, profile, statement_end(text, path.name), mapping)
                    isa_title = any(re.fullmatch(r'(?:\d+ Year Term Int )?Flexible Cash ISA', line.strip(), re.I)
                                    for line in transaction_text.splitlines())
                    account_type = 'cash_isa' if profile == 'barclays' and isa_title else profile
                    for row in rows:
                        row.update(account_id=account, account_type=account_type)
                    fields = TRANSACTION_FIELDS
                for row in rows:
                    row['source_id'] = source
                write_csv(args.output / f'{source}.csv', fields, rows)
                reports.append(dict(source_id=source, handler=profile, status='converted', rows=len(rows),
                                    balance_checks=checks, detail=''))
            except ConversionError as error:
                reports.append(dict(source_id=source, handler=profile, status='needs_review', rows=0,
                                    balance_checks=0, detail=str(error)))
            except Exception:
                # Library errors may include document text or personal filenames.
                reports.append(dict(source_id=source, handler=profile, status='needs_review', rows=0,
                                    balance_checks=0, detail='Unable to read or convert document.'))
        write_csv(args.output / 'conversion_report.csv', REPORT_FIELDS, reports)
        if args.source_index:
            with args.source_index.open('x', encoding='utf-8') as handle:
                json.dump(index, handle, indent=2)
        failed = sum(r['status'] != 'converted' for r in reports)
        print(f'Converted {len(reports) - failed}/{len(reports)} documents; {failed} need review. See conversion_report.csv.')
        return 1 if failed else 0
    except ConversionError as error:
        print(str(error), file=sys.stderr)
    except ImportError:
        print('Install scripts/bank-pdf-requirements.txt in your local virtual environment.', file=sys.stderr)
    except Exception:
        print('Unable to read configuration or create output. Check local paths and permissions.', file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main())
