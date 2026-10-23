# -*- coding: utf-8 -*-
"""
Noi dung email cua nhom: tieu de, plain text khong dau, va toan bo noi dung landing page cua TV1.
Giao dien HTML nam o template_minimal.py (cung dung noi dung trong file nay).
"""

from __future__ import annotations

import unicodedata

TEAM_NAME = "Nhom 9"
TEAM_NAME_VI = "Nhóm 9"
PROJECT_NAME_VI = "Phân tích và phòng chống tấn công mạng phổ biến tại Việt Nam"
CONTACT_EMAIL = "ngocnguyen.31251024154@st.ueh.edu.vn"

_PUNCT_MAP = str.maketrans({
    "–": "-", "—": "-", "‘": "'", "’": "'", "“": '"', "”": '"',
    "…": "...", "\u00a0": " ",
})


def strip_accents(text: str) -> str:
    text = (text or "").replace("đ", "d").replace("Đ", "D").translate(_PUNCT_MAP)
    decomposed = unicodedata.normalize("NFD", text)
    no_marks = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    return no_marks.encode("ascii", "ignore").decode("ascii")


def display_project_name(project_name: str) -> str:
    if strip_accents(PROJECT_NAME_VI) == project_name:
        return PROJECT_NAME_VI
    return project_name


def subject_basic(project_name: str) -> str:
    return f"Gioi thieu do an: {project_name}"


def subject_advanced(project_name: str) -> str:
    return f"Gioi thieu do an: {project_name}"


# (tu khoa trong role, loi chao khong dau, cau dan khong dau, loi chao co dau, cau dan co dau)
ROLE_RULES = [
    (("giang vien", "thay", "co giao", "huong dan"),
     "Kinh gui Thay/Co {name}", "Nhom em kinh mong nhan duoc nhan xet cua Thay/Co ve san pham nay.",
     "Kính gửi Thầy/Cô {name}", "Nhóm em kính mong nhận được nhận xét của Thầy/Cô về sản phẩm này."),
    (("kiem thu", "tester", "test"),
     "Chao ban {name}", "Nho ban kiem tra giup website, email va chuc nang gui thu cua nhom.",
     "Chào {name}", "Nhờ bạn kiểm tra giúp website, email và chức năng gửi thư của nhóm."),
    (("nhom truong", "truong nhom", "leader"),
     "Chao nhom truong {name}", "Day la ban tong hop de nhom truong theo doi tien do chung.",
     "Chào nhóm trưởng {name}", "Đây là bản tổng hợp để nhóm trưởng theo dõi tiến độ chung."),
]
DEFAULT_RULE = (
    (),
    "Xin chao {name}", "Rat mong ban danh it phut xem qua noi dung do an cua nhom.",
    "Xin chào {name}", "Rất mong bạn dành ít phút xem qua nội dung đồ án của nhóm.",
)


def match_role(role: str) -> tuple:
    role_key = strip_accents(role).lower()
    for rule in ROLE_RULES:
        if any(k in role_key for k in rule[0]):
            return rule
    return DEFAULT_RULE


def build_greeting(full_name: str, role: str) -> tuple[str, str]:
    rule = match_role(role)
    name = strip_accents(full_name).strip() or "ban"
    return rule[1].format(name=name), rule[2]


def build_greeting_vi(full_name: str, role: str, custom_message: str = "") -> tuple[str, str, str]:
    """Tra ve (loi chao co dau, vai tro, loi nhan) dung cho phan HTML."""
    rule = match_role(role)
    name = (full_name or "").strip() or "bạn"
    role_text = (role or "").strip() or "Thành viên"
    message = custom_message.strip() if custom_message and custom_message.strip() else rule[4]
    return rule[3].format(name=name), role_text, message


def render_basic_text(project_name: str, project_url: str) -> str:
    return (
        "Xin chao ban,\n\n"
        "Nhom chung minh xin gioi thieu do an mon Mang may tinh:\n"
        f'"{project_name}".\n\n'
        "Do an tim hieu cac kieu tan cong mang pho bien, mo phong\n"
        "mo hinh mang phong thu va dua ra huong dan phong chong.\n\n"
        f"Moi ban xem them tai: {project_url}\n\n"
        "Cam on ban da quan tam!\n\n"
        "Tran trong,\n"
        f"{TEAM_NAME}"
    )


