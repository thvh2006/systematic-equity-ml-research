# Research release 0.3.0 — 25 November 2026

Completed scope: a retrospective, fixed-sector-fund ML allocation study and reproducible public evidence. No promotion to trading.

| Deliverable | Release state |
|---|---|
| Source/units/action intake | Saved 2017–2025 private snapshot and public receipt; five split checks, 362 distribution comparisons, one resolved difference |
| Research design | Six fixed candidates; saved development selection and hash-referenced test; no post-test reselection |
| Economic tests | 22/22 pass |
| Public evidence verifier | 71 checks before release-file hashes; works without private inputs; file-manifest checks added at export |
| Notebooks | Eight canonical research notebooks, 31 code cells executed sequentially; native Jupyter kernel not used |
| Excel | 19 sheets, independent first-rebalance and five compounded-return checks; LibreOffice recalculation has zero cell errors |
| Reports | 11-page academic paper PDF, editable DOCX and Markdown; two-page decision memo |
| Dashboard | Eight views and independent calculator; 10 policy/chart combinations and three calculator scenarios checked in JavaScript |
| Attribution | Five strategy paths reconcile daily fund contributions to NAV changes; maximum residual below 5e-11 dollars |
| Reproduction | Public verification, tests, notebook executor and CI workflow; private-input rebuild route documented separately |
| Forward state | Snapshot stale; zero prospective signals/sessions. No live data service or trading system claimed |

Public release excludes raw provider files, credentials, private intake receipts and local caches. Source selection, feed vintage, opening execution and statistical limits are disclosed in the paper and model card. Native application/browser checks and GitHub publication are recorded in `artifacts/research/release_review.json` after review. A CI workflow being included is not itself evidence of a successful hosted CI run.

The bounded NumPy stump challenger is the implemented nonlinear model. XGBoost/LightGBM, shrinkage optimisation, post-test feature ablation, leave-sector-out studies and additional research families are not silently claimed. They would require a separately specified experiment. This release closes the chosen retrospective protocol; it does not imply every extension in the portfolio blueprint has been implemented.

Reporting revision, 25 November 2026: Times New Roman 12 pt throughout the paper and memo, continuous body sections, monochrome charts with line patterns, numbered tables/figures and hanging references. The Word version now includes the PDF appendix figures and tables. Original study source, configuration, selection, freeze and saved test remain unchanged. See `REVIEW_2026-11-25.md`.
