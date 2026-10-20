import flet as ft
import flet.canvas as cv
import json
import math
import os

# Android ও Windows উভয় প্ল্যাটফর্মে রাইটেবল পাথে ডাটাবেস সেভ করার ব্যবস্থা
DB_FILE = os.path.join(os.path.expanduser("~"), "pressnest_db_v3.json")

MASTER_SHEETS = [
    {"key": "20x30", "label": "20 x 30 inch (ডাবল ক্রাউন)", "short": "20×30", "w": 20.0, "h": 30.0},
    {"key": "23x36", "label": "23 x 36 inch (ডাবল ডেমি)", "short": "23×36", "w": 23.0, "h": 36.0},
    {"key": "25x37", "label": "25 x 37 inch", "short": "25×37", "w": 25.0, "h": 37.0},
    {"key": "22x28", "label": "22 x 28 inch", "short": "22×28", "w": 22.0, "h": 28.0},
    {"key": "22x34", "label": "22 x 34 inch", "short": "22×34", "w": 22.0, "h": 34.0}
]

def generate_default_db():
    gsms = [50, 55, 65, 70, 80, 100, 120, 150]
    papers = []

    for g in gsms:
        papers.append({
            "id": f"offset_{g}",
            "name": f"Offset Paper ({g} GSM)",
            "unit_sheets": 500,
            "unit_name": "রিম",
            "prices": {
                "20x30": round(g * 40.0),
                "23x36": round(g * 55.0),
                "25x37": round(g * 62.0),
                "22x28": round(g * 42.0),
                "22x34": round(g * 50.0)
            }
        })

    for g in gsms:
        papers.append({
            "id": f"art_{g}",
            "name": f"Art Paper ({g} GSM)",
            "unit_sheets": 500,
            "unit_name": "রিম",
            "prices": {
                "20x30": round(g * 45.0),
                "23x36": round(g * 62.0),
                "25x37": round(g * 70.0),
                "22x28": round(g * 47.0),
                "22x34": round(g * 56.0)
            }
        })

    extras = [
        ("color_paper", "Color Paper", 500, "রিম", {"20x30": 3200.0, "23x36": 4400.0, "25x37": 4900.0, "22x28": 3300.0, "22x34": 3900.0}),
        ("auto_carbon", "Auto Carbon", 500, "রিম", {"20x30": 4500.0, "23x36": 6000.0, "25x37": 6600.0, "22x28": 4600.0, "22x34": 5400.0}),
        ("board", "Board", 500, "রিম", {"20x30": 6500.0, "23x36": 8800.0, "25x37": 9600.0, "22x28": 6700.0, "22x34": 7900.0}),
        ("art_card", "Art Card", 500, "রিম", {"20x30": 7200.0, "23x36": 9600.0, "25x37": 10500.0, "22x28": 7400.0, "22x34": 8600.0}),
        ("sticker", "Sticker", 100, "প্যাকেট", {"20x30": 1200.0, "23x36": 1600.0, "25x37": 1800.0, "22x28": 1250.0, "22x34": 1450.0})
    ]
    for pid, pname, u_sheets, u_name, pr_dict in extras:
        papers.append({
            "id": pid,
            "name": pname,
            "unit_sheets": u_sheets,
            "unit_name": u_name,
            "prices": pr_dict
        })

    return {
        "presets": [
            {"label": "10 x 15", "val": "10x15", "w": 10.0, "h": 15.0},
            {"label": "7 x 20", "val": "7x20", "w": 7.0, "h": 20.0},
            {"label": "7.5 x 20", "val": "7.5x20", "w": 7.5, "h": 20.0},
            {"label": "18 x 23", "val": "18x23", "w": 18.0, "h": 23.0},
            {"label": "15 x 20", "val": "15x20", "w": 15.0, "h": 20.0},
            {"label": "11.5 x 18", "val": "11.5x18", "w": 11.5, "h": 18.0}
        ],
        "papers": papers,
        "machines": [
            {"id": "hamada_600", "name": "Hamada 600 Mini", "platePrice": 250.0, "printPer1000": 300.0},
            {"id": "hashimoto", "name": "HASHIMOTO", "platePrice": 350.0, "printPer1000": 400.0},
            {"id": "kord", "name": "KORD", "platePrice": 450.0, "printPer1000": 500.0}
        ],
        "job_types": [
            {"id": "poster_leaflet", "name": "পোস্টার-লিফলেট", "ratePer1000": 0.0},
            {"id": "cash_memo", "name": "ক্যাশ মেমো", "ratePer1000": 150.0},
            {"id": "pad", "name": "প্যাড", "ratePer1000": 200.0},
            {"id": "magazine", "name": "ম্যাগাজিন", "ratePer1000": 350.0},
            {"id": "book", "name": "বই", "ratePer1000": 300.0},
            {"id": "khata", "name": "খাতা", "ratePer1000": 250.0}
        ]
    }

