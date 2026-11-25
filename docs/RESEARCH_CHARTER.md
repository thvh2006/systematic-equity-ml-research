# Archived design note

This note predates the completed real-data study. Current scope/results are in `RELEASE_STATUS.md`, the saved protocol and the research paper. Historical future-tense and blocked-gate statements below are retained as design history.

# P2 research charter

Drafted24November2026. **Status: case/data feasibility review; no market-data test has been run.** The synthetic fixture exercises infrastructure and is not evidence for the research hypotheses.

## Preferred first case

**Does a small, regularised model improve monthly rotation among US equity-sector ETFs after costs, relative to equal weight and a predeclared momentum rule?** This is an equity-sector allocation case, not evidence of individual-stock alpha. A candidate fixed fund universe is XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV and XLY. Fund inception, changes in sector definitions, splits/distributions, complete coverage and use rights must be verified for every fund before the universe is frozen. Only XLK's issuer page has so far been checked in detail; do not describe the whole list as verified original1998 constituents.

The choice is motivated by a smaller, interpretable cross-section and a clear economic decision. Fund NAV data are useful for validation but are not executable opening market prices. Nine correlated sectors provide a small effective sample: thousands of daily panel rows are not thousands of independent monthly decisions. A null or negative incremental result is an acceptable completed study.

### Alternative and extension

Vietnamese equities remain an alternative if raw/action data, universe scope, local calendar, tradability, lot/price-limit rules and settlement constraints can be established. A fixed set of today's liquid names cannot be advertised as a historical VN30 or survivorship-free universe. The foundation's generic whole-share/T+1-fill fixture is not yet a Vietnam-market execution model. Do not simply swap in VN OHLCV and label it implementable.

## Design to freeze after the data audit

| Decision | Proposed study specification | Freeze gate |
|---|---|---|
| Universe | Candidate nine sector ETFs; SPY comparison if matching total-return/price data verified | Issuer identity/inception and historical scope receipt |
| Horizon | Monthly decision at signal close; next-session fill,21-session target | Actual session calendar and opening-price contract |
| Window | Prefer a long history through a closed calendar year, with train/development/final holdout set by the coverage audit | Do not choose start/end to improve Sharpe |
| Baselines | Equal weight and simple momentum with identical execution/cost budgets | Freeze lookback(s) before test evaluation |
| First ML | Ridge with train-only transforms. Foundation alpha10 is only a fixed technical example | A small, versioned development-only candidate grid |
| Challenger | Elastic Net or one bounded boosting family only after ridge/data baseline works | Record each trial; no unbounded model search |
| Portfolio | Long-only, top-ranked subset, declared name caps/cash rule | Same sizing for baseline and ML to isolate prediction value |
| Costs | Commissions, bid–ask/slippage assumptions, cost×1/×2/×3 and delayed execution | Date/source/rationale for each assumption |
| Cash return | Zero as a conservative assumption or verified short-rate proxy | Same cash convention in every comparison |
| Primary decision | Paired incremental net return/utility vs momentum with time-block uncertainty and drawdown/turnover constraints | No guaranteed profitability threshold |
| Diagnostics | Rank IC, error, exposure, concentration, turnover, costs and capacity | Do not promote a model solely on prediction accuracy |
| Final holdout | Evaluate once after specification/trial budget freeze; no retuning on results | Artifact/commit and all-trial register |
| Forward paper | Append-only forecasts after a dated strategy freeze | Cannot backdate simulated results as forward performance |

The research will compare prediction, sizing and execution effects separately. It will not infer a tradeable edge from a model that only improves an in-sample or fixture metric.

## Research packages before real-data results

1. Case/universe rationale and sector-methodology history.
2. Provider matrix and data contract: raw vs adjusted prices, distribution timing, splits and trading calendar.
3. Coverage and corporate-action spot checks against issuer records, including ordinary and stressed periods.
4. Availability, overlapping-label maturity and panel date-group split design.
5. Baseline and cost specification, fixed model-search budget and trial log.
6. Independent cash/holdings reconciliation, then bounded temporal model research.
7. Robustness and uncertainty, locked test and prospective paper protocol.

## Literature use

Gu, Kelly and Xiu's *Empirical Asset Pricing via Machine Learning* motivates comparing statistical approaches and testing economic usefulness. Its broad asset-pricing setting does not prove that nonlinear methods will help this small ETF case. The original NBER paper and official scikit-learn temporal-splitting documentation are recorded in the source register. A literature matrix and claim map are prepared before any results narrative; the research report itself has not been written.
