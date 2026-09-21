import csv
from datetime import date
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from bank_pdf_to_csv import ConversionError
from tax_pdfs_to_csv import (account_key, clean_merchant, detect, main, parse_p11d,
                             parse_p60, parse_statement, statement_end,
                             parse_hsbc_investment_tax_certificate)
from test_bank_pdf_to_csv import write_pdf


def w(text, x, y, right=None):
    return dict(text=text, x0=x, x1=right if right is not None else x + len(text) * 4, top=y)


def header(profile, y=50, foreign=False):
    if profile == 'barclays':
        return [w('Date', 58, y), w('Description', 92, y), w('Money', 256, y),
                w('out', 289, y, 304), w('Money', 318, y), w('in', 351, y, 360), w('Balance', 377, y, 412)]
    if profile == 'hsbc_uk':
        return [w('Date', 53, y), w('Payment', 117, y), w('type', 153, y), w('and', 172, y),
                w('details', 189, y), w('£Paid', 350, y), w('out', 376, y, 387),
                w('£Paid', 438, y), w('in', 464, y, 471), w('£Balance', 513, y, 549)]
    return ([w('CCY', 30, y)] if foreign else []) + [w('Date', 67, y), w('TransactionDetails', 94, y),
            w('Deposit', 338, y, 371), w('Withdrawal', 403, y, 452), w('Balance', 512, y, 547)]


def barclays():
    return [w('Barclays Your transactions', 30, 10), w('Account no. 12345678', 30, 25)] + header('barclays') + [
        w('31 Dec', 58, 70), w('Start balance', 92, 70), w('100.00', 385, 70, 412),
        w('02 Jan', 58, 90), w('Card Payment to Shop On 01', 109, 90, 248),
        w('10.00', 283, 90, 305), w('90.00', 385, 90, 412), w('Jan', 109, 100),
        w('03 Jan', 58, 120), w('Received From Jane Example', 109, 120, 240),
        w('20.00', 335, 120, 359), w('110.00', 385, 120, 412),
        w('Ref: secret account 12345678', 109, 130, 240),
        w('04 Jan', 58, 150), w('End balance', 92, 150), w('110.00', 385, 150, 412)]


