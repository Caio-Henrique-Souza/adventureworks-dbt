"""
Gera a planilha de METAS DE VENDAS (data/excel/metas_vendas.xlsx), simulando o arquivo
que o time comercial mantém no Excel: uma meta mensal em USD por território.

As metas são fictícias, derivadas da venda real de cada mês com uma variação aleatória
(seed fixa = sempre o mesmo arquivo). Rode depois de load_raw.py.

Uso:
    python ingestion/create_targets_excel.py
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

import duckdb
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "warehouse.duckdb"
OUT = ROOT / "data" / "excel" / "metas_vendas.xlsx"

SQL = """
select
    cast(substr(h.OrderDate, 1, 4) as int)  as ano,
    cast(substr(h.OrderDate, 6, 2) as int)  as mes,
    t.Name                                  as territorio,
    sum(cast(h.SubTotal as double))         as venda
from raw_sales.SalesOrderHeader h
join raw_sales.SalesTerritory t on t.TerritoryID = h.TerritoryID
group by all
order by ano, mes, territorio
"""


def main() -> int:
    random.seed(2025)
    con = duckdb.connect(str(DB_PATH), read_only=True)
    linhas = con.execute(SQL).fetchall()
    con.close()

    wb = Workbook()
    ws = wb.active
    ws.title = "Metas"
    cab = ["Ano", "Mês", "Território", "Meta (USD)", "Responsável"]
    ws.append(cab)
    responsaveis = ["Ana", "Bruno", "Carla", "Diego", "Eva"]
    for ano, mes, territorio, venda in linhas:
        meta = round(venda * random.uniform(0.92, 1.15), -3)
        ws.append([ano, mes, territorio, meta, responsaveis[sum(map(ord, territorio)) % len(responsaveis)]])

    azul = PatternFill("solid", fgColor="1F3A5F")
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = azul
        c.alignment = Alignment(horizontal="center")
    for row in ws.iter_rows(min_row=2, min_col=4, max_col=4):
        row[0].number_format = '#,##0'
    for i, w in enumerate([8, 6, 18, 14, 14], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    leia = wb.create_sheet("Leia-me")
    for linha in [
        ["Planilha de metas de vendas (dados fictícios para treino)"],
        ["Uma linha por território e mês. Valores em USD, sem impostos e frete."],
        ["Mantida pelo time comercial; o pipeline lê a aba 'Metas'."],
    ]:
        leia.append(linha)
    leia.column_dimensions["A"].width = 80

    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    print(f"{len(linhas)} metas gravadas em {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
