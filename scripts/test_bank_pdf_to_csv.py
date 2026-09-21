import csv
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
import tempfile
import unittest

from bank_pdf_to_csv import ConversionError, main, parse_pages


def word(text, x, y, width=None):
    return {'text': text, 'x0': x, 'x1': x + (width or len(text) * 5), 'top': y}


def fixture(direction='out', balance='88.00', date='05 Apr 2025'):
    words = [word('Date', 30, 50), word('Description', 100, 50),
             word('Money', 350, 50), word('out', 380, 50),
             word('Money', 430, 50), word('in', 460, 50), word('Balance', 520, 50),
             word('Opening balance', 100, 70), word('100.00', 525, 70),
             word(date, 30, 90, 60), word('ACME HOSTING PRIVATE REF 12345678', 100, 90),
             word('12.00', 370 if direction == 'out' else 445, 90),
             word(balance, 530, 90)]
    return words


def write_pdf(path):
    # A real, tiny PDF with fictional transactions; no statement fixtures needed.
    commands = []
    for item in fixture():
        text = item['text'].replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
        commands.append(f"BT /F1 8 Tf {item['x0']} {800-item['top']} Td ({text}) Tj ET")
    stream = '\n'.join(commands).encode()
    objects = [b'<< /Type /Catalog /Pages 2 0 R >>',
               b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
               b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 600 850] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',
               b'<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>',
               b'<< /Length ' + str(len(stream)).encode() + b' >>\nstream\n' + stream + b'\nendstream']
    data = bytearray(b'%PDF-1.4\n')
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(data))
        data.extend(f'{i} 0 obj\n'.encode() + obj + b'\nendobj\n')
    xref = len(data)
    data.extend(f'xref\n0 {len(offsets)}\n0000000000 65535 f \n'.encode())
    for offset in offsets[1:]:
        data.extend(f'{offset:010d} 00000 n \n'.encode())
    data.extend(f'trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode())
    path.write_bytes(data)


class ConversionTests(unittest.TestCase):
    def test_missing_input_explained_without_disclosing_path(self):
        with tempfile.TemporaryDirectory() as directory:
            errors = StringIO()
            with redirect_stderr(errors):
                result = main([str(Path(directory) / 'sensitive-name.pdf'),
                               '-o', str(Path(directory) / 'output.csv')])
            self.assertEqual(result, 1)
            self.assertIn('Input PDF not found', errors.getvalue())
            self.assertNotIn('sensitive-name', errors.getvalue())

    def test_description_preserved_and_outgoing(self):
        row = parse_pages([fixture()])[0]
        self.assertEqual(row, {'date': '2025-04-05', 'merchant': 'ACME HOSTING PRIVATE REF 12345678',
                               'money_in_gbp': '0.00', 'money_out_gbp': '12.00'})

    def test_incoming_and_mapping(self):
        row = parse_pages([fixture('in', '112.00')], mapping={'ACME HOSTING': 'Hosting'})[0]
        self.assertEqual(row['merchant'], 'Hosting')
        self.assertEqual(row['money_in_gbp'], '12.00')

    def test_wrong_balance_stops(self):
        with self.assertRaisesRegex(ConversionError, 'reconcile'):
            parse_pages([fixture(balance='90.00')])

    def test_paid_headers_and_multiline_description(self):
        words = fixture()
        for item in words:
            if item['text'] == 'Money':
                item['text'] = 'Paid'
        words.append(word('CLIENT NAME', 100, 100))
        self.assertEqual(parse_pages([words])[0]['merchant'],
                         'ACME HOSTING PRIVATE REF 12345678 CLIENT NAME')
        rows = parse_pages([words], mapping={'CLIENT NAME': 'Client A'})
        self.assertEqual(rows[0]['merchant'], 'Client A')

    def test_rollover_and_same_date_transactions(self):
        words = fixture(date='31 Dec')
        words.extend([word('01 Jan', 30, 110), word('Shop', 100, 110),
                      word('10.00', 370, 110), word('78.00', 530, 110),
                      word('Another shop', 100, 130), word('2.00', 375, 130),
                      word('76.00', 530, 130)])
        rows = parse_pages([words], year=2025)
        self.assertEqual([r['date'] for r in rows], ['2025-12-31', '2026-01-01', '2026-01-01'])

    def test_unrecognised_amount_is_rejected(self):
        words = fixture()
        words[-2]['text'] = '-12.00'
        with self.assertRaisesRegex(ConversionError, 'unsupported amount'):
            parse_pages([words])

    def test_missing_year_stops(self):
        with self.assertRaisesRegex(ConversionError, '--year'):
            parse_pages([fixture(date='05 Apr')])
        self.assertEqual(parse_pages([fixture(date='05 Apr')], year=2025)[0]['date'], '2025-04-05')

    def test_unsupported_page_stops(self):
        for page in ([], [word('Scan', 10, 20)]):
            with self.assertRaises(ConversionError):
                parse_pages([page])

    def test_ambiguous_mapping_stops(self):
        with self.assertRaisesRegex(ConversionError, 'conflicting'):
            parse_pages([fixture()], mapping={'ACME': 'A', 'HOSTING': 'B'})

    def test_formula_label_is_escaped(self):
        self.assertEqual(parse_pages([fixture()], mapping={'ACME': '=1+1'})[0]['merchant'], "'=1+1")

    def test_unmatched_mapping_preserves_description(self):
        self.assertEqual(parse_pages([fixture()], mapping={'OTHER SHOP': 'Shopping'})[0]['merchant'],
                         'ACME HOSTING PRIVATE REF 12345678')

    def test_original_formula_description_is_escaped(self):
        words = fixture()
        words[-3]['text'] = '=1+1'
        self.assertEqual(parse_pages([words])[0]['merchant'], "'=1+1")

    def test_real_pdf_to_csv_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / 'source.pdf', Path(directory) / 'out.csv'
            write_pdf(source)
            self.assertEqual(main([str(source), '-o', str(output)]), 0)
            original = output.read_bytes()
            with output.open() as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['money_out_gbp'], '12.00')
            self.assertEqual(rows[0]['merchant'], 'ACME HOSTING PRIVATE REF 12345678')
            self.assertEqual(main([str(source), '-o', str(output)]), 1)
            self.assertEqual(output.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
