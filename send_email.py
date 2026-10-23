# -*- coding: utf-8 -*-
"""
Che do 1: nhap 1 email, gui thu van ban (muc 4.2)
Che do 2: gui hang loat tu contacts.csv, co HTML + dinh kem + log (muc 4.3)
Che do 3: giong che do 2 nhung chi luu ra thu muc email_preview/, khong gui
"""

from __future__ import annotations

import argparse
import csv
import importlib
import logging
import mimetypes
import os
import re
import smtplib
import socket
import ssl
import sys
import textwrap
import time
from email import errors as email_errors
from email.headerregistry import Address
from email.message import EmailMessage
from pathlib import Path

import email_templates as tpl

BASE_DIR = Path(__file__).resolve().parent

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_TIMEOUT = 30

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_APP_PASSWORD")

PROJECT_NAME = "Phan tich va phong chong tan cong mang pho bien tai Viet Nam"
PROJECT_URL = "https://networksecurity-s9.42web.io/index.html"

SENDER_DISPLAY_NAME = "Nhom 9 - Mang May Tinh"

TEMPLATE_STYLE = "minimal"
HERO_IMAGE = BASE_DIR / "email_hero.jpg"

CONTACTS_FILE = BASE_DIR / "contacts.csv"
CONTACTS_COLUMNS = ("email", "full_name", "role")
COLUMN_ALIASES = {"name": "full_name", "ho_ten": "full_name", "message": "custom_message"}

ATTACH_ENABLED = True
DEFAULT_ATTACHMENT = BASE_DIR / "Tom_Tat_Du_An_An_Ninh_Mang.pdf"

LOG_FILE = BASE_DIR / "email_status.log"
PREVIEW_DIR = BASE_DIR / "email_preview"
DELAY_BETWEEN_EMAILS = 1.0

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


SUCCESS = 25
logging.addLevelName(SUCCESS, "SUCCESS")

_RESET = "\033[0m"
_COLORS = {
    logging.DEBUG: "\033[90m",
    logging.INFO: "\033[96m",
    SUCCESS: "\033[92m",
    logging.WARNING: "\033[93m",
    logging.ERROR: "\033[91m",
}


class ConsoleFormatter(logging.Formatter):
    def __init__(self, use_color: bool):
        super().__init__("%(asctime)s | %(levelname)-7s | %(message)s", "%Y-%m-%d %H:%M:%S")
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        text = super().format(record)
        if self.use_color:
            return f"{_COLORS.get(record.levelno, '')}{text}{_RESET}"
        return text


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("email_sender")
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)

    use_color = sys.stdout.isatty() and not os.getenv("NO_COLOR")
    if use_color and os.name == "nt":
        os.system("")

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(ConsoleFormatter(use_color))

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", "%Y-%m-%d %H:%M:%S")
    )

    logger.addHandler(console)
    logger.addHandler(file_handler)
    logger.propagate = False
    return logger


log = setup_logging()


def log_banner(title: str) -> None:
    line = "=" * 78
    log.info(line)
    log.info(title.center(78))
    log.info(line)


def require_credentials() -> tuple[str, str]:
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        raise ValueError(
            "Thieu bien moi truong SENDER_EMAIL hoac SENDER_APP_PASSWORD. "
            "Hay thiet lap truoc khi chay (xem README.md)."
        )
    return SENDER_EMAIL.strip(), SENDER_PASSWORD.replace(" ", "")


def is_valid_email(email: str) -> bool:
    return bool(email) and bool(EMAIL_REGEX.match(email.strip()))


def make_address(display_name: str, email: str) -> str:
    return str(Address(display_name=tpl.strip_accents(display_name), addr_spec=email.strip()))


