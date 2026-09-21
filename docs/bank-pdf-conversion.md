# Local bank PDF conversion

For a folder containing UK/Hong Kong statements and P60/P11D forms, use the newer
[batch converter](tax-pdf-batch-conversion.md). It has separate layout handlers and
removes personal transfer descriptions by default. The older single-file converter
below preserves descriptions and is not a redaction tool.

This converter reads text-based UK current-account PDFs with a single-line
`Date`, `Description`/`Details`/`Transactions`/`Type`, `Money in`/`Paid in`,
`Money out`/`Paid out`, and `Balance` table header. It is intended as a starting
point for HSBC and Barclays layouts, not a guarantee for every statement version.
It has not been validated against your actual statements. Prefer bank CSV exports
when available. Scans, credit-card statements, overdraft balances, multi-line
headers, and pages without transaction tables are rejected.

Run the converter yourself in a terminal. It uses no network services and does
not upload PDFs. Asking a cloud assistant to read raw PDFs or print their text
would expose that content to the assistant, even if the files are local.

```sh
python3 -m venv .venv-bank
.venv-bank/bin/python -m pip install -r scripts/bank-pdf-requirements.txt
mkdir -p private exports
.venv-bank/bin/python scripts/bank_pdf_to_csv.py private/hsbc.pdf \
  --year 2025 --output exports/hsbc.csv
.venv-bank/bin/python scripts/bank_pdf_to_csv.py private/barclays.pdf \
  --year 2025 --output exports/barclays.csv
```

`--year` means the first transaction's calendar year, not the tax year's ending
year. Explicit row years take precedence; December-to-January rollover is
supported for chronological statements. Each invocation processes one PDF.
Existing outputs are never overwritten. Output is written only after all pages
parse successfully. Errors omit source text and filenames.

Only `date,merchant,money_in_gbp,money_out_gbp` are exported. Both amount columns
contain positive numbers or zero. Statement account headers and balances are not
exported. Original transaction descriptions are preserved in `merchant`, including
names and references within those descriptions. Wrapped lines are joined with
spaces. Descriptions beginning with spreadsheet formula characters are prefixed
with an apostrophe to prevent formula execution.

Optionally replace selected descriptions with labels by creating
`private/merchant-map.json`, for example:

```json
{
  "ACME HOSTING": "Hosting",
  "EXAMPLE CLIENT LTD": "Client A"
}
```

Then add `--merchant-map private/merchant-map.json`. Matching is case-insensitive
substring matching; use specific snippets. Conflicting matches stop conversion.
Matching descriptions are replaced with the supplied label; unmatched descriptions
remain intact. Omit this option to preserve all descriptions. Keep the mapping private.

Before sharing, review the CSV locally, check its date range, count transactions,
and compare incoming/outgoing totals to the originals. The converter checks
running balances where present, but that is not a complete extraction guarantee.
Dates, amounts and merchant labels can still identify people or disclose sensitive
activity: this is reduced-detail data, not guaranteed anonymous data. Preserve
original statements securely. Keep accounts separate during analysis so transfers
between your own accounts can be identified; don't treat every incoming payment
as taxable income or every outgoing payment as deductible.

Tests use fictional data only:

```sh
.venv-bank/bin/python -m unittest discover -s scripts -p 'test_bank_pdf_to_csv.py'
```
