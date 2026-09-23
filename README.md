# Student Performance Analyzer

A Flask application for managing student records, viewing academic analytics, and exploring performance predictions.

## Database Setup

### Local development

If `DATABASE_URL` is not set, the application uses the existing `students.db` file beside `app.py`. On startup, it creates the database and `students` table if they do not exist. The SQLite database is ignored by Git and is not modified by the SQLite-to-PostgreSQL migration script.

To run locally on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in a browser. When a PostgreSQL `DATABASE_URL` is set in the environment, the application uses PostgreSQL instead of the SQLite fallback.

### PostgreSQL and Render

The application reads the `DATABASE_URL` environment variable for PostgreSQL. It supports PostgreSQL connection strings beginning with either `postgres://` or `postgresql://`. Credentials are not stored in the source code. On Render, startup fails clearly if `DATABASE_URL` is missing, so the service cannot silently fall back to ephemeral SQLite storage.

1. Create a Render PostgreSQL database.
2. In the Render web service's Environment settings, set `DATABASE_URL` to the database's internal connection URL. Use the internal URL when the web service and database are in the same Render region.
3. Keep the connection URL in Render's environment settings; do not commit it to Git.
4. Use `gunicorn app:app` as the web service start command.

On import, the Flask app safely runs `CREATE TABLE IF NOT EXISTS`. It does not drop, recreate, or migrate tables. On a fresh PostgreSQL database, this creates the existing `students` table automatically.

### Back up and migrate existing SQLite records

Back up the local database before migration. In PowerShell:

```powershell
Copy-Item .\students.db .\students.backup.db
```

On macOS or Linux:

```sh
cp students.db students.backup.db
```

Set `DATABASE_URL` in your shell to the target PostgreSQL connection URL, then run the explicit migration command from the project directory:

```powershell
python migrate_sqlite_to_postgres.py
```

The script opens `students.db` in read-only mode, creates the PostgreSQL table if needed, and copies records while preserving IDs. If an ID already exists in PostgreSQL, that source row is skipped rather than overwriting the existing record. The script reports inserted and skipped counts. It never runs automatically when the Flask app starts.

### PostgreSQL environment variable

For local PostgreSQL development, set `DATABASE_URL` in your shell or development environment before starting the application. If the variable is absent, local development continues to use SQLite. Do not place real connection credentials in this README, `.env` files committed to Git, or application code.
