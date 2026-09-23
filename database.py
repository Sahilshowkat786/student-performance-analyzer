"""Database configuration and connection helpers for SQLite and PostgreSQL."""

import logging
import os
import re
import sqlite3
from pathlib import Path


APP_DIRECTORY = Path(__file__).resolve().parent
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql://" + DATABASE_URL[len("postgres://"):]

USE_POSTGRES = bool(DATABASE_URL)
SQLITE_DATABASE = APP_DIRECTORY / "students.db"

STUDENT_COLUMNS = (
    "id", "name", "roll", "email", "age", "attendance", "study_hours",
    "assignment", "previous_marks", "python", "dsa", "dbms", "web",
    "total", "average", "percentage", "grade", "result"
)

logger = logging.getLogger("student_analyzer.database")


class DatabaseError(RuntimeError):
    """A sanitized database error safe to show through the app's error handler."""


class DatabaseCursor:
    """Wrap result reads so driver errors use the same safe error handling."""

    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.connection = connection

    def fetchone(self):
        try:
            return self.cursor.fetchone()
        except Exception as error:
            if self.connection.is_database_error(error):
                raise DatabaseError(_safe_error_message(error)) from None
            raise

    def fetchall(self):
        try:
            return self.cursor.fetchall()
        except Exception as error:
            if self.connection.is_database_error(error):
                raise DatabaseError(_safe_error_message(error)) from None
            raise


def _safe_error_message(error):
    message = str(error)
    for secret in (DATABASE_URL, os.environ.get("DATABASE_URL", "")):
        if secret:
            message = message.replace(secret, "[redacted DATABASE_URL]")
    message = re.sub(
        r"(?i)(postgres(?:ql)?://)[^/\s@]+@",
        r"\1[redacted]@",
        message
    )
    message = re.sub(
        r"(?i)(password\s*=\s*)(?:'[^']*'|\"[^\"]*\"|\S+)",
        r"\1[redacted]",
        message
    )
    return message or type(error).__name__


class DatabaseConnection:
    """Expose consistent execute, commit, and close methods for both drivers."""

    def __init__(self, raw_connection, postgres=False, driver=None):
        self.raw_connection = raw_connection
        self.postgres = postgres
        self.driver = driver
        self.closed = False

    def is_database_error(self, error):
        return isinstance(error, sqlite3.Error) or (
            self.postgres and self.driver and isinstance(error, self.driver.Error)
        )

    def execute(self, statement, parameters=None):
        parameters = () if parameters is None else parameters
        try:
            if self.postgres:
                from psycopg.rows import dict_row

                cursor = self.raw_connection.cursor(row_factory=dict_row)
                cursor.execute(statement, parameters)
                return DatabaseCursor(cursor, self)

            sqlite_statement = statement.replace("%s", "?")
            cursor = self.raw_connection.execute(sqlite_statement, parameters)
            return DatabaseCursor(cursor, self)
        except sqlite3.Error as error:
            raise DatabaseError(_safe_error_message(error)) from None
        except Exception as error:
            if self.postgres and self.driver and isinstance(error, self.driver.Error):
                raise DatabaseError(_safe_error_message(error)) from None
            raise

    def commit(self):
        try:
            self.raw_connection.commit()
        except sqlite3.Error as error:
            raise DatabaseError(_safe_error_message(error)) from None
        except Exception as error:
            if self.postgres and self.driver and isinstance(error, self.driver.Error):
                raise DatabaseError(_safe_error_message(error)) from None
            raise

    def close(self):
        if not self.closed:
            self.raw_connection.close()
            self.closed = True


def get_db_connection():
    """Open a fresh connection using DATABASE_URL or the local SQLite file."""
    if USE_POSTGRES:
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError:
            raise DatabaseError(
                "PostgreSQL is configured, but the psycopg driver is not installed."
            ) from None

        try:
            connection = psycopg.connect(
                DATABASE_URL,
                row_factory=dict_row,
                connect_timeout=10
            )
        except psycopg.Error as error:
            message = _safe_error_message(error)
            raise DatabaseError(message) from None

        return DatabaseConnection(connection, postgres=True, driver=psycopg)

    if os.environ.get("RENDER", "").lower() == "true":
        raise DatabaseError(
            "DATABASE_URL must be configured on Render; SQLite is only the local fallback."
        )

    try:
        SQLITE_DATABASE.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(str(SQLITE_DATABASE))
        connection.row_factory = sqlite3.Row
        return DatabaseConnection(connection)
    except sqlite3.Error as error:
        raise DatabaseError(_safe_error_message(error)) from None


def _create_students_table(connection):
    if USE_POSTGRES:
        statement = """
            CREATE TABLE IF NOT EXISTS students (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                roll TEXT NOT NULL,
                email TEXT NOT NULL,
                age INTEGER NOT NULL,
                attendance DOUBLE PRECISION NOT NULL,
                study_hours DOUBLE PRECISION NOT NULL,
                assignment DOUBLE PRECISION NOT NULL,
                previous_marks DOUBLE PRECISION NOT NULL,
                python DOUBLE PRECISION NOT NULL,
                dsa DOUBLE PRECISION NOT NULL,
                dbms DOUBLE PRECISION NOT NULL,
                web DOUBLE PRECISION NOT NULL,
                total DOUBLE PRECISION NOT NULL,
                average DOUBLE PRECISION NOT NULL,
                percentage DOUBLE PRECISION NOT NULL,
                grade TEXT NOT NULL,
                result TEXT NOT NULL
            )
        """
    else:
        statement = """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roll TEXT NOT NULL,
                email TEXT NOT NULL,
                age INTEGER NOT NULL,
                attendance REAL NOT NULL,
                study_hours REAL NOT NULL,
                assignment REAL NOT NULL,
                previous_marks REAL NOT NULL,
                python REAL NOT NULL,
                dsa REAL NOT NULL,
                dbms REAL NOT NULL,
                web REAL NOT NULL,
                total REAL NOT NULL,
                average REAL NOT NULL,
                percentage REAL NOT NULL,
                grade TEXT NOT NULL,
                result TEXT NOT NULL
            )
        """

    connection.execute(statement)


def create_database():
    """Create the existing students table if it does not already exist."""
    connection = get_db_connection()
    try:
        _create_students_table(connection)
        connection.commit()
    except DatabaseError as error:
        logger.error("Database initialization failed: %s", error)
        raise
    finally:
        connection.close()
