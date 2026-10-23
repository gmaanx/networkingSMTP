# Gửi email giới thiệu đồ án bằng Python

Chương trình gửi email giới thiệu đồ án **"Phân tích và phòng chống tấn công mạng phổ biến tại Việt Nam"** (Nhóm 9 – Mạng máy tính – UEH)
qua máy chủ **Gmail SMTP** (`smtp.gmail.com`, cổng **587**, mã hóa **STARTTLS**).

Website dự án: https://networksecurity-s9.42web.io/index.html

## Tính năng

- **Chế độ 1 – Cơ bản:** gửi 1 email văn bản thuần (không dấu) tới 1 người nhận.
- **Chế độ 2 – Nâng cao:** gửi hàng loạt theo danh sách trong `contacts.csv`
  - cá nhân hóa lời chào theo tên, vai trò và lời nhắn riêng của từng người;
  - mỗi thư gồm bản văn bản thuần không dấu + bản HTML có giao diện;
  - đính kèm file (mặc định `Tom_Tat_Du_An_An_Ninh_Mang.pdf`);
  - ghi trạng thái THÀNH CÔNG / THẤT BẠI của từng người ra màn hình và file `email_status.log`.
- **Chế độ 3 – Xem thử:** tạo thư giống chế độ 2 nhưng **không gửi**.

## Yêu cầu

- Python **3.8** trở lên (chỉ dùng thư viện chuẩn, không cần `pip install`).
- Một tài khoản Gmail đã bật **Xác minh 2 bước** và tạo **App Password**.

## Cấu trúc thư mục

| File | Mô tả |
|---|---|
| `send_email.py` | Chương trình chính: menu, đọc CSV, dựng thư, kết nối SMTP, ghi log |
| `email_templates.py` | Nội dung thư: tiêu đề, văn bản không dấu, nội dung các mục 1.1–1.8 |
| `template_minimal.py` | Giao diện HTML |
| `email_hero.jpg` | Ảnh đầu thư |
| `contacts.csv` | Danh sách người nhận |
| `Tom_Tat_Du_An_An_Ninh_Mang.pdf` | File đính kèm mặc định (tự tạo nếu chưa có) |
| `email_status.log` | Log gửi thư (tự sinh) |


## Cài đặt

### 1. Tạo App Password cho Gmail

1. Vào https://myaccount.google.com/security → bật **Xác minh 2 bước**.
2. Vào https://myaccount.google.com/apppasswords → đặt tên (vd `Python Mail`) → **Tạo**.
3. Sao chép mã 16 ký tự (dạng `abcd efgh ijkl mnop`; có khoảng trắng cũng được, chương trình tự bỏ).

### 2. Thiết lập biến môi trường

Mật khẩu **không** ghi trong code mà đọc từ biến môi trường `SENDER_EMAIL` và `SENDER_APP_PASSWORD`.

**PowerShell (Windows):**
```powershell
cd "đường dẫn đến file"
$env:SENDER_EMAIL = "email_cua_ban@gmail.com"
$env:SENDER_APP_PASSWORD = "abcd efgh ijkl mnop"
```

**macOS / Linux:**
```bash
export SENDER_EMAIL="email_cua_ban@gmail.com"
export SENDER_APP_PASSWORD="abcd efgh ijkl mnop"
```

Biến chỉ tồn tại trong cửa sổ terminal hiện tại; mở cửa sổ mới thì phải đặt lại.
Nếu thiếu một trong hai biến, chương trình báo lỗi `Thieu bien moi truong SENDER_EMAIL hoac SENDER_APP_PASSWORD`.

## Cách chạy

### Dùng menu

```powershell
python send_email.py
```

```
  1. Co ban  (Muc 4.2) : Nhap 1 email -> gui thu van ban
  2. Nang cao (Muc 4.3): Gui hang loat tu contacts.csv + HTML + dinh kem
  3. Xem thu : Tao email nhu che do 2 nhung KHONG gui that
  0. Thoat
```

- Chế độ 1: nhập email người nhận → gửi.
- Chế độ 2/3: chọn file đính kèm (`Enter` = file mặc định, `2` = chọn file khác, `3` = không đính kèm).
  Chế độ 2 hỏi xác nhận `[y/N]` trước khi gửi thật.

### Dùng tham số dòng lệnh

```powershell
python send_email.py --mode 1 --to ten@gmail.com          # gửi 1 thư văn bản
python send_email.py --mode 2                              # gửi hàng loạt từ contacts.csv
python send_email.py --mode 2 --csv danh_sach_khac.csv     # gửi theo file CSV khác
python send_email.py --mode 2 --attach "D:\baocao.pdf"     # đính kèm file khác
python send_email.py --mode 2 --no-attach                  # không đính kèm
python send_email.py --mode 3 --no-attach                  # xem thử, không gửi
```

| Tham số | Ý nghĩa |
|---|---|
| `--mode {1,2,3}` | Chạy thẳng một chế độ, bỏ qua menu |
| `--to EMAIL` | Email người nhận (chế độ 1) |
| `--csv PATH` | File danh sách người nhận (mặc định `contacts.csv`) |
| `--attach PATH` | File đính kèm (chế độ 2/3) |
| `--no-attach` | Không đính kèm file |

Chế độ 3 không cần biến môi trường. Sau khi chạy, mở file `.html` trong `email_preview/` bằng trình duyệt để xem thư:
```powershell
start (Get-ChildItem email_preview\01_*.html)
```

## Định dạng `contacts.csv`