DEFAULT_DB = generate_default_db()

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if all(k in data for k in ("presets", "papers", "machines", "job_types")):
                    return data
        except Exception:
            pass
    return json.loads(json.dumps(DEFAULT_DB))

def save_db_file(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

# ----------------- NESTING ENGINE -----------------
def build_grid_rects(start_x, start_y, cols, rows, u_w, u_h, rotated):
    rects = []
    for r in range(rows):
        for c in range(cols):
            rects.append({
                "x": start_x + c * u_w,
                "y": start_y + r * u_h,
                "w": u_w,
                "h": u_h,
                "rotated": rotated
            })
    return rects

def calc_nesting(unit_w, unit_h, sheet_w, sheet_h):
    if unit_w <= 0 or unit_h <= 0 or sheet_w <= 0 or sheet_h <= 0:
        return {"ups": 0, "rects": [], "sheetW": sheet_w, "sheetH": sheet_h, "wastagePct": 100.0, "desc": "বসবে না", "cutText": "", "mainCut": None}

    EPS = 0.0001
    candidates = []

    c1 = math.floor((sheet_w + EPS) / unit_w)
    r1 = math.floor((sheet_h + EPS) / unit_h)
    if c1 * r1 > 0:
        candidates.append({
            "ups": c1 * r1,
            "isMixed": False,
            "rects": build_grid_rects(0, 0, c1, r1, unit_w, unit_h, False),
            "mainCut": None,
            "desc": f"{c1} কলাম × {r1} সারি (সোজা)",
            "cutText": f'লম্বালম্বি {c1} ভাগ ({unit_w:g}") এবং আড়াআড়ি {r1} ভাগ ({unit_h:g}") = মোট {c1 * r1} পিস।'
        })

    c2 = math.floor((sheet_w + EPS) / unit_h)
    r2 = math.floor((sheet_h + EPS) / unit_w)
    if c2 * r2 > 0:
        candidates.append({
            "ups": c2 * r2,
            "isMixed": False,
            "rects": build_grid_rects(0, 0, c2, r2, unit_h, unit_w, True),
            "mainCut": None,
            "desc": f"{c2} কলাম × {r2} সারি (ঘুরিয়ে)",
            "cutText": f'ঘুরিয়ে লম্বালম্বি {c2} ভাগ ({unit_h:g}") এবং আড়াআড়ি {r2} ভাগ ({unit_w:g}") = মোট {c2 * r2} পিস।'
        })

    for left_rotated in [False, True]:
        wA = unit_h if left_rotated else unit_w
        hA = unit_w if left_rotated else unit_h
        wB = unit_w if left_rotated else unit_h
        hB = unit_h if left_rotated else unit_w

        max_cols_A = math.floor((sheet_w + EPS) / wA)
        rows_A = math.floor((sheet_h + EPS) / hA)

        for col_A in range(1, max_cols_A + 1):
            used_w = col_A * wA
            rem_w = sheet_w - used_w
            col_B = math.floor((rem_w + EPS) / wB)
            rows_B = math.floor((sheet_h + EPS) / hB)

            ups_A = col_A * rows_A
            ups_B = col_B * rows_B
            if ups_A > 0 and ups_B > 0:
                rects_A = build_grid_rects(0, 0, col_A, rows_A, wA, hA, left_rotated)
                rects_B = build_grid_rects(used_w, 0, col_B, rows_B, wB, hB, not left_rotated)
                candidates.append({
                    "ups": ups_A + ups_B,
                    "isMixed": True,
                    "rects": rects_A + rects_B,
                    "mainCut": {"type": "V", "pos": used_w},
                    "desc": f'কম্বিনেশন ({ups_A}টি {wA:g}"×{hA:g}" + {ups_B}টি {wB:g}"×{hB:g}")',
                    "cutText": f'প্রথমে {used_w:g}" মাপে লম্বা কোপ দিন। বাম অংশে {ups_A} পিস ({wA:g}"×{hA:g}") এবং ডান অংশে {ups_B} পিস ({wB:g}"×{hB:g}") = মোট {ups_A + ups_B} পিস।'
                })

    for top_rotated in [False, True]:
        wA = unit_h if top_rotated else unit_w
        hA = unit_w if top_rotated else unit_h
        wB = unit_w if top_rotated else unit_h
        hB = unit_h if top_rotated else unit_w

        cols_A = math.floor((sheet_w + EPS) / wA)
        max_rows_A = math.floor((sheet_h + EPS) / hA)

        for row_A in range(1, max_rows_A + 1):
            used_h = row_A * hA
            rem_h = sheet_h - used_h
            cols_B = math.floor((sheet_w + EPS) / wB)
            row_B = math.floor((rem_h + EPS) / hB)

            ups_A = cols_A * row_A
            ups_B = cols_B * row_B
            if ups_A > 0 and ups_B > 0:
                rects_A = build_grid_rects(0, 0, cols_A, row_A, wA, hA, top_rotated)
                rects_B = build_grid_rects(0, used_h, cols_B, row_B, wB, hB, not top_rotated)
                candidates.append({
                    "ups": ups_A + ups_B,
                    "isMixed": True,
                    "rects": rects_A + rects_B,
                    "mainCut": {"type": "H", "pos": used_h},
                    "desc": f'কম্বিনেশন ({ups_A}টি {wA:g}"×{hA:g}" + {ups_B}টি {wB:g}"×{hB:g}")',
                    "cutText": f'প্রথমে {used_h:g}" মাপে আড়াআড়ি কোপ দিন। উপরের অংশে {ups_A} পিস ({wA:g}"×{hA:g}") এবং নিচের অংশে {ups_B} পিস ({wB:g}"×{hB:g}") = মোট {ups_A + ups_B} পিস।'
                })

    if not candidates:
        return {"ups": 0, "rects": [], "sheetW": sheet_w, "sheetH": sheet_h, "wastagePct": 100.0, "desc": "বসবে না", "cutText": "এই সেটিংয়ে কোনো পিস ধরবে না।", "mainCut": None}

    candidates.sort(key=lambda x: (-x["ups"], 1 if x["isMixed"] else 0))
    best = candidates[0]
    sheet_area = sheet_w * sheet_h
    used_area = best["ups"] * (unit_w * unit_h)
    wastage_area = max(0.0, sheet_area - used_area)
    wastage_pct = (wastage_area / sheet_area) * 100.0

    best.update({
        "sheetW": sheet_w,
        "sheetH": sheet_h,
        "wastageArea": wastage_area,
        "wastagePct": wastage_pct
    })
    return best


# ----------------- ANDROID / MOBILE FLET UI -----------------
def main(page: ft.Page):
    page.title = "PressNest Estimator"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0d1117"
    page.padding = 12
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.window.width = 430
    page.window.height = 860

    db = load_db()

    C_SURFACE = "#161b22"
    C_CARD = "#1f242d"
    C_INPUT = "#21262d"
    C_BORDER = "#30363d"
    C_ACCENT = "#6366f1"
    C_EMERALD = "#10a37f"
    C_TEXT = "#e6edf3"
    C_MUTED = "#8b949e"

    color_map = {"1 Color": 1, "2 Color": 2, "3 Color": 3, "4 Color": 4}
    master_map = {m["label"]: m for m in MASTER_SHEETS}

    # --- UI Input Controls ---
    tf_work_w = ft.TextField(label="Width (inch)", value="7.5", keyboard_type=ft.KeyboardType.NUMBER, bgcolor=C_INPUT, border_radius=10, border_color=C_BORDER, text_size=14, expand=1, content_padding=12)
    tf_work_h = ft.TextField(label="Height (inch)", value="10", keyboard_type=ft.KeyboardType.NUMBER, bgcolor=C_INPUT, border_radius=10, border_color=C_BORDER, text_size=14, expand=1, content_padding=12)

    dd_setting = ft.Dropdown(label="Setting Layout (Preset)", value="18 x 23", bgcolor=C_INPUT, border_radius=10, border_color=C_BORDER, text_size=14, expand=True, content_padding=10)
    tf_qty = ft.TextField(label="Quantity (পিস)", value="1000", keyboard_type=ft.KeyboardType.NUMBER, bgcolor=C_INPUT, border_radius=10, border_color=C_BORDER, text_size=14, expand=1, content_padding=12)
    tf_extra = ft.TextField(label="অতিরিক্ত ওয়েস্টেজ (শিট)", value="0", keyboard_type=ft.KeyboardType.NUMBER, bgcolor=C_INPUT, border_radius=10, border_color=C_BORDER, text_size=14, expand=1, content_padding=12)

    dd_paper = ft.Dropdown(label="Paper Type (কাগজের ধরন)", bgcolor=C_INPUT, border_radius=10, border_color=C_BORDER, text_size=14, expand=True, content_padding=10)
    dd_job = ft.Dropdown(label="Type (কাজের ধরন)", bgcolor=C_INPUT, border_radius=10, border_color=C_BORDER, text_size=14, expand=1, content_padding=10)
    dd_master = ft.Dropdown(
        label="মূল কাগজ (Costing Calc.)",
        value="23 x 36 inch (ডাবল ডেমি)",
        options=[ft.dropdown.Option(k) for k in master_map.keys()],
        bgcolor=C_INPUT, border_radius=10, border_color=C_BORDER, text_size=13, expand=1, content_padding=10
    )

    dd_machine = ft.Dropdown(label="মেশিন", bgcolor=C_INPUT, border_radius=10, border_color=C_BORDER, text_size=14, expand=3, content_padding=10)
    dd_color = ft.Dropdown(
        label="কালার",
        value="1 Color",
        options=[ft.dropdown.Option(k) for k in color_map.keys()],
        bgcolor=C_INPUT, border_radius=10, border_color=C_BORDER, text_size=14, expand=2, content_padding=10
    )

    def refresh_dropdowns():
        preset_labels = [p["label"] for p in db["presets"]]
        dd_setting.options = [ft.dropdown.Option(l) for l in preset_labels]
        if dd_setting.value not in preset_labels:
            dd_setting.value = preset_labels[0]

        paper_names = [p["name"] for p in db["papers"]]
        dd_paper.options = [ft.dropdown.Option(n) for n in paper_names]
        if dd_paper.value not in paper_names:
            dd_paper.value = next((n for n in paper_names if "80 GSM" in n), paper_names[0])

        job_names = [j["name"] for j in db["job_types"]]
        dd_job.options = [ft.dropdown.Option(n) for n in job_names]
        if dd_job.value not in job_names:
            dd_job.value = next((n for n in job_names if "মেমো" in n), job_names[0])

        machine_names = [m["name"] for m in db["machines"]]
        dd_machine.options = [ft.dropdown.Option(n) for n in machine_names]
        if dd_machine.value not in machine_names:
            dd_machine.value = machine_names[0]

    refresh_dropdowns()

    # --- Output Containers ---
    rec_wrap = ft.Row(wrap=True, spacing=6, run_spacing=6)
    summary_text = ft.Text(size=13, weight=ft.FontWeight.BOLD, color=C_TEXT)
    summary_box = ft.Container(content=summary_text, bgcolor=C_CARD, border_radius=10, padding=12, border=ft.border.all(1, C_ACCENT))

    cost_rows_col = ft.Column(spacing=6)
    cut_text_lbl = ft.Text(size=13, weight=ft.FontWeight.BOLD, color="#f8fafc", text_align=ft.TextAlign.CENTER)

    CANVAS_W = 350
    CANVAS_H = 290
    nesting_canvas = cv.Canvas(width=CANVAS_W, height=CANVAS_H)

    card_left_text = ft.Text(size=12, color=C_TEXT)
    card_right_text = ft.Text(size=12, color=C_TEXT)

    def format_master_card(m_info, set_w, set_h, current_ups, work_w, work_h, qty, setting_sheets_needed, unit_sheets, unit_name):
        mw, mh = m_info["w"], m_info["h"]
        nest_m = calc_nesting(set_w, set_h, mw, mh)
        direct_m = calc_nesting(work_w, work_h, mw, mh)
        sheets_needed = math.ceil(setting_sheets_needed / nest_m["ups"]) if (nest_m["ups"] > 0 and setting_sheets_needed > 0) else 0
        units_count = sheets_needed / float(unit_sheets)
        direct_needed = math.ceil(qty / direct_m["ups"]) if direct_m["ups"] > 0 else 0

        txt = (
            f"📄 {m_info['label']} শিট\n"
            f"────────────────────────────\n"
            f"• ১টি বড় শিটে {set_w:g}×{set_h:g} সেটিং বের হবে: {nest_m['ups']} টি (মোট {nest_m['ups'] * current_ups} পিস)\n"
            f"• {qty} পিসের জন্য মূল {m_info['short']} শিট লাগবে: {sheets_needed} শিট ({units_count:.2f} {unit_name})\n"
            f"• সরাসরি {m_info['short']} এ সর্বোচ্চ ধরে: {direct_m['ups']} পিস/শিট (লাগবে {direct_needed} শিট)"
        )
        return txt, sheets_needed

    def draw_canvas(nest):
        shapes = []
        pad = 28
        avail_w = CANVAS_W - pad * 2
        avail_h = CANVAS_H - pad * 2

        scale = min(avail_w / nest["sheetW"], avail_h / nest["sheetH"]) if (nest["sheetW"] > 0 and nest["sheetH"] > 0) else 1
        draw_w = nest["sheetW"] * scale
        draw_h = nest["sheetH"] * scale
        start_x = (CANVAS_W - draw_w) / 2
        start_y = (CANVAS_H - draw_h) / 2 + 8

        # Wastage Background
        shapes.append(cv.Rect(start_x, start_y, draw_w, draw_h, paint=ft.Paint(color="#451a1c", style=ft.PaintingStyle.FILL)))
        shapes.append(cv.Rect(start_x, start_y, draw_w, draw_h, paint=ft.Paint(color="#94a3b8", stroke_width=2, style=ft.PaintingStyle.STROKE)))
        shapes.append(cv.Text(CANVAS_W / 2, start_y - 14, f'সেটিং শিট: {nest["sheetW"]:g}" × {nest["sheetH"]:g}" (মোট {nest["ups"]} পিস)', style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD, color="#e6edf3"), alignment=ft.alignment.center))

        if nest["ups"] > 0 and nest["rects"]:
            for idx, r in enumerate(nest["rects"]):
                x = start_x + r["x"] * scale
                y = start_y + r["y"] * scale
                w = r["w"] * scale
                h = r["h"] * scale

                fill_col = "#064e3b" if r["rotated"] else "#1e3a8a"
                stroke_col = "#10b981" if r["rotated"] else "#3b82f6"

                shapes.append(cv.Rect(x, y, w, h, paint=ft.Paint(color=fill_col, style=ft.PaintingStyle.FILL)))
                shapes.append(cv.Rect(x, y, w, h, paint=ft.Paint(color=stroke_col, stroke_width=1.5, style=ft.PaintingStyle.STROKE)))
                shapes.append(cv.Text(x + w / 2, y + h / 2 - 6, f"#{idx + 1}", style=ft.TextStyle(size=10, weight=ft.FontWeight.BOLD, color="#ffffff"), alignment=ft.alignment.center))
                shapes.append(cv.Text(x + w / 2, y + h / 2 + 7, f'{r["w"]:g}"×{r["h"]:g}"', style=ft.TextStyle(size=9, color="#cbd5e1"), alignment=ft.alignment.center))

            if nest["mainCut"]:
                cut_paint = ft.Paint(color="#ef4444", stroke_width=2.5, style=ft.PaintingStyle.STROKE)
                if nest["mainCut"]["type"] == "V":
                    cut_x = start_x + nest["mainCut"]["pos"] * scale
                    shapes.append(cv.Line(cut_x, start_y - 6, cut_x, start_y + draw_h + 6, paint=cut_paint))
                else:
                    cut_y = start_y + nest["mainCut"]["pos"] * scale
                    shapes.append(cv.Line(start_x - 6, cut_y, start_x + draw_w + 6, cut_y, paint=cut_paint))

        nesting_canvas.shapes = shapes
        cut_text_lbl.value = f"✂️ কাটিং নির্দেশনা: {nest['cutText']}"

    def select_preset(lbl):
        dd_setting.value = lbl
        calculate_all()

    def calculate_all(e=None):
        try:
            work_w = float(tf_work_w.value or 0)
        except ValueError:
            work_w = 0.0
        try:
            work_h = float(tf_work_h.value or 0)
        except ValueError:
            work_h = 0.0
        try:
            qty = int(float(tf_qty.value or 0))
        except ValueError:
            qty = 0
        try:
            extra_sheets = int(float(tf_extra.value or 0))
        except ValueError:
            extra_sheets = 0

        selected_label = dd_setting.value
        selected_preset = next((p for p in db["presets"] if p["label"] == selected_label), db["presets"][0])

        evaluated = []
        for s in db["presets"]:
            res = calc_nesting(work_w, work_h, s["w"], s["h"])
            item = dict(s)
            item.update(res)
            evaluated.append(item)

        valid_settings = [ev for ev in evaluated if ev["ups"] > 0]
        min_wastage = min((ev["wastagePct"] for ev in valid_settings), default=100.0)

        rec_wrap.controls.clear()
        for ev in evaluated:
            is_best = ev["ups"] > 0 and abs(ev["wastagePct"] - min_wastage) < 0.5
            is_active = ev["label"] == selected_label
            txt = f"{ev['label']}: {ev['ups']} পিস ({ev['wastagePct']:.1f}%)" if ev["ups"] > 0 else f"{ev['label']}: বসবে না"
            if is_best:
                txt += " ★"

            bg_c = C_ACCENT if is_active else ("#065f46" if is_best else C_INPUT)
            bd_c = "#818cf8" if is_active else (C_EMERALD if is_best else C_BORDER)

            rec_wrap.controls.append(
                ft.Container(
                    content=ft.Text(txt, size=11, weight=ft.FontWeight.BOLD, color=C_TEXT),
                    bgcolor=bg_c,
                    padding=ft.padding.symmetric(horizontal=10, vertical=6),
                    border_radius=16,
                    border=ft.border.all(1, bd_c),
                    on_click=lambda _, lbl=ev["label"]: select_preset(lbl)
                )
            )

        set_w, set_h = selected_preset["w"], selected_preset["h"]
        current_nest = calc_nesting(work_w, work_h, set_w, set_h)
        setting_sheets_needed = math.ceil(qty / current_nest["ups"]) + extra_sheets if current_nest["ups"] > 0 else 0

        paper_obj = next((p for p in db["papers"] if p["name"] == dd_paper.value), db["papers"][0])
        unit_sheets = paper_obj.get("unit_sheets", 500)
        unit_name = paper_obj.get("unit_name", "রিম")

        selected_master_info = master_map.get(dd_master.value, MASTER_SHEETS[1])
        if selected_master_info["key"] == "20x30":
            left_m, right_m = MASTER_SHEETS[0], MASTER_SHEETS[1]
        else:
            left_m, right_m = MASTER_SHEETS[0], selected_master_info

        txt_left, sheets_left = format_master_card(left_m, set_w, set_h, current_nest["ups"], work_w, work_h, qty, setting_sheets_needed, unit_sheets, unit_name)
        txt_right, sheets_right = format_master_card(right_m, set_w, set_h, current_nest["ups"], work_w, work_h, qty, setting_sheets_needed, unit_sheets, unit_name)

        card_left_text.value = txt_left
        card_right_text.value = txt_right

        chosen_master_sheets = sheets_left if selected_master_info["key"] == "20x30" else sheets_right

        if current_nest["ups"] > 0:
            summary_box.border = ft.border.all(1, C_ACCENT)
            summary_text.color = C_TEXT
            summary_text.value = f'📌 নির্বাচিত লেআউট ({set_w:g}" × {set_h:g}"): প্রতি শিটে {current_nest["ups"]} পিস [{current_nest["desc"]}] | Wastage: {current_nest["wastagePct"]:.2f}% | মোট সেটিং শিট: {setting_sheets_needed} শিট'
        else:
            summary_box.border = ft.border.all(1, "#ef4444")
            summary_text.color = "#f87171"
            summary_text.value = f'⚠️ সতর্কতা: {work_w:g}" × {work_h:g}" সাইজটি {set_w:g}" × {set_h:g}" সেটিংয়ে বসানো সম্ভব নয়!'

        machine_obj = next((m for m in db["machines"] if m["name"] == dd_machine.value), db["machines"][0])
        job_obj = next((j for j in db["job_types"] if j["name"] == dd_job.value), db["job_types"][0])

        colors = color_map.get(dd_color.value, 1)
        master_key = selected_master_info["key"]

        chosen_unit_price = paper_obj["prices"].get(master_key, 0.0)
        per_sheet_price = chosen_unit_price / float(unit_sheets)

        paper_cost = chosen_master_sheets * per_sheet_price
        plate_cost = colors * machine_obj["platePrice"]
        impression_thousands = math.ceil(setting_sheets_needed / 1000.0) if setting_sheets_needed > 0 else 0
        printing_cost = impression_thousands * colors * machine_obj["printPer1000"]
        binding_rate = job_obj["ratePer1000"]
        binding_cost = (qty / 1000.0) * binding_rate

        total_cost = paper_cost + plate_cost + printing_cost + binding_cost
        unit_cost = (total_cost / qty) if qty > 0 else 0.0

        cost_items = [
            (f"১. কাগজ ({paper_obj['name']} - {selected_master_info['short']})", f"{chosen_master_sheets} শিট × ৳{per_sheet_price:.2f} ({unit_name}: ৳{chosen_unit_price:g})", f"৳ {paper_cost:.2f}", False),
            (f"২. সিটিপি প্লেট ({machine_obj['name']})", f"{colors} টি প্লেট × ৳{machine_obj['platePrice']:g}", f"৳ {plate_cost:.2f}", False),
            (f"৩. ছাপার বিল (ইম্প্রেশন: {setting_sheets_needed} শিট)", f"{impression_thousands} হাজার রান × {colors} কালার × ৳{machine_obj['printPer1000']:g}", f"৳ {printing_cost:.2f}", False),
            (f"৪. Type / কাজের ধরন ({job_obj['name']})", f"{qty} পিস (@ ৳{binding_rate:g}/হাজার)", f"৳ {binding_cost:.2f}", False),
            ("মোট অর্ডার খরচ (Total Cost)", f"প্রতি পিস খরচ: ৳ {unit_cost:.2f}", f"৳ {total_cost:.2f}", True)
        ]

        cost_rows_col.controls.clear()
        for title, desc, amt, is_total in cost_items:
            cost_rows_col.controls.append(
                ft.Container(
                    bgcolor="#1e293b" if is_total else C_INPUT,
                    border_radius=8,
                    padding=10,
                    border=ft.border.all(1, C_ACCENT if is_total else C_BORDER),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=2,
                                expand=True,
                                controls=[
                                    ft.Text(title, size=13, weight=ft.FontWeight.BOLD if is_total else ft.FontWeight.W_600, color=C_TEXT),
                                    ft.Text(desc, size=11, color=C_TEXT if is_total else C_MUTED)
                                ]
                            ),
                            ft.Text(amt, size=14, weight=ft.FontWeight.BOLD, color="#38bdf8" if is_total else C_TEXT)
                        ]
                    )
                )
            )

        draw_canvas(current_nest)
        page.update()

    # Bind change events
    for ctrl in [tf_work_w, tf_work_h, dd_setting, tf_qty, tf_extra, dd_paper, dd_job, dd_master, dd_machine, dd_color]:
        ctrl.on_change = calculate_all

    # --- Add Custom Preset Dialog ---
    def open_add_preset_dlg(e):
        w_in = ft.TextField(label="Width (যেমন 12)", keyboard_type=ft.KeyboardType.NUMBER, bgcolor=C_INPUT, border_radius=8)
        h_in = ft.TextField(label="Height (যেমন 18)", keyboard_type=ft.KeyboardType.NUMBER, bgcolor=C_INPUT, border_radius=8)

        def save_preset(_):
            try:
                w = float(w_in.value)
                h = float(h_in.value)
                if w <= 0 or h <= 0:
                    raise ValueError
            except Exception:
                return
            label = f"{w:g} x {h:g}"
            val = f"{w:g}x{h:g}"
            if not any(p["label"] == label for p in db["presets"]):
                db["presets"].append({"label": label, "val": val, "w": w, "h": h})
                save_db_file(db)
                refresh_dropdowns()
            dd_setting.value = label
            page.close(dlg)
            calculate_all()

        dlg = ft.AlertDialog(
            bgcolor=C_SURFACE,
            title=ft.Text("নতুন কাস্টম প্রিসেট যোগ করুন", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Column([w_in, h_in], tight=True, spacing=10),
            actions=[
                ft.TextButton("বাতিল", on_click=lambda _: page.close(dlg)),
                ft.ElevatedButton("সেভ করুন", bgcolor=C_EMERALD, color="#ffffff", on_click=save_preset)
            ]
        )
        page.open(dlg)

    # --- Settings Full Modal ---
    def open_settings_dlg(e):
        paper_inputs = []
        machine_inputs = []
        job_inputs = []

        settings_col = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, spacing=12, height=520, width=380)

        # 1. Papers
        settings_col.controls.append(ft.Text("১. কাগজের মূল্য তালিকা (রিম=৫০০, Sticker প্যাকেট=১০০)", size=14, weight=ft.FontWeight.BOLD, color="#38bdf8"))
        for p in db["papers"]:
            p_fields = {}
            row_inputs = []
            for m in MASTER_SHEETS:
                mk = m["key"]
                tf = ft.TextField(label=m["short"], value=str(p["prices"].get(mk, 0.0)), keyboard_type=ft.KeyboardType.NUMBER, width=95, text_size=12, content_padding=8, bgcolor=C_INPUT, border_radius=8)
                p_fields[mk] = tf
                row_inputs.append(tf)
            paper_inputs.append(p_fields)

            u_info = f"{p.get('unit_name', 'রিম')} ({p.get('unit_sheets', 500)} পিস)"
            settings_col.controls.append(
                ft.Container(
                    bgcolor=C_CARD, padding=10, border_radius=10, border=ft.border.all(1, C_BORDER),
                    content=ft.Column([
                        ft.Text(f"{p['name']} — [{u_info}]", size=12, weight=ft.FontWeight.BOLD),
                        ft.Row(row_inputs, wrap=True, spacing=6, run_spacing=6)
                    ], spacing=6)
                )
            )

        # 2. Machines
        settings_col.controls.append(ft.Text("২. মেশিন অনুযায়ী প্লেট ও ছাপার বিল", size=14, weight=ft.FontWeight.BOLD, color="#38bdf8"))
        for m in db["machines"]:
            tf_p = ft.TextField(label="প্লেট (৳)", value=str(m["platePrice"]), keyboard_type=ft.KeyboardType.NUMBER, expand=1, text_size=12, content_padding=8, bgcolor=C_INPUT, border_radius=8)
            tf_r = ft.TextField(label="ছাপা/হাজার (৳)", value=str(m["printPer1000"]), keyboard_type=ft.KeyboardType.NUMBER, expand=1, text_size=12, content_padding=8, bgcolor=C_INPUT, border_radius=8)
            machine_inputs.append((tf_p, tf_r))
            settings_col.controls.append(
                ft.Container(
                    bgcolor=C_CARD, padding=10, border_radius=10, border=ft.border.all(1, C_BORDER),
                    content=ft.Column([
                        ft.Text(m["name"], size=12, weight=ft.FontWeight.BOLD),
                        ft.Row([tf_p, tf_r], spacing=8)
                    ], spacing=6)
                )
            )

        # 3. Job Types
        settings_col.controls.append(ft.Text("৩. Type (কাজের ধরন) খরচ (প্রতি হাজার)", size=14, weight=ft.FontWeight.BOLD, color="#38bdf8"))
        for j in db["job_types"]:
            tf_j = ft.TextField(label=f"{j['name']} (৳/১০০০ পিস)", value=str(j["ratePer1000"]), keyboard_type=ft.KeyboardType.NUMBER, text_size=12, content_padding=8, bgcolor=C_INPUT, border_radius=8)
            job_inputs.append(tf_j)
            settings_col.controls.append(tf_j)

        def save_all(_):
            for i, p_dict in enumerate(paper_inputs):
                for mk, tf in p_dict.items():
                    db["papers"][i]["prices"][mk] = float(tf.value or 0)
            for i, (tf_p, tf_r) in enumerate(machine_inputs):
                db["machines"][i]["platePrice"] = float(tf_p.value or 0)
                db["machines"][i]["printPer1000"] = float(tf_r.value or 0)
            for i, tf_j in enumerate(job_inputs):
                db["job_types"][i]["ratePer1000"] = float(tf_j.value or 0)

            save_db_file(db)
            page.close(s_dlg)
            calculate_all()

        def reset_defaults(_):
            nonlocal db
            db = json.loads(json.dumps(DEFAULT_DB))
            save_db_file(db)
            refresh_dropdowns()
            page.close(s_dlg)
            calculate_all()

        s_dlg = ft.AlertDialog(
            bgcolor=C_SURFACE,
            title=ft.Text("⚙️ মূল্য তালিকা ও সেটিংস", size=16, weight=ft.FontWeight.BOLD),
            content=settings_col,
            actions=[
                ft.TextButton("ডিফল্ট রিসেট", on_click=reset_defaults),
                ft.TextButton("বন্ধ করুন", on_click=lambda _: page.close(s_dlg)),
                ft.ElevatedButton("💾 সেভ করুন", bgcolor=C_EMERALD, color="#ffffff", on_click=save_all)
            ]
        )
        page.open(s_dlg)

    # --- Assemble Main Mobile Layout ---
    header_bar = ft.Container(
        bgcolor=C_SURFACE, border_radius=12, padding=ft.padding.symmetric(horizontal=14, vertical=10),
        border=ft.border.all(1, C_BORDER),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text("🖨️ PressNest Estimator", size=17, weight=ft.FontWeight.BOLD, color=C_TEXT),
                ft.ElevatedButton("⚙️ সেটিংস", bgcolor=C_ACCENT, color="#ffffff", on_click=open_settings_dlg)
            ]
        )
    )

    input_section = ft.Container(
        bgcolor=C_SURFACE, border_radius=12, padding=14, border=ft.border.all(1, C_BORDER),
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Row([tf_work_w, ft.Text("×", size=18, weight=ft.FontWeight.BOLD, color=C_MUTED), tf_work_h]),
                ft.Row([
                    dd_setting,
                    ft.ElevatedButton("+ প্রিসেট", bgcolor=C_CARD, color=C_TEXT, height=46, on_click=open_add_preset_dlg)
                ]),
                ft.Row([tf_qty, tf_extra]),
                dd_paper,
                ft.Row([dd_job, dd_master]),
                ft.Row([dd_machine, dd_color]),
                ft.Container(
                    bgcolor=C_CARD, border_radius=10, padding=10, border=ft.border.all(1, C_BORDER),
                    content=ft.Column([
                        ft.Text("⚡ অটো ওয়েস্টেজ তুলনা (ট্যাপ করে সিলেক্ট করুন):", size=12, weight=ft.FontWeight.BOLD, color=C_MUTED),
                        rec_wrap
                    ], spacing=6)
                )
            ]
        )
    )

    cost_section = ft.Container(
        bgcolor=C_SURFACE, border_radius=12, padding=14, border=ft.border.all(1, C_BORDER),
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Text("📊 ফলাফল ও কস্টিং হিসাব (Cost Estimation)", size=15, weight=ft.FontWeight.BOLD, color=C_TEXT),
                summary_box,
                cost_rows_col
            ]
        )
    )

    canvas_section = ft.Container(
        bgcolor=C_SURFACE, border_radius=12, padding=14, border=ft.border.all(1, C_BORDER),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            controls=[
                ft.Text("✂️ Nesting Layout & Cut Direction", size=15, weight=ft.FontWeight.BOLD, color=C_TEXT),
                ft.Container(content=nesting_canvas, bgcolor=C_CARD, border_radius=10, padding=6, border=ft.border.all(1, C_BORDER)),
                ft.Text("🟦 সোজা   🟩 ঘুরিয়ে (Rotated)   🟥 ওয়েস্টেজ   ✂️ লাল দাগ = কাটিং", size=11, color=C_MUTED),
                cut_text_lbl
            ]
        )
    )

    sheets_section = ft.Container(
        bgcolor=C_SURFACE, border_radius=12, padding=14, border=ft.border.all(1, C_BORDER),
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Text("📄 মূল কাগজের শিট ও রিম/প্যাকেট হিসাব", size=15, weight=ft.FontWeight.BOLD, color=C_TEXT),
                ft.Container(content=card_left_text, bgcolor=C_CARD, border_radius=10, padding=12, border=ft.border.all(1, C_BORDER)),
                ft.Container(content=card_right_text, bgcolor=C_CARD, border_radius=10, padding=12, border=ft.border.all(1, C_BORDER))
            ]
        )
    )

    page.add(header_bar, input_section, cost_section, canvas_section, sheets_section)
    calculate_all()

ft.app(target=main)