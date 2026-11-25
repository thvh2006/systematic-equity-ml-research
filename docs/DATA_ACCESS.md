# Data access and reproduction

## Public route: no provider data required

The repo includes generated test data, code, saved fits/ledgers, derived returns, diagnostics and a narrow first-rebalance quote slice. Install NumPy and run `verify_release.py`, the economic tests and notebook executor. These verify consistency of the saved study without downloading market prices or refitting a model.

## Private route: reproducing original intake and fitting

The original intake expects these private local files:

- `data/private/yahoo_pages/P2_ETF_history_20261124.csv`: captured visible history-table rows. Price rows contain ticker, English displayed date, Open, High, Low, Close, Adj Close, Volume. Action rows contain ticker, displayed date, displayed action. The importer accepts exactly these row shapes, rejects duplicates, and preserves original bytes for the receipt.
- `data/private/issuer_distributions.xlsx`: the issuer historical-distribution workbook in its captured layout, containing ticker, ex-date, payable date and income/capital-gain amounts.

The importer is tied to the reviewed 2017–2025 study window and the documented 2025 five-fund split convention. It is not a general downloader, automatic provider parser or current feed. Obtain source access only under terms applicable to you. Review the source units, distribution schema, corporate actions, special sessions and permitted use before import. Do not infer rights from download availability.

In an isolated new study directory, run `python scripts/intake_market.py`. It creates `data/private/market_2017_2025.csv`, the private event reconciliation and public receipt. The receipt hashes identify the exact original snapshot. A fresh download can differ due to provider revisions; do not replace the saved receipt to make an old freeze pass. Version the new study and record discrepancies instead.

The original experiment order was development → freeze → locked. The checked-in runner deliberately refuses to overwrite a frozen development or existing test. For a new experiment, use a separate copy/output namespace and prerecord its design. Do not delete the saved artifacts in this release to rerun it.

## Redistribution boundary

No bulk provider history or issuer workbook is published. The `.gitignore` and release exporter exclude `data/private`, private intake receipts, credentials and local caches. Public prices in the initial audit slice serve an economic reconciliation example. This project does not convey a market-data license or warrant provider accuracy. Read `SOURCES_AND_LIMITATIONS.md` and the research paper for source-vintage, rounding and execution limits.
