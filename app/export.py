"""Funções de exportação de relatórios — PDF e Excel."""
from __future__ import annotations

import datetime
import io

import pandas as pd


def generate_dashboard_pdf(
    kpis: dict[str, float],
    monthly_df: pd.DataFrame,
    last10_df: pd.DataFrame,
) -> bytes:
    """Gera relatório PDF do dashboard financeiro.

    Usa fpdf2 com core fonts + encoding windows-1252 para suporte a
    caracteres Portuguese (ã, ç, á, é, etc.) sem dependências externas de fonte.
    """
    from fpdf import FPDF  # import tardio — não bloqueia app se fpdf2 ausente

    today = datetime.date.today().strftime("%d/%m/%Y")

    pdf = FPDF()
    pdf.set_doc_option("core_fonts_encoding", "windows-1252")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── Faixa de cabeçalho ──────────────────────────────────────────────────
    pdf.set_fill_color(10, 25, 47)         # #0A192F
    pdf.rect(0, 0, 210, 24, "F")
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_text_color(100, 255, 218)      # #64FFDA
    pdf.set_xy(12, 8)
    pdf.cell(0, 8, "Inside Cash  |  Relatório Financeiro")

    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(140, 146, 176)      # #8892B0
    pdf.set_xy(12, 18)
    pdf.cell(0, 5, f"Gerado em {today}")

    pdf.ln(16)
    pdf.set_text_color(10, 25, 47)

    # ── Indicadores do período ──────────────────────────────────────────────
    _section_title(pdf, "Indicadores do Período")

    kpi_rows = [
        ("Total recebido pela PJ",  kpis.get("pj_income", 0.0)),
        ("Total recebido pela PF",  kpis.get("pf_income", 0.0)),
        ("Total de despesas",       kpis.get("expenses", 0.0)),
        ("Saldo do período",        kpis.get("balance", 0.0)),
    ]
    pdf.set_font("Helvetica", "", 10)
    for label, value in kpi_rows:
        pdf.set_x(12)
        pdf.cell(110, 7, label)
        color = (0, 180, 120) if label != "Total de despesas" else (200, 50, 50)
        pdf.set_text_color(*color)
        pdf.cell(0, 7, f"R$ {value:,.2f}", ln=True)
        pdf.set_text_color(10, 25, 47)

    pdf.ln(4)

    # ── Resultado mensal ────────────────────────────────────────────────────
    if not monthly_df.empty:
        _section_title(pdf, "Resultado Mensal")
        _table_header(pdf, [("Mês", 60), ("Resultado (R$)", 60)])
        pdf.set_font("Helvetica", "", 9)
        for _, row in monthly_df.iterrows():
            val = float(row["signed_amount"])
            pdf.set_x(12)
            pdf.cell(60, 6, str(row["month"]), border=1)
            pdf.set_text_color(0, 150, 90) if val >= 0 else pdf.set_text_color(200, 50, 50)
            pdf.cell(60, 6, f"R$ {val:,.2f}", border=1, ln=True)
            pdf.set_text_color(10, 25, 47)
        pdf.ln(4)

    # ── Últimos lançamentos ─────────────────────────────────────────────────
    if not last10_df.empty:
        _section_title(pdf, "Últimos Lançamentos")
        cols = [("Data", 22), ("Descrição", 62), ("Categoria", 36), ("Orig.", 14), ("Valor (R$)", 34)]
        _table_header(pdf, cols)
        pdf.set_font("Helvetica", "", 7)
        for _, row in last10_df.iterrows():
            pdf.set_x(12)
            pdf.cell(22, 5, _safe(row.get("Data", "")),        border=1)
            pdf.cell(62, 5, _safe(row.get("Descrição", ""), 38), border=1)
            pdf.cell(36, 5, _safe(row.get("Categoria", "")),   border=1)
            pdf.cell(14, 5, _safe(row.get("Origem", "")),      border=1)
            pdf.cell(34, 5, _safe(row.get("Valor (R$)", "")), border=1, ln=True)

    # ── Rodapé ──────────────────────────────────────────────────────────────
    pdf.set_y(-12)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(140, 146, 176)
    pdf.cell(0, 5, "Inside Cash — gerado automaticamente", align="C")

    return bytes(pdf.output())


def generate_excel(df: pd.DataFrame) -> bytes:
    """Serializa um DataFrame para bytes XLSX usando openpyxl."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Lançamentos")
    return buf.getvalue()


# ── helpers internos ────────────────────────────────────────────────────────

def _section_title(pdf, title: str) -> None:
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(10, 25, 47)
    pdf.set_x(12)
    pdf.cell(0, 6, title, ln=True)
    pdf.set_draw_color(100, 255, 218)
    pdf.line(12, pdf.get_y(), 198, pdf.get_y())
    pdf.ln(3)
    pdf.set_text_color(10, 25, 47)


def _table_header(pdf, cols: list[tuple[str, int]]) -> None:
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(240, 248, 252)
    pdf.set_text_color(10, 25, 47)
    pdf.set_x(12)
    for label, width in cols:
        pdf.cell(width, 6, label, border=1, fill=True)
    pdf.ln()


def _safe(value: object, max_len: int = 100) -> str:
    return str(value)[:max_len]
