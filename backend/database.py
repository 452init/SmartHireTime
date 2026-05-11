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
