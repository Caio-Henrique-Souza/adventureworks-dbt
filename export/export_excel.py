"""
Exporta os marts do dbt para uma planilha Excel formatada (output/adventureworks_vendas.xlsx).

Abas:
  - Realizado x Meta      por território e mês, com atingimento colorido
  - Vendas por categoria  faturamento líquido e margem por ano e categoria
  - Top produtos          20 produtos com maior faturamento
  - Top clientes          20 clientes com maior faturamento

Uso:
    python export/export_excel.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import pandas as pd
from openpyxl import load_workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "warehouse.duckdb"
OUT = ROOT / "output" / "adventureworks_vendas.xlsx"

MOEDA = '#,##0.00'
INTEIRO = '#,##0'
PCT = '0.0%'

ABAS = {
    "Realizado x Meta": ("""
        select month_start as "Mês", territory_name as "Território", owner_name as "Responsável",
               actual_amount as "Realizado (USD)", target_amount as "Meta (USD)",
               target_attainment as "Atingimento", orders as "Pedidos"
        from marts.fct_sales_vs_target_monthly
        order by month_start, territory_name
    """, {"Realizado (USD)": MOEDA, "Meta (USD)": MOEDA, "Atingimento": PCT, "Pedidos": INTEIRO,
          "Mês": "mmm/yyyy"}),
    "Vendas por categoria": ("""
        select year(f.order_date) as "Ano", p.product_category as "Categoria",
               sum(f.order_qty) as "Quantidade", sum(f.net_amount) as "Faturamento líquido (USD)",
               sum(f.margin_amount) as "Margem (USD)",
               sum(f.margin_amount) / nullif(sum(f.net_amount), 0) as "Margem %"
        from marts.fct_sales f
        join marts.dim_product p using (product_id)
        group by all
        order by 1, 4 desc
    """, {"Quantidade": INTEIRO, "Faturamento líquido (USD)": MOEDA, "Margem (USD)": MOEDA, "Margem %": PCT}),
    "Top produtos": ("""
        select p.product_number as "Código", p.product_name as "Produto", p.product_category as "Categoria",
               p.product_subcategory as "Subcategoria", sum(f.order_qty) as "Quantidade",
               sum(f.net_amount) as "Faturamento líquido (USD)"
        from marts.fct_sales f
        join marts.dim_product p using (product_id)
        group by all
        order by 6 desc
        limit 20
    """, {"Quantidade": INTEIRO, "Faturamento líquido (USD)": MOEDA}),
    "Top clientes": ("""
        select c.account_number as "Conta", c.customer_name as "Cliente", c.customer_type as "Tipo",
               t.territory_name as "Território", count(distinct f.sales_order_id) as "Pedidos",
               sum(f.net_amount) as "Faturamento líquido (USD)", max(f.order_date) as "Última compra"
        from marts.fct_sales f
        join marts.dim_customer c using (customer_id)
        left join marts.dim_territory t on t.territory_id = c.territory_id
        group by all
        order by 6 desc
        limit 20
    """, {"Pedidos": INTEIRO, "Faturamento líquido (USD)": MOEDA, "Última compra": "dd/mm/yyyy"}),
}


def formatar(ws, formatos: dict[str, str]) -> None:
    cab = [c.value for c in ws[1]]
    azul = PatternFill("solid", fgColor="1F3A5F")
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = azul
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 30
    for i, nome in enumerate(cab, 1):
        letra = get_column_letter(i)
        largura = max(len(str(nome)), *(len(str(c.value or "")) for c in ws[letra][1:200])) + 2
        ws.column_dimensions[letra].width = min(max(largura, 10), 45)
        if nome in formatos:
            for c in ws[letra][1:]:
                c.number_format = formatos[nome]
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    if "Atingimento" in cab:
        letra = get_column_letter(cab.index("Atingimento") + 1)
        faixa = f"{letra}2:{letra}{ws.max_row}"
        ws.conditional_formatting.add(faixa, CellIsRule(operator="greaterThanOrEqual", formula=["1"],
                                      fill=PatternFill("solid", fgColor="E5F4E4"), font=Font(color="15803D")))
        ws.conditional_formatting.add(faixa, CellIsRule(operator="lessThan", formula=["0.9"],
                                      fill=PatternFill("solid", fgColor="FBEBEB"), font=Font(color="B91C1C")))


def main() -> int:
    if not DB_PATH.exists():
        print("Banco não encontrado. Rode o pipeline antes: python run_pipeline.py")
        return 1
    con = duckdb.connect(str(DB_PATH), read_only=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(OUT, engine="openpyxl") as xw:
        for aba, (sql, _) in ABAS.items():
            df = con.execute(sql).df()
            df.to_excel(xw, sheet_name=aba, index=False)
            print(f"  {aba:<22} {len(df):>5} linhas")
    con.close()

    wb = load_workbook(OUT)
    for aba, (_, formatos) in ABAS.items():
        formatar(wb[aba], formatos)
    wb.save(OUT)
    print(f"Planilha gerada: {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
