# Archived design note

This note predates the completed real-data study. Current scope/results are in `RELEASE_STATUS.md`, the saved protocol and the research paper. Historical future-tense and blocked-gate statements below are retained as design history.

# P2 — Case, research và kế hoạch chuyển sang dữ liệu thật

Ngày rà soát: 24/11/2026. Bám thứ tự blueprint: P1 FPT → P2 Systematic Equity & ML → P3 crypto carry → P4 bonds → P5 options → P6 fund/risk. Đây là kế hoạch thực thi, chưa phải báo cáo kết quả học thuật.

## 1. Case được ưu tiên và lý do

**ML có cải thiện phân bổ ETF ngành Mỹ theo tháng, sau chi phí, so với equal-weight và momentum không?**

Candidate universe: XLB/XLE/XLF/XLI/XLK/XLP/XLU/XLV/XLY; SPY là benchmark ứng viên. Chưa khóa universe, thời kỳ hay tập test vì chưa kiểm tra đủ lịch sử và nguồn dữ liệu. Đây là allocation giữa các ETF ngành; không được viết thành nghiên cứu chọn cổ phiếu riêng lẻ. Các ngành tương quan cao và số quyết định tháng hữu hạn, nên không được lấy số dòng panel làm cỡ mẫu độc lập.

Lựa chọn này bổ sung trực tiếp cho P1: từ phân tích một doanh nghiệp sang tạo tín hiệu, kiểm định thời gian, danh mục và thực thi. Đây là judgement về phạm vi học tập, không phải kết luận rằng ETF dễ kiếm lợi nhuận hơn cổ phiếu Việt Nam. Nếu không có nguồn đạt yêu cầu, đổi case có biên bản lý do trước khi nghiên cứu mô hình.

## 2. Research và data cần làm

| Gói | Việc làm cụ thể | Điều kiện hoàn thành |
|---|---|---|
| Câu hỏi kinh tế | Giải thích tại sao momentum/risk có thể có ích; viết lập luận phản biện và giả thuyết không có cải thiện | Một trang charter và tiêu chí đánh giá định trước, không viết kết luận trước |
| Literature | Đọc bản gốc về ML asset pricing, backtest overfitting, momentum ngành và trading costs; lập claim–source–limitation matrix | Mỗi luận điểm có nguồn gốc và giới hạn áp dụng; paper đã đọc ban đầu chưa đủ để gọi literature review hoàn tất |
| Universe | Kiểm tra issuer, inception/listing, ticker changes, mergers/closures và thay đổi phân ngành cho từng ETF | Có receipt từng mã; giới hạn fixed-fund universe và selection bias được công bố |
| Giá giao dịch | Tìm feed có raw OHLCV và định nghĩa timestamp/session rõ ràng; phân biệt adjusted/raw/total return | Một fund và benchmark qua audit trước khi mở rộng; không thay NAV cho opening market price |
| Corporate actions | Lịch split và cash distribution có ex-date/pay-date; đối chiếu issuer, đơn vị và adjustment factors | Ít nhất một split và một cổ tức kiểm tra độc lập; không double-adjust |
| Calendar | Ngày nghỉ, early close, timezone, ngày tín hiệu và phiên khớp tiếp theo | Tất cả ngày được map tới calendar thực; không dùng weekday calendar của fixture |
| Missing/quality | Missing bars, zeros, duplicates, stale marks, revisions, outliers, volume và thời kỳ gián đoạn | Mỗi lỗi có rule và disposition; không forward-fill tạo lệnh khớp giả |
| Quyền dùng | Kiểm tra research/export/derived output/redistribution của từng nguồn | Phân biệt quyền phân tích với quyền đưa raw data lên GitHub; không giả định download được là open license |
| Benchmark/cash | Cùng calendar/corporate-action convention; chọn tiền mặt zero hoặc short-rate có nguồn | Benchmark và cash convention được khóa trước đánh giá |
| Execution | Next-session rule, fees/spread/slippage, round lots, residual cash, capacity/delayed execution | Giả định có lý do/ngày hiệu lực; daily volume không chứng minh đủ thanh khoản ở open |

### Nguồn đã khảo sát thực tế

- **State Street:** đã mở trang XLK và trang phân phối, tìm thấy liên kết NAV-history/product data. Chưa tải và audit đầy đủ file nhị phân; NAV không phải dữ liệu khớp lệnh. Chưa kiểm tra xong cả chín ETF.
- **Stooq:** thử tải trực tiếp không nhận được CSV do DNS trong môi trường hiện tại; trang download yêu cầu xác minh bằng trình duyệt. Không vượt xác minh, không gọi nguồn này là đã có data.
- **Vnstock:** tài liệu chính thức cảnh báo OHLCV đã điều chỉnh và rủi ro điều chỉnh trùng; chưa có snapshot giá raw/actions được duyệt cho case Việt Nam.
- **RMIT:** trang công khai là đầu mối kiểm tra quyền truy cập học thuật, chưa chứng minh tài khoản của người dùng có quyền LSEG/WRDS/CRSP hoặc quyền công bố lại.

Danh sách URL và trạng thái đọc được lưu trong `data/manifests/source_register.json` và `docs/DATA_FEASIBILITY.md`. Nguồn còn thiếu phải được giải quyết trước real-data fitting, không dùng dữ liệu giả lập thay thế kết quả tài chính.