def explain_error(exc: Exception) -> str:
    if isinstance(exc, smtplib.SMTPAuthenticationError):
        return ("Dang nhap that bai: sai SENDER_EMAIL/App Password, hoac tai khoan chua bat "
                "xac thuc 2 buoc (535)")
    if isinstance(exc, smtplib.SMTPRecipientsRefused):
        return "Gmail tu choi dia chi nguoi nhan (khong ton tai/sai dinh dang)"
    if isinstance(exc, smtplib.SMTPSenderRefused):
        return "Gmail tu choi dia chi nguoi gui"
    if isinstance(exc, smtplib.SMTPDataError):
        return f"Gmail tu choi noi dung thu (ma {exc.smtp_code}) - co the bi gioi han so luong gui"
    if isinstance(exc, smtplib.SMTPServerDisconnected):
        return "May chu SMTP ngat ket noi dot ngot"
    if isinstance(exc, smtplib.SMTPConnectError):
        return "Khong ket noi duoc may chu SMTP"
    if isinstance(exc, (socket.timeout, TimeoutError)):
        return f"Het thoi gian cho ({SMTP_TIMEOUT}s) - kiem tra mang/tuong lua"
    if isinstance(exc, socket.gaierror):
        return "Khong phan giai duoc smtp.gmail.com - kiem tra ket noi Internet"
    if isinstance(exc, ssl.SSLError):
        return f"Loi TLS/SSL: {exc}"
    if isinstance(exc, FileNotFoundError):
        return f"Khong tim thay file: {exc}"
    if isinstance(exc, (email_errors.MessageDefect, email_errors.HeaderParseError)):
        return "Dia chi email sai cu phap (vi du hai dau cham lien nhau) - khong tao duoc thu"
    if isinstance(exc, smtplib.SMTPException):
        return f"Loi SMTP: {exc}"
    return f"{type(exc).__name__}: {exc}"


def _pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def create_sample_pdf(path: Path, title: str, lines: list[str]) -> None:
    wrapped: list[str] = []
    for line in lines:
        wrapped.extend(textwrap.wrap(line, 90) or [""])

    stream = [f"BT /F1 18 Tf 50 790 Td ({_pdf_escape(title)}) Tj", "/F1 11 Tf 0 -34 Td 16 TL"]
    for line in wrapped[:42]:
        stream.append(f"({_pdf_escape(line)}) Tj T*")
    stream.append("ET")
    content = "\n".join(stream).encode("latin-1", "replace")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Contents 5 0 R /Resources << /Font << /F1 4 0 R >> >> >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref_pos = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode() + b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += (f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_pos}\n%%EOF\n").encode()
    path.write_bytes(bytes(out))


def create_sample_attachment(path: Path = DEFAULT_ATTACHMENT) -> None:
    title = "TOM TAT DU AN AN NINH MANG"
    lines = [
        f"De tai: {PROJECT_NAME}",
        f"Website: {PROJECT_URL}",
        "",
        "1. Boi canh: tan cong mang tai Viet Nam ngay cang da dang va tinh vi.",
        "2. Cac hinh thuc pho bien: phishing, ransomware, DDoS, khai thac lo hong web.",
        "3. Giai phap: xac thuc 2 lop, cap nhat va loi, sao luu du lieu, nang cao nhan thuc.",
    ]
    if path.suffix.lower() == ".pdf":
        create_sample_pdf(path, title, [tpl.strip_accents(x) for x in lines])
    else:
        path.write_text(title + "\n\n" + "\n".join(lines) + "\n", encoding="utf-8")


def ensure_sample_files() -> None:
    if not DEFAULT_ATTACHMENT.exists():
        create_sample_attachment()
        log.info("Da tao file dinh kem mau %s", DEFAULT_ATTACHMENT.name)


