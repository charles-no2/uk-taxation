# Public tax explanations

These are supplementary source documents, not taxpayer records. They explain
tax mechanics in less technical language than legislation and internal manuals.

The [19 September 2026 snapshot](20260919T080223011317Z/INDEX.md) contains 19
selected public guidance pages. Each retains original GOV.UK content JSON,
HTML and readable text, with official source, update date and retrieval date.
Multi-part guides retain all parts supplied by the content service.

The snapshot is mixed-year material, not a replacement for the 2025–26 annual
forms or rates. Its manifest records successes, errors, skipped attachments and
unfollowed child publications. A successful download does not establish legal
completeness. The requested `/income-tax-reliefs` address resolved to the narrower
maintenance-payments relief page; the saved title and source identify that scope.

Run `python3 scripts/fetch-tax-explainers.py` to create a new dated snapshot.
It does not overwrite the existing annual pack or prior explainer snapshots.
The script reuses the existing content conversion and attachment downloader;
attachment selection retains its 2026/undated filter. These selected guide pages
are not a recursive mirror of everything they link to.

Explanations based on these sources are in the [guidance summary](../guidance/SUMMARY.md)
and [rules summary](../rules/SUMMARY.md).
