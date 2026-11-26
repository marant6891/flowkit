"""Testy skilla flowkit-sql-data-assistant i automatycznego doboru działania orkiestratora.
Uruchom: python -m unittest tests/test_sql.py
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "flowkit-sql-data-assistant"
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(ROOT / "runtime"))

import check_sql  # noqa: E402
import flowkit_exec as fx  # noqa: E402

SAFE_INSERT = """/* ZGŁOSZENIE: T-1 */
-- Baza: SQL Server
SET XACT_ABORT ON;
DROP TABLE IF EXISTS #Plan;
BEGIN TRY
BEGIN TRANSACTION;
/* KROK 1: parametry */
DECLARE @Id int = 1;
DECLARE @Oczekiwane int = 1;
/* KROK 2: PRZED */
SELECT t.id FROM dbo.t AS t WHERE t.id = @Id;
/* KROK 3: INSERT */
INSERT INTO dbo.t (id) SELECT @Id WHERE NOT EXISTS (SELECT 1 FROM dbo.t AS x WHERE x.id = @Id);
IF @@ROWCOUNT <> @Oczekiwane THROW 50001, 'x', 1;
/* KROK 4: PO */
SELECT t.id FROM dbo.t AS t WHERE t.id = @Id;
ROLLBACK TRANSACTION;
-- COMMIT TRANSACTION;
END TRY
BEGIN CATCH
IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
THROW;
END CATCH;
DROP TABLE IF EXISTS #Plan;
"""
TEMPLATES = SKILL / "templates" / "safe-write-templates.md"


def template_blocks():
    return re.findall(r"```sql\n(.*?)```", TEMPLATES.read_text(encoding="utf-8"), re.S)


class TestSafetyChecker(unittest.TestCase):

    def assert_rejected(self, sql, text):
        errors = check_sql.check(sql)
        self.assertTrue(any(text in e for e in errors), errors)

    def test_all_templates_pass(self):
        templates = (SKILL / "templates" / "safe-write-templates.md").read_text(encoding="utf-8")
        blocks = re.findall(r"```sql\n(.*?)```", templates, re.S)
        self.assertEqual(len(blocks), 9)
        for block in blocks:
            self.assertEqual(check_sql.check(block), [], block[:40])

    def test_each_database_type_is_covered(self):
        templates = TEMPLATES.read_text(encoding="utf-8")
        for database, count in (("PostgreSQL", 2), ("SQL Server", 3), ("Oracle", 2), ("MySQL", 2)):
            self.assertEqual(templates.count(f"-- Baza: {database}"), count, database)

    def test_templates_are_wrapped(self):
        for block in template_blocks():
            name = block[:160]
            self.assertRegex(block, r"^/\* =+\n   SKRYPT:", name)
            for element in ("ZGŁOSZENIE:", "KROKI:", "ZATWIERDZENIE:", "KROK 1: parametry", "NAZWA_BAZY",
                            "PRZED", "PO - ", "ODTWORZENIE", "ROLLBACK"):
                self.assertIn(element, block, f"{element}: {name}")
            self.assertRegex(block, r"(?m)^\s*--\s*COMMIT", name)

    def test_wrapping_is_required_for_write_scripts(self):
        self.assert_rejected(SAFE_INSERT.replace("/* ZGŁOSZENIE: T-1 */\n", ""), "ZGŁOSZENIE")
        self.assert_rejected(re.sub(r"/\* KROK \d: \w+ \*/\n", "", SAFE_INSERT), "KROK")
        without_try = SAFE_INSERT.replace("BEGIN TRY\n", "").split("END TRY")[0]
        self.assert_rejected(without_try, "BEGIN TRY")
        # Zestawienie nie wymaga opakowania zmiany danych.
        self.assertEqual(check_sql.check("-- Baza: MySQL\nSELECT COUNT(*) AS liczba FROM a;\n"), [])

    def test_only_temporary_tables_can_be_dropped(self):
        self.assertEqual(check_sql.check(SAFE_INSERT), [])
        real = SAFE_INSERT.replace("DROP TABLE IF EXISTS #Plan;\nBEGIN TRY", "DROP TABLE IF EXISTS dbo.Plan;\nBEGIN TRY")
        self.assert_rejected(real, "struktury")
        self.assert_rejected("-- Baza: MySQL\nDROP TABLE plan_zmian;\nSELECT COUNT(*) AS n FROM a;\n", "struktury")

    def test_mysql_update_with_join_is_checked_as_a_write(self):
        mysql_update = next(b for b in template_blocks()
                            if "-- Baza: MySQL" in b and "UPDATE schemat.tabela AS t\nJOIN" in b)
        self.assert_rejected(mysql_update.replace("ROLLBACK;\n", ""), "ROLLBACK")

    def test_safe_script_passes(self):
        self.assertEqual(check_sql.check(SAFE_INSERT), [])

    def test_database_type_is_required(self):
        self.assert_rejected(SAFE_INSERT.replace("-- Baza: SQL Server\n", ""), "typem bazy")

    def test_insert_without_duplicate_guard_is_rejected(self):
        sql = SAFE_INSERT.replace("SELECT @Id WHERE NOT EXISTS (SELECT 1 FROM dbo.t AS x WHERE x.id = @Id)", "VALUES (@Id)")
        self.assert_rejected(sql, "NOT EXISTS")

    def test_write_without_transaction_is_rejected(self):
        self.assert_rejected(SAFE_INSERT.replace("BEGIN TRANSACTION;\n", ""), "transakcji")

    def test_active_commit_is_rejected_but_comment_is_allowed(self):
        self.assert_rejected(SAFE_INSERT.replace("-- COMMIT TRANSACTION;", "COMMIT TRANSACTION;"), "COMMIT")

    def test_row_count_and_variables_are_required(self):
        self.assert_rejected(SAFE_INSERT.replace("@@ROWCOUNT", "1"), "liczbę zmienionych")
        self.assert_rejected(SAFE_INSERT.replace("DECLARE @", "-- DECLARE @"), "zmiennych")

    def test_update_and_delete_need_safe_where(self):
        base = SAFE_INSERT.replace("INSERT INTO dbo.t (id) SELECT @Id WHERE NOT EXISTS (SELECT 1 FROM dbo.t AS x WHERE x.id = @Id);", "{}")
        self.assert_rejected(base.format("UPDATE dbo.t SET a = 1;"), "WHERE")
        self.assert_rejected(base.format("DELETE FROM dbo.t;"), "WHERE")
        self.assert_rejected(base.format("UPDATE dbo.t SET a = 1 WHERE 1=1;"), "wszystkich")

    def test_overwriting_and_destructive_statements_are_rejected(self):
        for statement, text in (("MERGE INTO a USING b ON 1=1", "MERGE"), ("DROP TABLE a", "struktury"),
                                ("TRUNCATE TABLE a", "struktury"), ("REPLACE INTO a VALUES (1)", "REPLACE"),
                                ("EXEC sp_x", "dynamiczny"),
                                ("INSERT INTO a VALUES (1) ON DUPLICATE KEY UPDATE b = 1", "DUPLICATE")):
            self.assert_rejected(f"-- Baza: MySQL\n{statement};\n", text)

    def test_text_values_do_not_trigger_false_alarms(self):
        sql = "-- Baza: PostgreSQL\nSELECT t.id, 'DROP TABLE' AS opis FROM s.t AS t LIMIT 10;\n"
        self.assertEqual(check_sql.check(sql), [])

    def test_report_needs_columns_and_limit(self):
        self.assert_rejected("-- Baza: MySQL\nSELECT * FROM a LIMIT 5;\n", "SELECT *")
        self.assert_rejected("-- Baza: MySQL\nSELECT a.id FROM a;\n", "limitu")
        self.assertEqual(check_sql.check("-- Baza: Oracle\nSELECT COUNT(*) AS liczba FROM a;\n"), [])

    def test_other_aggregates_count_as_report(self):
        for function in ("AVG", "MIN", "MAX", "COUNT_BIG"):
            sql = f"-- Baza: SQL Server\nSELECT {function}(a.kwota) AS wynik FROM dbo.a AS a;\n"
            self.assertEqual(check_sql.check(sql), [], function)


class TestAnalyticsReport(unittest.TestCase):
    PATTERNS = SKILL / "references" / "analytics-report-patterns.md"

    def blocks(self):
        return re.findall(r"```sql\n(.*?)```", self.PATTERNS.read_text(encoding="utf-8"), re.S)

    def test_all_analytics_patterns_pass_checker(self):
        blocks = self.blocks()
        self.assertGreaterEqual(len(blocks), 9)
        for block in blocks:
            self.assertEqual(check_sql.check(block), [], block[:60])

    def test_full_report_example_for_each_database(self):
        examples = [b for b in self.blocks() if "Raport: sprzedaż netto miesięcznie" in b]
        self.assertEqual(sorted(re.search(r"-- Baza: (.+)", b).group(1) for b in examples),
                         ["MySQL", "Oracle", "PostgreSQL", "SQL Server"])
        for block in examples:
            for element in ("LAG(", "NULLIF(", "LEFT JOIN", "OVER ()", "ROWS UNBOUNDED PRECEDING"):
                self.assertIn(element, block)

    def test_oracle_examples_do_not_alias_tables_with_as(self):
        for block in self.blocks():
            if "-- Baza: Oracle" in block:
                self.assertNotRegex(block, r"\b(FROM|JOIN)\s+[\w.]+\s+AS\s+\w+")

    def test_skill_documents_analytics_mode(self):
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        checklist = (SKILL / "checklists" / "sql-safety-checklist.md").read_text(encoding="utf-8")
        self.assertIn("`ANALYTICS_REPORT`", skill)
        for link in ("references/analytics-report-patterns.md", "templates/analytics-report-template.md"):
            self.assertIn(link, skill)
        self.assertIn("ANALYTICS_REPORT", checklist)
        template = (SKILL / "templates" / "analytics-report-template.md").read_text(encoding="utf-8")
        for section in ("## Karta raportu", "## Słownik miar", "## Kontrola spójności", "## Założenia i niewiadome"):
            self.assertIn(section, template)


class TestSqlIntegration(unittest.TestCase):

    def test_agents_can_check_but_never_connect_to_database(self):
        script = "C:/x/flowkit-sql-data-assistant/scripts/check_sql.py"
        self.assertIsNone(fx.check("orchestrator", ["python", script, "a.sql"]))
        self.assertIsNone(fx.check("analyst", ["python", script, "a.sql"]))
        self.assertIsNone(fx.check("verifier", ["python", script, "a.sql"]))  # kontrola w audycie, tylko odczyt
        self.assertIsNotNone(fx.check("validator", ["python", script, "a.sql"]))
        for client in ("psql", "sqlcmd", "sqlplus", "mysql", "mariadb", "sqlite3"):
            for role in fx.ROLE_COMMANDS:
                self.assertIsNotNone(fx.check(role, [client, "-c", "select 1"]), f"{role}: {client}")

    def test_orchestrator_chooses_action_without_prefix(self):
        source = (ROOT / "agents" / "flowkit-orchestrator_agent.md").read_text(encoding="utf-8")
        self.assertIn("## Automatic routing", source)
        self.assertIn("Prefixes are optional", source)
        for target in ("`flowkit-sql-data-assistant`", "Analyzer", "Diagnostics", "Analyst", "Planner"):
            self.assertIn(target, source)
        self.assertNotIn("Unknown profile → ask before starting", source)

    def test_skill_is_available_on_all_channels(self):
        self.assertIn("flowkit-sql-data-assistant", (ROOT / "scripts" / "install.sh").read_text(encoding="utf-8"))
        self.assertIn("**flowkit-sql-data-assistant**", (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn("flowkit-sql-data-assistant", (ROOT / ".github" / "copilot-instructions.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