def read_contacts(path: Path = CONTACTS_FILE) -> list[dict[str, str]]:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Khong tim thay file danh sach lien he: {path}")

    contacts: list[dict[str, str]] = []
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise ValueError(f"File {path.name} rong.")
            headers = [h.strip().lower() for h in reader.fieldnames]
            reader.fieldnames = [COLUMN_ALIASES.get(h, h) for h in headers]
            missing = [c for c in CONTACTS_COLUMNS if c not in reader.fieldnames]
            if missing:
                raise ValueError(
                    f"File {path.name} sai dinh dang: thieu cot {missing}. "
                    "Header hop le: email,name,role[,custom_message] "
                    "(hoac email,full_name,role)"
                )
            for line_no, row in enumerate(reader, start=2):
                email = (row.get("email") or "").strip()
                full_name = (row.get("full_name") or "").strip()
                role = (row.get("role") or "").strip()
                custom_message = (row.get("custom_message") or "").strip()
                if not (email or full_name or role):
                    continue
                if not is_valid_email(email):
                    log.warning("Bo qua dong %d trong %s: email khong hop le (%r)",
                                line_no, path.name, email)
                    continue
                contacts.append({"email": email, "full_name": full_name, "role": role,
                                 "custom_message": custom_message})
    except UnicodeDecodeError as exc:
        raise ValueError(f"File {path.name} khong phai UTF-8: {exc}") from exc
    except csv.Error as exc:
        raise ValueError(f"File {path.name} sai dinh dang CSV: {exc}") from exc

    if not contacts:
        raise ValueError(f"File {path.name} khong co lien he hop le nao.")
    return contacts


def attach_file(message: EmailMessage, file_path: Path) -> None:
    file_path = Path(file_path)
    if not file_path.is_file():
        raise FileNotFoundError(str(file_path))
    ctype, encoding = mimetypes.guess_type(file_path.name)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"
    maintype, subtype = ctype.split("/", 1)
    message.add_attachment(
        file_path.read_bytes(), maintype=maintype, subtype=subtype, filename=file_path.name
    )


def build_basic_message(sender: str, recipient: str) -> EmailMessage:
    if not recipient or not recipient.strip():
        raise ValueError("Email nguoi nhan khong duoc de trong.")
    if not is_valid_email(recipient):
        raise ValueError(f"Email nguoi nhan khong hop le: {recipient!r}")

    message = EmailMessage()
    message["Subject"] = tpl.subject_basic(PROJECT_NAME)
    message["From"] = make_address(SENDER_DISPLAY_NAME, sender)
    message["To"] = recipient.strip()
    message.set_content(tpl.render_basic_text(PROJECT_NAME, PROJECT_URL))
    return message


def build_advanced_message(sender: str, contact: dict[str, str],
                           attachment: Path | None) -> EmailMessage:
    email, full_name, role = contact["email"], contact["full_name"], contact["role"]
    custom_message = contact.get("custom_message", "")
    if not email or not email.strip():
        raise ValueError("Email nguoi nhan khong duoc de trong.")

    message = EmailMessage()
    message["Subject"] = tpl.subject_advanced(PROJECT_NAME)
    message["From"] = make_address(SENDER_DISPLAY_NAME, sender)
    message["To"] = make_address(full_name or email, email)

    message.set_content(
        tpl.render_plain_text(full_name, role, PROJECT_NAME, PROJECT_URL, custom_message)
    )

    design = importlib.import_module(f"template_{TEMPLATE_STYLE}")
    hero_cid = getattr(design, "HERO_CID", None) if HERO_IMAGE.is_file() else None

    message.add_alternative(
        design.render_html(full_name, role, PROJECT_NAME, PROJECT_URL, custom_message,
                           contact_email=tpl.CONTACT_EMAIL, hero_cid=hero_cid),
        subtype="html",
    )
    if hero_cid:
        message.get_body(preferencelist=("html",)).add_related(
            HERO_IMAGE.read_bytes(), maintype="image", subtype="jpeg",
            cid=f"<{hero_cid}>", filename=HERO_IMAGE.name,
        )

    if attachment:
        attach_file(message, attachment)
    return message


def connect_smtp(sender: str, password: str) -> smtplib.SMTP:
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=SMTP_TIMEOUT)
    try:
        server.ehlo()
        server.starttls(context=ssl.create_default_context())
        server.ehlo()
        server.login(sender, password)
    except Exception:
        server.close()
        raise
    return server


