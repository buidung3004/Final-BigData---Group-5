# Final-BigData-Group-5

Codebase phục vụ đề tài bài tập lớn cuối kì môn Phân tích dữ liệu lớn trong tài chính (Fintech) 

Người thực hiện: Các thành viên nhóm 5 bao gồm VietNMM, MinhDLH, MinhNVQ, MinhNC, DungBN.

Đề tài: Codebase phục vụ user customize danh mục đầu tư.

Ngôn ngữ lập trình sử dụng: Python, code OOP thì càng tốt.

Các nhiệm vụ cơ bản cần hoàn thành:

- Tập hợp được đầy đủ dữ liệu nhất có thể trong khả năng (tối thiểu: giá, khối lượng, vốn hóa, các thông tin cơ bản, ngành, sàn giao dịch, các chỉ số index cơ bản,…).
- Xử lí, clean data một cách tốt nhất để phục vụ cho quá trình tối ưu hóa (xử lí các TH null, lỗi dữ liệu,…).
- Cho phép user customize thông qua các bước lọc cổ phiểu theo yêu cầu, tự chọn các phương thức tối ưu hóa, 1 method riêng. User có thể lưu trữ portfolio, thực hiện backtest để kiểm tra kết quả danh mục.

Nâng cao: có thể triển khai web app nếu khả thi.

Cấu trúc của project như sau:

## 1. Các bước collect, crawl data

Các dữ liệu về giá, kl, vốn, ngành, sàn, có thể sử dụng trực tiếp từ api vnstock (cần đánh giá lại về tính chính xác và đầy đủ của api này) → sử dụng vnstock để tiết kiệm thời gian (vietstock hay cafef có thể sẽ tốn nhiều thời gian và phức tạp hơn trong khâu coding).

⇒ Có thể triển khai trong một jupyter notebook, ưu tiên kết quả đầu ra là dữ liệu đầy đủ, chính xác.

1. Data lấy xong lưu vào đâu để lôi ra sử dụng dễ dàng ? (excel, db nào đó,…)

## 2.Class Market

Class này đơn giản chỉ phục vụ mục đích gọi dữ liệu ra để sử dụng, ví dụ: prices data được lưu vào trong attribute prices, …. Dữ liệu gọi ra lúc này đã là dữ liệu clean

→ Ở bước này có thể thêm một số tùy chính nhanh nhằm mục đích không phải load toàn bộ dữ liệu lên 1 lúc ví dụ(lọc theo giai đoạn cụ thể, lọc theo các ngành cụ thể,…) → nhằm tăng tốc độ của chương trình.

1. Nghiên cứu kĩ thuật triển khai lazy-loading ? (có thể tìm hiểu kĩ thuật khác)

## 3.Class Filter

Đây sẽ là class lọc chính, là bước user có thể customize portfolio tùy theo ý tưởng của mình: 

1. Nghiên cứu các tùy chọn lọc khả thi ?

## 4.Class Optimize

Cơ bản nhất cần làm được là MPT

→ phát triển những method khác 

## 5.Class Portfolio

Phân bổ danh mục đầu tư theo optimize ở bên trên, theo từng giải đoạn nắm giữ(ví dụ nắm giữ danh mục 3 tháng rebalance lại 1 lần chẳng hạn).
