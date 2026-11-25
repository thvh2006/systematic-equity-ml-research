# Model card — sector ETF allocation, 0.3.0

**Purpose:** auditable retrospective research on the incremental value of monthly ML rankings. **Decision:** no promotion to trading.

| Field | Specification |
|---|---|
| Universe | Nine fixed sector-fund wrappers; SPY comparator; not all historical sector funds |
| Data | Rounded retrospective Yahoo price/volume tables, issuer cash distributions/pay dates; 2017–2025 |
| Features | 21/63-session wealth momentum, 20-session daily volatility, 63-session drawdown, log dollar volume |
| Target | Next-open to open 21 sessions later, distribution-inclusive; labels matured with additional session gap |
| Model | Train-only standardisation; 24 sequential decision stumps, learning rate .05; original NumPy implementation |
| Selection | Highest development net daily zero-cash Sharpe among six fixed candidates; momentum was stronger in development |
| Portfolio | Monthly top three, one-third targets; no shorting/leverage; whole shares and cash residual |
| Primary fill | Following-session opening marks with assumed costs and prior-volume caps; idealised sizing at the open |
| Evaluation | Saved 2023–2025 results, monthly past-only refits; only selected ML policy tested as primary |
| Key result | ML CAGR 12.41%, momentum 13.19%, equal-weight 14.16%; paired interval includes zero |
| Diagnostic | Mean rank IC −0.0271 over 36 eligible date groups; no annualised IC ratio |
| Delay stress | An additional session changes the ranking; do not use it to reselect the rule |
| Prohibited interpretation | Live performance, independently preregistered alpha, broker-fill certification, survivorship-free market study |
| Current operation | Stale snapshot; no forecast/order; zero forward observations |

A 35% construction cap describes targets, not a continuously enforced realised-weight ceiling. Weights can drift with market returns. Fund-level P&L attribution includes costs but is not causal selection alpha or Brinson attribution. Stump split counts are not feature ablation evidence.

The source/config/engine references remain tied to the original saved evaluation. Reporting code, docs and UI were added afterwards and do not change frozen fitted outcomes. All additional diagnostics are labelled post-evaluation descriptive work. Future changes to features, labels or execution require a new versioned study rather than replacement of this result.
