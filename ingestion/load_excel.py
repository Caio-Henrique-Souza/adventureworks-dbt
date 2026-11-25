"""
Carrega a planilha de metas (data/excel/metas_vendas.xlsx, aba 'Metas') no DuckDB,
em raw_excel.metas_vendas. Como na carga dos CSVs, tudo entra como texto.

Uso:
    python ingestion/load_excel.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "warehouse.duckdb"
XLSX = ROOT / "data" / "excel" / "metas_vendas.xlsx"


def main() -> int:
    if not XLSX.exists():
        print(f"Planilha não encontrada: {XLSX}\nRode antes: python ingestion/create_targets_excel.py")
        return 1
    df = pd.read_excel(XLSX, sheet_name="Metas", dtype=str)
    df.columns = ["ano", "mes", "territorio", "meta_usd", "responsavel"]
    df["_source_file"] = XLSX.name
    df["_loaded_at"] = pd.Timestamp.now(tz="UTC").isoformat()

    con = duckdb.connect(str(DB_PATH))
    con.execute("create schema if not exists raw_excel")
    con.register("df_metas", df)
    con.execute("create or replace table raw_excel.metas_vendas as select * from df_metas")
    con.close()
    print(f"raw_excel.metas_vendas: {len(df):,} linhas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
