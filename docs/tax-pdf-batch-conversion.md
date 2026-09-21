# Private PDF to CSV conversion

`scripts/tax_pdfs_to_csv.py` converts a local folder into separate CSV files,
using document-specific handlers. It uses `pdfplumber` locally, with no network
calls or external extraction service. The handlers are tested with fictional
data, including a generated PDF. These tests verify parsing and the checks below,
not a manual comparison of every row in your documents.

## Run locally

From the repository root, using the existing Python environment:

```sh
.venv-bank/bin/python scripts/tax_pdfs_to_csv.py private/pdfs \
  --output exports/tax-csvs \
  --source-index private/tax-csv-source-index.json
```

If the environment does not exist yet:

```sh
python3 -m venv .venv-bank
.venv-bank/bin/python -m pip install -r scripts/bank-pdf-requirements.txt
```

Both destinations must be new. Input PDFs are never modified. `private/`,
`exports/` and CSV files are already excluded from Git in this workspace.

The optional source index contains original filenames and must remain private,
outside the export directory. It connects `document_001` in the report to its
original PDF. Document and account IDs are assigned within each run; do not assume
they stay the same if you change the input batch.

## Handlers

| Handler | Supported extraction |
| --- | --- |
| `hsbc_uk` | Premier account transaction tables, wrapped card descriptions, explicit row years, carried balances |
| `hsbc_hk_premier` | Premier deposit/withdrawal tables, including separate foreign currency balances |
| `hsbc_hk_savings` | Hong Kong dollar savings tables, opening-year rows and compact labels |
| `barclays` | Current account and cash ISA transaction tables; an ISA is an Individual Savings Account |
| `p60` | Previous/current employment pay and deducted tax, annual totals, final tax code; recognized National Insurance and loan deduction rows |
| `p11d` | Populated pound-value boxes in sections A–E and I–N, retaining section, occurrence and monetary column |
| `hsbc_investment_tax_certificate` | HSBC UK consolidated investment certificate: GBP UK unit trust/OEIC dividend paid, tax credits and equalisation, plus explicit no-income sections |

Detection uses document contents. To force a handler on a single file or a batch
of the same layout, add, for example, `--handler hsbc_hk_savings`.
These are handlers for recognizable layouts, not universal parsers for every
version of a bank's statements or payroll software.

Investment certificates use the form-file columns below. Dividend paid, tax
credits and equalisation are separate fields, not amounts to add together.
The tax-year end comes from the printed reporting period, not the issue date.
Explicit `No income received` sections produce zero values; missing sections,
populated alternative income sections and additional monetary schedules require
review. The supported layout is the GBP summary with UK unit trust/OEIC income
(OEIC means open-ended investment company). Names and account details are omitted.

P60 statutory payment fields and alternate layouts need additional handling when
populated: unaccounted-for decimal amounts stop the export. P11D populated car,
van and loan monetary boxes are explicitly rejected. P11D empty boxes are omitted,
not treated as zero. P11D cost and cash-equivalent columns may repeat a value;
they are distinct fields and must not be added together. Free-text form descriptions,
vehicle details and employer identifiers are not exported.

## Output and privacy

Each successfully parsed PDF produces `document_NNN.csv`. Bank files contain:

```text
source_id,page,account_id,account_type,date,currency,merchant,transaction_type,money_in,money_out
```

Form files contain:

```text
source_id,page,form,tax_year_end,field,value,currency
```

The script excludes account-holder names, addresses, account numbers, sort codes,
National Insurance numbers, payroll numbers, original filenames and raw descriptions
from exports. Account numbers are used only in memory to group statements under
neutral account IDs. Merchant labels come from card transaction lines, with common
reference patterns removed. Non-card payment descriptions default to
`Transfer / other payment`; they can contain personal names, so they are not copied.
Interest, bank fees, cash withdrawals and credit card payments receive generic labels.
Form fields use a fixed vocabulary rather than copying personal text.

For specific transfers, direct debits or merchants, provide an optional private
JSON mapping of description snippets to labels you have checked:

```json
{
  "EXAMPLE EMPLOYER LTD": "Employer A salary",
  "EXAMPLE PERSONAL TRANSFER": "Own-account transfer",
  "EXAMPLE ENERGY": "Electricity supplier"
}
```

Add `--merchant-map private/merchant-map.json`. Matching ignores case. Conflicting
labels reject that document. Mapping values are exported exactly, apart from
spreadsheet formula protection, so do not put personal information in them.
Card merchant names can themselves identify people or sensitive activity; review
the reduced-detail CSVs locally before sharing. This is not guaranteed anonymization.

## Validation and review

`conversion_report.csv` lists every PDF, its handler, row count, balance-check count
and either `converted` or `needs_review`. Errors omit filenames and source text.
One rejected document does not prevent the remaining documents from converting.
The command exits with status 1 if any document needs review; a successful batch
returns 0. A rejected parse produces no transaction/form CSV for that document.

Statements require an opening balance and reconcile subsequent printed balances
using exact decimal arithmetic, independently for each currency. The final payment
must have a reconciled running or closing balance. Unreadable pages, ambiguous dates,
unexpected monetary columns and unsupported layouts stop that document. A statement
containing only an opening balance is flagged for review. Informational pages are
not exported. Balance reconciliation cannot prove that all source information was
captured; compare row counts and totals to the PDFs before relying on them.

For dates without years, the script uses a `_YYYYMMDD.pdf` filename suffix as the
statement end date, or the latest full printed date if there is no suffix. A row
later than that end date is assigned to the preceding year. This assumes statements
cover at most one year; a mismatched suffix or a longer interval requires review.

Currencies remain unchanged: Hong Kong dollars and US dollars are not converted
to pounds. All statement dates are retained, including dates outside your tax year.
There is no automatic classification of taxable income or deductible expenses.
Account summaries, balances, portfolio valuations and exchange-rate tables are
not exported as transactions. Overlapping statements are not deduplicated.

## Tests

```sh
.venv-bank/bin/python -m unittest discover -s scripts -p 'test*pdf*csv.py'
```

Tests use fictional accounts, names and amounts. They cover the four statement
handlers, both form handlers, wrapped rows, year rollover, multiple currencies,
balance failures, redaction, spreadsheet formula protection, batch reports and
refusal to overwrite existing exports.