class Statements(unittest.TestCase):
    def test_barclays_rollover_and_privacy(self):
        rows, checks = parse_statement([barclays()], 'barclays', date(2026, 1, 4))
        self.assertEqual([r['date'] for r in rows], ['2026-01-02', '2026-01-03'])
        self.assertEqual(rows[0]['merchant'], 'Shop')
        self.assertEqual(rows[1]['merchant'], 'Transfer / other payment')
        self.assertNotIn('Jane', str(rows))
        self.assertNotIn('12345678', str(rows))
        self.assertEqual(checks, 3)

    def test_hsbc_wrapped_and_same_day_transactions(self):
        page = header('hsbc_uk') + [
            w('01 Apr 25', 53, 70, 88), w('BALANCEBROUGHTFORWARD', 140, 70), w('100.00', 520, 70, 550),
            w('02 Apr 25', 53, 90, 88), w('VIS', 113, 90), w("INT'L 999999999", 140, 90),
            w('EXAMPLE HOSTING', 140, 100), w('Internet', 140, 110), w('10.00', 370, 110, 390),
            w('DR', 113, 120), w('Non-Sterling', 140, 120), w('Transaction Fee', 140, 130),
            w('0.25', 374, 130, 390), w('89.75', 520, 130, 550),
            w('BALANCECARRIEDFORWARD', 140, 150), w('89.75', 520, 150, 550)]
        rows, checks = parse_statement([page], 'hsbc_uk', date(2025, 4, 11))
        self.assertEqual([r['merchant'] for r in rows], ['EXAMPLE HOSTING', 'Bank fee'])
        self.assertEqual(rows[1]['money_out'], '0.25')
        self.assertEqual(checks, 2)

    def test_hong_kong_savings(self):
        page = header('hsbc_hk_savings') + [
            w('19-Mar', 66, 70, 89), w('2025', 93, 70), w('B/FBALANCE', 113, 70), w('100.00', 503, 70, 535),
            w('28-Mar', 66, 90, 89), w('CREDITINTEREST', 93, 90), w('0.25', 357, 90, 372), w('100.25', 503, 90, 535),
            w('02-Apr', 66, 110, 89), w('CREDITCARDPAYMENT', 93, 110), w('10.00', 429, 110, 453), w('90.25', 503, 110, 535),
            w('1234567890123456', 93, 120),
            w('17-Apr', 66, 140, 89), w('C/FBALANCE', 93, 140), w('90.25', 503, 140, 535)]
        rows, _ = parse_statement([page], 'hsbc_hk_savings', date(2025, 4, 17))
        self.assertEqual([r['merchant'] for r in rows], ['Bank interest', 'Credit card payment'])
        self.assertEqual(rows[0]['currency'], 'HKD')

    def test_foreign_currency_separate_balances(self):
        page = header('hsbc_hk_premier', foreign=True) + [
            w('USD', 30, 70), w('03 Apr', 67, 70, 91), w('B/F BALANCE', 117, 70), w('100.00', 503, 70, 535),
            w('28 Apr', 67, 90, 91), w('CREDIT INTEREST', 117, 90), w('1.00', 357, 90, 372), w('101.00', 503, 90, 535),
            w('GBP', 30, 110), w('03 Apr', 67, 110, 91), w('B/F BALANCE', 117, 110), w('20.00', 503, 110, 535),
            w('28 Apr', 67, 130, 91), w('CREDIT INTEREST', 117, 130), w('0.10', 357, 130, 372), w('20.10', 503, 130, 535)]
        rows, _ = parse_statement([page], 'hsbc_hk_premier', date(2025, 5, 3))
        self.assertEqual([r['currency'] for r in rows], ['USD', 'GBP'])

    def test_merged_hong_kong_date_year_and_description(self):
        page = header('hsbc_hk_savings') + [
            w('19-May2025', 66, 70, 110), w('B/FBALANCE', 113, 70), w('100.00', 503, 70, 535),
            w('28-MayCREDITINTEREST', 66, 90, 161), w('0.25', 357, 90, 372), w('100.25', 503, 90, 535),
            w('19-JunC/FBALANCE', 66, 110, 142), w('100.25', 503, 110, 535)]
        rows, _ = parse_statement([page], 'hsbc_hk_savings', date(2025, 6, 19))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['date'], '2025-05-28')
        self.assertEqual(rows[0]['merchant'], 'Bank interest')

    def test_premier_description_left_of_column_label(self):
        page = header('hsbc_hk_premier')
        next(w for w in page if w['text'] == 'TransactionDetails')['x0'] = 119.4
        page += [w('03 Apr', 67, 70, 91), w('B/F', 116.6, 70), w('BALANCE', 130, 70), w('100.00', 503, 70, 535),
                 w('28 Apr', 67, 90, 91), w('CREDIT INTEREST', 116.6, 90), w('1.00', 357, 90, 372), w('101.00', 503, 90, 535)]
        rows, _ = parse_statement([page], 'hsbc_hk_premier', date(2025, 5, 3))
        self.assertEqual(rows[0]['money_in'], '1.00')

    def test_bad_balance_fails(self):
        page = barclays()
        next(w for w in page if w['text'] == '90.00')['text'] = '91.00'
        with self.assertRaisesRegex(ConversionError, 'reconcile'):
            parse_statement([page], 'barclays', date(2026, 1, 4))

    def test_unchecked_final_payment_fails(self):
        page = [w for w in barclays() if w['top'] < 150 and not (w['top'] == 120 and w['text'] == '110.00')]
        with self.assertRaisesRegex(ConversionError, 'Final transactions'):
            parse_statement([page], 'barclays', date(2026, 1, 4))

    def test_unreadable_page_fails(self):
        with self.assertRaises(ConversionError):
            parse_statement([barclays(), []], 'barclays', date(2026, 1, 4))

    def test_mapping_and_formula(self):
        self.assertEqual(clean_merchant(['Jane secret'], 'transfer', {'Jane': 'Client A'}), 'Client A')
        self.assertEqual(clean_merchant(['=evil'], 'card', {}), "'=evil")
        with self.assertRaises(ConversionError):
            clean_merchant(['Jane secret'], 'transfer', {'Jane': 'A', 'secret': 'B'})

    def test_six_digit_card_reference_is_removed(self):
        self.assertEqual(clean_merchant(['Example Shop 123456'], 'card', {}), 'Example Shop')

    def test_detection_and_account(self):
        self.assertEqual(detect('Hong Kong Dollar Statement Savings'), 'hsbc_hk_savings')
        self.assertEqual(account_key('Account no. 12345678', 'barclays'), 'barclays:12345678')
        self.assertEqual(statement_end('', 'example_20260104.pdf'), date(2026, 1, 4))


