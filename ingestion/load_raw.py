"""
Carrega os CSVs da Adventure Works (OLTP) no DuckDB, camada raw.

Os CSVs da Microsoft não têm cabeçalho e usam dois formatos:
  - tabulação + quebra de linha (maioria);
  - '+|' entre campos e '&|' + quebra de linha entre registros (tabelas com XML/texto livre).
Os nomes das colunas e os delimitadores são lidos do script oficial instawdb.sql.

Tudo é gravado como texto (VARCHAR). Tipos e regras de negócio ficam no dbt (staging).

Uso:
    python ingestion/load_raw.py
"""
from __future__ import annotations

import re
import sys
import time
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
SQL_SCRIPT = RAW_DIR / "instawdb.sql"
DB_PATH = ROOT / "data" / "warehouse.duckdb"

RE_CREATE = re.compile(r"CREATE TABLE \[(\w+)\]\.\[(\w+)\]\s*\((.*?)\n\)\s*ON", re.S)
RE_COLUMN = re.compile(r"^\s*\[(\w+)\]\s+(\S.*)$")
RE_BULK = re.compile(
    r"BULK INSERT \[(\w+)\]\.\[(\w+)\] FROM '\$\(SqlSamplesSourceDataPath\)([^']+)'\s*WITH\s*\((.*?)\)",
    re.S,
)
RE_OPTION = re.compile(r"(\w+)\s*=\s*'([^']*)'")


def unescape(term: str) -> str:
    """Converte os terminadores do BULK INSERT ('\\t', '0x0a', '&|\\n') em texto real."""
    if term.lower().startswith("0x"):
        return bytes.fromhex(term[2:]).decode()
    return term.replace("\\t", "\t").replace("\\n", "\n")


def parse_script(sql: str) -> list[dict]:
    """Devolve, para cada tabela, o arquivo, os delimitadores e as colunas presentes no CSV."""
    columns: dict[tuple[str, str], tuple[list[str], list[str]]] = {}
    for schema, table, body in RE_CREATE.findall(sql):
        todas, fisicas = [], []
        for line in body.splitlines():
            m = RE_COLUMN.match(line)
            if not m:
                continue  # CONSTRAINT, linhas em branco etc.
            name, rest = m.groups()
            todas.append(name)
            if not re.match(r"AS\b", rest, re.I):
                fisicas.append(name)  # colunas calculadas (AS ...) podem ou não vir no CSV
        columns[(schema, table)] = (todas, fisicas)

    tables = []
    for schema, table, file_name, options in RE_BULK.findall(sql):
        opts = {k.upper(): v for k, v in RE_OPTION.findall(options)}
        tables.append({
            "schema": schema,
            "table": table,
            "file": file_name,
            "field_sep": unescape(opts.get("FIELDTERMINATOR", "\\t")),
            "row_sep": unescape(opts.get("ROWTERMINATOR", "\\n")),
            "columns_all": columns[(schema, table)][0],
            "columns_physical": columns[(schema, table)][1],
        })
    return tables


def read_file(path: Path) -> str:
    data = path.read_bytes()
    if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
        return data.decode("utf-16")
    return data.decode("utf-8-sig")


def split_rows(text: str, row_sep: str) -> list[str]:
    rows = text.replace("\r\n", "\n").split(row_sep)
    if rows and rows[-1].strip() == "":
        rows.pop()
    return rows


def parse_rows(rows: list[str], field_sep: str, row_sep: str, n_cols: int, name: str) -> list[list[str | None]]:
    """Separa os campos. Se um texto livre tiver quebra de linha dentro, junta as linhas
    até completar o número de campos esperado."""
    parsed = []
    buffer = None
    for i, row in enumerate(rows, 1):
        buffer = row if buffer is None else buffer + row_sep + row
        fields = buffer.split(field_sep)
        if len(fields) < n_cols:
            continue
        if len(fields) > n_cols:
            raise ValueError(f"{name}: registro até a linha {i} tem {len(fields)} campos, esperado {n_cols}")
        parsed.append([f if f != "" else None for f in fields])
        buffer = None
    if buffer is not None:
        raise ValueError(f"{name}: último registro incompleto")
    return parsed


def parse_table(linhas: list[str], t: dict) -> tuple[list[str], list[list[str | None]]]:
    """Tenta sem as colunas calculadas e, se não bater, com elas (alguns CSVs trazem o valor)."""
    erros = []
    for cols in (t["columns_physical"], t["columns_all"]):
        try:
            return cols, parse_rows(linhas, t["field_sep"], t["row_sep"], len(cols), t["file"])
        except ValueError as e:
            erros.append(str(e))
    raise ValueError(" | ".join(erros))


def main() -> int:
    if not SQL_SCRIPT.exists():
        print(f"Script não encontrado: {SQL_SCRIPT}\nRode antes: python ingestion/download_data.py")
        return 1

    tables = parse_script(read_file(SQL_SCRIPT))
    con = duckdb.connect(str(DB_PATH))
    inicio = time.time()
    total = 0
    for t in tables:
        schema = f"raw_{t['schema'].lower()}"
        con.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')
        linhas = split_rows(read_file(RAW_DIR / t["file"]), t["row_sep"])
        cols, rows = parse_table(linhas, t)
        df = pd.DataFrame(rows, columns=cols, dtype="string")
        df["_loaded_at"] = pd.Timestamp.now(tz="UTC").isoformat()
        con.register("df_carga", df)
        con.execute(f'CREATE OR REPLACE TABLE "{schema}"."{t["table"]}" AS SELECT * FROM df_carga')
        con.unregister("df_carga")
        total += len(df)
        print(f"  {schema}.{t['table']:<38} {len(df):>8,} linhas")
    con.close()
    print(f"\n{len(tables)} tabelas, {total:,} linhas carregadas em {time.time() - inicio:.1f}s -> {DB_PATH.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
