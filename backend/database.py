import json

import psycopg


class MissingDatabaseUrlError(Exception):
    pass


def initialize_database(database_url):
    if not database_url:
        raise MissingDatabaseUrlError(
            "Missing DATABASE_URL. Add a PostgreSQL connection string to your .env file."
        )

    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS interview_question_sets (
                    id SERIAL PRIMARY KEY,
                    job_title TEXT NOT NULL,
                    questions JSONB NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    password_hash TEXT,
                    google_sub TEXT,
                    profile_image_url TEXT,
                    profile_image_public_id TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                """
            )
            cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_image_url TEXT;")
            cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_image_public_id TEXT;")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS auth_codes (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    sent_to TEXT NOT NULL,
                    code_hash TEXT NOT NULL,
                    expires_at TIMESTAMPTZ NOT NULL,
                    consumed_at TIMESTAMPTZ
                );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS refresh_tokens (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    token_hash TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    expires_at TIMESTAMPTZ NOT NULL,
                    revoked_at TIMESTAMPTZ,
                    replaced_by INTEGER REFERENCES refresh_tokens(id)
                );
                """
            )


def save_question_set(database_url, job_title, questions):
    if not database_url:
        raise MissingDatabaseUrlError(
            "Missing DATABASE_URL. Add a PostgreSQL connection string to your .env file."
        )

    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO interview_question_sets (job_title, questions)
                VALUES (%s, %s::jsonb)
                RETURNING id;
                """,
                (job_title, json.dumps(questions)),
            )
            row = cursor.fetchone()

    return row[0]


def get_user_by_email(database_url, email):
    if not database_url:
        raise MissingDatabaseUrlError(
            "Missing DATABASE_URL. Add a PostgreSQL connection string to your .env file."
        )

    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, email, first_name, last_name, password_hash, google_sub, profile_image_url, profile_image_public_id
                FROM users
                WHERE email = %s;
                """,
                (email,),
            )
            row = cursor.fetchone()

    return _user_row_to_dict(row)


def get_user_by_id(database_url, user_id):
    if not database_url:
        raise MissingDatabaseUrlError(
            "Missing DATABASE_URL. Add a PostgreSQL connection string to your .env file."
        )

    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, email, first_name, last_name, password_hash, google_sub, profile_image_url, profile_image_public_id
                FROM users
                WHERE id = %s;
                """,
                (user_id,),
            )
            row = cursor.fetchone()

    return _user_row_to_dict(row)


def create_user(database_url, first_name, last_name, email, password_hash=None, google_sub=None):
    if not database_url:
        raise MissingDatabaseUrlError(
            "Missing DATABASE_URL. Add a PostgreSQL connection string to your .env file."
        )

    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (email, first_name, last_name, password_hash, google_sub)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, email, first_name, last_name, password_hash, google_sub, profile_image_url, profile_image_public_id;
                """,
                (email, first_name, last_name, password_hash, google_sub),
            )
            row = cursor.fetchone()

    return _user_row_to_dict(row)


def set_user_google_sub(database_url, user_id, google_sub):
    if not database_url:
        raise MissingDatabaseUrlError(
            "Missing DATABASE_URL. Add a PostgreSQL connection string to your .env file."
        )

    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE users
                SET google_sub = %s
                WHERE id = %s
                RETURNING id, email, first_name, last_name, password_hash, google_sub, profile_image_url, profile_image_public_id;
                """,
                (google_sub, user_id),
            )
            row = cursor.fetchone()

    return _user_row_to_dict(row)


def update_user_profile_image(database_url, user_id, image_url, image_public_id):
    if not database_url:
        raise MissingDatabaseUrlError(
            "Missing DATABASE_URL. Add a PostgreSQL connection string to your .env file."
        )

    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE users
                SET profile_image_url = %s, profile_image_public_id = %s
                WHERE id = %s
                RETURNING id, email, first_name, last_name, password_hash, google_sub, profile_image_url, profile_image_public_id;
                """,
                (image_url, image_public_id, user_id),
            )
            row = cursor.fetchone()

    return _user_row_to_dict(row)


