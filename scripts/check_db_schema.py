import sys
from pathlib import Path

from sqlalchemy import inspect


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db.session import engine


EXPECTED_TABLES = {
    "users",
    "sessions",
    "vehicles",
    "manuals",
    "manual_chunks",
    "query_logs",
    "eval_questions",
    "eval_runs",
    "eval_results",
}


def main() -> int:
    tables = set(inspect(engine).get_table_names())
    missing = EXPECTED_TABLES - tables

    print("Found tables:")
    for table in sorted(tables & EXPECTED_TABLES):
        print(f"- {table}")

    if missing:
        print("Missing expected tables:", ", ".join(sorted(missing)), file=sys.stderr)
        return 1

    print("All expected database tables exist.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