def render_plain_text(full_name: str, role: str, project_name: str, project_url: str,
                      custom_message: str = "") -> str:
    greeting, role_line = build_greeting(full_name, role)
    role_plain = strip_accents(role) or "Thanh vien"
    if custom_message and custom_message.strip():
        role_line = "Loi nhan rieng: " + strip_accents(custom_message.strip())

    return (
        f"{greeting},\n"
        f"(Vai tro cua ban trong du an: {role_plain})\n\n"
        "Nhom chung minh xin gioi thieu do an mon Mang may tinh:\n"
        f'"{project_name}".\n\n'
        "Do an tim hieu cac kieu tan cong mang pho bien, mo phong\n"
        "mo hinh mang phong thu va dua ra huong dan phong chong.\n\n"
        f"{role_line}\n\n"
        f"Moi ban xem them tai: {project_url}\n\n"
        "Cam on ban da quan tam!\n\n"
        "Tran trong,\n"
        f"{TEAM_NAME}\n"
    )


# Noi dung landing page cua TV1 (muc 1.1 - 1.8)

BACKGROUND = ("Ở Việt Nam, Internet đã đi vào mọi mặt đời sống: học online, mua sắm, ngân hàng số, mạng xã hội. "
              "Người dùng và doanh nghiệp càng dùng nhiều dịch vụ trực tuyến thì càng là mục tiêu của kẻ xấu, "
              "từ lừa đảo qua email, tin nhắn đến tấn công vào hệ thống mạng.")

PROBLEMS = [
    "Nhiều người dùng chưa nhận ra các kiểu tấn công phổ biến, dễ bị lừa mất tài khoản và dữ liệu.",
    "Doanh nghiệp nhỏ thường chưa có mô hình mạng được bảo vệ đúng cách (thiếu tường lửa, không chia vùng mạng).",
    "Thiếu tài liệu hướng dẫn phòng chống ngắn gọn, dễ hiểu, dễ áp dụng.",
]

GENERAL_GOAL = ("Giúp nhận biết và phòng chống các kiểu tấn công mạng phổ biến tại Việt Nam bằng một mô hình "
                "mạng an toàn hơn.")

SPECIFIC_GOALS = [
    "Tìm hiểu và mô tả các kiểu tấn công mạng phổ biến.",
    "Thiết kế mô hình mạng có các lớp bảo vệ và mô phỏng bằng Packet Tracer hoặc GNS3.",
    "Đưa ra hướng dẫn phòng chống đơn giản cho người dùng và doanh nghiệp nhỏ.",
]

EXPECTED_INTRO = "Dự án hướng đến hoàn thiện các sản phẩm cụ thể:"

EXPECTED_RESULTS = [
    "Một bộ phân tích các kiểu tấn công mạng phổ biến.",
    "Một mô hình mạng phòng thủ đã mô phỏng trên công cụ chuyên dụng.",
    "Bộ khuyến nghị bảo mật thiết thực, dễ hiểu và dễ áp dụng vào thực tế.",
]

SOLUTIONS_INTRO = "Giải pháp của nhóm gồm 3 phần chính:"

SOLUTIONS = [
    ("Phân tích tấn công",
     "Phân tích chi tiết các kiểu tấn công mạng phổ biến và đưa ra giải pháp phòng chống cụ thể "
     "(chi tiết tại bảng bên dưới)."),
    ("Mô hình mạng phòng thủ",
     "Tường lửa (firewall) chặn truy cập không mong muốn; chia vùng mạng bằng VLAN và DMZ để máy chủ "
     "công khai tách khỏi mạng nội bộ; VPN cho truy cập từ xa."),
    ("Giao thức & Công nghệ",
     "HTTP/HTTPS, DNS, SMTP, FTP, TLS; mô phỏng bằng Packet Tracer hoặc GNS3."),
]

# (kieu tan cong, giai thich phuong thuc, cach phong chong)
ATTACK_TABLE = [
    ("Phishing (lừa đảo)",
     "Gửi email hoặc link giả mạo để lừa người dùng nhập mật khẩu, thông tin ngân hàng.",
     "Kiểm tra địa chỉ người gửi và link trước khi bấm; bật xác minh 2 bước; lọc thư rác."),
    ("DDoS (làm sập dịch vụ)",
     "Gửi cực nhiều yêu cầu cùng lúc để máy chủ quá tải, người dùng thật không vào được.",
     "Dùng tường lửa, giới hạn số yêu cầu, dịch vụ chống DDoS."),
    ("Dò mật khẩu (brute force)",
     "Thử rất nhiều mật khẩu liên tục cho đến khi đoán đúng.",
     "Mật khẩu dài và khác nhau, khóa tạm sau nhiều lần sai, xác minh 2 bước."),
    ("Giả mạo DNS",
     "Làm cho tên miền thật bị dẫn tới địa chỉ giả để lấy thông tin.",
     "Dùng DNS đáng tin cậy, kiểm tra ổ khóa HTTPS của trang web."),
    ("Nghe lén dữ liệu",
     "Đọc trộm dữ liệu khi truyền không mã hóa (như HTTP, FTP).",
     "Dùng HTTPS, SFTP hoặc VPN để mã hóa dữ liệu."),
]

