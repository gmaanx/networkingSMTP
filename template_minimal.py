# -*- coding: utf-8 -*-
"""Giao dien email minimal (nen sang, chu den), dung toan bo noi dung landing page cua TV1."""

from __future__ import annotations

import html

import email_templates as c

HERO_CID = "hero_image"

PAGE = "#f4f4f5"
CARD = "#ffffff"
SOFT = "#f6f6f7"
LINE = "#ececec"
TEXT = "#111111"
MUTED = "#6b7280"
LIGHT = "#9ca3af"
FONT = "'Inter','Segoe UI',Roboto,Helvetica,Arial,sans-serif"
WIDTH = 560


def _e(text: str) -> str:
    return html.escape(text, quote=False)


def _spacer(h: int = 20) -> str:
    return f'<div style="height:{h}px;line-height:{h}px;font-size:0;">&nbsp;</div>'


def _table(inner: str, style: str = "") -> str:
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
            f'style="{style}">{inner}</table>')


def _p(text_html: str, color: str = MUTED, size: int = 14, extra: str = "") -> str:
    return (f'<p style="margin:0;font-family:{FONT};font-size:{size}px;line-height:1.7;'
            f'color:{color};{extra}">{text_html}</p>')


def _section(eyebrow: str, title: str) -> str:
    return (f'{_spacer(40)}'
            f'<div style="font-family:{FONT};font-size:12px;font-weight:600;letter-spacing:1px;'
            f'color:{LIGHT};">{_e(eyebrow)}</div>'
            f'<h2 style="margin:4px 0 14px 0;font-family:{FONT};font-size:19px;line-height:1.4;'
            f'font-weight:700;color:{TEXT};">{_e(title)}</h2>')


def _subhead(text: str, margin_top: int = 20) -> str:
    return (f'<div style="margin:{margin_top}px 0 10px 0;font-family:{FONT};font-size:14px;'
            f'font-weight:600;color:{TEXT};">{_e(text)}</div>')


def _numbered(items: list[tuple[str, str]], start: int = 1) -> str:
    """Moi item: (tieu de, mo ta html). Tieu de rong thi chi hien mo ta."""
    out = []
    for i, (title, desc_html) in enumerate(items, start=start):
        title_html = (f'<div style="font-family:{FONT};font-size:15px;line-height:1.5;font-weight:600;'
                      f'color:{TEXT};">{_e(title)}</div>') if title else ""
        desc_color = MUTED if title else TEXT
        desc_size = 13 if title else 14
        out.append(_table(
            f'<tr><td width="44" valign="top" style="padding:16px 0 16px 18px;font-family:{FONT};'
            f'font-size:28px;line-height:1;font-weight:700;color:{TEXT};">{i}</td>'
            f'<td valign="top" style="padding:16px 18px 16px 8px;">{title_html}'
            f'<div style="margin-top:{4 if title else 2}px;font-family:{FONT};font-size:{desc_size}px;'
            f'line-height:1.6;color:{desc_color};">{desc_html}</div></td></tr>',
            f"margin-bottom:10px;background-color:{CARD};border:1px solid {LINE};border-radius:12px;",
        ))
    return "".join(out)


def _bullets(items: list[str]) -> str:
    rows = "".join(
        f'<tr><td width="18" valign="top" style="padding:3px 0;font-family:{FONT};font-size:14px;'
        f'line-height:1.7;color:{LIGHT};">&bull;</td>'
        f'<td valign="top" style="padding:3px 0;font-family:{FONT};font-size:14px;line-height:1.7;'
        f'color:{MUTED};">{_e(x)}</td></tr>'
        for x in items
    )
    return _table(rows)


