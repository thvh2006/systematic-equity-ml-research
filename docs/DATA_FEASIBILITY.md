# Updated status: 25 November 2026

A retrospective Yahoo/issuer snapshot was subsequently imported and the saved study has been reviewed. Read `SOURCES_AND_LIMITATIONS.md`, `PROTOCOL_FREEZE.md` and `RESEARCH_RELEASE_VI.md`. Its exploratory acceptance does not resolve feed vintage, execution or redistribution limitations. The discovery notes below are historical and are superseded for current status.

# Case and data feasibility audit

Audit date24November2026. No real market-data snapshot has been imported or approved. No claim is made that free data are unavailable everywhere; these are the specific routes checked so far.

| Route | What was actually checked | Unresolved items | Decision |
|---|---|---|---|
| Existing FPT monthly sample | Earlier project audit: one asset,70 monthly observations,2020–2025 | Multi-asset daily bars/actions/calendar/benchmark/universe | Pipeline fixture only; not P2 study data |
| Stooq daily CSV | Direct Python HTTPS attempt failed DNS. Official historical-download page returned a JS browser-verification notice | Adjustment/action semantics, usage/redistribution terms, actual coverage | Do not claim downloaded or approved; no anti-bot workaround |
| Vnstock official docs | Price-adjustment and input docs opened. Documentation says downloaded OHLCV are already adjusted; adding actions can double count. Raw validation needs separately archived raw prices/events; one helper is currently disabled across action periods | Actual provider account/source, raw/action history, membership, rights and VN execution rules | Useful provider lead; no package/account access or dataset assumed |
| State Street XLK issuer page | Fund identity/inception, NAV-history workbook link, distribution page and product-data workbook link | Whole candidate universe, actual file bytes/coverage, raw trade prices, splits and permission to republish | Preferred ETF-case validation source, not a complete price feed |
| State Street historical distributions | Issuer page explains ex/pay dates and offers XLSX download. A restriction on reproducing/transmitting content is visible | Research use/redistribution permission and permitted derived outputs | Keep provider raw data private unless permission is established; downloadability is not a public-data license |
| RMIT data access | Public Vietnam library pages and a public RMIT LSEG-related teaching/event page | User's specific access, campus/account scope, export and portfolio-publication rights | Potential licensed route only. No WRDS/CRSP or LSEG entitlement inferred |

## Verified discovery links

- XLK official fund page: https://www.ssga.com/us/en/individual/etfs/state-street-technology-select-sector-spdr-etf-xlk
- NAV-history link returned by that page: https://www.ssga.com/library-content/products/fund-data/etfs/us/navhist-us-en-xlk.xlsx
- Product-data link: https://www.ssga.com/library-content/products/fund-data/etfs/us/spdr-product-data-us-en.xlsx
- Distribution page: https://www.ssga.com/us/en/individual/resources/documents/etf-dividend-distributions
- Vnstock adjusted-price documentation: https://www.vnstocks.com/docs/vnstock_quant/v1/du-lieu/gia-dieu-chinh
- Vnstock backtest input documentation: https://vnstocks.com/docs/vnstock_quant/v1/backtest/du-lieu-va-tin-hieu
- RMIT Vietnam library resources: https://www.rmit.edu.vn/libraryvn/borrowing-and-resources/library-resources

The web reader reported unsupported XLSX content type for the two State Street workbook links. That establishes a discovered link, not a successful binary download or a coverage audit. Issuer NAV and published performance returns also have different semantics from executable opening-market prices; they must not silently substitute for the execution feed.

## First real-data acceptance slice

Before downloading a whole universe, acquire a permitted small sample for one fund and benchmark, with raw OHLCV, splits and cash distribution ex/pay dates. Verify source byte hashes, date/time conventions and price units. Reconcile one split and one cash distribution against issuer evidence and distinguish market price from NAV. Expand to all candidate funds only after the contract works. Freeze the universe and train/development/test calendar after coverage, before fitting/evaluating any real-data model.

Public project assets can contain generated fixtures, schema, manifests and code. Provider records are not automatically eligible for redistribution. The project release gate deliberately remains BLOCKED until a declared market-data snapshot satisfies the contract.
