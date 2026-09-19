# Guidance index

For explanations of how the taxes work, read the [tax summary](SUMMARY.md) first.

Start here to locate HM Revenue & Customs (HMRC) interpretations. These are not legislation.

1. Select a topic below, then search that manual's page-title index.
2. Open only the matching text files. For a known identifier, open its lowercase `.txt` file directly.
3. Check the page's source, update/retrieval dates, withdrawal notices and tax-year applicability.
   Check the manifest for gaps/errors; a completed crawl is not proof of complete tax coverage.

For form boxes and annual completion notes, start at [Self Assessment sources](../self-assessment/INDEX.md).
For statutory wording, use the [rules index](../rules/INDEX.md).

## Choose a manual

Page counts include the manual landing page. Status and gap counts come from saved manifests.

| Topic / search terms | Page-title index | Indexed pages | Run status | Gaps / errors / missing files |
|---|---|---:|---|---|
| Self-employment, trading profits, expenses, losses, partnerships | [business-income-manual](business-income-manual/INDEX.md) | 2079 | complete | 0 / 0 / 0 |
| Business equipment, capital expenditure, allowances | [capital-allowances-manual](capital-allowances-manual/INDEX.md) | 697 | complete | 0 / 0 / 0 |
| Asset disposals, shares, property gains, losses, reliefs | [capital-gains-manual](capital-gains-manual/INDEX.md) | 3147 | completed_with_gaps | 1 / 0 / 0 |
| Cryptoassets, tokens, trading and disposals | [cryptoassets-manual](cryptoassets-manual/INDEX.md) | 130 | complete | 0 / 0 / 0 |
| Employment pay, benefits, expenses, share schemes, pension income | [employment-income-manual](employment-income-manual/INDEX.md) | 2843 | complete | 0 / 0 / 0 |
| Inheritance, gifts, estates; usually outside the personal return | [inheritance-tax-manual](inheritance-tax-manual/INDEX.md) | 3252 | complete | 0 / 0 / 0 |
| National Insurance contributions, employment status, contribution classes | [national-insurance-manual](national-insurance-manual/INDEX.md) | 1753 | completed_with_gaps | 1 / 0 / 0 |
| Pension contributions, relief, annual and other allowance charges | [pensions-tax-manual](pensions-tax-manual/INDEX.md) | 528 | complete | 0 / 0 / 0 |
| Rental income, landlord expenses, property businesses, Rent a Room | [property-income-manual](property-income-manual/INDEX.md) | 226 | complete | 0 / 0 / 0 |
| Residence, foreign income and gains regime, overseas workday relief | [residence-and-fig-regime-manual](residence-and-fig-regime-manual/INDEX.md) | 224 | complete | 0 / 0 / 0 |
| Domicile, remittance basis, historical and transitional overseas cases | [residence-domicile-and-remittance-basis](residence-domicile-and-remittance-basis/INDEX.md) | 451 | complete | 0 / 0 / 0 |
| Interest, dividends, savings, investment income | [savings-and-investment-manual](savings-and-investment-manual/INDEX.md) | 288 | complete | 0 / 0 / 0 |
| Return administration, filing, payments, amendments, enquiries | [self-assessment-manual](self-assessment-manual/INDEX.md) | 1115 | completed_with_gaps | 3 / 0 / 0 |
| Trusts, settlements, estate income, beneficiaries | [trusts-settlements-and-estates-manual](trusts-settlements-and-estates-manual/INDEX.md) | 927 | complete | 0 / 0 / 0 |

## Targeted lookup

Run from the repository root:

```sh
rg -n -i 'rent a room|repairs' docs/guidance/property-income-manual/INDEX.md
rg -n -i 'staking|airdrop' docs/guidance/cryptoassets-manual/INDEX.md
# If the topic is unclear, search titles across all manuals, not every source body.
rg -n -i 'foreign tax' docs/guidance/*/INDEX.md
```

A title search can miss a concept discussed only in the body. Follow the matching page's contents/links
or search within the selected manual as a fallback. No match does not mean no applicable rule.

## Refresh

Generated offline with `python3 scripts/build-source-indexes.py`.
Run it after downloading sources; `--check` detects stale indexes without writing.
Only manifest-listed successful pages are indexed; unlisted leftover files are not treated as current.
See [download instructions](README.md). Index generation does not refresh or verify official sources.
