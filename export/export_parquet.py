"""
Exporta todas as tabelas do schema marts para arquivos Parquet (output/parquet/),
prontos para o Power BI: Obter dados > Pasta (ou Parquet).

Vantagem: o Power BI não abre o banco DuckDB, então o pipeline pode rodar com o
relatório aberto sem conflito de acesso ao arquivo.

Uso:
    python export/export_parquet.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "warehouse.duckdb"
OUT_DIR = ROOT / "output" / "parquet"


def main() -> int:
    if not DB_PATH.exists():
        print("Banco não encontrado. Rode o pipeline antes: python run_pipeline.py")
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH), read_only=True)
    tabelas = [r[0] for r in con.execute(
        "select table_name from information_schema.tables "
        "where table_schema = 'marts' and table_type = 'BASE TABLE' order by table_name"
    ).fetchall()]
    if not tabelas:
        print("Nenhuma tabela no schema marts. Rode o dbt antes.")
        return 1
    for t in tabelas:
        destino = OUT_DIR / f"{t}.parquet"
        con.execute(f"copy marts.\"{t}\" to '{destino.as_posix()}' (format parquet, compression zstd)")
        linhas = con.execute(f'select count(*) from marts."{t}"').fetchall()[0][0]
        print(f"  {t:<30} {linhas:>9,} linhas  {destino.stat().st_size / 1024:>8,.0f} KB")
    con.close()
    print(f"{len(tabelas)} arquivos Parquet em {OUT_DIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