def clear_user_profile_image(database_url, user_id):
    if not database_url:
        raise MissingDatabaseUrlError(
            "Missing DATABASE_URL. Add a PostgreSQL connection string to your .env file."
        )

    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE users
                SET profile_image_url = NULL, profile_image_public_id = NULL
                WHERE id = %s
                RETURNING id, email, first_name, last_name, password_hash, google_sub, profile_image_url, profile_image_public_id;
                """,
                (user_id,),
            )
            row = cursor.fetchone()

    return _user_row_to_dict(row)


def update_user_password_hash(database_url, user_id, password_hash):
    if not database_url:
        raise MissingDatabaseUrlError(
            "Missing DATABASE_URL. Add a PostgreSQL connection string to your .env file."
        )

    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE users
                SET password_hash = %s
                WHERE id = %s
                RETURNING id, email, first_name, last_name, password_hash, google_sub, profile_image_url, profile_image_public_id;
                """,
                (password_hash, user_id),
            )
            row = cursor.fetchone()

    return _user_row_to_dict(row)


def create_auth_code(database_url, user_id, sent_to, code_hash, expires_at):
    if not database_url:
        raise MissingDatabaseUrlError(
            "Missing DATABASE_URL. Add a PostgreSQL connection string to your .env file."
        )

    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO auth_codes (user_id, sent_to, code_hash, expires_at)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """,
                (user_id, sent_to, code_hash, expires_at),
            )
            row = cursor.fetchone()

    return row[0]


def consume_auth_code(database_url, user_id, code_hash, now):
    if not database_url:
        raise MissingDatabaseUrlError(
            "Missing DATABASE_URL. Add a PostgreSQL connection string to your .env file."
        )

    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE auth_codes
                SET consumed_at = %s
                WHERE id = (
                    SELECT id
                    FROM auth_codes
                    WHERE user_id = %s
                      AND code_hash = %s
                      AND consumed_at IS NULL
                      AND expires_at > %s
                    ORDER BY id DESC
                    LIMIT 1
                )
                RETURNING id;
                """,
                (now, user_id, code_hash, now),
            )
            row = cursor.fetchone()

    return row is not None


def create_refresh_token(database_url, user_id, token_hash, expires_at):
    if not database_url:
        raise MissingDatabaseUrlError(
            "Missing DATABASE_URL. Add a PostgreSQL connection string to your .env file."
        )

    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (user_id, token_hash, expires_at),
            )
            row = cursor.fetchone()

    return row[0]


def get_refresh_token_by_hash(database_url, token_hash):
    if not database_url:
        raise MissingDatabaseUrlError(
            "Missing DATABASE_URL. Add a PostgreSQL connection string to your .env file."
        )

    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, user_id, expires_at, revoked_at
                FROM refresh_tokens
                WHERE token_hash = %s;
                """,
                (token_hash,),
            )
            row = cursor.fetchone()

    if not row:
        return None

    return {
        "id": row[0],
        "user_id": row[1],
        "expires_at": row[2],
        "revoked_at": row[3],
    }


def revoke_refresh_token(database_url, token_id, revoked_at, replaced_by=None):
    if not database_url:
        raise MissingDatabaseUrlError(
            "Missing DATABASE_URL. Add a PostgreSQL connection string to your .env file."
        )

    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE refresh_tokens
                SET revoked_at = %s, replaced_by = %s
                WHERE id = %s;
                """,
                (revoked_at, replaced_by, token_id),
            )


def _user_row_to_dict(row):
    if not row:
        return None

    return {
        "id": row[0],
        "email": row[1],
        "first_name": row[2],
        "last_name": row[3],
        "password_hash": row[4],
        "google_sub": row[5],
        "profile_image_url": row[6],
        "profile_image_public_id": row[7],
    }