def _divider_list(items: list[tuple[str, str]]) -> str:
    rows = []
    for idx, (name, desc) in enumerate(items):
        line = "" if idx == len(items) - 1 else f"border-bottom:1px solid {LINE};"
        rows.append(
            f'<tr><td style="padding:12px 0;{line}">'
            f'<div style="font-family:{FONT};font-size:14px;font-weight:600;color:{TEXT};">{_e(name)}</div>'
            f'<div style="margin-top:2px;font-family:{FONT};font-size:13px;line-height:1.6;color:{MUTED};">'
            f'{_e(desc)}</div></td></tr>'
        )
    return _table("".join(rows), f"border-top:1px solid {LINE};")


def _grid2(cells: list[tuple[str, str]]) -> str:
    def box(title: str, desc: str) -> str:
        return _table(
            f'<tr><td style="padding:14px 16px;">'
            f'<div style="font-family:{FONT};font-size:14px;font-weight:600;color:{TEXT};">{_e(title)}</div>'
            f'<div style="margin-top:4px;font-family:{FONT};font-size:13px;line-height:1.55;color:{MUTED};">'
            f'{_e(desc)}</div></td></tr>',
            f"background-color:{CARD};border:1px solid {LINE};border-radius:12px;",
        )

    rows = []
    for i in range(0, len(cells), 2):
        left = box(*cells[i])
        right = box(*cells[i + 1]) if i + 1 < len(cells) else ""
        rows.append(
            f'<tr><td class="col" width="50%" valign="top" style="padding:0 5px 10px 0;">{left}</td>'
            f'<td class="col" width="50%" valign="top" style="padding:0 0 10px 5px;">{right}</td></tr>'
        )
    return _table("".join(rows))


def _soft_box(inner: str, extra: str = "") -> str:
    return _table(f'<tr><td style="padding:18px 20px;">{inner}</td></tr>',
                  f"background-color:{SOFT};border-radius:12px;{extra}")


def _button(url: str, label: str) -> str:
    return (f'<a href="{url}" target="_blank" style="display:inline-block;padding:13px 28px;'
            f'background-color:{TEXT};border-radius:999px;font-family:{FONT};font-size:14px;font-weight:600;'
            f'color:#ffffff;text-decoration:none;">{_e(label)}</a>')