File UTF-8 (lưu từ Excel bằng *CSV UTF-8* cũng được), dòng đầu là tiêu đề:

```csv
name,email,role,custom_message
Nguyễn Văn A,nguyenvana@gmail.com,Trưởng nhóm,"Lời nhắn riêng cho bạn A."
Trần Thị B,tranthib@gmail.com,Thành viên,
```

| Cột | Bắt buộc | Ghi chú |
|---|---|---|
| `email` | Có | Dòng có email sai định dạng sẽ bị bỏ qua và cảnh báo |
| `name` (hoặc `full_name`) | Có | Dùng trong lời chào |
| `role` | Có | Ảnh hưởng lời chào: chứa *trưởng nhóm* → "Chào nhóm trưởng…", *giảng viên/thầy/cô* → "Kính gửi Thầy/Cô…", *kiểm thử* → "Chào…" |
| `custom_message` | Không | Hiện trong khung "Lời nhắn riêng"; để trống thì dùng câu mặc định theo vai trò |

> [!NOTE]
> Các địa chỉ trong `contacts.csv` hiện là **địa chỉ tạm** (vd `giaman.tv7@ueh.edu.vn`), gửi tới sẽ không có ai nhận.
> Muốn chạy thật, hãy đổi sang địa chỉ có thật, vd dạng `mando.31251021092+tv7@st.ueh.edu.vn`
> (phần `+tv7` giúp phân biệt từng thư mà tất cả vẫn về cùng một hộp thư).

## Cấu hình

Các hằng số ở đầu `send_email.py`:

| Hằng số | Mặc định | Ý nghĩa |
|---|---|---|
| `PROJECT_URL` | `https://networksecurity-s9.42web.io/index.html` | Link website trong thư |
| `SENDER_DISPLAY_NAME` | `Nhom 9 - Mang May Tinh` | Tên người gửi hiển thị |
| `TEMPLATE_STYLE` | `minimal` | Giao diện HTML (file `template_<tên>.py`) |
| `DEFAULT_ATTACHMENT` | `Tom_Tat_Du_An_An_Ninh_Mang.pdf` | File đính kèm mặc định |
| `DELAY_BETWEEN_EMAILS` | `1.0` | Số giây nghỉ giữa hai thư |
| `SMTP_TIMEOUT` | `30` | Thời gian chờ kết nối SMTP (giây) |

Email liên hệ trong mục 1.8 của thư nằm ở hằng số `CONTACT_EMAIL` trong `email_templates.py`.

Khi đổi `PROJECT_URL`, hãy xóa file `Tom_Tat_Du_An_An_Ninh_Mang.pdf` để chương trình tạo lại PDF với link mới.

## Kết quả

Mỗi lần chạy chế độ 2 in ra (và ghi vào `email_status.log`):

```
2026-10-23 07:30:01 | INFO    | Da doc 7 lien he tu contacts.csv
2026-10-23 07:30:01 | INFO    | Nguoi gui     : email_cua_ban@gmail.com
2026-10-23 07:30:01 | INFO    | So nguoi nhan : 7
2026-10-23 07:30:01 | INFO    | Dinh kem      : Tom_Tat_Du_An_An_Ninh_Mang.pdf
2026-10-23 07:30:03 | SUCCESS | [1/7] a@gmail.com | Nguyễn Văn A | Trưởng nhóm | Trang thai: THÀNH CÔNG
2026-10-23 07:30:04 | ERROR   | [2/7] b@gmail.com | Trần Thị B | Thành viên | Trang thai: THẤT BẠI | Nguyen nhan: ...
...
2026-10-23 07:30:10 | INFO    | TONG KET: Tong 7 | THÀNH CÔNG: 6 | THẤT BẠI: 1
```

Trên terminal, dòng THÀNH CÔNG màu xanh lá, THẤT BẠI màu đỏ, cảnh báo màu vàng
(đặt biến `NO_COLOR=1` để tắt màu).

## Lỗi thường gặp

| Thông báo | Nguyên nhân / cách xử lý |
|---|---|
| `Thieu bien moi truong SENDER_EMAIL hoac SENDER_APP_PASSWORD` | Chưa đặt biến môi trường trong cửa sổ terminal đang dùng |
| `Dang nhap that bai ... (535)` | Sai email / App Password, hoặc chưa bật Xác minh 2 bước. Tạo App Password mới |
| `Khong tim thay file danh sach lien he` | Sai đường dẫn `--csv` |
| `File ... sai dinh dang: thieu cot [...]` | Dòng tiêu đề CSV thiếu cột `email`, `name` hoặc `role` |
| `Bo qua dong N ... email khong hop le` | Dòng đó có email sai định dạng, các dòng khác vẫn gửi bình thường |
| `Dia chi email sai cu phap` | Địa chỉ không hợp lệ theo chuẩn email (vd hai dấu chấm liền nhau) |
| `Het thoi gian cho (30s)` / `Khong phan giai duoc smtp.gmail.com` | Mất mạng hoặc tường lửa chặn cổng 587 |
| `Gmail tu choi noi dung thu ... gioi han so luong gui` | Vượt giới hạn gửi của Gmail (~500 thư/ngày), thử lại sau |
| Thư vào mục Spam | Bấm *Không phải thư rác* trong hộp thư người nhận |
| Log báo THÀNH CÔNG nhưng người nhận không thấy thư | Địa chỉ không tồn tại: Gmail vẫn nhận thư rồi gửi thư báo lỗi (bounce) về hộp thư người gửi sau vài phút |
