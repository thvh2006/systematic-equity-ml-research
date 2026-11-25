# Real-data study protocol

Declared before locked evaluation on 24 November 2026. Question: incremental economic value of a bounded ML sector-allocation model versus momentum, not whether any tuned curve looks attractive.

## Data-dependent scope decisions made before financial evaluation

Nine fixed selected sector funds XLB/XLE/XLF/XLI/XLK/XLP/XLU/XLV/XLY, plus SPY. The 2017–2025 sample begins after XLF's documented 2016 in-kind XLRE distribution, which must not be treated as an ordinary fractional stock split. Sector classification changed during the sample; the study tracks fund wrappers, not constant historical sector membership. Selection/survivorship limitations remain.

Historical table capture provides 70,230 price observations across ten funds for 1998–2026. Normalised study data have 22,620 observations, 2,262 sessions, five integer 2-for-1 splits and 362 cash distributions. Issuer payable dates govern cash availability. Yahoo split-adjusted display prices are reconstructed to contemporaneous share units and checked against the issuer's published pre-split prices. Source display prices are rounded. The original input snapshot is retrospective and may contain later corrections; it is not an archived point-in-time feed.

Reported volume divided by future split factors is an explicit conservative capacity proxy, not independently validated auction liquidity. Fees of 1bp and slippage of 5bp per side are analyst assumptions, not broker-calibrated estimates. Capacity uses the prior session's volume; zero return on cash and no separate tax model. Rebalancing uses next-session opening marks and whole shares. Target sizing at that open is an idealised execution convention. Daily-bar fill realism is limited. ETF operating expenses already affect observed fund prices/NAV; no duplicate expense-ratio subtraction is made.

## Locked design

- Train from 2017, features after 63-session warmup; monthly development fills 2020–2022 and locked fills 2023–2025.
- Five technical/liquidity features; no revised fundamentals or today's constituent list as historical holdings.
- Next-open to open 21 sessions later target, matured labels with one further session gap; whole date groups remain together. Train-only transforms and equal aggregate weighting per date.
- Six candidates only: ridge alpha 0.1/10/100, elastic net alpha .001/.01 with l1 ratio .5, and 24 boosted decision stumps at learning rate .05. The custom NumPy stump learner is not XGBoost or LightGBM. No hidden search or test-selected feature family.
- Baselines: equal-weight, 63-session momentum, inverse-volatility, and costed SPY buy-and-hold. ML/momentum top three equally weighted, no shorting/leverage; target name cap35%.
- Choose the ML candidate with the highest development net daily Sharpe with zero cash benchmark. The selection does not itself promote ML to trading, especially when momentum wins development.
- The holdout is evaluated once after freeze.json records dataset/config/engine/development hashes and source commit. Do not overwrite the result or retune it. Monthly refits within the holdout are permitted by this predeclared walk-forward algorithm and only use matured past outcomes.
- Report all six development trials; evaluate only the selected candidate as the main locked ML model. Cost0/1/2/3 and a further-session execution delay are predeclared descriptive stresses.
- Paired net monthly return difference versus momentum receives a circular three-month block-bootstrap95% interval,2,000 replicates, fixed seed20261124. Small samples, volatility clustering and selection effects limit inference. This is not a PBO estimate, multiple-testing correction, or proof of alpha.

## Publication and forward monitoring

Publish original code, synthetic fixture, method/configs and derived research outputs. Do not upload raw Yahoo/issuer records to GitHub or grant a data license. Research conclusions remain retrospective and exploratory; there is no live track record. A forward paper process can start only with timestamps after publication; it begins with zero realised forward sessions. Data staleness must be visible. Historical outcomes through2025 cannot be reclassified as prospective performance in2026.

The broader professional release still requires native document/UI review, external data/execution review, a functioning refresh source and actual forward observations. All release labels must preserve these limits.
