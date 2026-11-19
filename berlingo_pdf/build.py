# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                PageBreak, Table, TableStyle, Flowable, KeepTogether)

D = "/usr/share/fonts/truetype/liberation/"
pdfmetrics.registerFont(TTFont("F", D + "LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("FB", D + "LiberationSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("FI", D + "LiberationSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("FBI", D + "LiberationSans-BoldItalic.ttf"))
pdfmetrics.registerFontFamily("F", normal="F", bold="FB", italic="FI", boldItalic="FBI")

NAVY = colors.HexColor("#14284b")
BLUE = colors.HexColor("#1f5fa8")
LBLUE = colors.HexColor("#e8f0fa")
RED = colors.HexColor("#c62828")
LRED = colors.HexColor("#fdecea")
GREEN = colors.HexColor("#2e7d32")
LGREEN = colors.HexColor("#e8f5e9")
ORANGE = colors.HexColor("#ef8a00")
LORANGE = colors.HexColor("#fff4e0")
GREY = colors.HexColor("#6b7280")
LGREY = colors.HexColor("#f1f3f5")
DARK = colors.HexColor("#222222")

W = A4[0] - 36 * mm  # content width

body = ParagraphStyle("body", fontName="F", fontSize=9.6, leading=14, textColor=DARK, spaceAfter=4)
small = ParagraphStyle("small", parent=body, fontSize=8.2, leading=11.5, textColor=GREY)
h1 = ParagraphStyle("h1", fontName="FB", fontSize=17, leading=21, textColor=NAVY, spaceBefore=4, spaceAfter=8)
h2 = ParagraphStyle("h2", fontName="FB", fontSize=12.5, leading=16, textColor=BLUE, spaceBefore=8, spaceAfter=4, keepWithNext=1)
h3 = ParagraphStyle("h3", fontName="FB", fontSize=10.3, leading=14, textColor=NAVY, spaceBefore=5, spaceAfter=2, keepWithNext=1)
bul = ParagraphStyle("bul", parent=body, leftIndent=12, bulletIndent=2, spaceAfter=2)
cell = ParagraphStyle("cell", parent=body, fontSize=8.6, leading=11.6, spaceAfter=0)
cellb = ParagraphStyle("cellb", parent=cell, fontName="FB", textColor=colors.white)
cap = ParagraphStyle("cap", parent=body, fontSize=8, leading=10.5, textColor=GREY, alignment=TA_CENTER)


def P(t, s=body): return Paragraph(t, s)
def B(items): return [Paragraph(i, bul, bulletText="•") for i in items]
def H1(t): return Paragraph(t, h1)
def H2(t): return Paragraph(t, h2)
def H3(t): return Paragraph(t, h3)


def box(text_or_list, kind="info", title=None):
    bg, bd = {"info": (LBLUE, BLUE), "warn": (LORANGE, ORANGE), "danger": (LRED, RED), "ok": (LGREEN, GREEN)}[kind]
    items = []
    if title:
        items.append(Paragraph("<b>%s</b>" % title, ParagraphStyle("bt", parent=body, textColor=bd, spaceAfter=2)))
    if isinstance(text_or_list, str):
        items.append(Paragraph(text_or_list, ParagraphStyle("bx", parent=body, spaceAfter=0)))
    else:
        items += [Paragraph(i, ParagraphStyle("bx2", parent=bul, spaceAfter=1), bulletText="•") for i in text_or_list]
    t = Table([[items]], colWidths=[W])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), bg), ("LINEBEFORE", (0, 0), (0, -1), 3, bd),
                           ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                           ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return t


def table(rows, widths, head=True, zebra=True, rh=None):
    data = []
    for i, r in enumerate(rows):
        data.append([Paragraph(c, cellb if (head and i == 0) else cell) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1 if head else 0, rowHeights=([None] + [rh] * (len(rows) - 1)) if rh else None)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c9ced6")),
          ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
          ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]
    if head: st.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    if zebra:
        for i in range(1 if head else 0, len(rows)):
            if i % 2 == 0: st.append(("BACKGROUND", (0, i), (-1, i), LGREY))
    t.setStyle(TableStyle(st))
    return t


# ---------------- drawing helpers ----------------
class Fig(Flowable):
    def __init__(self, h, fn, w=None):
        super().__init__()
        self.width = w or W
        self.height = h
        self.fn = fn

    def wrap(self, aw, ah): return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        c.setStrokeColor(colors.HexColor("#d0d5dd"))
        c.setFillColor(colors.white)
        c.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=1)
        c.restoreState()
        c.saveState()
        self.fn(c, self.width, self.height)
        c.restoreState()


def T(c, x, y, s, size=8, font="F", col=DARK, al="l"):
    c.setFont(font, size); c.setFillColor(col)
    if al == "l": c.drawString(x, y, s)
    elif al == "c": c.drawCentredString(x, y, s)
    else: c.drawRightString(x, y, s)


def num(c, x, y, n, col=RED, r=7):
    c.setFillColor(col); c.setStrokeColor(colors.white); c.setLineWidth(1)
    c.circle(x, y, r, fill=1, stroke=1)
    T(c, x, y - 3, str(n), 8, "FB", colors.white, "c")


def line(c, x1, y1, x2, y2, col=GREY, w=0.7, dash=None):
    c.setStrokeColor(col); c.setLineWidth(w)
    if dash: c.setDash(*dash)
    c.line(x1, y1, x2, y2); c.setDash()


def arrow(c, x1, y1, x2, y2, col=DARK, w=1.2):
    import math
    line(c, x1, y1, x2, y2, col, w)
    a = math.atan2(y2 - y1, x2 - x1)
    c.setFillColor(col)
    p = c.beginPath()
    p.moveTo(x2, y2)
    p.lineTo(x2 - 6 * math.cos(a - .4), y2 - 6 * math.sin(a - .4))
    p.lineTo(x2 - 6 * math.cos(a + .4), y2 - 6 * math.sin(a + .4))
    p.close(); c.drawPath(p, fill=1, stroke=0)


def car_top(c, cx, cy, w=110, h=235, front_up=True):
    """top view; returns dict of key coords. cx,cy = center"""
    x0, y0 = cx - w / 2, cy - h / 2
    c.setFillColor(colors.HexColor("#dfe6ee")); c.setStrokeColor(NAVY); c.setLineWidth(1.4)
    c.roundRect(x0, y0, w, h, 18, fill=1, stroke=1)
    # wheels
    c.setFillColor(colors.HexColor("#444"))
    for wy in (y0 + 30, y0 + h - 62):
        c.roundRect(x0 - 6, wy, 8, 32, 2, fill=1, stroke=0)
        c.roundRect(x0 + w - 2, wy, 8, 32, 2, fill=1, stroke=0)
    # windshield (front=top)
    c.setFillColor(colors.HexColor("#a9c7e8")); c.setStrokeColor(NAVY); c.setLineWidth(0.8)
    p = c.beginPath(); p.moveTo(x0 + 12, y0 + h - 62); p.lineTo(x0 + w - 12, y0 + h - 62)
    p.lineTo(x0 + w - 18, y0 + h - 34); p.lineTo(x0 + 18, y0 + h - 34); p.close(); c.drawPath(p, fill=1, stroke=1)
    # rear glass
    p = c.beginPath(); p.moveTo(x0 + 14, y0 + 34); p.lineTo(x0 + w - 14, y0 + 34)
    p.lineTo(x0 + w - 10, y0 + 18); p.lineTo(x0 + 10, y0 + 18); p.close(); c.drawPath(p, fill=1, stroke=1)
    # mirrors
    c.setFillColor(colors.HexColor("#9aa7b6"))
    c.roundRect(x0 - 11, y0 + h - 72, 11, 14, 3, fill=1, stroke=1)
    c.roundRect(x0 + w, y0 + h - 72, 11, 14, 3, fill=1, stroke=1)
    T(c, cx, cy + 5, "BERLINGO", 9, "FB", GREY, "c")
    T(c, cx, cy - 6, "(üstten şematik görünüm)", 6.5, "F", GREY, "c")
    T(c, cx, y0 + h + 4, "ÖN", 7, "FB", NAVY, "c")
    T(c, cx, y0 - 9, "ARKA", 7, "FB", NAVY, "c")
    return dict(x0=x0, y0=y0, w=w, h=h)