def render_html(full_name: str, role: str, project_name: str, project_url: str,
                custom_message: str = "", contact_email: str = c.CONTACT_EMAIL, hero_cid: str | None = HERO_CID) -> str:
    greeting, role_text, message = c.build_greeting_vi(full_name, role, custom_message)
    project_name = c.display_project_name(project_name)
    url = html.escape(project_url, quote=True)

    logo = (
        f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center"><tr>'
        f'<td width="30" height="30" align="center" valign="middle" style="width:30px;height:30px;'
        f'background-color:{TEXT};border-radius:50%;font-family:{FONT};font-size:14px;font-weight:700;'
        f'color:#ffffff;">9</td>'
        f'<td style="padding-left:10px;font-family:{FONT};font-size:13px;font-weight:600;letter-spacing:1px;'
        f'color:{TEXT};">NHÓM 9 &middot; UEH</td></tr></table>'
    )

    hero_img = (
        f'{_spacer(24)}<img src="cid:{hero_cid}" width="{WIDTH - 64}" alt="An ninh mạng" '
        f'style="display:block;width:100%;max-width:{WIDTH - 64}px;height:auto;border:0;border-radius:12px;">'
        if hero_cid else ""
    )

    intro = (
        f'{_spacer(28)}<div style="text-align:center;">'
        f'<span style="display:inline-block;padding:5px 14px;background-color:{SOFT};border-radius:999px;'
        f'font-family:{FONT};font-size:12px;font-weight:600;color:{MUTED};">'
        f'Môn học Mạng máy tính &middot; UEH</span>'
        f'<h1 style="margin:16px 0 0 0;font-family:{FONT};font-size:26px;line-height:1.3;font-weight:700;'
        f'letter-spacing:-0.3px;color:{TEXT};">{_e(project_name)}</h1></div>'
        f'{_spacer(24)}'
        + _p(f'<strong style="color:{TEXT};">{_e(greeting)},</strong>', TEXT, 15)
        + _p(f'Nhóm 9 xin giới thiệu đồ án môn Mạng máy tính. {_e(c.BACKGROUND)}', MUTED, 15,
             "margin-top:8px;")
        + f'<div style="margin-top:16px;"><span style="display:inline-block;padding:6px 14px;'
          f'border:1px solid {LINE};border-radius:999px;font-family:{FONT};font-size:12px;color:{MUTED};">'
          f'Vai trò: <strong style="color:{TEXT};">{_e(role_text)}</strong></span></div>'
        + _spacer(16)
        + _soft_box(
            f'<div style="font-family:{FONT};font-size:12px;font-weight:600;letter-spacing:1px;color:{LIGHT};">'
            f'LỜI NHẮN RIÊNG</div>'
            + _p(_e(message), TEXT, 14, "margin-top:6px;")
        )
    )

    problems = _section("1.1", "Vấn đề thực tiễn cần giải quyết") + _numbered([("", _e(x)) for x in c.PROBLEMS])

    objectives = (
        _section("1.2", "Mục tiêu dự án")
        + _subhead("Mục tiêu chung", 0) + _p(_e(c.GENERAL_GOAL))
        + _subhead("Mục tiêu cụ thể") + _numbered([("", _e(x)) for x in c.SPECIFIC_GOALS])
        + _subhead("Kết quả mong đợi", 14) + _p(_e(c.EXPECTED_INTRO), extra="margin-bottom:6px;")
        + _bullets(c.EXPECTED_RESULTS)
    )

    solutions = (
        _section("1.3", "Giải pháp đề xuất")
        + _p(_e(c.SOLUTIONS_INTRO), extra="margin-bottom:12px;")
        + _numbered([(t, _e(d)) for t, d in c.SOLUTIONS])
        + _subhead("Phương thức tấn công & cách phòng chống", 22)
        + _numbered([
            (name, f'{_e(method)}<br><span style="color:{TEXT};"><strong>Phòng chống:</strong> '
                   f'{_e(defense)}</span>')
            for name, method, defense in c.ATTACK_TABLE
        ])
    )

    features = _section("1.4", "Tính năng chính") + _grid2(c.FEATURES)

    diagram = (
        _section("1.5", "Mô hình hoặc sơ đồ minh họa")
        + _subhead("Mô hình mạng phòng thủ đề xuất", 0) + _p(_e(c.MODEL_INTRO))
        + _subhead("Các thành phần chính") + _divider_list(c.COMPONENTS)
        + _subhead("Luồng hoạt động và biện pháp phòng thủ", 22)
        + _numbered([("", _e(x)) for x in c.FLOW])
        + _p(_e(c.MODEL_NOTE), TEXT, 14, "margin-top:6px;font-style:italic;")
        + _subhead("Công cụ mô phỏng", 22) + _p(_e(c.TOOLS_TEXT))
        + _table(
            f'<tr><td align="center" style="padding:32px 20px;font-family:{FONT};">'
            f'<div style="font-size:13px;font-weight:600;letter-spacing:0.5px;color:{TEXT};">'
            f'{_e(c.DIAGRAM_TITLE)}</div>'
            f'<div style="margin-top:6px;font-size:13px;color:{MUTED};">{_e(c.DIAGRAM_TOOL)}</div>'
            f'<div style="margin-top:4px;font-size:12px;color:{LIGHT};">{_e(c.DIAGRAM_NOTE)}</div>'
            f'</td></tr>',
            f"margin-top:14px;background-color:{SOFT};border:1px dashed #d1d5db;border-radius:12px;",
        )
    )

    team = (
        _section("1.6", "Thành viên nhóm")
        + _p(_e(c.TEAM_INTRO), extra="margin-bottom:12px;")
        + _divider_list(c.TEAM)
    )

    timeline = (
        _section("1.7", "Tiến độ thực hiện")
        + _p(_e(c.TIMELINE_INTRO), extra="margin-bottom:12px;")
        + _numbered([
            (t, f'{_e(work)}<br><span style="color:{TEXT};"><strong>Kết quả:</strong> {_e(result)}</span>')
            for t, work, result in c.TIMELINE
        ])
        + _p(_e(c.TIMELINE_NOTE), size=13, extra="margin-top:6px;font-style:italic;")
    )

    email_value = (f'<a href="mailto:{html.escape(contact_email, quote=True)}" style="color:{TEXT};">'
                   f'{_e(contact_email)}</a>' if contact_email else "[Điền email đại diện của nhóm]")
    info_rows = [
        ("Tên đề tài", _e(project_name)),
        ("Nhóm thực hiện", "Nhóm 9"),
        ("Môn học", "Mạng máy tính"),
        ("Đơn vị", "Đại học Kinh tế TP. Hồ Chí Minh (UEH)"),
        ("Email liên hệ", email_value),
        ("Website", f'<a href="{url}" target="_blank" style="color:{TEXT};word-break:break-all;">'
                    f'{_e(project_url)}</a>'),
    ]
    info = _table("".join(
        f'<tr><td class="col" width="120" valign="top" style="padding:5px 0;font-family:{FONT};font-size:13px;'
        f'color:{MUTED};">{k}</td><td class="col" valign="top" style="padding:5px 0;font-family:{FONT};'
        f'font-size:13px;line-height:1.6;color:{TEXT};">{v}</td></tr>'
        for k, v in info_rows
    ))
    contact = (
        _section("1.8", "Thông tin liên hệ")
        + _soft_box(info)
        + _p(_e(c.CONTACT_ABOUT), extra="margin-top:16px;")
        + _p(_e(c.CONTACT_UPDATE), extra="margin-top:8px;")
        + f'{_spacer(28)}<div style="text-align:center;">{_button(url, "Xem website dự án")}</div>'
        + _p(f'hoặc mở: <a href="{url}" target="_blank" style="color:{MUTED};word-break:break-all;">'
             f'{_e(project_url)}</a>', LIGHT, 12, "margin-top:12px;text-align:center;")
        + _p("Cảm ơn bạn đã quan tâm!", TEXT, 14, "margin-top:28px;")
        + _p("Trân trọng,<br><strong>Nhóm 9</strong>", TEXT, 14, "margin-top:8px;")
    )

    footer = (
        f'<p style="margin:0;font-family:{FONT};font-size:12px;line-height:1.6;color:{LIGHT};">{_e(c.FOOTER)}</p>'
        f'<p style="margin:4px 0 0 0;font-family:{FONT};font-size:12px;line-height:1.6;color:{LIGHT};">'
        f'Email gửi tự động bằng Python (smtplib &middot; STARTTLS &middot; cổng 587)</p>'
    )

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="color-scheme" content="light">
<meta name="supported-color-schemes" content="light">
<title>{_e(project_name)} - Nhóm 9 (UEH)</title>
<style>
  @media only screen and (max-width:600px) {{
    .wrap {{ width:100% !important; }}
    .card {{ padding:28px 20px !important; border-radius:0 !important; }}
    .col {{ display:block !important; width:100% !important; padding-left:0 !important; padding-right:0 !important; }}
  }}
</style>
</head>
<body style="margin:0;padding:0;background-color:{PAGE};">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;">{_e(greeting)} - {_e(project_name)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{PAGE}" style="background-color:{PAGE};">
  <tr><td align="center" style="padding:32px 12px;">
    <table role="presentation" class="wrap" width="{WIDTH}" cellpadding="0" cellspacing="0" border="0" style="width:{WIDTH}px;max-width:{WIDTH}px;">
      <tr><td class="card" style="padding:36px 32px;background-color:{CARD};border-radius:16px;">
        {logo}
        {hero_img}
        {intro}
        {problems}
        {objectives}
        {solutions}
        {features}
        {diagram}
        {team}
        {timeline}
        {contact}
      </td></tr>
      <tr><td align="center" style="padding:20px 16px 0 16px;">
        {footer}
      </td></tr>
    </table>
  </td></tr>
</table>
</body>
</html>
"""
