# UK individual-tax legislation

Run `scripts/fetch-uk-tax-law.sh` from the project root to download the current revised versions of the selected Acts from legislation.gov.uk.

The script writes plain-text statutory copies under topical folders. It retains the legislation’s headings, provision numbers, numbered paragraphs, and wording; it removes XML tags and other structural markup. Each output file states its official source URL and fetch time. [FETCHED_AT.md](FETCHED_AT.md) records the most recent complete run.

The selected Acts cover income from trading and property, income-tax reliefs, capital allowances, capital gains, VAT, National Insurance, Self Assessment administration, pensions, inheritance tax, property-transfer taxes, and the current Finance Act. Supporting regulations, HMRC guidance, and court decisions are outside this collection.
