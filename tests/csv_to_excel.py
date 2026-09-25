import csv
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.chart import BarChart, Reference

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "hasil_pengujian_kriptografi.csv"
OUT_DIR = ROOT / "docs"
OUT_DIR.mkdir(exist_ok=True)
OUT_PATH = OUT_DIR / "hasil_pengujian_kriptografi.xlsx"

def keterangan(entropi: float) -> str:
    if entropi >= 7.9:
        return "Entropi mendekati maksimum (8.0) - ciphertext acak sempurna"
    elif entropi >= 7.0:
        return "Entropi tinggi - ciphertext tampak acak"
    else:
        return "Entropi lebih rendah, kemungkinan karena ukuran data kecil"

with open(CSV_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

wb = Workbook()
ws = wb.active
ws.title = "Hasil Pengujian"

headers = [
    "Nama Berkas / Skenario", "Ukuran (Bytes)", "Waktu Enkripsi (ms)",
    "Waktu Dekripsi (ms)", "Entropi Cipherteks", "Avalanche Effect (%)", "Keterangan"
]
ws.append(headers)

header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
header_font = Font(color="FFFFFF", bold=True)
for cell in ws[1]:
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal="center")

for row in rows:
    entropi = float(row["Entropi Cipherteks"])
    ws.append([
        row["Nama Berkas / Skenario"],
        int(row["Ukuran (Bytes)"]),
        float(row["Waktu Enkripsi (ms)"]),
        float(row["Waktu Dekripsi (ms)"]),
        entropi,
        float(row["Avalanche Effect (%)"]),
        keterangan(entropi),
    ])

for i, col in enumerate(ws.columns, start=1):
    max_len = max(len(str(c.value)) for c in col)
    ws.column_dimensions[col[0].column_letter].width = max_len + 4

chart = BarChart()
chart.title = "Waktu Enkripsi vs Dekripsi per Skenario"
chart.y_axis.title = "Waktu (ms)"
chart.x_axis.title = "Skenario"
data = Reference(ws, min_col=3, max_col=4, min_row=1, max_row=ws.max_row)
cats = Reference(ws, min_col=1, min_row=2, max_row=ws.max_row)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
ws.add_chart(chart, "I2")

wb.save(OUT_PATH)
print(f"Selesai: {OUT_PATH}")