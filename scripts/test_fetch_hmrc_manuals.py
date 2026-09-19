"""Offline checks for content preservation and resumable traversal."""

import argparse
import importlib.util
import json
from io import BytesIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

spec = importlib.util.spec_from_file_location(
    "manuals", Path(__file__).with_name("fetch-hmrc-manuals.py"))
manuals = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manuals)


class ManualTests(unittest.TestCase):
    def test_source_gaps_and_recovery_through_real_fetch(self):
        root = '/hmrc-internal-manuals/capital-gains-manual'
        moved, missing = root + '/cg76921', root + '/cg99999'
        index = {'base_path': root, 'document_type': 'hmrc_manual', 'title': 'Manual',
                 'details': {'child_section_groups': [{'child_sections': [
                     {'base_path': p, 'title': 'Section'} for p in (moved, missing)]}]}}
        redirect = {'base_path': moved, 'document_type': 'redirect',
                    'redirects': [{'path': moved, 'destination': root, 'type': 'exact'}]}
        calls = []
        recovered = False

        def respond(request, **kwargs):
            path = request.full_url.removeprefix(manuals.ORIGIN + '/api/content')
            calls.append(path)
            if path == root:
                data = index
            elif recovered:
                data = {'base_path': path, 'document_type': 'hmrc_manual_section',
                        'title': 'Recovered', 'details': {'body': '<p>Guidance</p>'}}
            elif path == moved:
                data = redirect
            else:
                raise HTTPError(request.full_url, 404, 'Not Found', {}, None)
            return BytesIO(json.dumps(data).encode())

        with tempfile.TemporaryDirectory() as directory, patch.object(manuals, 'urlopen', side_effect=respond):
            args = argparse.Namespace(output=Path(directory), resume=False, max_pages=0, delay=0)
            folder = args.output / 'capital-gains-manual'
            self.assertEqual(manuals.download('capital-gains-manual', args), 0)
            state = json.loads((folder / 'manifest.json').read_text())
            self.assertEqual(state['status'], 'completed_with_gaps')
            self.assertEqual(state['gaps'][moved]['destinations'], [manuals.ORIGIN + root])
            self.assertEqual(state['gaps'][missing]['http_status'], 404)
            self.assertEqual(state['errors'], {})
            self.assertFalse((folder / 'cg76921.txt').exists())
            self.assertFalse((folder / 'cg99999.txt').exists())
            original = (folder / 'index.txt').read_bytes()
            calls.clear()
            args.resume = True
            self.assertEqual(manuals.download('capital-gains-manual', args), 0)
            self.assertEqual(calls, [moved, missing])
            recovered = True
            self.assertEqual(manuals.download('capital-gains-manual', args), 0)
            state = json.loads((folder / 'manifest.json').read_text())
            self.assertEqual(state['status'], 'complete')
            self.assertEqual(state['gaps'], {})
            self.assertEqual((folder / 'index.txt').read_bytes(), original)

    def test_missing_manual_root_is_failure(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(
                manuals, 'urlopen', side_effect=HTTPError('url', 404, 'Not Found', {}, None)):
            args = argparse.Namespace(output=Path(directory), resume=False, max_pages=0, delay=0)
            self.assertEqual(manuals.download('capital-gains-manual', args), 1)
            state = json.loads((args.output / 'capital-gains-manual' / 'manifest.json').read_text())
            self.assertEqual(state['status'], 'failed')

    def test_text_keeps_words_links_and_table_rows(self):
        text = manuals.plain_text(
            '<p>A <strong>tax</strong> &amp; <a href="/example">relief</a>.</p>'
            '<ul><li>First</li><li>Second</li></ul>'
            '<table><tr><th>Year</th><th>Amount</th></tr>'
            '<tr><td>2025</td><td>£100</td></tr></table>', manuals.ORIGIN)
        self.assertIn('A tax & relief (https://www.gov.uk/example).', text)
        self.assertIn('- First\n\n- Second', text)
        self.assertIn('Year | Amount |\n\n2025 | £100 |', text)

    def test_resume_follows_saved_contents_and_retries_failed_pages(self):
        root = '/hmrc-internal-manuals/property-income-manual'

        def document(path, sections):
            return {
                'base_path': path, 'title': 'Test page',
                'details': {'body': '<p>Original text.</p>',
                            'child_section_groups': [{'child_sections': [
                                {'base_path': p, 'title': 'Child'} for p in sections]}]},
            }

        documents = {
            root: document(root, [root + '/pim1000']),
            root + '/pim1000': document(root + '/pim1000', [root + '/pim1001']),
            root + '/pim1001': document(root + '/pim1001', []),
        }
        with tempfile.TemporaryDirectory() as directory:
            args = argparse.Namespace(output=Path(directory), resume=False,
                                      max_pages=1, delay=0)
            manifest = args.output / 'property-income-manual' / 'manifest.json'
            with patch.object(manuals, 'fetch', side_effect=lambda p, _: documents[p]):
                self.assertEqual(manuals.download('property-income-manual', args), 0)
            self.assertEqual(json.loads(manifest.read_text())['status'], 'partial')
            args.resume, args.max_pages = True, 0
            with patch.object(manuals, 'fetch', side_effect=URLError('offline')):
                self.assertEqual(manuals.download('property-income-manual', args), 1)
            self.assertEqual(json.loads(manifest.read_text())['status'], 'failed')
            with patch.object(manuals, 'fetch', side_effect=lambda p, _: documents[p]) as fetch:
                self.assertEqual(manuals.download('property-income-manual', args), 0)
                self.assertEqual(fetch.call_count, 2)
            state = json.loads(manifest.read_text())
            self.assertEqual(state['status'], 'complete')
            self.assertEqual(len(state['pages']), 3)
            self.assertEqual(state['errors'], {})
            self.assertIn('Original text.', (manifest.parent / 'pim1001.txt').read_text())


if __name__ == '__main__':
    unittest.main()
