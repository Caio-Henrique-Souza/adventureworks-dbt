"""
Roda o pipeline completo, de ponta a ponta:

  1. download_data.py        baixa e extrai a base Adventure Works (se ainda não existir)
  2. load_raw.py             CSVs -> DuckDB (schemas raw_*)
  3. create_targets_excel.py gera a planilha de metas (se ainda não existir)
  4. load_excel.py           planilha de metas -> DuckDB (raw_excel)
  5. dbt build               staging -> intermediate -> marts, com testes
  6. export_excel.py         marts -> output/adventureworks_vendas.xlsx
  7. export_parquet.py       marts -> output/parquet/*.parquet (para o Power BI)

Uso:
    python run_pipeline.py
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = sys.executable
DBT = Path(PY).with_name("dbt.exe" if sys.platform == "win32" else "dbt")


def passo(nome: str, cmd: list[str], cwd: Path = ROOT) -> None:
    print(f"\n=== {nome} ===", flush=True)
    inicio = time.time()
    resultado = subprocess.run(cmd, cwd=cwd)
    if resultado.returncode != 0:
        print(f"\nFalhou em: {nome}")
        sys.exit(resultado.returncode)
    print(f"--- ok em {time.time() - inicio:.1f}s", flush=True)


def main() -> None:
    passo("1. Download da base", [PY, "ingestion/download_data.py"])
    passo("2. Carga raw (CSV -> DuckDB)", [PY, "ingestion/load_raw.py"])
    if not (ROOT / "data" / "excel" / "metas_vendas.xlsx").exists():
        passo("3. Geração da planilha de metas", [PY, "ingestion/create_targets_excel.py"])
    passo("4. Carga do Excel de metas", [PY, "ingestion/load_excel.py"])
    passo("5. dbt build (modelos + testes)", [str(DBT), "build", "--profiles-dir", "."], cwd=ROOT / "transform")
    passo("6. Exportação para Excel", [PY, "export/export_excel.py"])
    passo("7. Exportação para Parquet (Power BI)", [PY, "export/export_parquet.py"])
    print("\nPipeline concluído.")


if __name__ == "__main__":
    main()
