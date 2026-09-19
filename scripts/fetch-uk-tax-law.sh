#!/usr/bin/env bash
# Download current revised legislation from legislation.gov.uk and write plain-text copies.
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
rules_dir="${RULES_DIR:-$project_dir/docs/rules}"
stylesheet="$project_dir/scripts/legislation-to-text.xsl"
fetched_at="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
scratch_dir="$(mktemp -d "${TMPDIR:-/tmp}/uk-tax-law.XXXXXX")"
trap 'rm -rf "$scratch_dir"' EXIT

for command in curl xmllint xsltproc; do
  command -v "$command" >/dev/null || { echo "Missing required command: $command" >&2; exit 1; }
done

# topic|file name|official legislation.gov.uk document URL
sources=(
  'income-tax|income-tax-earnings-and-pensions-act-2003|https://www.legislation.gov.uk/ukpga/2003/1'
  'income-tax|income-tax-trading-and-other-income-act-2005|https://www.legislation.gov.uk/ukpga/2005/5'
  'income-tax|income-tax-act-2007|https://www.legislation.gov.uk/ukpga/2007/3'
  'income-tax|capital-allowances-act-2001|https://www.legislation.gov.uk/ukpga/2001/2'
  'capital-gains|taxation-of-chargeable-gains-act-1992|https://www.legislation.gov.uk/ukpga/1992/12'
  'vat|value-added-tax-act-1994|https://www.legislation.gov.uk/ukpga/1994/23'
  'national-insurance|social-security-contributions-and-benefits-act-1992|https://www.legislation.gov.uk/ukpga/1992/4'
  'tax-administration|taxes-management-act-1970|https://www.legislation.gov.uk/ukpga/1970/9'
  'pensions|finance-act-2004|https://www.legislation.gov.uk/ukpga/2004/12'
  'inheritance-tax|inheritance-tax-act-1984|https://www.legislation.gov.uk/ukpga/1984/51'
  'property-transactions|finance-act-2003-sdlt-england-northern-ireland|https://www.legislation.gov.uk/ukpga/2003/14'
  'property-transactions|land-and-buildings-transaction-tax-scotland-act-2013|https://www.legislation.gov.uk/asp/2013/11'
  'property-transactions|land-transaction-tax-wales-act-2017|https://www.legislation.gov.uk/anaw/2017/1'
)

# The official search feed is newest-first. Its first result is the current Finance Act.
finance_feed="$scratch_dir/finance-acts.xml"
curl --fail --location --retry 2 --silent --show-error 'https://www.legislation.gov.uk/ukpga/data.feed?title=Finance%20Act' --output "$finance_feed"
finance_url="$(xmllint --xpath "string((//*[local-name()='entry'][1]/*[local-name()='id'])[1])" "$finance_feed")"
finance_url="${finance_url/http:/https:}"
test -n "$finance_url" || { echo 'Could not find a Finance Act in the official search feed.' >&2; exit 1; }
sources+=("annual-finance|finance-act-latest|$finance_url")

mkdir -p "$rules_dir"
metadata_tmp="$scratch_dir/FETCHED_AT.md"
printf '# Fetch record\n\nFetched (UTC): %s\n\nSource: current revised legislation downloaded from legislation.gov.uk.\n\n## Documents\n' "$fetched_at" > "$metadata_tmp"

for entry in "${sources[@]}"; do
  IFS='|' read -r topic filename source_url <<< "$entry"
  destination_dir="$rules_dir/$topic"
  xml_file="$scratch_dir/$filename.xml"
  text_file="$destination_dir/$filename.txt"
  mkdir -p "$destination_dir"
  curl --fail --location --retry 2 --silent --show-error "$source_url/data.xml" --output "$xml_file"
  xmllint --noout "$xml_file"
  xsltproc --stringparam source_url "$source_url" --stringparam fetched_at "$fetched_at" "$stylesheet" "$xml_file" > "$text_file.tmp"
  mv "$text_file.tmp" "$text_file"
  printf -- '- [%s](%s)\n' "$filename.txt" "$source_url" >> "$metadata_tmp"
done

mv "$metadata_tmp" "$rules_dir/FETCHED_AT.md"
echo "Fetched ${#sources[@]} documents into $rules_dir at $fetched_at"
