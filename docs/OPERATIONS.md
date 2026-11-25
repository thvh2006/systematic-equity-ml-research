# Operational runbook

## What runs now

This is a completed retrospective research release, not a live trading system. The static dashboard explores saved outputs. `paper_monitor.py --check-only` returns exit 2 when the end date of the source receipt is stale relative to the New York session expected at the wall clock. Without `--check-only` it appends a hash-linked status event. It never emits orders or fabricates a forecast.

The source snapshot ends 2025-12-31; zero forward sessions and zero prospective signals have been realised. The monitor alone does not validate every fresh source cell or constitute a data feed. No schedule is configured by this release.

## Before prospective paper research

1. Establish permitted fresh price/action sources, rights and source timestamps; validate schema, sessions, units, distributions, revisions and stale/missing observations.
2. Independently review opening-auction execution, sizing and capacity. Identify the portfolio policy to be approved; the present ML result is not promoted.
3. Freeze the approved prospective strategy and source/code versions. Create new append-only forecast/intent records with real timestamps before outcomes; never relabel historical outputs as forward evidence.
4. Run in observation mode, validate intended trades and hypothetical fills against incoming prices, log rejected/stale batches and deviations, and preserve source snapshots under their permissions.
5. Attribute cash/holdings/receivables/costs daily; halt on reconciliation failure, missing actions, source uncertainty or stale data. Reconcile incident resolution without deleting the incident.
6. Review evidence before any further promotion. Broker credentials, live orders, automatic deployment or trading authority are outside this release.

## Refresh and failures

A new snapshot is a new version. Do not overwrite `freeze.json`, `locked.json`, the source receipt or the historical dashboard. Archive outputs and record code/config/source digests. A provider correction creates a documented revision comparison. Missing or nonfinite data blocks the affected batch; do not forward-fill executable prices to invent a trade. More stringent feed checks are needed before the health monitor can ever be interpreted as production readiness.

## Local review

Serve `index.html` using `python -m http.server 8768`. Run public verification after changing reporting/UI code. Changes to `src` or `run_research.py` invalidate the frozen-engine reference and need explicit versioning. Recalculate rebuilt workbooks before publishing them. The workflow tests public evidence on pushes; it is not a trading scheduler.