class Forms(unittest.TestCase):
    def test_p60_totals_and_allowlist(self):
        text = ('P60 End of Year Certificate Tax year to 5 April 2026\n'
                'In previous\n1000.00 100.00\nIn this\n2000.00 200.00\n'
                'Total for year 3000.00 300.00\nFinal tax code 1257L\n'
                'Jane Example AB123456C Payroll 99999999\nCertificate shows total pay in this')
        pages = [[w(line, 50, i * 12) for i, line in enumerate(text.splitlines())]]
        rows = parse_p60(pages, text)
        self.assertEqual(len(rows), 7)
        self.assertEqual(rows[4]['value'], '3000.00')
        self.assertNotIn('Jane', str(rows))
        self.assertNotIn('AB123456C', str(rows))
        pages[0][5]['text'] = 'Total for year 9999.00 300.00'
        with self.assertRaises(ConversionError):
            parse_p60(pages, text)

    def test_p11d_populated_boxes_only(self):
        page = [w('I Private medical treatment or insurance', 20, 50),
                w('Private medical treatment', 20, 70), w('£', 300, 70), w('250.00', 315, 70),
                w('–', 355, 70), w('£', 370, 70), w('=', 410, 70), w('11', 425, 70),
                w('£', 450, 70), w('250.00', 465, 70), w('1A', 510, 70)]
        rows = parse_p11d([page], 'P11D Expenses and benefits 2025 to 2026')
        self.assertEqual([r['field'] for r in rows], ['private_medical_1_cost', 'private_medical_1_cash_equivalent'])
        self.assertEqual([r['value'] for r in rows], ['250.00', '250.00'])
        page[0]['text'] = 'F Cars and car fuel'
        with self.assertRaisesRegex(ConversionError, 'cars, vans or loans'):
            parse_p11d([page], 'Expenses and benefits 2025 to 2026')

    def test_p11d_offset_values_and_separate_heading_letter(self):
        page = [w('Private medical treatment or insurance', 45, 50),
                w('Private medical treatment', 45, 70), w('£', 300, 70), w('250.00', 315, 70.2),
                w('–', 355, 67), w('£', 370, 70), w('=', 410, 68), w('11', 425, 68),
                w('£', 450, 69), w('250.00', 465, 70.3), w('1A', 510, 68)]
        rows = parse_p11d([page], 'P11D Expenses and benefits 2025 to 2026')
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1]['field'], 'private_medical_1_cash_equivalent')


