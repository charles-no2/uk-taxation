# HMRC guidance

Start with [how personal taxation works](SUMMARY.md) for tax mechanics, examples
and nuances with references to the detailed rules. Use the
[topic and page-title index](INDEX.md) for more detailed lookup. Rebuild indexes after downloads with
`python3 scripts/build-source-indexes.py` (or use `--check` to check for drift).

Download the seven selected personal-tax manuals with Python 3.10 or newer.
No third-party packages are needed. Run from the project root:

```sh
python3 scripts/fetch-hmrc-manuals.py
```

The script uses GOV.UK's public content API, traverses each manual's contents
recursively, and saves one UTF-8 text file per page under
`docs/guidance/<manual>/<section-id>.txt`. Each manual also has `index.txt`.
The full collection can contain thousands of pages and take a substantial time.

```sh
# Continue an interrupted download, reusing saved pages.
python3 scripts/fetch-hmrc-manuals.py --resume

# Refresh one manual from GOV.UK.
python3 scripts/fetch-hmrc-manuals.py --manual property-income-manual

# Small live sample: three pages per manual, including its index.
python3 scripts/fetch-hmrc-manuals.py --max-pages 3
```

The default manuals are Employment Income, Savings and Investment, Property
Income, Capital Gains, Pensions Tax, Inheritance Tax, and National Insurance.
These are complete manuals: mixed personal/company material and historical
guidance are retained. Other manuals linked from body text are not downloaded.

Text retains titles, section identifiers, source URLs, publication/update dates,
retrieval dates, withdrawal notices, paragraph boundaries and link destinations.
Tables are rendered as rows with ` | ` between cells; complex visual layouts and
images are not reproduced (image alternative text is retained when present).
Wording is not summarised or interpreted. The output does not identify which
tax years a page applies to beyond what its original text states.

Each `manifest.json` records downloaded pages, contents links, failures and run
status (`in_progress`, `partial`, `failed`, `completed_with_gaps` or `complete`).
Missing sections (HTTP 404/410) and redirect records are listed in `gaps`, with
the check date and either the HTTP status or redirect destinations. No text file
is fabricated for these pages, and redirects are not followed or treated as the
original guidance. Existing older text files, if any, remain untouched; check the
manifest for gaps before using them. A run with only source gaps reports
`completed_with_gaps` and exits successfully. Every `--resume` run checks gaps
again and removes a gap if the original page becomes available.

A missing or redirected manual index is still a failure: its contents cannot be
traversed. Network failures, unexpected content and other request errors also
remain failures and produce a nonzero exit status. A limited sample is explicitly
marked `partial` unless it encounters a failure. Temporary server failures are
retried. Writes replace each output
file atomically. Run only one downloader against a given output directory at a time.

Resume is for completing the existing snapshot; omit `--resume` to fetch current
versions. Refreshes do not delete older files that have disappeared from the
contents. Use `--output <new-directory>` for a separate clean snapshot. The script
follows published contents links; it cannot discover orphan pages absent from them.

Source: https://www.gov.uk/government/collections/hmrc-manuals

These are HMRC's published interpretations, not legislation. Keep them distinct
from `docs/rules`; check source dates and applicability when using them.

## Additional Self Assessment manuals

The downloader also accepts `--manual` for Business Income, Capital Allowances,
Cryptoassets, Self Assessment, Residence and FIG Regime, Remittance Basis and
Domicile, and Trusts/Settlements/Estates. These were added as supporting sources
for the walkthrough. The default remains the original seven manuals.

See [data sources](../data-sources.md) for local copies, official fetch links,
annual forms, completion notes, helpsheets, calculation files and remaining
reference-data work.
