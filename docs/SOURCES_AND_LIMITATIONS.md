# Sources, assumptions and release scope

Reviewed24November2026. This repository publishes original code, a fictional engineering fixture, a small independent-review quote slice and derived retrospective study outputs. Bulk Yahoo price histories and the issuer distribution workbook stay private; no raw-data redistribution license is asserted.

| Evidence | Source | Application and limit |
|---|---|---|
| Daily opening/closing prices, volume, split markers | Yahoo Finance Historical Data pages for XLB/XLE/XLF/XLI/XLK/XLP/XLU/XLV/XLY/SPY; example https://finance.yahoo.com/quote/XLK/history/ | Visible tables captured24November2026. Prices rounded to two decimals, split-adjusted display basis, retrospective corrections possible. Source receipt stores hashes. This is not an institutionally validated feed. |
| Cash distributions and payment dates | State Street Historical Distributions workbook, linked at https://www.ssga.com/us/en/individual/resources/documents/etf-dividend-distributions | 362 study-window cash events checked; issuer amounts and payable dates drive the ledger. One SPY2021-12-17 discrepancy resolved by issuer precedence. Full private reconciliation retained. |
| Five 2-for-1 splits | State Street20November2025 press release: https://investors.statestreet.com/investor-news-events/press-releases/news-details/2025/State-Street-Investment-Management-Announces-Share-Splits-for-Five-Select-Sector-SPDR-ETFs/default.aspx | Effective5December2025. Reconstructed18November closes differ by at most$0.01 from published prices. Does not establish auction liquidity or all source fields. |
| XLF2016 policy/spinoff | SEC disclosure https://www.sec.gov/Archives/edgar/data/1064641/000119312516719418/R2.htm | In-kind XLRE distribution motivates starting the simpler fixed-fund study in2017. The1.231 Yahoo event must not be applied as an ordinary fractional share split. |
| Sessions/hours | NYSE https://www.nyse.com/trade/hours-calendars and2025 mourning closure https://www.nasdaqtrader.com/TraderNews.aspx?id=ETA2024-87 | Rule calendar with2018/2025 exceptions exactly matches observed SPY sessions in2017–2025. Signal timestamp16:15ET is conservatively later than early closes. |
| Temporal validation | Official scikit-learn https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html | Motivates ordered evaluation; local code additionally groups panel dates and requires label maturity. No claim that ordinary TimeSeriesSplit alone purges overlapping labels. |
| ML comparison | Gu, Kelly and Xiu,2020, https://doi.org/10.1093/rfs/hhaa009 | Comparative asset-pricing motivation only. A nine-fund technical study is not a replication of a broad stock-characteristics panel or a guarantee of nonlinear model gains. |
| Research selection risk | Bailey et al.,2015, https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf | Bounded trials and a saved holdout reduce discretionary search. This project does not implement CSCV or estimate PBO and cannot claim to eliminate overfitting. |
| Trading-cost context | Frazzini, Israel and Moskowitz,2018, https://www.aqr.com/Insights/Research/Working-Paper/Trading-Costs | Costs depend on trading conditions. The1bp fee/5bp slippage assumptions here are not calibrated from that paper's institutional trades; fixed multipliers and delay are scenario checks. |

## Material assumptions

The five pre-split price histories are multiplied by two before5December2025; cash distributions use unadjusted issuer amounts. Displayed volume divided by the future split factor is an explicitly conservative capacity proxy whose source basis has not been independently certified. Signals use trailing total-return wealth features so split dates do not create false momentum. Raw prices and separate actions drive accounting; adjusted close is not used as an execution price or credited with dividends again.

The model uses 1bp commission and5bp adverse slippage per side, prior-session volume participation1%, whole shares, no borrowing/shorting/taxes/FX, and zero cash return. Portfolio target sizing at the next open is an idealised daily-bar convention. Liquidity caps do not certify fillability. Prices embed ETF expenses; subtracting an expense ratio a second time would double count.

## What the release establishes

An end-to-end retrospective sector-fund allocation study with bounded development selection, a saved hash-protected test, self-financing cash/action accounting, independent spreadsheet/JavaScript first-rebalance checks, and transparent negative comparative evidence. Results are not live returns, a survivorship-free equity universe, causal alpha, native broker executions or a full statistical multiple-testing correction.

The snapshot ends31December2025. Forward monitoring deliberately reports stale data and publishes no present trading signal. Scheduled health checks are not a live data feed. Third-party raw source licensing, historical data vintages, precise opening liquidity and institutional review remain unresolved. Those limits remain visible in the dashboard and model card.
