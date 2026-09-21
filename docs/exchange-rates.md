# HMRC exchange-rate downloader

Run from the project root with Python 3 (standard library only):

```sh
python3 scripts/fetch_exchange_rates.py --start 2025-04-06 --end 2026-04-05 --currency HKD --output exports/hmrc-monthly-hkd-2025-26.csv
```

The dates select calendar months, so this example fetches 13 months, April
2025 through April 2026. Repeat `--currency` for additional currencies.
Existing output is protected: select a new filename for a refresh.

Each row includes the original rate, its inverse, validity dates, source URL
and UTC retrieval timestamp. To convert HKD to GBP, divide by
`currency_units_per_gbp`. The inverse is provided to 12 decimal places;
use the original rate for calculations and apply rounding at the entry stage.
The script validates the entire requested range before creating the CSV.

These are HMRC monthly customs reference rates, not daily spot rates or
monthly averages. Fetching them does not establish the appropriate conversion
method for a particular Self Assessment entry. Conversion using rates on
individual interest-credit dates is a separate method; choose the applicable
method before using this output in a return.

Sources: [HMRC monthly publication](https://www.trade-tariff.service.gov.uk/exchange_rates/monthly),
[official service implementation](https://github.com/trade-tariff/trade-tariff-frontend/blob/main/app/controllers/exchange_rates_controller.rb).
The script uses the same public data service as that website, which was tested
on 20 September 2026. No private transaction data is transmitted.

Verification:

```sh
python3 -m unittest discover -s scripts -p test_fetch_exchange_rates.py
```