def investment_certificate():
    return ('Consolidated Tax Certificate (dividends and interest)\n'
            'From 6 Apr 2025 to 5 Apr 2026\n'
            'HSBC UK Bank plc certifies income for Jane Example. Currency is GBP.\n'
            'Dividends from UK securities\nDividend paid Tax credits Equalisation\n'
            'Unit Trust/OEICs 1,234.56 0.00 345.67\n'
            'Interest from UK securities\nNo income received\n'
            'Overseas dividend income received\nNo income received\n'
            'Overseas interest income received\nNo income received\n'
            'Other taxable income\nNo income received\n'
            'The original tax credit certificate of deduction of income tax')


class InvestmentCertificate(unittest.TestCase):
    def parse(self, text):
        pages = [[w('Private cover letter', 30, 30)],
                 [w(line, 30, 30 + i * 15) for i, line in enumerate(text.splitlines())]]
        return parse_hsbc_investment_tax_certificate(pages, text)

    def test_summary_values_zero_sections_and_privacy(self):
        text = investment_certificate()
        self.assertEqual(detect(text), 'hsbc_investment_tax_certificate')
        rows = self.parse(text)
        self.assertEqual([r['value'] for r in rows],
                         ['1234.56', '0.00', '345.67', '0.00', '0.00', '0.00', '0.00'])
        self.assertTrue(all(r['page'] == 2 and r['tax_year_end'] == '2026-04-05' for r in rows))
        self.assertNotIn('Jane', str(rows))
        self.assertEqual(rows[2]['field'], 'uk_unit_trust_oeic_equalisation')

    def test_unsupported_or_incomplete_certificate_fails(self):
        original = investment_certificate()
        cases = [original.replace('2025 to', '2024 to'),
                 original.replace('Currency is GBP', 'Currency is USD'),
                 original.replace('No income received', 'Interest paid 12.00', 1),
                 original.replace('Equalisation', 'Tax deducted'),
                 original.replace('345.67', '345.678'),
                 original.replace('Other taxable income\nNo income received\n', ''),
                 original + '\nAdditional schedule 19.99', original + '\n' + original]
        for text in cases:
            with self.subTest(text=text), self.assertRaises(ConversionError):
                self.parse(text)

    def test_real_pdf_command(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'certificate.pdf'
            words = [w(line, 30, 30 + i * 15)
                     for i, line in enumerate(investment_certificate().splitlines())]
            with patch('test_bank_pdf_to_csv.fixture', return_value=words):
                write_pdf(source)
            output = root / 'exports'
            self.assertEqual(main([str(source), '--output', str(output)]), 0)
            with (output / 'document_001.csv').open() as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 7)
            self.assertEqual(rows[0]['value'], '1234.56')
            with (output / 'conversion_report.csv').open() as handle:
                report = list(csv.DictReader(handle))
            self.assertEqual(report[0]['handler'], 'hsbc_investment_tax_certificate')
            self.assertEqual(report[0]['rows'], '7')


class Command(unittest.TestCase):
    def test_real_pdf_batch_private_index_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'Personal-Name_20260104.pdf'
            with patch('test_bank_pdf_to_csv.fixture', return_value=barclays()):
                write_pdf(source)
            output = root / 'exports'
            index = root / 'private-index.json'
            self.assertEqual(main([str(source), '--output', str(output), '--source-index', str(index)]), 0)
            result = (output / 'document_001.csv').read_text()
            self.assertNotIn('Personal-Name', result)
            self.assertNotIn('Jane', result)
            self.assertIn('account_001', result)
            self.assertIn('Personal-Name', index.read_text())
            self.assertEqual(main([str(source), '--output', str(output)]), 1)

    def test_failed_document_has_report_and_no_csv(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'Private-Name.pdf'
            source.write_bytes(b'not a PDF')
            output = root / 'exports'
            self.assertEqual(main([str(source), '--output', str(output)]), 1)
            self.assertFalse((output / 'document_001.csv').exists())
            with (output / 'conversion_report.csv').open() as handle:
                report = list(csv.DictReader(handle))
            self.assertEqual(report[0]['status'], 'needs_review')
            self.assertNotIn('Private-Name', str(report))


if __name__ == '__main__':
    unittest.main()
