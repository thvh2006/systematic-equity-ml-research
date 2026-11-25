# Release 0.4.0 - 25 November 2026

The historical study remains the original consumed 2023-2025 test. This is a post-study review and presentation release, not a new investment experiment.

## Visible changes

- Dashboard: nine views, including **Why ML lagged**, a momentum/equal-weight comparator, a zero-cost-to-net NAV bridge, full-test relative wealth, fund-contribution differences and a derived CSV export. Summary links give a reading order. The header identifies review release 0.4.0 and its update date.
- Notebooks: all eight canonical notebooks now include explicit questions, interpretations and captured HTML tables or SVG figures. The saved-test notebook explains comparator-dependent friction rather than attributing every loss to turnover.
- Workbook: the existing 19-sheet layout remains. Comparison gains a formula-linked comparator, fund-contribution bridge and relative-wealth chart. Execution Lab gains a native two-input fee/slippage Data Table and a missing-driver state. Scenario-minus-default is labelled as a scenario difference rather than a universal audit failure.
- Report: a post-study explanation and dollar bridge are added to the academic Times New Roman 12 pt paper and editable Word version. The primary results and conclusion are retained.
- Tests: future price/volume perturbations now challenge the selected 24-stump fit, scores, top-three choices and an eligible earlier portfolio fill. The public verifier independently checks the new descriptions against saved artifacts.
- GitHub language accounting: generated HTML exports and generated artifact/figure paths are marked as generated in `.gitattributes`. The authored Python research and HTML dashboard template remain visible as source. This does not change file formats or executable behavior.

## Reproduce the review layer

```sh
python scripts/prepare_polish.py
python scripts/build_review_notebooks.py
python scripts/build_polished_dashboard.py
python scripts/run_checks.py
node scripts/check_research_dashboard.cjs
```

The report builder requires the documented delivery dependencies and Times New Roman fonts. The workbook polish builder imports the delivered XLSX with the artifact runtime; it is an authoring tool, not a dependency for opening the workbook. Verify and export a fresh public package after rebuilding to update the file manifest.

## Interpretation that changed in depth, not selection

Against momentum, the ML zero-cost final-NAV gap is about -$3,045. Differential friction offsets about $83, leaving a costed gap of about -$2,962. Against equal weight, the zero-cost gap is about -$4,360 and differential friction adds about -$2,307, leaving about -$6,666. Cost drag depends on the comparator. Fund contribution differences reconcile the gap but are not isolated causal allocation/selection effects.

No raw provider snapshots are added to the public repository. No new held-out period, refit, post-test rule promotion or prospective performance is claimed. The original stale-data block remains active.