def send_basic_email(recipient: str) -> bool:
    log_banner("CHE DO 1: GUI EMAIL CO BAN (Muc 4.2)")
    try:
        sender, password = require_credentials()
        message = build_basic_message(sender, recipient)
        log.info("Dang ket noi %s:%d (STARTTLS) ...", SMTP_SERVER, SMTP_PORT)
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=SMTP_TIMEOUT) as server:
            server.ehlo()
            server.starttls(context=ssl.create_default_context())
            server.ehlo()
            server.login(sender, password)
            server.send_message(message)
        log.log(SUCCESS, "Nguoi nhan: %s | Trang thai: THÀNH CÔNG", recipient.strip())
        return True
    except ValueError as exc:
        log.error("Loi cau hinh/du lieu: %s", exc)
    except Exception as exc:
        log.error("Nguoi nhan: %s | Trang thai: THẤT BẠI | Nguyen nhan: %s",
                  (recipient or "").strip(), explain_error(exc))
    return False


def save_preview(message: EmailMessage, index: int, email: str) -> Path:
    PREVIEW_DIR.mkdir(exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9_.@-]", "_", email)
    eml_path = PREVIEW_DIR / f"{index:02d}_{safe}.eml"
    eml_path.write_bytes(bytes(message))
    html_part = message.get_body(preferencelist=("html",))
    if html_part is not None:
        content = html_part.get_content()
        if HERO_IMAGE.is_file():
            content = content.replace("cid:hero_image", HERO_IMAGE.as_uri())
        (PREVIEW_DIR / f"{index:02d}_{safe}.html").write_text(content, encoding="utf-8")
    return eml_path


def send_bulk(contacts: list[dict[str, str]], attachment: Path | None,
              dry_run: bool = False) -> tuple[int, int]:
    title = "CHE DO 3: XEM THU (KHONG GUI THAT)" if dry_run \
        else "CHE DO 2: GUI HANG LOAT NANG CAO (Muc 4.3)"
    log_banner(title)

    if dry_run:
        sender, password = (SENDER_EMAIL or "demo.sender@gmail.com"), ""
    else:
        sender, password = require_credentials()

    total = len(contacts)
    log.info("Nguoi gui     : %s", sender)
    log.info("So nguoi nhan : %d", total)
    log.info("Dinh kem      : %s", attachment.name if attachment else "(khong)")
    log.info("-" * 78)

    ok = fail = 0
    server: smtplib.SMTP | None = None
    fatal_reason: str | None = None
    try:
        for idx, c in enumerate(contacts, start=1):
            prefix = f"[{idx}/{total}] {c['email']} | {c['full_name']} | {c['role']}"
            if fatal_reason:
                # dang nhap loi thi khong thu lai nua
                fail += 1
                log.error("%s | Trang thai: THẤT BẠI | Nguyen nhan: %s", prefix, fatal_reason)
                continue
            try:
                message = build_advanced_message(sender, c, attachment)
                if dry_run:
                    path = save_preview(message, idx, c["email"])
                    log.log(SUCCESS, "%s | Trang thai: THÀNH CÔNG (xem thu -> %s)", prefix, path.name)
                else:
                    if server is None:
                        try:
                            server = connect_smtp(sender, password)
                        except Exception as conn_exc:
                            fatal_reason = explain_error(conn_exc)
                            raise
                    server.send_message(message)
                    log.log(SUCCESS, "%s | Trang thai: THÀNH CÔNG", prefix)
                ok += 1
            except Exception as exc:
                fail += 1
                reason = explain_error(exc)
                log.error("%s | Trang thai: THẤT BẠI | Nguyen nhan: %s", prefix, reason)
                if isinstance(exc, smtplib.SMTPServerDisconnected) and server is not None:
                    server = None
                    fatal_reason = None
            if not dry_run and idx < total:
                time.sleep(DELAY_BETWEEN_EMAILS)
    finally:
        if server is not None:
            try:
                server.quit()
            except Exception:
                server.close()

    log.info("-" * 78)
    log.info("TONG KET: Tong %d | THÀNH CÔNG: %d | THẤT BẠI: %d", total, ok, fail)
    log.info("Log chi tiet luu tai: %s", LOG_FILE.name)
    if dry_run:
        log.info("File xem thu luu tai thu muc: %s", PREVIEW_DIR.name)
    return ok, fail


