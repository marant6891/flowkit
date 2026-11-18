"""Główny runner walidacji FlowKit.
Uruchamia walidację skilli, agentów, manifestów wtyczki oraz testy jednostkowe.
Uruchom: python scripts/validate_all.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"

SCRIPTS = [
    ("validate_skills.py", "Walidacja skilli i katalogu README"),
    ("validate_agents.py", "Walidacja definicji agentów i adapterów"),
    ("validate_manifest.py", "Walidacja manifestów Claude Plugin"),
]


def run_check(script_name: str, desc: str) -> bool:
    print(f"\n--- {desc} ({script_name}) ---")
    script_path = SCRIPTS_DIR / script_name
    res = subprocess.run([sys.executable, str(script_path)], capture_output=False)
    return res.returncode == 0


def run_unit_tests() -> bool:
    print("\n--- Testy jednostkowe kontraktów i integracji (tests/) ---")
    passed = True
    for name in ("test_flowkit.py", "test_diagrams.py"):
        res = subprocess.run([sys.executable, "-m", "unittest", str(ROOT / "tests" / name)], capture_output=False)
        passed = passed and res.returncode == 0
    return passed


def main() -> int:
    print("=== FlowKit Comprehensive Validation Suite ===")
    failed = []
    for script_name, desc in SCRIPTS:
        if not run_check(script_name, desc):
            failed.append(script_name)

    if not run_unit_tests():
        failed.append("tests/")

    print("\n" + "=" * 46)
    if failed:
        print(f"Validation FAILED in: {', '.join(failed)}")
        return 1
    print("All validations & tests PASSED! Repository is healthy and compliant.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
