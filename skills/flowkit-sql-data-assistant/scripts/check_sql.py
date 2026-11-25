"""Lokalna kontrola bezpieczeństwa skryptu SQL. Skrypt nie łączy się z bazą.

Użycie: python check_sql.py skrypt.sql
Kody wyjścia: 0 = brak błędów, 1 = wykryto błędy, 2 = nie można odczytać pliku.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DIALECTS = {
    "postgresql": "postgresql", "postgres": "postgresql", "sql server": "sqlserver", "mssql": "sqlserver",
    "t-sql": "sqlserver", "oracle": "oracle", "mysql": "mysql", "mariadb": "mysql",
}
TRANSACTION = {
    "postgresql": r"^\s*(BEGIN\s*;|START\s+TRANSACTION\b)",
    "sqlserver": r"\bBEGIN\s+TRAN(SACTION)?\b",
    "mysql": r"\bSTART\s+TRANSACTION\b",
    "oracle": r"\bBEGIN\b",
}
ROW_COUNT = {
    "postgresql": r"\bGET\s+DIAGNOSTICS\b[^;]*\bROW_COUNT\b",
    "sqlserver": r"@@ROWCOUNT",
    "mysql": r"\bROW_COUNT\s*\(\s*\)",
    "oracle": r"\bSQL%ROWCOUNT\b",
}
VARIABLES = {
    "postgresql": r"\bCREATE\s+TEMP(ORARY)?\s+TABLE\b|\bDECLARE\b",
    "sqlserver": r"\bDECLARE\s+@",
    "mysql": r"\bSET\s+@",
    "oracle": r"\bDECLARE\b",
}
AGGREGATION_OR_LIMIT = (
    r"\b(TOP\s*\(?\s*\d|LIMIT\s+\d|FETCH\s+FIRST|ROWNUM|GROUP\s+BY"
    r"|(COUNT|COUNT_BIG|SUM|AVG|MIN|MAX|PERCENTILE_CONT|PERCENTILE_DISC)\s*\()"
)
FORBIDDEN = (
    (r"\b(DROP|TRUNCATE|ALTER|GRANT|REVOKE|SHUTDOWN|BACKUP|RESTORE)\b", "zmiana struktury lub uprawnień jest zabroniona"),
    (r"\bCREATE\b(?!\s+(LOCAL\s+)?TEMP(ORARY)?\b)(?!\s+TABLE\s+#)", "tworzenie obiektów jest zabronione"),
    (r"\bEXEC(UTE)?\b|\bxp_cmdshell\b|\bsp_executesql\b", "dynamiczny SQL i uruchamianie procedur są zabronione"),
    (r"\bMERGE\b", "MERGE może nadpisać dane"),
    (r"\bREPLACE\s+INTO\b", "REPLACE INTO nadpisuje dane"),
    (r"\bON\s+DUPLICATE\s+KEY\b", "ON DUPLICATE KEY UPDATE nadpisuje dane"),
    (r"\bON\s+CONFLICT\b[^;]*\bDO\s+UPDATE\b", "ON CONFLICT DO UPDATE nadpisuje dane"),
    (r"\bINSERT\s+IGNORE\b", "INSERT IGNORE ukrywa błędy"),
    (r"\bINTO\s+(OUTFILE|DUMPFILE)\b", "zapis do pliku jest zabroniony"),
    (r"\bSELECT\s+(DISTINCT\s+)?(TOP\s*\(?\d+\)?\s+)?\*", "użyj konkretnych kolumn zamiast SELECT *"),
    (r"\bCOMMIT\b", "COMMIT musi pozostać komentarzem"),
)


def mask(sql: str) -> str:
    """Usuwa komentarze i treść tekstów, aby kontrolować tylko aktywny kod."""
    out, i, size = [], 0, len(sql)
    while i < size:
        pair = sql[i:i + 2]
        if pair == "--":
            end = sql.find("\n", i)
            i = size if end < 0 else end
        elif pair == "/*":
            end = sql.find("*/", i + 2)
            i = size if end < 0 else end + 2
            out.append(" ")
        elif sql[i] == "'":
            i += 1
            while i < size:
                if sql[i] == "'" and sql[i:i + 2] != "''":
                    i += 1
                    break
                i += 2 if sql[i:i + 2] == "''" else 1
            out.append("''")
        else:
            out.append(sql[i])
            i += 1
    return "".join(out)


def statements(code: str, pattern: str) -> list[str]:
    return [code[m.start():(code.find(";", m.start()) + 1 or len(code))]
            for m in re.finditer(pattern, code, re.IGNORECASE)]


def check(sql: str) -> list[str]:
    errors: list[str] = []
    header = re.search(r"^\s*--\s*Baza:\s*(.+?)\s*$", sql, re.IGNORECASE | re.MULTILINE)
    dialect = DIALECTS.get(re.sub(r"\s+\d.*$", "", header.group(1)).casefold()) if header else None
    if dialect is None:
        errors.append("brak wiersza '-- Baza: <typ>' z obsługiwanym typem bazy")
    # ON COMMIT DROP dotyczy wyłącznie tabeli tymczasowej z parametrami.
    code = re.sub(r"\bON\s+COMMIT\s+(DROP|DELETE\s+ROWS|PRESERVE\s+ROWS)\b", " ", mask(sql), flags=re.IGNORECASE)
    for pattern, message in FORBIDDEN:
        if re.search(pattern, code, re.IGNORECASE):
            errors.append(message)

    inserts = statements(code, r"\bINSERT\s+INTO\b")
    updates = statements(code, r"\bUPDATE\s+[\w.\"`\[\]#]+(\s+(AS\s+)?\w+)?\s+SET\b")
    deletes = statements(code, r"\bDELETE\s+(FROM\s+)?[\w.\"`\[\]#]+")
    if not (inserts or updates or deletes):
        if not re.search(r"\bSELECT\b", code, re.IGNORECASE):
            errors.append("skrypt nie zawiera zapytania SELECT")
        elif not re.search(AGGREGATION_OR_LIMIT, code, re.IGNORECASE):
            errors.append("zestawienie wymaga limitu wierszy albo agregacji")
        return errors

    for statement in inserts:
        if not re.search(r"\bNOT\s+EXISTS\b|\bON\s+CONFLICT\b[^;]*\bDO\s+NOTHING\b", statement, re.IGNORECASE):
            errors.append("INSERT wymaga warunku NOT EXISTS albo ON CONFLICT DO NOTHING")
    for statement in updates + deletes:
        where = re.search(r"\bWHERE\b(.*)", statement, re.IGNORECASE | re.DOTALL)
        if not where:
            errors.append("UPDATE i DELETE wymagają warunku WHERE")
        elif re.match(r"\s*(1\s*=\s*1|TRUE|'' *= *'')\s*;?\s*$", where.group(1), re.IGNORECASE):
            errors.append("warunek WHERE nie może obejmować wszystkich wierszy")

    if dialect:
        if not re.search(TRANSACTION[dialect], code, re.IGNORECASE | re.MULTILINE):
            errors.append("zmiana danych musi działać w transakcji")
        if not re.search(ROW_COUNT[dialect], code, re.IGNORECASE):
            errors.append("skrypt musi sprawdzać liczbę zmienionych wierszy")
        if not re.search(VARIABLES[dialect], code, re.IGNORECASE):
            errors.append("wartości muszą być podane w zmiennych")
        if dialect == "sqlserver" and not re.search(r"\bSET\s+XACT_ABORT\s+ON\b", code, re.IGNORECASE):
            errors.append("SQL Server wymaga SET XACT_ABORT ON")
    without_changes = code
    for statement in inserts:
        without_changes = without_changes.replace(statement, " ")
    if not re.search(r"\bSELECT\b", without_changes, re.IGNORECASE):
        errors.append("skrypt musi zawierać sprawdzenie wyniku przez SELECT")
    if not re.search(r"\bROLLBACK\b", code, re.IGNORECASE):
        errors.append("skrypt musi domyślnie kończyć się ROLLBACK")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("script", type=Path)
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        sql = args.script.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as error:
        print(f"BŁĄD: nie można odczytać pliku: {error}")
        return 2
    errors = check(sql)
    for error in errors:
        print(f"BŁĄD: {error}")
    print("OK: skrypt spełnia zasady bezpieczeństwa" if not errors else f"Znaleziono błędów: {len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