FEATURES = [
    ("Thư viện tấn công", "Mô tả từng kiểu tấn công và dấu hiệu nhận biết."),
    ("Mô hình mạng phòng thủ", "Sơ đồ có firewall, DMZ, VLAN, mô phỏng bằng Packet Tracer hoặc GNS3."),
    ("Hướng dẫn phòng chống", "Các bước đơn giản cho người dùng và doanh nghiệp nhỏ."),
    ("Landing Page giới thiệu", "Đưa lên Internet bằng hosting, ai cũng truy cập được."),
    ("Email giới thiệu tự động", "Gửi bằng chương trình Python qua SMTP."),
    ("Mô phỏng WebRTC", "Minh họa kết nối trực tiếp giữa các máy (P2P)."),
]

MODEL_INTRO = ("Nhóm đề xuất xây dựng mô hình mạng phòng thủ nhằm minh họa cách bảo vệ hệ thống trước các kiểu "
               "tấn công mạng phổ biến tại Việt Nam. Mô hình sử dụng nhiều lớp bảo vệ, kết hợp giữa tường lửa, "
               "phân chia vùng mạng và các giao thức truyền dữ liệu an toàn.")

COMPONENTS = [
    ("Internet", "Môi trường kết nối giữa người dùng và hệ thống mạng, đồng thời cũng là nơi phát sinh "
                 "các nguy cơ tấn công từ bên ngoài."),
    ("Router", "Chuyển tiếp lưu lượng dữ liệu giữa các mạng theo cấu hình."),
    ("Firewall (tường lửa)", "Kiểm soát lưu lượng truy cập vào và ra khỏi hệ thống dựa trên các quy tắc bảo mật."),
    ("DMZ", "Vùng mạng dành cho máy chủ cung cấp dịch vụ công khai, giúp tách biệt máy chủ với mạng nội bộ."),
    ("VLAN", "Phân chia mạng nội bộ thành các vùng logic để quản lý truy cập và hạn chế ảnh hưởng khi xảy ra sự cố."),
    ("VPN", "Hỗ trợ người dùng được cấp quyền truy cập mạng từ xa thông qua kết nối được mã hóa."),
    ("Máy chủ và máy tính nội bộ", "Cung cấp dịch vụ, lưu trữ dữ liệu và phục vụ hoạt động của người dùng "
                                   "trong hệ thống."),
]

FLOW = [
    "Người dùng từ Internet gửi yêu cầu truy cập đến hệ thống.",
    "Router và Firewall tiếp nhận, định tuyến và kiểm soát lưu lượng theo cấu hình.",
    "Các yêu cầu truy cập dịch vụ công khai được chuyển đến máy chủ trong vùng DMZ theo quy tắc cho phép.",
    "Mạng nội bộ được phân chia bằng VLAN nhằm hạn chế truy cập không cần thiết giữa các nhóm thiết bị.",
    "Người dùng làm việc từ xa có thể kết nối qua VPN khi được cấp quyền.",
    "Hệ thống áp dụng HTTPS/TLS, mật khẩu mạnh và xác thực hai yếu tố để tăng cường bảo vệ tài khoản và dữ liệu.",
]

MODEL_NOTE = ("Mô hình hướng đến việc hạn chế truy cập trái phép, giảm nguy cơ lộ dữ liệu và tăng khả năng "
              "kiểm soát lưu lượng mạng.")

TOOLS_TEXT = ("Nhóm dự kiến sử dụng Cisco Packet Tracer hoặc GNS3 để xây dựng và kiểm tra mô hình mạng. Sơ đồ "
              "kiến trúc chi tiết sẽ do thành viên phụ trách thiết kế thực hiện và được bổ sung vào Landing "
              "Page sau khi hoàn thành.")

DIAGRAM_TITLE = "[ KHUNG DÀNH CHO SƠ ĐỒ MÔ HÌNH MẠNG ]"
DIAGRAM_TOOL = "Công cụ mô phỏng: Cisco Packet Tracer / GNS3"
DIAGRAM_NOTE = ("(TV3 – Nguyễn Thanh Tuấn sẽ chèn ảnh sơ đồ kiến trúc mạng đồ họa chất lượng cao "
                "tại vị trí này)")

TEAM_INTRO = ("Đồ án “Phân tích và phòng chống tấn công mạng phổ biến tại Việt Nam” được thực hiện bởi nhóm 9 "
              "trong khuôn khổ môn học Mạng máy tính tại Đại học Kinh tế TP. Hồ Chí Minh (UEH). Mỗi thành viên "
              "đảm nhận một nhiệm vụ cụ thể, phối hợp với các thành viên khác để hoàn thành sản phẩm chung.")

