# P2 — Bản nghiên cứu hoàn thiện để công bố

Cập nhật 25/11/2026. Đã hoàn thành phạm vi nghiên cứu hồi cứu ETF ngành theo protocol đã lưu: dữ liệu/units/corporate actions, sáu ứng viên ML, baseline, test đã khóa, sensitivity và uncertainty, attribution, report, notebook và deliverables review.

Kết quả chính không đổi: ML CAGR 12,41%; momentum 13,19%; equal-weight 14,16%. Khoảng bootstrap chênh lệch lợi suất tháng chứa 0. Không có cơ sở promote ML này sang giao dịch. Delay thêm một phiên làm đổi thứ hạng; đó là điểm nhạy thực thi được công bố, không dùng để chọn lại rule.

Bộ mới có report PDF 16 trang, DOCX chỉnh sửa, memo PDF 2 trang, tám notebook với 31 code cells đã chạy, Excel 19 sheets và dashboard tám views. Attribution từng ETF khớp P&L hàng ngày. Excel được tính lại bằng LibreOffice, không có ô lỗi; NAV rebalance đầu khớp Python và compounded monthly returns khớp cả năm chiến lược.

Đọc `RELEASE_STATUS.md` để xem phạm vi kiểm tra, `MODEL_CARD.md` để hiểu phương pháp/giới hạn, `DATA_ACCESS.md` để phân biệt kiểm tra public với rebuild cần private inputs, và `OPERATIONS.md` để biết điều kiện bắt đầu prospective paper. Script public verifier không cần dữ liệu nguồn riêng và không fit lại mô hình.

Snapshot kết thúc 31/12/2025; không có live signal hoặc forward returns. Không gọi trạng thái này là hoàn tất live trading. Các extension như thêm model families, leave-sector-out, tối ưu covariance hoặc feed hiện tại cần nghiên cứu/vận hành riêng và không được mô tả là đã thực hiện.
