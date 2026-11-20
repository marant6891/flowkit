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

SAFE_INSERT = """-- Baza: SQL Server
SET XACT_ABORT ON;
DECLARE @Id int = 1;
DECLARE @Oczekiwane int = 1;
SELECT t.id FROM dbo.t AS t WHERE t.id = @Id;
BEGIN TRANSACTION;
INSERT INTO dbo.t (id) SELECT @Id WHERE NOT EXISTS (SELECT 1 FROM dbo.t AS x WHERE x.id = @Id);
IF @@ROWCOUNT <> @Oczekiwane BEGIN ROLLBACK TRANSACTION; THROW 50001, 'x', 1; END;
SELECT t.id FROM dbo.t AS t WHERE t.id = @Id;
ROLLBACK TRANSACTION;
-- COMMIT TRANSACTION;
"""


class TestSafetyChecker(unittest.TestCase):

    def assert_rejected(self, sql, text):
        errors = check_sql.check(sql)
        self.assertTrue(any(text in e for e in errors), errors)

    def test_all_templates_pass(self):
        templates = (SKILL / "templates" / "safe-write-templates.md").read_text(encoding="utf-8")
        blocks = re.findall(r"```sql\n(.*?)```", templates, re.S)
        self.assertEqual(len(blocks), 8)
        for block in blocks:
            self.assertEqual(check_sql.check(block), [], block[:40])

    def test_each_database_type_is_covered(self):
        templates = (SKILL / "templates" / "safe-write-templates.md").read_text(encoding="utf-8")
        for database in ("PostgreSQL", "SQL Server", "Oracle", "MySQL"):
            self.assertEqual(templates.count(f"-- Baza: {database}"), 2, database)

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


class TestSqlIntegration(unittest.TestCase):

    def test_agents_can_check_but_never_connect_to_database(self):
        script = "C:/x/flowkit-sql-data-assistant/scripts/check_sql.py"
        self.assertIsNone(fx.check("orchestrator", ["python", script, "a.sql"]))
        self.assertIsNone(fx.check("analyst", ["python", script, "a.sql"]))
        self.assertIsNotNone(fx.check("verifier", ["python", script, "a.sql"]))
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