TEAM = [
    ("TV1 – Nguyễn Phúc Khánh Ngọc",
     "Điều phối nhóm; biên soạn nội dung Landing Page phần 1–4; soạn email giới thiệu; giải thích lý thuyết "
     "mạng và các giao thức DNS, HTTP/HTTPS, FTP, SMTP; tổng hợp báo cáo."),
    ("TV2 – Lê Thành Tài",
     "Biên soạn nội dung Landing Page phần 5–8; sử dụng AI tạo mã nguồn HTML/CSS thô; tạo file contacts.csv "
     "phục vụ tính năng gửi email cá nhân hóa."),
    ("TV3 – Nguyễn Thanh Tuấn",
     "Thiết kế sơ đồ kiến trúc mạng, luồng tấn công và mô hình phòng thủ; chèn sơ đồ vào website và tối ưu "
     "giao diện trên điện thoại, máy tính bảng."),
    ("TV4 – Hoàng Ngọc Thảo Như",
     "Đăng ký hosting InfinityFree; sử dụng FileZilla tải website và file WebRTC lên máy chủ; cung cấp đường "
     "dẫn website thực tế; hỗ trợ kiểm tra kết nối SMTP."),
    ("TV5 – Thái Hoàng Long",
     "Thực hiện mô phỏng WebRTC P2P ở phía Peer A; tạo Offer và gửi cho Peer B; phối hợp mở rộng mô phỏng "
     "kết nối ba người dùng."),
    ("TV6 – Lâm Bội San",
     "Thực hiện mô phỏng WebRTC P2P ở phía Peer B; tạo Answer và hoàn tất kết nối; viết tài liệu so sánh "
     "SMTP và HTTP; kiểm tra email nhận được."),
    ("TV7 – Đỗ Gia Mẫn",
     "Lập trình Python gửi email qua Gmail SMTP; sử dụng file contacts.csv để cá nhân hóa email; ghi nhận "
     "trạng thái gửi thành công hoặc thất bại."),
]

TIMELINE_INTRO = ("Đồ án được triển khai theo các giai đoạn nhằm đảm bảo nội dung nghiên cứu, mô hình mạng và các "
                  "chức năng minh họa được hoàn thiện theo kế hoạch.")

# (giai doan, noi dung cong viec, ket qua du kien)
TIMELINE = [
    ("Giai đoạn 1: Nghiên cứu",
     "Tìm hiểu các kiểu tấn công mạng phổ biến và tổng hợp biện pháp phòng chống.",
     "Nội dung nghiên cứu và giải pháp đề xuất."),
    ("Giai đoạn 2: Thiết kế",
     "Xây dựng mô hình mạng phòng thủ, biên soạn nội dung và thiết kế giao diện Landing Page.",
     "Sơ đồ mạng và giao diện website cơ bản."),
    ("Giai đoạn 3: Phát triển",
     "Tạo mã nguồn HTML/CSS, triển khai hosting và tải website lên máy chủ.",
     "Website có thể truy cập qua Internet."),
    ("Giai đoạn 4: Kiểm thử",
     "Kiểm tra website, thử nghiệm gửi email SMTP và mô phỏng kết nối WebRTC P2P.",
     "Kết quả kiểm thử và ảnh minh chứng."),
    ("Giai đoạn 5: Hoàn thiện",
     "Tổng hợp kết quả, hoàn thiện báo cáo và chuẩn bị nội dung thuyết trình.",
     "Báo cáo đồ án và sản phẩm hoàn chỉnh."),
]

TIMELINE_NOTE = ("Tiến độ thực tế sẽ được cập nhật theo quá trình làm việc của các thành viên. Nhóm sẽ ghi nhận "
                 "những công việc đã hoàn thành, những nội dung còn tồn đọng và điều chỉnh kế hoạch khi cần thiết.")

CONTACT_ABOUT = ("Thông qua dự án, nhóm mong muốn chia sẻ kiến thức an toàn thông tin một cách trực quan, dễ hiểu "
                 "và có tính ứng dụng. Người truy cập có thể tìm hiểu các kiểu tấn công mạng phổ biến, nhận biết "
                 "dấu hiệu nguy hiểm và tham khảo những biện pháp bảo vệ tài khoản, dữ liệu cá nhân cũng như hệ "
                 "thống mạng của doanh nghiệp nhỏ.")

CONTACT_UPDATE = ("Mọi thông tin về tiến độ và sản phẩm của dự án sẽ được cập nhật trên Landing Page sau khi nhóm "
                  "hoàn thiện và kiểm tra các chức năng.")

FOOTER = "© Đồ án môn Mạng máy tính - Nhóm 9 - UEH"
