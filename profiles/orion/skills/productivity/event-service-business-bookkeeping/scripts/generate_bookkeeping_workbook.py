#!/usr/bin/env python3
"""
Deterministic generator for Event & Service Business Bookkeeping Excel Workbook.
Produces a 6-sheet connected model: Dashboard, Registrasi_Klien, Transaksi_Pendapatan,
Pengeluaran_Operasional, Arus_Kas, Master_Data.
"""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def build_workbook(output_path):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    NAVY_FILL = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    ROSE_FILL = PatternFill(start_color="9D174D", end_color="9D174D", fill_type="solid")
    GOLD_FILL = PatternFill(start_color="B89968", end_color="B89968", fill_type="solid")

    CARD_BLUE_BG = PatternFill(start_color="EFF6FF", end_color="EFF6FF", fill_type="solid")
    CARD_GREEN_BG = PatternFill(start_color="F0FDF4", end_color="F0FDF4", fill_type="solid")
    CARD_AMBER_BG = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
    CARD_ROSE_BG = PatternFill(start_color="FFF1F2", end_color="FFF1F2", fill_type="solid")
    CARD_PURPLE_BG = PatternFill(start_color="FAF5FF", end_color="FAF5FF", fill_type="solid")

    FONT_APP_TITLE = Font(name="Calibri", size=16, bold=True, color="1E293B")
    FONT_SUBTITLE = Font(name="Calibri", size=10, italic=True, color="64748B")
    FONT_TBL_HEADER = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    FONT_BOLD = Font(name="Calibri", size=10, bold=True, color="0F172A")
    FONT_REGULAR = Font(name="Calibri", size=10, color="0F172A")
    FONT_CARD_TITLE = Font(name="Calibri", size=9, bold=True, color="475569")
    FONT_CARD_VAL = Font(name="Calibri", size=15, bold=True, color="0F172A")
    FONT_SECTION_HDR = Font(name="Calibri", size=12, bold=True, color="1E293B")

    BORDER_THIN = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1")
    )
    BORDER_TOTAL = Border(
        top=Side(style="thin", color="000000"),
        bottom=Side(style="double", color="000000"),
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1")
    )

    ALIGN_LEFT = Alignment(horizontal="left", vertical="center")
    ALIGN_CENTER = Alignment(horizontal="center", vertical="center")
    ALIGN_RIGHT = Alignment(horizontal="right", vertical="center")

    FORMAT_CURRENCY = 'Rp #,##0'
    FORMAT_DATE = 'YYYY-MM-DD'
    FORMAT_PERCENT = '0.0%'

    # 1. Master_Data
    ws_master = wb.create_sheet(title="Master_Data")
    ws_master.views.sheetView[0].showGridLines = True
    ws_master["A2"] = "MASTER DATA & PRICELIST LAYANAN"
    ws_master["A2"].font = FONT_APP_TITLE

    for c_idx, h in enumerate(["Kode_Paket", "Nama_Paket", "Kategori", "Harga_Dasar", "Inklusi", "Keterangan"], 1):
        c = ws_master.cell(row=5, column=c_idx, value=h)
        c.fill, c.font, c.alignment, c.border = NAVY_FILL, FONT_TBL_HEADER, ALIGN_CENTER, BORDER_THIN

    # 2. Dashboard
    ws_dash = wb.create_sheet(title="Dashboard")
    ws_dash.views.sheetView[0].showGridLines = True
    ws_dash["A2"] = "DASHBOARD KEUANGAN & ARUS KAS"
    ws_dash["A2"].font = FONT_APP_TITLE

    # 3. Registrasi_Klien
    ws_reg = wb.create_sheet(title="Registrasi_Klien")
    ws_reg.views.sheetView[0].showGridLines = True
    ws_reg["A2"] = "BUKU REGISTRASI KLIEN & PIPELINE"
    ws_reg["A2"].font = FONT_APP_TITLE

    # 4. Transaksi_Pendapatan
    ws_in = wb.create_sheet(title="Transaksi_Pendapatan")
    ws_in.views.sheetView[0].showGridLines = True
    ws_in["A2"] = "BUKU KAS MASUK (INFLOW)"
    ws_in["A2"].font = FONT_APP_TITLE

    # 5. Pengeluaran_Operasional
    ws_out = wb.create_sheet(title="Pengeluaran_Operasional")
    ws_out.views.sheetView[0].showGridLines = True
    ws_out["A2"] = "BUKU PENGELUARAN & COGS (OUTFLOW)"
    ws_out["A2"].font = FONT_APP_TITLE

    # 6. Arus_Kas
    ws_cf = wb.create_sheet(title="Arus_Kas")
    ws_cf.views.sheetView[0].showGridLines = True
    ws_cf["A2"] = "LAPORAN ARUS KAS (CASHFLOW STATEMENT)"
    ws_cf["A2"].font = FONT_APP_TITLE

    for sheet in wb.worksheets:
        for col in sheet.columns:
            sheet.column_dimensions[get_column_letter(col[0].column)].width = 16

    wb.save(output_path)
    return output_path

if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "bookkeeping.xlsx"
    build_workbook(out)
    print("Created", out)
