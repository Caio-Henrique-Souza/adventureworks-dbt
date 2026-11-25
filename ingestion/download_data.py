"""
Baixa a base Adventure Works (OLTP, em CSV) do repositório oficial da Microsoft
e extrai em data/raw.

Fonte: https://github.com/microsoft/sql-server-samples/releases/tag/adventureworks

Uso:
    python ingestion/download_data.py           # baixa só se ainda não existir
    python ingestion/download_data.py --force   # baixa de novo
"""
from __future__ import annotations

import sys
import urllib.request
import zipfile
from pathlib import Path

URL = ("https://github.com/microsoft/sql-server-samples/releases/download/"
       "adventureworks/AdventureWorks-oltp-install-script.zip")

ROOT = Path(__file__).resolve().parents[1]
DOWNLOAD_DIR = ROOT / "data" / "_download"
RAW_DIR = ROOT / "data" / "raw"
ZIP_PATH = DOWNLOAD_DIR / "AdventureWorks-oltp-install-script.zip"


def main() -> int:
    force = "--force" in sys.argv
    if (RAW_DIR / "instawdb.sql").exists() and not force:
        print(f"Base já extraída em {RAW_DIR} (use --force para baixar de novo).")
        return 0

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    if not ZIP_PATH.exists() or force:
        print(f"Baixando {URL} ...")
        urllib.request.urlretrieve(URL, ZIP_PATH)
    print(f"Arquivo: {ZIP_PATH.name} ({ZIP_PATH.stat().st_size / 1_048_576:.1f} MB)")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH) as z:
        for member in z.namelist():  # evita caminhos fora da pasta de destino
            destino = (RAW_DIR / member).resolve()
            if not str(destino).startswith(str(RAW_DIR.resolve())):
                raise RuntimeError(f"Caminho suspeito no zip: {member}")
        z.extractall(RAW_DIR)
    print(f"{len(list(RAW_DIR.glob('*.csv')))} CSVs extraídos em {RAW_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
