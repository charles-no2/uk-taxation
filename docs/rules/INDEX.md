# Rules index

For explanations of how the tax rules work, read the [tax summary](SUMMARY.md) first.

Use this index for statutory wording, after identifying the issue in the [guidance index](../guidance/INDEX.md).
For return boxes and completion instructions, use [annual Self Assessment sources](../self-assessment/INDEX.md).

These are saved revised-law snapshots, not a verified set of rules for a particular tax year.
Check the official provision, commencement dates, amendments and territorial scope before applying it.
Supporting regulations and case law are not included. Topic folders are routing hints, not limits on an Act's scope.

## Choose an Act

Each heading index lists local line numbers so you can read a small relevant passage.

| Topic | Act / local text | Heading index | Source lines | Fetch time |
|---|---|---|---:|---|
| annual-finance | [Finance Act 2026](annual-finance/finance-act-latest.txt) | [Headings](annual-finance/finance-act-latest.index.md) — **CHECK: no headings found** | 7 | 2026-09-18T13:30:14Z |
| capital-gains | [Taxation of Chargeable Gains Act 1992](capital-gains/taxation-of-chargeable-gains-act-1992.txt) | [Headings](capital-gains/taxation-of-chargeable-gains-act-1992.index.md) | 20723 | 2026-09-18T13:30:14Z |
| income-tax | [Capital Allowances Act 2001](income-tax/capital-allowances-act-2001.txt) | [Headings](income-tax/capital-allowances-act-2001.index.md) | 16328 | 2026-09-18T13:30:14Z |
| income-tax | [Income Tax Act 2007](income-tax/income-tax-act-2007.txt) | [Headings](income-tax/income-tax-act-2007.index.md) | 32330 | 2026-09-18T13:30:14Z |
| income-tax | [Income Tax (Earnings and Pensions) Act 2003](income-tax/income-tax-earnings-and-pensions-act-2003.txt) | [Headings](income-tax/income-tax-earnings-and-pensions-act-2003.index.md) | 25006 | 2026-09-18T16:20:00.361186+00:00 |
| income-tax | [Income Tax (Trading and Other Income) Act 2005](income-tax/income-tax-trading-and-other-income-act-2005.txt) | [Headings](income-tax/income-tax-trading-and-other-income-act-2005.index.md) | 23503 | 2026-09-18T13:30:14Z |
| inheritance-tax | [Inheritance Tax Act 1984](inheritance-tax/inheritance-tax-act-1984.txt) | [Headings](inheritance-tax/inheritance-tax-act-1984.index.md) | 7645 | 2026-09-18T13:30:14Z |
| national-insurance | [Social Security Contributions and Benefits Act 1992](national-insurance/social-security-contributions-and-benefits-act-1992.txt) | [Headings](national-insurance/social-security-contributions-and-benefits-act-1992.index.md) | 7439 | 2026-09-18T13:30:14Z |
| pensions | [Finance Act 2004](pensions/finance-act-2004.txt) | [Headings](pensions/finance-act-2004.index.md) | 19392 | 2026-09-18T13:30:14Z |
| property-transactions | [Finance Act 2003](property-transactions/finance-act-2003-sdlt-england-northern-ireland.txt) | [Headings](property-transactions/finance-act-2003-sdlt-england-northern-ireland.index.md) | 15463 | 2026-09-18T13:30:14Z |
| property-transactions | [Land and Buildings Transaction Tax (Scotland) Act 2013](property-transactions/land-and-buildings-transaction-tax-scotland-act-2013.txt) | [Headings](property-transactions/land-and-buildings-transaction-tax-scotland-act-2013.index.md) | 5321 | 2026-09-18T13:30:14Z |
| property-transactions | [Land Transaction Tax and Anti-avoidance of Devolved Taxes (Wales) Act 2017](property-transactions/land-transaction-tax-wales-act-2017.txt) | [Headings](property-transactions/land-transaction-tax-wales-act-2017.index.md) | 7097 | 2026-09-18T13:30:14Z |
| tax-administration | [Taxes Management Act 1970](tax-administration/taxes-management-act-1970.txt) | [Headings](tax-administration/taxes-management-act-1970.index.md) | 6050 | 2026-09-18T13:30:14Z |
| vat | [Value Added Tax Act 1994](vat/value-added-tax-act-1994.txt) | [Headings](vat/value-added-tax-act-1994.index.md) | 13081 | 2026-09-18T13:30:14Z |

## Targeted lookup

Run from the repository root:

```sh
rg -n -i 'property business|rent.a.room' docs/rules/income-tax/*.index.md
rg -n -i 'notice.*return|amendment' docs/rules/tax-administration/*.index.md
# Use the source-line column, not rg's index-file line number.
sed -n '40,95p' docs/rules/income-tax/income-tax-act-2007.txt
```

Search headings first; if necessary search the selected Act's text. Heading extraction is a navigation aid
and may omit headings or include quoted provisions; it does not establish legal coverage.

## Source limitations

Any Act flagged above with no headings needs a completeness check before use. A file containing
only introductory text is not a full Act; do not infer that a rule is absent.
The filename `latest` is not a freshness guarantee. Consult the official source when needed.

## Refresh

Regenerate after source downloads with `python3 scripts/build-source-indexes.py`.
Use `--check` to detect stale indexes without writing. This does not fetch or legally verify sources.
See [download instructions](README.md) and [fetch record](FETCHED_AT.md).
