# Systematic Equity & ML Research

**Does bounded machine learning improve monthly sector ETF allocation after costs?**

A completed retrospective research case with a negative comparative result: the development-selected ML model does not establish an advantage over momentum or equal-weight in the primary 2023–2025 test. Original code, an auditable ledger, a bounded trial register and review deliverables make that conclusion inspectable.

| Primary saved test | Net CAGR | Sharpe, cash = 0 | Maximum drawdown |
|---|---:|---:|---:|
| Selected ML: 24 boosted stumps | 12.41% | 0.785 | −19.94% |
| Momentum, 63 sessions | 13.19% | 0.936 | −16.63% |
| Equal-weight | 14.16% | 1.088 | −15.59% |
| SPY buy-and-hold | 22.39% | 1.418 | −18.31% |

These are hypothetical results after assumed 1 bp fees and 5 bp adverse slippage per side. The paired monthly ML–momentum interval includes zero. Delaying fills by another session reverses their ranking: an execution-sensitivity warning, not a newly selected strategy.

## Open the evidence

| Artifact | Purpose |
|---|---|
| [Research paper: PDF](deliverables/P2_Research_Paper.pdf) · [DOCX](deliverables/P2_Research_Paper.docx) · [Markdown](reports/results/P2_Research_Paper.md) | 16-page technical narrative, method, test results, diagnostics and limitations |
| [Two-page decision memo](deliverables/P2_Decision_Memo.pdf) | Decision and implementation conditions |
| [Excel review](deliverables/P2_Systematic_Equity_Research.xlsx) | 19 sheets, editable first-rebalance formulas and independent return checks |
| [Interactive dashboard](index.html) | Eight views: data, validation, backtest, holdings, costs, uncertainty and paper readiness |
| [Eight research notebooks](notebooks) | Executed walkthrough from source audit to stale-data controls |
| [Attribution](artifacts/research/sector_attribution.csv) · [Trial register](reports/plan/trial_register.csv) | All six candidates and fund-level P&L contribution |
| [Protocol](docs/PROTOCOL_FREEZE.md) · [Sources](docs/SOURCES_AND_LIMITATIONS.md) · [Model card](docs/MODEL_CARD.md) | What was frozen, assumptions and appropriate interpretation |

Open `index.html` locally or serve the repository with `python -m http.server 8768`. The dashboard is a saved-results explorer, not a market-data service. Its policy selector reads precomputed artifacts; the first-rebalance calculator alone recomputes local economics.

## Reproduce the public evidence

Python 3.10+ with NumPy; Node 18+ for the dashboard checks. The original study used Python 3.12.14 and NumPy 2.3.5. No training or source-data download occurs in these verification commands:

```sh
python -m pip install -e .
python scripts/run_checks.py
python scripts/verify_release.py
node scripts/check_research_dashboard.cjs
python scripts/run_notebooks.py
```

The public verifier checks the saved engine/config/development/freeze references, recomputed metrics, monthly returns, P&L identities, exposures, paired bootstrap, trial selection and release-file hashes. A clean checkout can run these checks without private market inputs. Notebook execution uses a sequential Python executor with captured outputs; no claim of native Jupyter-kernel verification is made. To use native Jupyter, install it separately and choose this project environment.

The legacy fictional fixture remains for split, dividend, suspension, delisting, cash-cap and leakage tests. It does not supply any financial result above.

## Study design

- Nine fixed sector funds: XLB/XLE/XLF/XLI/XLK/XLP/XLU/XLV/XLY; SPY benchmark.
- Normalised data: 2017–2025, 2,262 sessions and 22,620 records including benchmark. Corrected retrospective history, not archived provider vintages.
- Training from 2017; development 2020–2022; saved test 2023–2025. Monthly expanding fits use matured forward labels and a session gap; date groups stay together.
- Five technical/liquidity features; six candidates: three ridge, two elastic net and one 24-stump challenger. The NumPy stump model is not XGBoost/LightGBM.
- Long-only, whole-share, next-session opening-mark execution, cash/volume limits and explicit split/distribution accounting. All comparisons share that engine.
- Predeclared cost multipliers and further-session delay, paired time-block uncertainty; no post-test rule reselection.

## Rebuild and data access

[Data-access guide](docs/DATA_ACCESS.md) separates public verification from private-input training. Raw Yahoo history and issuer files are excluded; this repository grants no provider-data license. Reproducing intake/training requires separately permitted source inputs. Do not overwrite the saved development, freeze or test. A new dataset/specification needs a separately versioned experiment.

For local delivery builders, install the `delivery` extras. `complete_research.py` and the workbook builder require the private normalised snapshot for their original accounting cross-check; the PDF report can be generated from public saved outputs:

```sh
python -m pip install -e '.[delivery]'
python scripts/build_research_report.py
```

`build_complete_delivery.py` creates formulas without cached results. Recalculate its output in a spreadsheet application before distributing it. The release workbook was recalculated with LibreOffice and checked independently. Native Microsoft Excel review is recorded separately in the release receipt.

## Forward status and boundaries

**No current signal.** The data end on 2025-12-31. The staleness check deliberately blocks current forecasts and exits 2:

```sh
python scripts/paper_monitor.py --check-only
```

Published forward signals: 0; realised forward sessions: 0. No broker connection, live feed or scheduled refresh is claimed. [Operations](docs/OPERATIONS.md) explains the conditions required to start prospective paper research.

Fixed-fund selection, changing sector classification, rounded/revised prices, unvalidated opening liquidity, assumed costs, zero cash yield, no separate tax model and 36 test months materially limit inference. A local freeze is not independent preregistration. The result supports **no promotion of this model**; it does not establish a universal conclusion about ML or investment advice.