# ---------- Figure 1: overall map ----------
def fig_map(c, w, h):
    T(c, w / 2, h - 16, "ŞEKİL 1 – Sistem bileşenlerinin yaklaşık yerleri (şematik, sol direksiyonlu araç)", 9, "FB", NAVY, "c")
    cx, cy = w / 2, h / 2 - 8
    k = car_top(c, cx, cy, 110, 235)
    x0, y0, cw, ch = k["x0"], k["y0"], k["w"], k["h"]
    # front sensors
    c.setFillColor(GREEN); c.setStrokeColor(colors.white)
    for fx in (-40, -14, 14, 40):
        c.circle(cx + fx, y0 + ch - 3, 4, fill=1, stroke=1)
        c.circle(cx + fx, y0 + 3, 4, fill=1, stroke=1)
    # BSM at rear corners
    c.setFillColor(ORANGE)
    c.rect(x0 + 2, y0 + 2, 11, 9, fill=1, stroke=1); c.rect(x0 + cw - 13, y0 + 2, 11, 9, fill=1, stroke=1)
    # camera
    c.setFillColor(RED); c.rect(cx - 8, y0 + ch - 66, 16, 7, fill=1, stroke=1)
    # mirror LEDs
    c.setFillColor(ORANGE); c.circle(x0 - 5, y0 + ch - 65, 3.5, fill=1, stroke=1); c.circle(x0 + cw + 5, y0 + ch - 65, 3.5, fill=1, stroke=1)
    # dash area / OBD
    c.setFillColor(colors.HexColor("#5b6b82")); c.rect(x0 + 8, y0 + ch - 100, 34, 8, fill=1, stroke=1)
    # engine bay battery
    c.setFillColor(colors.HexColor("#111")); c.rect(x0 + 10, y0 + ch - 24, 26, 12, fill=1, stroke=1)
    L = 40; R = w - 40
    items_l = [
        (y0 + ch - 18, "Akü (+ / –) – motor bölmesi", "A", x0 + 23),
        (y0 + ch - 96, "OBD-II soketi + iç sigorta kutusu\n(sürücü tarafı, torpido altı)", "B", x0 + 25),
        (y0 + 8, "Kör nokta dedektörleri\n(arka tampon köşeleri, iç tarafta)", "C", x0 + 7),
    ]
    items_r = [
        (y0 + ch + 2, "Ön park sensörleri (4 adet, varsa)", "D", cx + 40),
        (y0 + ch - 63, "Şerit takip kamerası\n(ön cam üst orta, ayna arkası)", "E", cx + 8),
        (y0 + ch - 65, "", "", 0),
        (y0 - 2, "Arka park sensörleri (4 adet)", "F", cx + 40),
    ]
    for (yy, label, n, tx) in items_l:
        line(c, tx, yy, 150, yy + (4 if yy > cy else 0))
        num(c, 150, yy + (4 if yy > cy else 0), n)
        for i, ln in enumerate(label.split("\n")):
            T(c, 8, yy + 8 - i * 10 + (4 if yy > cy else 0), ln, 8, "FB" if i == 0 else "F", NAVY)
    for (yy, label, n, tx) in items_r:
        if not label: continue
        ty = yy + (8 if n == "D" else (-4 if n == "F" else 0))
        line(c, tx, yy, w - 150, ty)
        num(c, w - 150, ty, n)
        for i, ln in enumerate(label.split("\n")):
            T(c, w - 138, ty + 2 - i * 10, ln, 8, "FB" if i == 0 else "F", NAVY)
    # mirror led label
    T(c, w - 138, y0 + ch - 82, "Dış ayna uyarı LED'i (kör nokta)", 7.5, "F", NAVY)
    line(c, x0 + cw + 5, y0 + ch - 65, w - 150, y0 + ch - 80, ORANGE)
    num(c, w - 150, y0 + ch - 80, "G")
    # legend
    lx, ly = 10, 14
    for col, t in ((GREEN, "park sensörü"), (ORANGE, "kör nokta / LED"), (RED, "kamera")):
        c.setFillColor(col); c.circle(lx + 4, ly + 3, 3.5, fill=1, stroke=0)
        T(c, lx + 11, ly, t, 7.5, "F", GREY); lx += 90
    T(c, w - 10, 6, "Konumlar donanım paketine göre değişir; kesin yer için kullanım kılavuzuna bakın.", 6.8, "FI", GREY, "r")