## 3. Trình tự phát triển và skills phải thể hiện

| Stage | Thực hiện | Skill/evidence để reviewer kiểm tra |
|---|---|---|
| A — Case/data audit | Chốt câu hỏi, nguồn, schema, coverage và event reconciliation | Data engineering, market conventions, provenance; schema và source receipts |
| B — Baselines | Equal-weight và momentum trên cùng sizing/execution/cost | Asset allocation, fair comparison; holdings/cash/trade logs |
| C — Ridge | Train-only transforms, regularization, date-group split, matured labels và gap | Statistical learning, leakage control; fitted parameters, information timeline và tests |
| D — Challenger | Chỉ thêm Elastic Net hoặc một họ boosting sau baseline; giới hạn số trial | Model selection và experiment discipline; trial register đầy đủ, kể cả thất bại |
| E — Portfolio/economics | Net/gross return, turnover, drawdown, exposures, concentration, cash | Portfolio construction và economic evaluation; attribution, cost decomposition |
| F — Robustness | Costs ×1/×2/×3, delay, thời kỳ stress, feature ablation, time-block uncertainty | Model risk và inference; không diễn giải correlated panel như IID |
| G — Locked test | Khóa config/commit, đánh giá một lần, không retune theo kết quả | Research integrity; freeze receipt và paired baseline comparison |
| H — Forward paper | Dự báo append-only có timestamp sau freeze | Monitoring và operational discipline; không backdate kết quả |

Tiêu chí master: giải thích được từng feature, label, tham số, bút toán cash/action và lý do một trade xuất hiện; dựng lại một rebalance bằng tay và bằng Excel; phát hiện một future-data leak chủ động cài vào; chạy lại từ raw snapshot tới outputs có hashes; bảo vệ được kết luận không có alpha nếu bằng chứng nói vậy. Không yêu cầu kết quả dương để hoàn thành dự án.

## 4. Bộ deliverables ở bản nghiên cứu hoàn chỉnh

- **Notebooks:** data QA; features/labels; walk-forward baselines; bounded ML; portfolio/execution; robustness; frozen-result reproduction. Phần nào chưa có real data phải đánh dấu chưa chạy.
- **Excel:** assumptions/source register, independent sample ledger và corporate actions, baseline/model comparison, risk/exposure, costs/capacity. Excel kiểm tra kinh tế; không giả vờ thay toàn bộ model-training pipeline.
- **HTML:** source/as-of/status, benchmark comparison, holdings/trades, risk/exposure, cost sensitivities và model diagnostics. Phân biệt snapshot, local calculation và live refresh. Chỉ gắn nhãn live sau khi feed/scheduler/failure alerts thực sự hoạt động.
- **Code/ops:** configs, modules, meaningful economic tests, dependency instructions, data-access guide, reproducible run receipts, release notes và CI khi có repo/remote thực tế.
- **Research assets:** charter, literature matrix, data dictionary, trial register, figure/table plan, locked-test receipt và limitations.

## 5. Kế hoạch report — chưa viết report

Hai tầng đầu ra dự kiến: technical research paper khoảng 4.000–6.000 từ tùy độ phức tạp, appendix tách riêng; investment/research memo 2 trang để người đọc hiểu nhanh. Đây là phạm vi đề xuất cho portfolio cá nhân, không phải quy định học thuật hay lời hứa phải đủ số từ.

| Phần | Bằng chứng cần có trước khi viết |
|---|---|
| Introduction/hypotheses | Charter, economic mechanism, contrary argument, scope |
| Literature/context | Primary-paper matrix; điểm giống/khác với case ETF |
| Data | Source rights, coverage, attrition, raw/adjusted/action audit |
| Method | Information timeline, label maturity, split dates, candidate budget, train-only transforms |
| Portfolio/execution | Fill rules, costs, actions, cash/NAV identities và independent checks |
| Results | Locked OOS real-data artifacts và baseline comparison; không dùng fixture NAV |
| Robustness/limitations | Time-block uncertainty, cost/delay stress, selection/sector-history biases và failed trials |
| Conclusion | Câu trả lời phù hợp bằng chứng, kể cả không có cải thiện; chưa được viết trước |
| Appendix/reproduction | Hashes/config/version, source receipts, ledger samples và run instructions |

Bây giờ chỉ chuẩn bị outline, claim–source matrix, bảng/hình trống và checklist. Abstract, results narrative, kết luận và recommendation chờ sau real-data study. Một chart đẹp hoặc metric trên fixture không phải kết quả học thuật.

## 6. Thứ tự tiếp theo đã xác định

1. Hoàn tất discovery nguồn có quyền sử dụng và sample một ETF + benchmark, gồm raw prices/actions.
2. Audit sample; xử lý chỗ sai/thiếu trước khi mở rộng universe.
3. Chốt universe, khoảng dữ liệu, train/development/locked-test và trial budget **trước fitting dữ liệu thật**.
4. Chạy baselines, sau đó ridge, rồi mới quyết định có cần challenger.
5. Làm bộ economic evidence/robustness và đối chiếu deliverables; cuối cùng mới viết report theo plan.

FPT vẫn có workstream riêng: stage trước định giá đã đạt checks được ghi nhận, nhưng WACC/DCF/EV-to-equity/share bridge, stock pitch và industry research chưa được gọi là hoàn tất. Mở P2 không đồng nghĩa đóng P1.
