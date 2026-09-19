# Data sources for the Self Assessment walkthrough

Reference collection started on **18 September 2026**. The intended tool suggests entries and explains fields; the user completes and submits their own return. No taxpayer records are included or required in this folder.

The initial annual pack is **2025–26: 6 April 2025 to 5 April 2026**. HM Revenue & Customs (HMRC) labels these forms **2026**. General guidance and manuals are current snapshots containing material for multiple years; they are not automatically 2025–26 rules.

## What is stored and where to fetch it

The [downloaded-source index](self-assessment/INDEX.md) links each publication to its official refresh page, local readable text and downloaded attachments. The [download manifest](self-assessment/manifest.json) records retrieval dates, source update dates, attachment URLs, file sizes, SHA-256 checksums, excluded older attachments and any failures. A checksum is a fingerprint used to check that a downloaded file has not changed.

| Information needed | Local location | Official source / fetch entry point | Purpose |
|---|---|---|---|
| Main individual return (SA100), main completion notes (SA150), and supplementary forms with their notes | [2025–26 forms](self-assessment/2025-26/forms/) | [Main return and supplementary-page links](https://www.gov.uk/guidance/how-to-complete-your-self-assessment-tax-return-for-last-tax-year) | Exact field labels, box numbers, declarations, section selection and completion instructions |
| Public guidance on completing each section | [Completion guidance](self-assessment/completion-guidance/) | [Get help filling in your return](https://www.gov.uk/government/collections/get-help-filling-in-your-self-assessment-tax-return) | User-facing explanations for employment, trading, property, foreign income, gains, pensions, giving, reliefs and loans |
| Employment helpsheets | [2025–26 helpsheets](self-assessment/2025-26/helpsheets/) | [Employment forms and helpsheets](https://www.gov.uk/government/collections/self-assessment-helpsheets-employment) | Detailed instructions and supporting calculations for employment cases |
| Self-employment and partnership helpsheets | [2025–26 helpsheets](self-assessment/2025-26/helpsheets/) | [Self-employment and partnerships](https://www.gov.uk/government/collections/self-assessment-helpsheets-self-employment-and-partnerships) | Profit adjustments, losses, allowances and partnership cases |
| Capital gains helpsheets | [2025–26 helpsheets](self-assessment/2025-26/helpsheets/) | [Capital gains forms and helpsheets](https://www.gov.uk/government/collections/self-assessment-helpsheets-capital-gains) | Asset calculations, losses and reliefs |
| Foreign-income helpsheets | [2025–26 helpsheets](self-assessment/2025-26/helpsheets/) | [Foreign forms and helpsheets](https://www.gov.uk/government/collections/self-assessment-helpsheets-foreign) | Foreign income, foreign tax and related claims |
| Residence and foreign income and gains guidance | [2025–26 helpsheets](self-assessment/2025-26/helpsheets/) | [Residence forms and helpsheets](https://www.gov.uk/government/collections/self-assessment-helpsheets-residence-and-remittance-basis) | Residence questions, relief claims and transitional situations |
| Trust and estate income guidance | [2025–26 helpsheets](self-assessment/2025-26/helpsheets/) | [Trust and estate forms and helpsheets](https://www.gov.uk/government/collections/self-assessment-helpsheets-trusts-and-estates) | Income received from trusts and estates; distinguish an individual's return from a trustee's return |
| Tax calculation specification, mappings, test-case generator, special and exclusion cases | [2025–26 calculations](self-assessment/2025-26/calculations/) | [2026 technical specifications](https://www.gov.uk/government/publications/self-assessment-technical-specifications-2026-for-individual-returns) | Check suggested calculated values; needed for a tax-bill estimate, not for every field explanation |
| Rates, thresholds and allowances | [Rates and allowances](self-assessment/rates-and-allowances/) | [Income Tax](https://www.gov.uk/government/publications/rates-and-allowances-income-tax), [National Insurance](https://www.gov.uk/government/publications/rates-and-allowances-national-insurance-contributions), [Capital Gains Tax](https://www.gov.uk/government/publications/rates-and-allowances-capital-gains-tax) | Source material for a year-specific rate table; includes current and historical material |
| Regional income-tax rules | [Rates and allowances](self-assessment/rates-and-allowances/) | [Scotland](https://www.gov.uk/scottish-income-tax), [Wales](https://www.gov.uk/welsh-income-tax) | Determine the applicable regional treatment, then select the correct year |
| Dividends, savings, trading/property allowances, pension relief and student-loan guidance | [Rates and allowances](self-assessment/rates-and-allowances/) and [completion guidance](self-assessment/completion-guidance/) | [Dividends](https://www.gov.uk/tax-on-dividends), [savings](https://www.gov.uk/apply-tax-free-interest-on-savings), [trading/property allowances](https://www.gov.uk/guidance/tax-free-allowances-on-property-and-trading-income), [pension relief](https://www.gov.uk/tax-on-your-private-pension/pension-tax-relief), [student loans](https://www.gov.uk/government/publications/student-loans-a-guide-to-terms-and-conditions) | Explain related fields and identify additional annual thresholds required |
| Filing eligibility, deadlines, records, corrections and submission routes | [Filing guidance](self-assessment/filing-guidance/) | [Self Assessment returns](https://www.gov.uk/self-assessment-tax-returns) | Decide which process applies and explain the user's next steps |
| Payments on account (advance instalments towards a later tax bill) | [Filing guidance](self-assessment/filing-guidance/) and [calculations](self-assessment/2025-26/calculations/) | [Payments on account](https://www.gov.uk/understand-self-assessment-bill/payments-on-account) | Distinguish return-year liability from the amount due for payment |
| Making Tax Digital eligibility (the digital reporting process for qualifying taxpayers) | [Filing guidance](self-assessment/filing-guidance/) | [Check eligibility](https://www.gov.uk/guidance/check-if-youre-eligible-for-making-tax-digital-for-income-tax) | Identify when a conventional annual-return walkthrough is insufficient |

The annual forms include additional information (SA101), employment (SA102), short/full self-employment (SA103S/SA103F), short/full partnership income (SA104S/SA104F), UK property (SA105), foreign income (SA106), trust/estate income (SA107), capital gains (SA108), residence and foreign income and gains (SA109), and tax calculation summary (SA110). Specialist forms for ministers of religion, parliamentarians and Lloyd's underwriters are also retained where linked by the main return page. Downloading these does not establish that the future tool supports every specialist case.

## Supporting manuals and legislation

Manuals explain HMRC's interpretation. Legislation provides the statutory wording. Both may include historical provisions, company material or matters outside an individual's return.

Each manual folder contains an `index.txt`, individual section text files and a `manifest.json` describing completeness, missing pages and redirects. Body-text links to other manuals are not automatically downloaded.

| Manual | Local copy | Official source |
|---|---|---|
| Business Income — added for trading and self-employment | [Business Income](guidance/business-income-manual/index.txt) | [Fetch](https://www.gov.uk/hmrc-internal-manuals/business-income-manual) |
| Capital Allowances — added for qualifying business expenditure | [Capital Allowances](guidance/capital-allowances-manual/index.txt) | [Fetch](https://www.gov.uk/hmrc-internal-manuals/capital-allowances-manual) |
| Cryptoassets — added for cryptocurrency cases | [Cryptoassets](guidance/cryptoassets-manual/index.txt) | [Fetch](https://www.gov.uk/hmrc-internal-manuals/cryptoassets-manual) |
| Self Assessment — added for administration and processing | [Self Assessment](guidance/self-assessment-manual/index.txt) | [Fetch](https://www.gov.uk/hmrc-internal-manuals/self-assessment-manual) |
| Residence and FIG Regime — FIG means foreign income and gains | [Residence and FIG](guidance/residence-and-fig-regime-manual/index.txt) | [Fetch](https://www.gov.uk/hmrc-internal-manuals/residence-and-fig-regime-manual) |
| Remittance Basis and Domicile — includes historical and transitional guidance | [Remittance and domicile](guidance/residence-domicile-and-remittance-basis/index.txt) | [Fetch](https://www.gov.uk/hmrc-internal-manuals/residence-domicile-and-remittance-basis) |
| Trusts, Settlements and Estates | [Trusts](guidance/trusts-settlements-and-estates-manual/index.txt) | [Fetch](https://www.gov.uk/hmrc-internal-manuals/trusts-settlements-and-estates-manual) |
| Employment Income — existing | [Employment](guidance/employment-income-manual/index.txt) | [Fetch](https://www.gov.uk/hmrc-internal-manuals/employment-income-manual) |
| Savings and Investment — existing | [Savings](guidance/savings-and-investment-manual/index.txt) | [Fetch](https://www.gov.uk/hmrc-internal-manuals/savings-and-investment-manual) |
| Property Income — existing | [Property](guidance/property-income-manual/index.txt) | [Fetch](https://www.gov.uk/hmrc-internal-manuals/property-income-manual) |
| Capital Gains — existing | [Capital gains](guidance/capital-gains-manual/index.txt) | [Fetch](https://www.gov.uk/hmrc-internal-manuals/capital-gains-manual) |
| Pensions Tax — existing | [Pensions](guidance/pensions-tax-manual/index.txt) | [Fetch](https://www.gov.uk/hmrc-internal-manuals/pensions-tax-manual) |
| National Insurance — existing | [National Insurance](guidance/national-insurance-manual/index.txt) | [Fetch](https://www.gov.uk/hmrc-internal-manuals/national-insurance-manual) |
| Inheritance Tax — existing; supporting background rather than a core annual-return reference | [Inheritance Tax](guidance/inheritance-tax-manual/index.txt) | [Fetch](https://www.gov.uk/hmrc-internal-manuals/inheritance-tax-manual) |

The missing [Income Tax (Earnings and Pensions) Act 2003](rules/income-tax/income-tax-earnings-and-pensions-act-2003.txt) has been added, with its [original XML](rules/income-tax/income-tax-earnings-and-pensions-act-2003.xml). Fetch from the [official Act](https://www.legislation.gov.uk/ukpga/2003/1) or [XML endpoint](https://www.legislation.gov.uk/ukpga/2003/1/data.xml). Other existing Acts and their sources are listed in the [legislation fetch record](rules/FETCHED_AT.md).

Current revised legislation is not a verified historical snapshot for every supported tax year. Earlier Finance Acts, commencement provisions, regulations and archived versions may need to be fetched for particular rules. Use the [official legislation service](https://www.legislation.gov.uk/) and the citations in each form's notes or relevant manual; do not assume the latest Finance Act provides every annual rule.

## Information still to assemble for the tool

These are required derived reference datasets, not missing taxpayer documents. Downloading the source library does not create them.

| Needed dataset | Content to record | Sources / remaining work |
|---|---|---|
| Supported scope | Tax years, individual taxpayer circumstances, sections and filing routes supported; explicit handling for unsupported situations | Select from the downloaded forms, completion guidance and filing guidance |
| Field catalogue | Tax year; form; section; box number; exact label; data type; permitted values; required/optional status; source citation | Extract and review the annual forms and notes; preserve form layout in the original PDF |
| Section-selection rules | Questions that establish applicable pages, short/full choices, repeated employment/business sections and dependencies | Main-return questions, supplementary notes and completion guidance |
| Field explanations | What to enter; inclusions/exclusions; where the user finds it; blank versus zero; gross versus net; totals; rounding; currency; dates; links to supporting instructions | Annual notes and helpsheets, supported by manuals |
| Online-field mapping | Actual online question labels and order, conditional screens, help text and their correspondence with form boxes | Verify against the relevant year's official online journey and public guidance. Downloaded technical mappings alone are not proof of the screen layout. No authenticated screens were captured |
| Annual parameter table | Rates, bands, allowances, relief limits, loan-plan thresholds, regional rules, effective dates and authoritative source references | Extract only the applicable year from rates publications and annual calculation specification; reconcile differences before use |
| Calculation and validation rules | Per-field arithmetic, cross-field consistency, mutually exclusive claims, loss/carry-forward handling, missing-information checks and unsupported cases | Notes, worksheets, technical specification, special/exclusion cases and manuals |
| Checked sample entries | Fictional input facts, expected sections/fields/amounts, explanation, supporting source and review status | Adapt official examples and worksheets; use the downloaded test-case generator if calculating tax. No bespoke sample-return suite has been created |
| Source applicability and refresh record | Source version, tax years covered, effective dates, withdrawn status, local file, official URL, review date and known gaps | Download manifests supply retrieval metadata; tax-year applicability still requires review |

A description such as “consult the employer's annual pay-and-tax certificate” belongs in the reference data. The user's actual certificate, bank statement, personal identifiers and transaction data do not.

## Refreshing the downloads

From the project root:

```sh
# Refresh the 2025–26 forms, notes, helpsheets, public guidance and calculations.
python3 scripts/fetch-self-assessment-sources.py

# Refresh one additional manual (repeat --manual to select others).
python3 scripts/fetch-hmrc-manuals.py --manual business-income-manual

# Finish an interrupted manual download using the saved snapshot.
python3 scripts/fetch-hmrc-manuals.py --manual business-income-manual --resume

# Refresh the complete selected legislation collection, now including the 2003 Act.
bash scripts/fetch-uk-tax-law.sh
```

The reference downloader requires Python 3.10 or newer and uses only its standard library. If `pdftotext` is installed, it also extracts layout-preserving text from PDFs. Original PDF, spreadsheet, OpenDocument and archive attachments remain unchanged; downloaded spreadsheets and archives are not executed. HTML publications retain the source JSON, body HTML and readable text.

The reference script is deliberately configured for the **2026 forms / 2025–26 return**, not “whatever year is latest”. It selects attachments labelled 2026 and undated supporting attachments, and records skipped older attachments. Some mixed-year publications and undated attachments are retained for context: review their applicability. It follows the selected collections, relevant forms, HTML attachments and helpsheet links; it does not mirror every linked external page or every link inside a PDF. Welsh attachments are retained where included in the selected publications; this is not a separate complete Welsh-language crawl.

The main-return landing page is a rolling URL. The script stops that page's download if it no longer contains the 2026 main form; replace the seed with the archived 2025–26 publication when necessary. To support another year, create a separate annual pack and update the selection rules, rather than relabelling this pack.

Refreshes replace successfully fetched files but do not remove older files. Use the manifest and generated index to identify the current successful run; do not treat every leftover file as current. For an immutable snapshot, retain a separate copy before refreshing. `--resume` on the manual downloader completes the saved snapshot; it is not a freshness check for already-downloaded pages.

## Completeness and limitations

Consult [the reference manifest](self-assessment/manifest.json) and each manual's manifest for the actual run status. A `complete` status means the downloader completed its selected traversal; it does not mean every possible Self Assessment source or taxpayer circumstance has been covered.

The original collection already recorded a redirected capital-gains section and an unavailable National Insurance section. The added Self Assessment Manual also records three unavailable sections: `sam32020`, `sam114040` and `sam122200` (HTTP 404). See its [manifest](guidance/self-assessment-manual/manifest.json) for their exact source URLs and check dates. These gaps are preserved explicitly rather than filled with invented text. They must be assessed if a supported field relies on the missing section.

This collection supplies reference material. Field mappings, reviewed decision rules, year-specific parameter tables and checked sample answers remain to be assembled before it can support a dependable walkthrough.
