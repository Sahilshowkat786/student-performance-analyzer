"""Explicitly copy local SQLite student records into the configured PostgreSQL DB."""

import sqlite3
import sys
from pathlib import Path

from database import (
    DATABASE_URL,
    DatabaseError,
    STUDENT_COLUMNS,
    create_database,
    get_db_connection,
)


def migrate():
    if not DATABASE_URL:
        raise DatabaseError(
            "Set DATABASE_URL to the target PostgreSQL database before running this script."
        )

    sqlite_path = Path(__file__).resolve().with_name("students.db")
    if not sqlite_path.is_file():
        raise FileNotFoundError(f"SQLite source database was not found: {sqlite_path}")

    # Open the source in read-only mode so migration cannot modify the local file.
    source_connection = sqlite3.connect(
        sqlite_path.as_uri() + "?mode=ro",
        uri=True
    )
    source_connection.row_factory = sqlite3.Row
    postgres_connection = None

    try:
        rows = source_connection.execute(
            "SELECT " + ", ".join(STUDENT_COLUMNS) + " FROM students ORDER BY id"
        ).fetchall()

        create_database()
        postgres_connection = get_db_connection()

        column_sql = ", ".join(STUDENT_COLUMNS)
        placeholders = ", ".join(["%s"] * len(STUDENT_COLUMNS))
        insert_sql = (
            f"INSERT INTO students ({column_sql}) VALUES ({placeholders}) "
            "ON CONFLICT (id) DO NOTHING RETURNING id"
        )

        inserted = 0
        skipped = 0
        for row in rows:
            cursor = postgres_connection.execute(
                insert_sql,
                tuple(row[column] for column in STUDENT_COLUMNS)
            )
            if cursor.fetchone() is None:
                skipped += 1
            else:
                inserted += 1

        # Advance the serial sequence after explicit IDs were copied.
        postgres_connection.execute("""
            SELECT setval(
                pg_get_serial_sequence('students', 'id'),
                COALESCE((SELECT MAX(id) FROM students), 1),
                EXISTS (SELECT 1 FROM students)
            )
        """)
        postgres_connection.commit()

        print(f"SQLite records found: {len(rows)}")
        print(f"Records inserted into PostgreSQL: {inserted}")
        print(f"Records skipped because their IDs already exist: {skipped}")
    finally:
        source_connection.close()
        if postgres_connection is not None:
            postgres_connection.close()


if __name__ == "__main__":
    try:
        migrate()
    except (DatabaseError, sqlite3.Error, OSError) as error:
        print(f"Migration stopped safely: {error}", file=sys.stderr)
        raise SystemExit(1) from None