MENU = """
   GUI EMAIL TU DONG  |  SMTP Gmail : STARTTLS : 587 

  1. Co ban  (Muc 4.2) : Nhap 1 email -> gui thu van ban                  
  2. Nang cao (Muc 4.3): Gui hang loat tu contacts.csv + HTML + dinh kem  
  3. Xem thu: Tao email nhu che do 2 nhung KHONG gui that      
  0. Thoat                                                                
"""


def choose_attachment() -> Path | None:
    if not ATTACH_ENABLED:
        return None
    print("\nDinh kem file?")
    print(f"  [1] Dung file mac dinh: {DEFAULT_ATTACHMENT.name}  (Enter)")
    print("  [2] Chon file khac (nhap duong dan)")
    print("  [3] Khong dinh kem")
    choice = input("Chon [1/2/3]: ").strip() or "1"
    if choice == "3":
        return None
    if choice == "2":
        raw = input("Duong dan file: ").strip().strip('"')
        path = Path(raw)
        if path.is_file():
            return path
        log.warning("Khong tim thay %r -> dung file mac dinh.", raw)
    if not DEFAULT_ATTACHMENT.exists():
        create_sample_attachment()
    return DEFAULT_ATTACHMENT


def load_contacts_or_report(path: Path) -> list[dict[str, str]] | None:
    try:
        contacts = read_contacts(path)
    except (FileNotFoundError, ValueError) as exc:
        log.error("%s", exc)
        return None
    log.info("Da doc %d lien he tu %s", len(contacts), path.name)
    return contacts


def run_mode_1(recipient: str | None) -> None:
    if recipient is None:
        recipient = input("Nhap email nguoi nhan: ").strip()
    send_basic_email(recipient)


def run_mode_2(csv_path: Path, attach_arg: str | None, no_attach: bool, dry_run: bool) -> None:
    contacts = load_contacts_or_report(csv_path)
    if contacts is None:
        return
    if no_attach:
        attachment = None
    elif attach_arg:
        attachment = Path(attach_arg)
        if not attachment.is_file():
            log.error("Khong tim thay file dinh kem: %s", attachment)
            return
    else:
        attachment = choose_attachment()
    if not dry_run:
        confirm = input(f"Gui email that toi {len(contacts)} nguoi? [y/N]: ").strip().lower()
        if confirm != "y":
            log.info("Da huy.")
            return
    try:
        send_bulk(contacts, attachment, dry_run=dry_run)
    except ValueError as exc:
        log.error("Loi cau hinh: %s", exc)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="TV7 - Gui email tu dong (smtplib + Gmail STARTTLS)")
    parser.add_argument("--mode", choices=["1", "2", "3"], help="1=co ban, 2=nang cao, 3=xem thu")
    parser.add_argument("--to", help="Email nguoi nhan (che do 1)")
    parser.add_argument("--csv", default=str(CONTACTS_FILE), help="Duong dan contacts.csv")
    parser.add_argument("--attach", help="Duong dan file dinh kem (che do 2/3)")
    parser.add_argument("--no-attach", action="store_true", help="Khong dinh kem file")
    parser.add_argument("--style", choices=["minimal"], help="Giao dien HTML (mac dinh: minimal)")
    args = parser.parse_args()

    if args.style:
        global TEMPLATE_STYLE
        TEMPLATE_STYLE = args.style

    ensure_sample_files()

    if args.mode:
        if args.mode == "1":
            run_mode_1(args.to)
        else:
            run_mode_2(Path(args.csv), args.attach, args.no_attach, dry_run=(args.mode == "3"))
        return 0

    while True:
        print(MENU)
        choice = input("Chon che do [0-3]: ").strip()
        if choice == "1":
            run_mode_1(None)
        elif choice in ("2", "3"):
            run_mode_2(Path(args.csv), None, False, dry_run=(choice == "3"))
        elif choice == "0":
            print("Tam biet!")
            return 0
        else:
            print("Lua chon khong hop le.")
        input("\nNhan Enter de quay lai menu...")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nDa huy boi nguoi dung.")
        sys.exit(130)