# ---------- Figure 2: windshield camera ----------
def fig_cam(c, w, h):
    T(c, w / 2, h - 16, "ŞEKİL 2 – Ön cam ve şerit takip kamerası: kamerayı \"kör\" eden şeyler", 9, "FB", NAVY, "c")
    cx = w * 0.36
    c.setFillColor(colors.HexColor("#cfe3f6")); c.setStrokeColor(NAVY); c.setLineWidth(1.5)
    p = c.beginPath(); p.moveTo(cx - 150, 30); p.lineTo(cx + 150, 30); p.lineTo(cx + 125, h - 40); p.lineTo(cx - 125, h - 40); p.close()
    c.drawPath(p, fill=1, stroke=1)
    # mirror housing
    c.setFillColor(colors.HexColor("#3a3f47")); c.roundRect(cx - 32, h - 78, 64, 34, 5, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#111")); c.circle(cx, h - 62, 7, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#7a8da3")); c.circle(cx, h - 62, 3, fill=1, stroke=0)
    # camera view cone zone (hatched red/green)
    c.setStrokeColor(GREEN); c.setLineWidth(1.2); c.setDash(4, 3)
    p = c.beginPath(); p.moveTo(cx - 40, h - 80); p.lineTo(cx + 40, h - 80); p.lineTo(cx + 85, 50); p.lineTo(cx - 85, 50); p.close()
    c.drawPath(p, fill=0, stroke=1); c.setDash()
    T(c, cx, 60, "kamera görüş alanı – TEMİZ ve boş olmalı", 7.5, "FB", GREEN, "c")
    # wiper sweep arc
    c.setStrokeColor(GREY); c.setDash(2, 2); c.arc(cx - 110, -60, cx + 110, 120, 20, 140); c.setDash()
    # obstacles
    c.setFillColor(RED)
    c.rect(cx - 70, h - 80, 26, 16, fill=1, stroke=0); T(c, cx - 57, h - 74, "HGS", 6.5, "FB", colors.white, "c")
    c.rect(cx + 44, h - 90, 22, 22, fill=1, stroke=0); T(c, cx + 55, h - 81, "DASH", 5.8, "FB", colors.white, "c")
    c.rect(cx - 30, h - 110, 60, 8, fill=1, stroke=0); T(c, cx, h - 108, "koyu cam bandı / film", 5.8, "FB", colors.white, "c")
    # right-hand explanation
    ex = w * 0.68
    rows = [("1", RED, "HGS / OGS etiketi, otopark / geçiş kartı kamera önündeyse"),
            ("2", RED, "Araç kamerası (dashcam) veya tutucusu görüş alanında"),
            ("3", RED, "Cam filmi, koyu şerit bandı, bant, çıkartma"),
            ("4", ORANGE, "Cam değişimi / çatlak / çip → kalibrasyon gerekebilir"),
            ("5", ORANGE, "İç camda buğu, yağ filmi, sigara/nem tabakası"),
            ("6", ORANGE, "Silecek taramasının dışında kalan kirli bölge")]
    yy = h - 50
    for n, col, t in rows:
        num(c, ex, yy + 3, n, col)
        # wrap text manually
        words = t.split(); lines = []; cur = ""
        for wd in words:
            if c.stringWidth(cur + " " + wd, "F", 7.6) < w - ex - 28: cur = (cur + " " + wd).strip()
            else: lines.append(cur); cur = wd
        lines.append(cur)
        for i, ln in enumerate(lines): T(c, ex + 12, yy + 3 - i * 9.5, ln, 7.6, "F", DARK)
        yy -= 14 + 9.5 * (len(lines) - 1) + 8


# ---------- Figure 3: rear bumper + sensor conditions ----------
def sensor_closeup(c, x, y, r, state):
    c.setFillColor(colors.HexColor("#e3e8ee")); c.setStrokeColor(NAVY); c.setLineWidth(1)
    c.roundRect(x - 52, y - 40, 104, 80, 10, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#222")); c.setStrokeColor(colors.HexColor("#555")); c.setLineWidth(2)
    c.circle(x, y, r, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#444")); c.circle(x, y, r - 6, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#999")); pp=c.beginPath(); pp.moveTo(x,y+5); pp.lineTo(x-4,y-3); pp.lineTo(x+4,y-3); pp.close(); c.drawPath(pp,fill=1,stroke=0)
    if state == "ok":
        pass
    elif state == "crack":
        c.setStrokeColor(RED); c.setLineWidth(1.3)
        c.line(x - 14, y + 16, x - 4, y + 2); c.line(x - 4, y + 2, x + 6, y + 6); c.line(x + 6, y + 6, x + 16, y - 12)
        c.setFillColor(colors.HexColor("#d9d2b8")); c.setStrokeColor(colors.HexColor("#d9d2b8"))
        c.rect(x - 52, y + 22, 104, 8, fill=1, stroke=0)
    elif state == "loose":
        c.setStrokeColor(ORANGE); c.setLineWidth(2)
        c.circle(x + 4, y - 3, r, fill=0, stroke=1)
        c.setStrokeColor(RED); c.setLineWidth(1); c.setDash(2, 2); c.line(x - r - 4, y - 28, x + r + 8, y - 28); c.setDash()


def fig_bumper(c, w, h):
    T(c, w / 2, h - 16, "ŞEKİL 3 – Arka tampon: sensörlerin yeri ve dışarıdan gözle kontrol", 9, "FB", NAVY, "c")
    cx = w / 2
    # bumper
    c.setFillColor(colors.HexColor("#dfe6ee")); c.setStrokeColor(NAVY); c.setLineWidth(1.5)
    c.roundRect(cx - 190, h - 100, 380, 62, 18, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#c4ccd6")); c.rect(cx - 45, h - 92, 90, 22, fill=1, stroke=1)
    T(c, cx, h - 85, "PLAKA", 8, "FB", GREY, "c")
    c.setFillColor(colors.HexColor("#222")); c.setStrokeColor(colors.HexColor("#666"))
    xs = (-130, -80, 80, 130)
    for i, sx in enumerate(xs):
        c.circle(cx + sx, h - 66, 7, fill=1, stroke=1)
        num(c, cx + sx, h - 40, i + 1, BLUE, 6.5)
    c.setFillColor(ORANGE)
    c.rect(cx - 188, h - 98, 14, 10, fill=0, stroke=1); c.rect(cx + 174, h - 98, 14, 10, fill=0, stroke=1)
    c.setStrokeColor(ORANGE); c.setDash(2, 2)
    c.rect(cx - 188, h - 98, 14, 10, fill=0, stroke=1); c.rect(cx + 174, h - 98, 14, 10, fill=0, stroke=1); c.setDash()
    T(c, cx - 181, h - 112, "kör nokta*", 6.5, "FB", ORANGE, "c"); T(c, cx + 181, h - 112, "kör nokta*", 6.5, "FB", ORANGE, "c")
    T(c, cx, h - 112, "Mavi daireler = 4 arka park sensörü (araca göre 2/4 adet olabilir)", 7, "F", GREY, "c")
    # closeups
    yy = 86
    for i, (st, ttl, sub) in enumerate((("ok", "SAĞLAM", "yüzey düz, halka yerinde,"), ("crack", "ŞÜPHELİ", "çatlak / kalın boya / çıkartma"), ("loose", "ŞÜPHELİ", "halka gevşek / içeri-dışarı kaçık"))):
        x = w * (0.2 + 0.3 * i)
        sensor_closeup(c, x, yy, 16, st)
        col = GREEN if st == "ok" else RED
        T(c, x, yy - 52, ttl, 8.5, "FB", col, "c")
        T(c, x, yy - 62, sub, 7, "F", GREY, "c")
    T(c, w - 8, 5, "* Kör nokta dedektörü tampon arkasındadır, dışarıdan görünmeyebilir.", 6.5, "FI", GREY, "r")


# ---------- Figure 4: click test ----------
def fig_click(c, w, h):
    T(c, w / 2, h - 16, "ŞEKİL 4 – \"Tık testi\": çalışan ultrasonik sensör hafif tıkırdar / titreşir", 9, "FB", NAVY, "c")
    cx = 130; cy = h / 2 - 8
    c.setFillColor(colors.HexColor("#dfe6ee")); c.setStrokeColor(NAVY); c.setLineWidth(1.4)
    c.rect(cx - 10, cy - 38, 22, 76, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#222")); c.rect(cx + 12, cy - 12, 14, 24, fill=1, stroke=1)
    c.setStrokeColor(BLUE); c.setLineWidth(1.4)
    for i, r in enumerate((14, 24, 34)):
        c.arc(cx + 26 - r, cy - r, cx + 26 + r, cy + r, -35, 70)
    # finger
    c.setFillColor(colors.HexColor("#e8b898")); c.setStrokeColor(colors.HexColor("#9c6b4b"))
    c.roundRect(cx + 40, cy - 7, 60, 14, 7, fill=1, stroke=1)
    c.roundRect(cx + 95, cy - 12, 50, 24, 8, fill=1, stroke=1)
    T(c, cx + 30, cy + 48, "tık – tık", 8, "FB", BLUE, "c")
    T(c, cx - 4, cy - 52, "tampon", 7, "F", GREY, "c")
    ex = 290
    steps = ["Kontak AÇIK, motor çalışabilir, vites GERİ (ön sensörler için ön tarafı dinleyin).",
             "Ortam sessiz olsun; yan yana duran 2. kişi ekrandaki/ses uyarısını izlesin.",
             "Parmak ucunu sensörün yüzeyine hafifçe değdirin.",
             "Sağlam sensör: çok hafif tıkırtı/titreşim hissedilir.",
             "Tık YOK = o sensör (veya kablosu/ soketi) şüpheli → numarasını not edin."]
    yy = h - 40
    for i, s in enumerate(steps):
        num(c, ex, yy + 3, i + 1, BLUE, 6.5)
        words = s.split(); lines = []; cur = ""
        for wd in words:
            if c.stringWidth(cur + " " + wd, "F", 7.8) < w - ex - 22: cur = (cur + " " + wd).strip()
            else: lines.append(cur); cur = wd
        lines.append(cur)
        for j, ln in enumerate(lines): T(c, ex + 11, yy + 2 - j * 9.5, ln, 7.8, "F", DARK)
        yy -= 11 + 9.5 * (len(lines) - 1) + 8


# ---------- Figure 5: voltage ----------
def fig_volt(c, w, h):
    T(c, w / 2, h - 16, "ŞEKİL 5 – Akü / şarj voltajı okuma rehberi (multimetre, DC 20 V kademesi)", 9, "FB", NAVY, "c")
    x0, x1 = 60, w - 40
    def pos(v): return x0 + (v - 11.0) / (15.5 - 11.0) * (x1 - x0)
    def bar(y, title, zones):
        T(c, x0, y + 30, title, 8.3, "FB", NAVY)
        for a, b, col, lab in zones:
            c.setFillColor(col); c.rect(pos(a), y, pos(b) - pos(a), 16, fill=1, stroke=0)
            T(c, (pos(a) + pos(b)) / 2, y + 4.5, lab, 6.6, "FB", colors.white, "c")
        c.setStrokeColor(DARK); c.setLineWidth(.6)
        for v in range(11, 16):
            c.line(pos(v), y, pos(v), y - 4); T(c, pos(v), y - 12, "%d V" % v, 7, "F", GREY, "c")
    bar(h - 74, "A) Kontak KAPALI, araç en az 30 dk dinlenmiş (kutup başlarından ölç)",
        [(11.0, 12.2, RED, "ZAYIF / BOŞ"), (12.2, 12.4, ORANGE, "sınır"), (12.4, 12.9, GREEN, "NORMAL"), (12.9, 15.5, colors.HexColor("#9bbf9d"), "")])
    bar(h - 132, "B) Motor ÇALIŞIRKEN (rölanti ~1500 dev/dk, ışık-klima kapalı)",
        [(11.0, 13.4, RED, "ŞARJ YOK / DÜŞÜK"), (13.4, 13.8, ORANGE, "sınır"), (13.8, 14.8, GREEN, "NORMAL"), (14.8, 15.5, RED, "AŞIRI")])
    T(c, w / 2, 10, "Çok düşük voltaj, sürüş yardım sistemlerinin aynı anda hata vermesinin en yaygın ortak nedenlerinden biridir.", 7, "FI", GREY, "c")


# ---------- Figure 6: mirror LED / BSM zone ----------
def fig_bsm(c, w, h):
    T(c, w / 2, h - 16, "ŞEKİL 6 – Kör nokta uyarı sistemi: ayna LED'i ve tarama bölgesi (şematik)", 9, "FB", NAVY, "c")
    # left: car top mini with zones
    cx, cy = 120, h / 2 - 8
    k = car_top(c, cx, cy, 70, 150)
    x0, y0, cw, ch = k["x0"], k["y0"], k["w"], k["h"]
    c.setFillColor(colors.Color(1, .54, 0, alpha=.25)); c.setStrokeColor(ORANGE); c.setDash(3, 2)
    c.rect(x0 - 38, y0 - 22, 30, 100, fill=1, stroke=1); c.rect(x0 + cw + 8, y0 - 22, 30, 100, fill=1, stroke=1); c.setDash()
    T(c, x0 - 23, y0 + 28, "kör", 7, "FB", ORANGE, "c"); T(c, x0 - 23, y0 + 19, "nokta", 7, "FB", ORANGE, "c")
    T(c, x0 + cw + 23, y0 + 28, "kör", 7, "FB", ORANGE, "c"); T(c, x0 + cw + 23, y0 + 19, "nokta", 7, "FB", ORANGE, "c")
    # mirror
    mx = 330
    c.setFillColor(colors.HexColor("#c9d4e0")); c.setStrokeColor(NAVY); c.setLineWidth(1.5)
    c.roundRect(mx, h / 2 - 28, 110, 62, 14, fill=1, stroke=1)
    c.setFillColor(ORANGE); c.setStrokeColor(DARK)
    p = c.beginPath(); p.moveTo(mx + 86, h / 2 + 22); p.lineTo(mx + 102, h / 2 - 4); p.lineTo(mx + 70, h / 2 - 4); p.close()
    c.drawPath(p, fill=1, stroke=1)
    T(c, mx + 86, h / 2 + 2, "!", 8, "FB", DARK, "c")
    T(c, mx + 55, h / 2 - 44, "Dış ayna camı: turuncu uyarı simgesi", 7, "F", GREY, "c")
    T(c, mx + 55, h / 2 - 53, "(araca göre ışık ayna camında görünür)", 7, "F", GREY, "c")
    T(c, mx + 55, h / 2 + 50, "ARAÇ KÖR NOKTADA → LED yanar", 7.5, "FB", ORANGE, "c")
    T(c, w - 8, 5, "Sistem genelde belirli hızın üzerinde aktiftir; park halinde LED yanmaması normaldir.", 6.5, "FI", GREY, "r")


# ---------- Figure 7: rear bumper inside / wiring checkpoints ----------
def fig_wiring(c, w, h):
    T(c, w / 2, h - 16, "ŞEKİL 7 – Arka tampon içi / bagaj tarafı: kablo ve soket kontrol noktaları (şematik)", 9, "FB", NAVY, "c")
    cx = w * 0.35
    c.setFillColor(colors.HexColor("#eef1f5")); c.setStrokeColor(NAVY); c.setLineWidth(1.4)
    c.roundRect(cx - 168, 30, 336, 100, 14, fill=1, stroke=1)
    T(c, cx, 114, "tampon kaplamasının iç yüzü (arkadan bakış)", 7, "FI", GREY, "c")
    xs = (-130, -75, 75, 130)
    pts = []
    for sx in xs:
        c.setFillColor(colors.HexColor("#222")); c.circle(cx + sx, 100, 8, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#d4b106")); c.rect(cx + sx - 6, 78, 12, 10, fill=1, stroke=1)  # connector
        c.setStrokeColor(colors.HexColor("#222")); c.setLineWidth(1.6)
        c.line(cx + sx, 92, cx + sx, 88); c.line(cx + sx, 78, cx + sx, 62)
        pts.append(cx + sx)
    c.line(pts[0], 62, pts[1], 62); c.line(pts[1], 62, cx - 20, 62); c.line(cx - 20, 62, cx - 20, 52)
    c.line(pts[3], 62, pts[2], 62); c.line(pts[2], 62, cx + 20, 62); c.line(cx + 20, 62, cx + 20, 52)
    c.setFillColor(colors.HexColor("#d4b106")); c.rect(cx - 28, 46, 56, 8, fill=1, stroke=1)
    # BSM modules
    c.setFillColor(ORANGE); c.rect(cx - 165, 100, 26, 22, fill=1, stroke=1); c.rect(cx + 139, 100, 26, 22, fill=1, stroke=1)
    T(c, cx - 152, 107, "KN", 7, "FB", colors.white, "c"); T(c, cx + 152, 107, "KN", 7, "FB", colors.white, "c")
    # ground
    c.setFillColor(colors.HexColor("#777")); c.rect(cx + 150, 44, 14, 10, fill=1, stroke=1)
    # numbers
    num(c, pts[0], 120, 1); num(c, pts[0] + 6, 70, 2, RED, 7)
    num(c, cx, 38, 3); num(c, cx + 157, 36, 4); num(c, cx - 152, 130, 5, ORANGE)
    num(c, cx + 100, 62 + 10, 6)
    items = ["Sensör arka halkası ve soket sekmesi (gevşek mi, oturmuş mu?)",
             "Kablo demeti: yırtık bant, ezilme, tampon kenarında sürtme",
             "Ana soket: nem, yeşil oksit, eğik pin, kilit sekmesi kırık",
             "Toprak (şase) noktası: boya/pas altında kötü temas",
             "Kör nokta dedektörleri: yerinde mi, çarpma izi, braket kırığı",
             "Sonradan eklenen kablo: çeki demiri, kamera, alarm → ekleme / sıkıştırma izi"]
    ex = 352
    yy = h - 36
    for i, s in enumerate(items):
        num(c, ex - 8, yy + 3, i + 1, ORANGE if i == 4 else RED, 6.5)
        words = s.split(); lines = []; cur = ""
        for wd in words:
            if c.stringWidth(cur + " " + wd, "F", 6.9) < w - ex - 6: cur = (cur + " " + wd).strip()
            else: lines.append(cur); cur = wd
        lines.append(cur)
        for j, ln in enumerate(lines): T(c, ex, yy + 2 - j * 8.3, ln, 6.9, "F", DARK)
        yy -= 9 + 8.3 * (len(lines) - 1) + 6.2


# ---------- Figure 8: fuse ----------
def fig_fuse(c, w, h):
    T(c, w / 2, h - 16, "ŞEKİL 8 – Sigorta kutusu ve sigorta kontrolü (genel şema)", 9, "FB", NAVY, "c")
    # box
    bx, by = 25, 18
    c.setFillColor(colors.HexColor("#3a3f47")); c.setStrokeColor(DARK); c.roundRect(bx, by, 180, h - 50, 6, fill=1, stroke=1)
    import random
    random.seed(4)
    cols = [colors.HexColor(x) for x in ("#e0c000", "#d33", "#3a9", "#6ab", "#e0c000", "#a55")]
    for r in range(5):
        for k in range(8):
            c.setFillColor(random.choice(cols)); c.rect(bx + 10 + k * 20, by + 12 + r * 18, 14, 11, fill=1, stroke=0)
    # highlighted
    c.setStrokeColor(RED); c.setLineWidth(2); c.rect(bx + 10 + 3 * 20 - 2, by + 12 + 2 * 18 - 2, 18, 15, fill=0, stroke=1)
    T(c, bx + 90, h - 29, "Kapak iç yüzündeki ŞEMAYA göre ilgili sigortayı bulun", 6.6, "FB", DARK, "c")
    # good vs blown
    gx = 250
    for i, (ok, lab) in enumerate(((True, "SAĞLAM: ince tel kesintisiz"), (False, "ATIK: tel kopuk / yanık izi"))):
        x = gx + i * 125
        c.setFillColor(colors.HexColor("#e0c000")); c.setStrokeColor(DARK); c.setLineWidth(1)
        c.rect(x, h / 2 - 8, 40, 30, fill=1, stroke=1)
        c.setFillColor(colors.HexColor("#f6e58d")); c.rect(x + 7, h / 2 - 2, 26, 18, fill=1, stroke=0)
        c.setStrokeColor(DARK); c.setLineWidth(1.6)
        if ok:
            c.line(x + 10, h / 2 + 2, x + 10, h / 2 + 12); c.line(x + 10, h / 2 + 12, x + 30, h / 2 + 12); c.line(x + 30, h / 2 + 12, x + 30, h / 2 + 2)
        else:
            c.line(x + 10, h / 2 + 2, x + 10, h / 2 + 12); c.line(x + 10, h / 2 + 12, x + 17, h / 2 + 12)
            c.line(x + 24, h / 2 + 12, x + 30, h / 2 + 12); c.line(x + 30, h / 2 + 12, x + 30, h / 2 + 2)
            c.setFillColor(colors.HexColor("#555")); c.circle(x + 20, h / 2 + 10, 3, fill=1, stroke=0)
        T(c, x + 20, h / 2 - 22, lab, 6.8, "FB", GREEN if ok else RED, "c")
    T(c, gx + 62, h - 40, "Sigorta çıkarma cımbızı kullanın; aynı AMPERDE yenisini takın.", 7.2, "F", DARK, "c")
    T(c, gx + 62, 14, "Sigorta sağlam olsa da yuvanın gevşek/oksitli olması hata üretebilir.", 7.2, "FI", GREY, "c")


# ---------- Figure 9: swap ----------
def fig_swap(c, w, h):
    T(c, w / 2, h - 16, "ŞEKİL 9 – Ayrıştırma (yer değiştirme) testi: arıza sensörde mi, kabloda mı?", 9, "FB", NAVY, "c")
    xa, xb = w * 0.11, w * 0.34
    for x, lab, col in ((xa, "Şüpheli sensör (tık yok)", RED), (xb, "Çalışan komşu sensör", GREEN)):
        c.setFillColor(colors.HexColor("#222")); c.circle(x, h / 2 - 5, 13, fill=1, stroke=0)
        c.setFillColor(col); c.rect(x - 10, h / 2 - 40, 20, 12, fill=1, stroke=0)
        T(c, x, h / 2 + 22, lab, 7.5, "FB", col, "c")
    arrow(c, xa + 26, h / 2 + 6, xb - 26, h / 2 + 6, BLUE); arrow(c, xb - 26, h / 2 - 16, xa + 26, h / 2 - 16, BLUE)
    T(c, (xa + xb) / 2, h / 2 - 6, "soketleri çaprazla", 7.2, "FB", BLUE, "c")
    ex = w * 0.5
    lines = ["Kontak kapalı iken iki sensörün soketini çıkarıp çaprazlayın.",
             "Tık testini tekrarlayın:",
             "• Tık yeri DEĞİŞİRSE → sensörün kendisi bozuk.",
             "• Tık AYNI konumda yoksa → kablo/soket/modül tarafı.",
             "Not: Bazı araçlarda sensörler eşleşmeli/kodlu olabilir;",
             "emin değilseniz bu testi servis yapsın."]
    yy = h - 38
    for i, s in enumerate(lines):
        T(c, ex, yy - i * 11.5, s, 7.6, "FB" if i == 1 else ("FI" if i >= 4 else "F"), DARK if i < 4 else GREY)


# ---------- Figure 10: flowchart ----------
def fig_flow(c, w, h):
    T(c, w / 2, h - 16, "ŞEKİL 10 – Karar akışı: sonuca göre ne yapılır?", 9, "FB", NAVY, "c")
    def bx(x, y, bw, bh, text, col=LBLUE, bd=BLUE, tc=DARK, size=7.5):
        c.setFillColor(col); c.setStrokeColor(bd); c.setLineWidth(1.1); c.roundRect(x - bw / 2, y - bh / 2, bw, bh, 6, fill=1, stroke=1)
        ls = text.split("\n")
        for i, l in enumerate(ls):
            T(c, x, y + (len(ls) - 1) * 4.6 - i * 9.2 - 2.5, l, size, "FB" if i == 0 else "F", tc, "c")
    cx = w / 2
    bx(cx, h - 42, 250, 30, "BAŞLA: mesajı, menüyü ve kodu kaydet\n(Adım 1)")
    arrow(c, cx, h - 58, cx, h - 74)
    bx(cx, h - 90, 250, 30, "Akü voltajı normal mi? (Adım 2)\nHayır → aküyü/şarjı düzelt, test et", LORANGE, ORANGE)
    arrow(c, cx, h - 106, cx, h - 122)
    bx(cx, h - 138, 250, 30, "Sigortalar, OBD'deki takılı cihaz, kamera önü\n(Adım 3 – 4) temiz ve sağlam mı?", LORANGE, ORANGE)
    arrow(c, cx, h - 154, cx, h - 170)
    bx(cx, h - 186, 250, 30, "Sensörler: görsel + tık testi + engel testi\n(Adım 5 – 6)", LBLUE, BLUE)
    arrow(c, cx, h - 202, cx, h - 218)
    bx(cx, h - 234, 250, 30, "Soket / kablo / toprak ve ayrıştırma testi\n(Adım 7 – 8)", LBLUE, BLUE)
    # outcomes
    arrow(c, cx - 70, h - 250, 80, h - 276); arrow(c, cx, h - 250, cx, h - 276); arrow(c, cx + 70, h - 250, w - 80, h - 276)
    bx(80, h - 292, 152, 30, "Tek sensör / tek soket bulundu\n→ onar / değiştir, sonra kodları OKU", LGREEN, GREEN)
    bx(cx, h - 292, 152, 30, "Hiçbir fiziki sorun yok ya da\nlamba sürüyor → TANI CİHAZI", LORANGE, ORANGE)
    bx(w - 80, h - 292, 152, 30, "Aralıklı / karışık belirti\n→ soket-toprak-voltaj tekrar bak", LBLUE, BLUE)
    T(c, cx, 14, "Kodları silmeden ÖNCE mutlaka okuyup fotoğraflayın; kök neden giderilmezse arıza geri gelir.", 7.4, "FB", RED, "c")


# ---------------- page template ----------------
def on_page(c, doc):
    c.saveState()
    c.setFillColor(NAVY); c.rect(0, A4[1] - 12 * mm, A4[0], 12 * mm, fill=1, stroke=0)
    c.setFont("FB", 8.5); c.setFillColor(colors.white)
    c.drawString(18 * mm, A4[1] - 8 * mm, "Citroën Berlingo (2020) – Sürüş Yardım Sistemleri Arıza Rehberi")
    c.setFont("F", 8); c.setFillColor(GREY)
    c.drawString(18 * mm, 9 * mm, "Genel bilgilendirme amaçlıdır; kesin teşhis için tanı cihazı / yetkili servis gerekir.")
    c.drawRightString(A4[0] - 18 * mm, 9 * mm, "Sayfa %d" % doc.page)
    c.restoreState()


def on_cover(c, doc):
    c.saveState()
    c.setFillColor(NAVY); c.rect(0, A4[1] - 100 * mm, A4[0], 100 * mm, fill=1, stroke=0)
    c.setFillColor(ORANGE); c.rect(0, A4[1] - 103 * mm, A4[0], 3 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white); c.setFont("FB", 24)
    c.drawString(18 * mm, A4[1] - 40 * mm, "Berlingo (2020)")
    c.setFont("FB", 17)
    c.drawString(18 * mm, A4[1] - 54 * mm, "Park Sensörü – Şerit Takip – Kör Nokta")
    c.drawString(18 * mm, A4[1] - 64 * mm, "Arızası: Cihazsız Fiziksel Kontrol Rehberi")
    c.setFont("F", 10.5)
    c.drawString(18 * mm, A4[1] - 80 * mm, "Resimli, adım adım kontrol listesi  +  OBD / tanı cihazı seçim kılavuzu")
    c.restoreState()


doc = BaseDocTemplate("/home/user/deneme/berlingo_pdf/Berlingo_2020_Surus_Yardim_Ariza_Rehberi.pdf", pagesize=A4,
                      leftMargin=18 * mm, rightMargin=18 * mm, topMargin=20 * mm, bottomMargin=17 * mm,
                      title="Citroën Berlingo 2020 – Park Sensörü / Şerit Takip / Kör Nokta Arıza Rehberi",
                      author="Claude Code")
fr = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
fr_cover = Frame(doc.leftMargin, doc.bottomMargin, doc.width, A4[1] - 130 * mm, id="fc")
doc.addPageTemplates([PageTemplate("cover", [fr_cover], onPage=on_cover, autoNextPageTemplate="main"),
                      PageTemplate("main", [fr], onPage=on_page)])

S = []
# ---------------- COVER ----------------
S += [Spacer(1, 4), H2("Bu rehber ne işe yarar?"),
      P("Aracınızda <b>park sensörü, şerit takip ve kör nokta uyarısı</b> sistemleri çalışmıyor; bir süre sürdükten sonra "
        "arıza lambaları yanıyor. Satın alırken arızaların menüden kapatılmış / silinmiş olduğunu, park yardımı menüden "
        "tekrar açılınca arızanın ortaya çıktığını belirtiyorsunuz. Bu rehber (1) arızayı bulup silebilecek "
        "<b>doğru tanı cihazı</b> seçimini ve (2) cihaza ihtiyaç duymadan yapabileceğiniz <b>fiziksel kontrolleri</b> "
        "adım adım anlatır."),
      box(["Park yardımı menüden <b>kapalıyken</b> arıza mesajı görünmez – bu arızanın yok olduğu anlamına gelmez, sadece uyarı susturulmuştur.",
           "Menüden açınca arıza çıkıyorsa modül kendi kendini kontrol ediyor ve bir bileşeni (sensör, kablo, besleme) bulamıyor demektir.",
           "\"Arızayı sildim\" = hata <i>kodu</i> silinmiş, <i>sebep</i> giderilmemiş olabilir. Sebep durdukça kod birkaç kilometre sonra geri gelir – sizdeki tablo tam budur.",
           "Üç sistemin birden arıza vermesi çoğu zaman <b>ortak bir nedene</b> işaret eder: akü/voltaj, sigorta, arka tampon kablo demeti, yazılım/kodlama ya da onarım sonrası kalibrasyon eksikliği."],
          "warn", "Önce şunu bilin"),
      Spacer(1, 6),
      box(["Aşağıdaki <b>şekiller şematik çizimdir</b>, aracınızın gerçek fotoğrafı değildir; parçaların yeri donanım paketine ve sürüme göre değişebilir. Kesin konumlar için kullanım kılavuzunuza bakın.",
           "Cihazsız kontrol yalnızca <b>görülebilir / ölçülebilir</b> nedenleri bulur. Sensörün veya modülün içindeki elektronik arızalar ancak tanı cihazıyla kesinleşir.",
           "Şerit takip, kör nokta ve park yardımı <b>sürücüye yardımcı</b> sistemlerdir; çalışıyor olsalar bile dikkatli sürüşün yerini tutmaz."],
          "info", "Sınırlar ve dürüst uyarı"),
      Spacer(1, 4), P("<b>İçindekiler:</b> 1) OBD / tanı cihazı seçimi · 2) Hazırlık ve güvenlik · 3) Adım 1–10 fiziksel kontrol · 4) Belirti–neden tablosu · 5) Karar akışı ve kayıt formu", small),
      PageBreak()]

# ---------------- SECTION 1: OBD ----------------
S += [H1("1. Hangi OBD / tanı cihazını almalısınız?"),
      P("Park yardımı, kör nokta ve şerit takip kamerası, motor değil <b>gövde/konfor/sürüş yardım modülleridir</b>. "
        "Bunların hata kodlarını okuyabilmek için cihazın PSA (Citroën/Peugeot) <b>tüm sistem (full system)</b> okuma desteği olması gerekir."),
      box(["<b>Ucuz ELM327 (Bluetooth/Wi-Fi, 300–600 TL sınıfı) + telefon uygulaması bu iş için genellikle YETERSİZDİR.</b> Çoğu yalnızca genel OBD-II (motor/emisyon) okur; park, kamera ve kör nokta modüllerini göremez.",
           "Silmek için de aynı modüllerle konuşabilen cihaz gerekir."], "danger", "Alınmaması gereken"),
      Spacer(1, 6),
      table([["Seçenek", "Ne yapar", "Yorum"],
             ["<b>A. Çok markalı tablet tarama cihazı</b><br/>(Launch X431 serisi, Autel MaxiCOM MK808 / MK808S / MK906, Foxwell NT serisi vb.)",
              "Tüm sistem tarama; park yardımı, kamera/radar modülü, ABS, SRS vb. hata kodu <b>okuma + silme</b>, canlı veri, bazı servis fonksiyonları.",
              "<b>Şahsi kullanım için en mantıklı seçenek.</b> Aldığınız modelin <i>Citroën Berlingo 2018+ (K9)</i> için park/kör nokta/kamera modüllerini kapsadığını satıcıdan yazılı teyit edin."],
             ["<b>B. PSA'ya özel Diagbox + arayüz (Lexia / PP2000 tipi)</b>",
              "Fabrika tanı yazılımı; en derin okuma, kodlama, konfigürasyon, kalibrasyon.",
              "Orijinal/lisanslısı yetkili servislerdedir. Ucuz kopya setler uyumsuzluk ve modülü bozma riski taşır; <b>kodlama/konfigürasyon deneyimi yoksa kurcalamayın</b>."],
             ["<b>C. Yetkili servis veya PSA'da uzman özel servis</b>",
              "Diagbox ile tüm modülleri okur, kodlama ve kamera kalibrasyonunu doğru yapar.",
              "Tek seferlik tanı genelde ücretlidir ama en kesin yoldur; tamir için de zaten gerekebilir."],
             ["<b>D. Sadece okuma amaçlı dar kapsamlı el cihazları</b> (Launch Creader sınıfı)",
              "Motor, ABS, SRS gibi birkaç sistemi okur.",
              "Park/kör nokta/kamera modülleri için çoğunlukla yetmez; satın almadan önce kapsam listesine bakın."]],
            [58 * mm, 55 * mm, W - 113 * mm]),
      Spacer(1, 6),
      box(["\"Citroën Berlingo (K9, 2018 ve sonrası) için <b>park yardımı, kör nokta ve şerit/kamera modüllerinden hata kodu okuma ve silme</b> yapıyor mu?\"",
           "Yazılım güncellemesi ücretsiz mi, kaç yıl? Türkçe destek ve iade/değişim koşulu var mı?",
           "Araçta OBD-II soketi (16 pin) standarttır; kablo/dönüştürücü gerekmez."],
          "ok", "Satın almadan önce satıcıya sorulacaklar"),
      Spacer(1, 6),
      box(["<b>Önce OKU, sonra SİL.</b> Tüm kodları ve (varsa) \"sabit/aralıklı\" durumlarını fotoğraflayın.",
           "Önce kök nedeni (sensör, soket, voltaj) giderin; ardından kodları silin ve sürüş testi yapın.",
           "Park yardımı gibi sistemlerde bazı parça değişimlerinden sonra <b>kalibrasyon/yapılandırma</b> gerekebilir; bunu yapamayan cihazla ısrar etmeyin, servise bırakın."],
          "warn", "Cihazı aldıktan sonra doğru kullanım"),
      PageBreak()]

# ---------------- SECTION 2: prep ----------------
S += [H1("2. Hazırlık, malzeme ve güvenlik"),
      table([["Malzeme", "Ne için?"],
             ["Dijital multimetre (DC volt ölçer)", "Akü ve şarj voltajı, sigorta sürekliliği"],
             ["El feneri / kafa lambası", "Tampon içi, sigorta kutusu, soketler"],
             ["Plastik trim sökme takımı, yıldız (Torx) uçlar", "Kaplama ve kapakları çizmeden açmak"],
             ["Mikrofiber bez + izopropil alkol", "Sensör yüzeyi, ön cam kamera alanı temizliği"],
             ["Elektrik kontak temizleme spreyi, (varsa) dielektrik gres", "Soket temizliği / nem koruması"],
             ["Sigorta çıkarma cımbızı", "Sigorta kontrolü"],
             ["Telefon (foto/video) + kağıt/kalem", "Her adımın kaydı – servis için çok değerlidir"],
             ["2. kişi", "Tık testi ve kör nokta testinde yardımcı olması için"]],
            [75 * mm, W - 75 * mm]),
      Spacer(1, 6),
      box(["Kontakta ya da motor çalışırken <b>yalnızca</b> belirtilen testleri yapın; soket takıp çıkarırken kontak <b>kapalı</b> olsun.",
           "<b>Hava yastığı (SRS) kablolarına/sarı soketlere dokunmayın</b>, sivri uçla kablo delmeyin.",
           "Aküyü sökmek gerekirse önce (–) kutbu çıkarın; saat/radyo/pencere hafıza ayarlarının sıfırlanabileceğini unutmayın.",
           "Düz zeminde, el freni çekili, motor soğukken çalışın. Motor çalışırken fan ve kayışlardan uzak durun.",
           "Tampon sökmeyi gerektiren işleri (klips kırılabilir, sensör yönü bozulabilir) emin değilseniz uzmana bırakın."],
          "danger", "Güvenlik"),
      Spacer(1, 8),
      Fig(330, fig_map),
      Spacer(1, 4),
      P("<b>Harf rehberi:</b> A akü · B OBD soketi + iç sigorta kutusu · C kör nokta dedektörleri · D/F ön ve arka park sensörleri · E şerit takip kamerası · G dış ayna uyarı LED'i.", small),
      PageBreak()]

# ---------------- SECTION 3: steps ----------------
S += [H1("3. Cihazsız fiziksel kontrol – adım adım"),
      P("Adımları <b>sırayla</b> uygulayın: en kolay ve en çok ortak neden yaratanlardan (akü, sigorta) başlayıp tek tek bileşenlere iner. "
        "Her adımın sonunda arıza lambasının davranışını kaydedin.", body),
      H2("ADIM 1 – Belirtiyi kayda alın (10 dk)"),
      *B(["Gösterge panelinde / ekranda <b>tam mesaj metnini</b> fotoğraflayın (örn. \"Park yardımı arızası\", \"Kör nokta sistemi arızası\", \"Şerit takip sistemi arızalı\").",
          "Arıza ne zaman çıkıyor: <b>kontak açılır açılmaz mı, kaç km/dk sonra mı</b>? Soğukta mı sıcakta mı, yağmurda/yıkamadan sonra mı, rölantide mi hareket halinde mi?",
          "Üç sistem <b>aynı anda</b> mı gidiyor, yoksa sırayla mı? Başka lamba (ABS, ESP, Start-Stop, motor) da yanıyor mu?",
          "Dokunmatik ekranda <b>Araç / Sürüş yardımları ayarları</b> menüsüne girin (menü adı sürüme göre değişir): Park yardımı, Kör nokta uyarısı, Şerit takibi <b>AÇIK</b> olsun. Hangi sistemin hangi mesajı verdiğini not edin.",
          "Son pano/bakım kayıtlarını ve geçmişte çarpma, tampon onarımı, cam değişimi, akü değişimi, çeki demiri/aksesuar montajı olup olmadığını araştırın."]),
      box("<b>İpucu:</b> Şerit takip ve kör nokta sistemleri düşük hızda aktif olmaz; mesajı <i>hızlıyken</i> (ör. 30–50 km/s üstü) doğrulayın. Aracı satanın hangi menüleri kapattığını da deneyin: kapalı olan bir fonksiyon, gerçek arızayı gizliyor olabilir.", "info"),
      Spacer(1, 6),
      H2("ADIM 2 – Akü ve şarj sistemi (en sık ortak neden)"),
      P("Sürüş yardım modülleri düşük/dalgalı gerilimde hata kodu üretir ve kendini devre dışı bırakır. Arızanın \"bir süre gittikten sonra\" çıkması şarj/akü sorununu şüpheli kılar."),
      Fig(195, fig_volt),
      Spacer(1, 4),
      *B(["Multimetreyi <b>DC V (20 V)</b> kademesine alın; kırmızı uç (+) kutba, siyah uç (–) kutba.",
          "<b>A)</b> Kontak kapalı, araç 30 dk dinlenmişken okuyun. <b>B)</b> Motor çalışırken (rölanti ~1500 dev/dk, ışık ve klima kapalı) tekrar okuyun.",
          "Kutup başlarını sallayın: gevşek, oksitli (beyaz/yeşil kırağı) ise temizleyip sıkın. (–) şase kablosunun gövdeye bağlandığı vidayı da kontrol edin.",
          "Aracınızda <b>Start-Stop</b> varsa akü tipi (AGM/EFB) özeldir; yanlış tip ya da <b>kaydedilmeden</b> değiştirilmiş akü birçok modülde hata üretebilir. Akü yaşını/etiketini kontrol edin.",
          "Akü bakım cihazıyla <b>yük testi</b> (çoğu akü satıcısı ücretsiz yapar) yaptırın; voltaj iyi görünse de akü yük altında çökebilir."]),
      ]

S += [H2("ADIM 3 – Sigortalar ve OBD soketine takılı cihazlar"),
      Fig(150, fig_fuse),
      Spacer(1, 4),
      *B(["Sigorta kutuları: <b>motor bölmesinde akü yanında</b> ve <b>gösterge altında sürücü tarafında</b> (sol direksiyonda sol alt torpido) bulunur; kapak iç yüzündeki şema ve <b>kullanım kılavuzundaki \"Sigortalar\" bölümü</b> hangi sigortanın park yardımı / kamera / kör nokta / BSI'ye ait olduğunu söyler. (Sigorta numaralarını tahminle değil, kılavuzla bulun.)",
          "İlgili sigortaları cımbızla çıkarın; ince telin <b>kopuk veya yanık</b> olup olmadığına bakın ya da multimetreyi süreklilik (bip) kademesine alıp iki ucunu ölçün.",
          "Yuvaların içine bakın: çürüme, erime, yeşil oksit, gevşek temas. Hafifçe kontak spreyi sıkıp kurutun ve yerine <b>aynı amperde</b> takın.",
          "<b>OBD soketine</b> takılı bir şey var mı? (Araç takip cihazı, sigorta/\"filo\" cihazı, ucuz ELM327, alarm modülü...) Bu cihazlar CAN veri hattına çıkıp aşırı yük/parazit bindirebilir; çıkarıp denemek bedavadır."]),
      Spacer(1, 4),
      H2("ADIM 4 – Ön kamera ve şerit takip sistemi"),
      Fig(228, fig_cam),
      Spacer(1, 4),
      *B(["Şerit takip kamerası <b>ön camın üst orta kısmında, iç dikiz aynasının arkasındaki kapakta</b> bulunur. Kapağı <b>sökmeyin</b>; kamera yönü kayarsa yeniden kalibrasyon gerekir.",
          "Camın <b>iç ve dış yüzünü</b> alkollü bezle silin; kamera önünde HGS/OGS çıkartması, geçiş kartı, dashcam veya bant olmamalı (Şekil 2).",
          "Ön camı inceleyin: çatlak, çip, film. <b>Cam daha önce değiştirildiyse</b> (fatura/ort. cam sticker'ı) kamera kalibrasyonu yapılmamış olabilir; bu şerit takip + diğer kamera tabanlı yardımları devre dışı bırakır.",
          "Silecek temizleme alanının kamera hizasını kapladığından ve camın içinde buğu / yağ tabakası olmadığından emin olun.",
          "Test: Gündüz, çizgisi belirgin bir yolda, hızlı sürüşte sistem ışığının/uyarısının davranışını izleyin. Çizgi silik, güneş karşıdan veya yağmurda geçici pasif kalması normaldir; <b>sürekli \"arıza\" mesajı</b> gerçek arızadır."]),
      ]

S += [H2("ADIM 5 – Park sensörleri (arka ve ön)"),
      Fig(262, fig_bumper),
      Spacer(1, 4),
      H3("5a. Gözle kontrol"),
      *B(["Sensörlerin yüzeyini ıslak bezle ve alkolle <b>silin</b>; çamur, kar, böcek, WAX veya çıkartma sinyali bozar.",
          "Sensör yüzeyinde çatlak, delik, aşırı <b>kalın boya</b> (tampon boyandıysa) var mı? Ultrasonik sensör yüzeyine boya fazla gelirse veya yanlış boyanırsa \"kör\" kalabilir.",
          "Sensör halkası (çerçeve) tampon ile <b>aynı seviyede</b> mi? İçeri/dışarı kaçıksa gevşek demektir. Sensör üzerindeki <b>ok/\"UP\"</b> işareti yukarıyı göstermeli.",
          "Tamponda çarpma, çizik, onarım izi, aftermarket tampon, çeki demiri, bisiklet/bagaj taşıyıcı var mı? Bunlar sensör görüş açısını bozar veya sistemi \"römork modu\"na alabilir.",
          "Aynı yükseklikte duran sensörler birbirinin aynısı olmalı (renk, kenar halkası). Farklı görünen sensör sonradan takılmış/değiştirilmiş olabilir."]),
      Fig(168, fig_click),
      Spacer(1, 4),
      H3("5b. Tık testi ve 5c. Engel testi"),
      *B(["<b>Tık testi (Şekil 4):</b> Her sensörde hafif tıkırtı/titreşim hissediliyor mu? Hissedilmeyen sensörü numarasıyla (soldan sağa 1–4) kaydedin.",
          "<b>Engel testi:</b> Aracın arkasında 30–60 cm mesafede karton/kutu tutun, <b>her sensörün tam hizasında</b> tek tek gezdirin. Ekranda ve sesli uyarıda o bölgenin çubuğu/ bip sesi tepki vermeli. Tepki vermeyen bölge hangi sensöre denk geliyorsa şüpheli odur.",
          "<b>Ön sensörler:</b> Aynı testi ön tamponda uygulayın (ön park sensörü varsa ön vitese takıp çok yavaş giderken ya da kontak açıkken)."]),
      ]

S += [H2("ADIM 6 – Kör nokta uyarı sistemi"),
      Fig(235, fig_bsm),
      Spacer(1, 4),
      *B(["<b>Kontak açılış testi:</b> Kontak açıldığında bazı araçlarda dış ayna uyarı LED'i kısa süre yanıp söner (kendi testi). Hiç yanmıyorsa not edin (araca göre değişir, kesin kural değildir).",
          "Arka tampon köşelerinin iç yüzünde (Şekil 1-C ve Şekil 7-5) <b>dedektör modüllerinin</b> yerinde, çarpık veya kırık braketli olup olmadığına bakın. Köşeye çarpma/sürtme, tampon onarımı ve boya bu sistemin <b>ilk bozulan</b> kısmıdır.",
          "Tampon köşesine <b>bant, koruma filmi, plaka, çamur</b> yapışmış mı? Temizleyin.",
          "Aracınızda <b>çeki demiri</b> veya römork soketi sonradan takıldıysa kontrol edin: bazı araçlarda römork bağlıymış gibi algılandığında park ve kör nokta devre dışı kalır ya da hata verir; kablo bağlantısı yanlışsa arıza lambası yanar.",
          "<b>Yol testi:</b> 2. kişi arkanızdan yaklaşıp yan şeritte yavaşça sizi geçsin (düz yol, güvenli ortam); sistem aktif hızda ayna LED'i yanmalıdır."]),
      Spacer(1, 6),
      H2("ADIM 7 – Kablolama, soketler ve topraklama (en önemli adım)"),
      Fig(170, fig_wiring),
      Spacer(1, 4),
      *B(["<b>Neden önemli:</b> Birkaç km gittikten sonra çıkan arızalar çoğunlukla ısınma ve titreşimle temasını yitiren <b>soket/pin/toprak</b> noktalarından kaynaklanır.",
          "Bagaj içi yan kaplamaları ve arka stop lambası arkasını açın (trim aletiyle). <b>Arka sensör ve kör nokta kablo demetinin</b> geçtiği yolu el feneriyle izleyin.",
          "Her sokette: kilit sekmesi tam kapalı mı, <b>pin eğik mi</b>, su izi var mı, <b>yeşil/beyaz oksit</b> var mı? Sorun görürseniz sokete kontak spreyi sıkın, kurusun, sürekli bastırarak <b>çıkar-tak</b> yapın; kuru ise ince bir kat dielektrik gres sürün.",
          "Kablo izolasyonunda <b>çatlak, sargı bandı sarkması, ezilme, keskin kenarda sürtme</b> arayın (özellikle tampon kenarları, bagaj kapısı menteşe geçişleri).",
          "<b>Sonradan eklenmiş kablo</b> (çeki demiri, ek kamera, alarm, multimedya, park kamerası) var mı? Kesip ek yapılmış, <b>mavi/kırmızı tek kullanımlık ek (\"Scotch lock\")</b> ile sıkıştırılmış kablo demeti CAN/sensör hatlarını bozabilir; bu ekleri sökün/doğrulatın.",
          "Şase (toprak) noktalarını arayın (gövdeye cıvatalı kalın kablolar): boya/pas altında kalmışsa yüzeyi parlatıp sıkın.",
          "Arıza <b>araç yıkamadan/yağmurdan sonra</b> başladıysa tampon içine su girmiş olabilir: soketleri açıp kurulayın."]),
      ]

S += [H2("ADIM 8 – Ayrıştırma testi"),
      Fig(120, fig_swap),
      Spacer(1, 4),
      H2("ADIM 9 – Sürüş testi ve kayıt"),
      *B(["Her müdahaleden sonra <b>kontak aç-kapa</b> yapın, 10–20 km sürüş yapın (en az arıza çıktığı süre kadar).",
          "Arıza lambası/mesaj geri geliyor mu? Geliyorsa kaç km sonra? Önceki adıma göre değişim var mı? Son sayfadaki kayıt tablosunu doldurun.",
          "Yalnızca <b>bir değişiklik</b> yapıp test edin; aynı anda çok şey değiştirirseniz nedeni bulamazsınız."]),
      H2("ADIM 10 – Ne zaman cihaza/servise geçmeli?"),
      *B(["Akü/şarj, sigorta, kamera önü, sensör temizliği, soket ve şase kontrollerinden sonra <b>lamba hâlâ yanıyorsa</b>.",
          "Birden fazla sensör aynı anda tepki vermiyorsa (soket/toprak/besleme veya modül sorunu).",
          "Cam, tampon veya kamera/dedektör değişimi sonrası kalibrasyon şüphesi varsa.",
          "Tampon sökmeyi gerektiren iç kontrol gerekiyorsa."]),
      Spacer(1, 4),
      PageBreak(), H1("4. Belirti – olası neden tablosu"),
      table([["Gözlenen durum", "Olası anlam", "Önce bakılacak"],
             ["Yalnızca park yardımı arızası; kör nokta ve şerit normal", "Park sensörü / sensör kablosu / park modülü", "Adım 5, 7, 8"],
             ["Park + kör nokta birlikte; şerit normal", "Arka tampon kablo demeti, ortak besleme/şase, tampon onarımı", "Adım 7, 6"],
             ["Yalnızca şerit takip arızası", "Ön cam/kamera: kirli, film, çatlak, cam değişimi, kalibrasyon", "Adım 4"],
             ["Üçü birden + başka lambalar (ABS/ESP/Start-Stop)", "Düşük voltaj, akü, ortak sigorta/şase, CAN hattı", "Adım 2, 3, 7"],
             ["Birkaç km sonra çıkıyor, soğukken yok", "Isınınca gevşeyen soket, oksit, kablo sürtmesi, zayıf akü/alternatör", "Adım 7, 2"],
             ["Yıkama/yağmur sonrası başladı", "Nem/su girişi (tampon içi, soketler)", "Adım 7"],
             ["Çarpma/tampon boya/cam değişimi sonrası", "Sensör yönü, boya, kablo, braket, kalibrasyon eksikliği", "Adım 5, 6, 4 + servis"],
             ["Menüden kapatınca mesaj yok, açınca var", "Gerçek hata kodu aktif; sistem bileşeni bulamıyor", "Tüm adımlar + tanı cihazı"]],
            [60 * mm, 70 * mm, W - 130 * mm]),
      Spacer(1, 8),
      H2("Kayıt tablosu (yazdırıp doldurabilirsiniz)"),
      table([["Tarih / km", "Yapılan adım", "Gözlem (mesaj, kaç km sonra)", "Sonuç"],
             ["", "", "", ""], ["", "", "", ""], ["", "", "", ""], ["", "", "", ""], ["", "", "", ""], ["", "", "", ""]],
            [28 * mm, 52 * mm, W - 28 * mm - 52 * mm - 28 * mm, 28 * mm], zebra=False, rh=24),
      PageBreak()]

# ---------------- SECTION 5 ----------------
S += [*[x for x in []]]
S += [H1("5. Karar akışı ve sonraki adımlar"),
      Fig(345, fig_flow),
      Spacer(1, 8),
      H2("Servise / tanı cihazına giderken isteyin"),
      *B(["<b>Tüm modüllerin</b> (park yardımı, kamera/şerit, kör nokta/radar, BSI, ABS/ESP) hata kodlarının <b>çıktısı veya fotoğrafı</b> – silmeden önce.",
          "Kodların <b>sabit mi aralıklı mı</b> olduğu ve (varsa) hata oluşma koşulları (km, voltaj, sıcaklık).",
          "Modüllerin <b>konfigürasyon/kodlama</b> kontrolü: fonksiyonlar araç donanımıyla uyumlu etkinleştirilmiş mi? (Satıcı \"kapatmış\" olabilir.)",
          "Parça değiştirilirse <b>kalibrasyon/eşleştirme</b> yapılması ve yazılı iş emri.",
          "Yetkili serviste, araca ait <b>fabrika garantisi / uzatılmış garanti / geri çağırma</b> kapsamı olup olmadığı sorgulaması (araç yaşınıza göre)."]),
      Spacer(1, 6),
      box("Araç satıcı tarafından, bu sistemlerin arızalı olduğu bilinerek ve gizlenerek satılmışsa, Tüketici Hukuku'ndaki <b>ayıplı mal</b> hükümleri devreye girebilir. "
          "Yetkili servisten <b>yazılı arıza/tanı raporu</b> ve onarım teklifi alın; satış sözleşmesi, ekspertiz raporu ve ilan metnini saklayın; gerekirse tüketici hakem heyeti/avukat ile görüşün. "
          "(Bu bölüm hukuki tavsiye değildir.)", "warn", "Not"),
      ]

doc.build(S)
print("ok")
