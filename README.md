# SmartHireTime

SmartHireTime is a simple web app that accepts a job title and returns three thoughtful AI-generated interview questions for that role. The primary example in the input is **Customer Success Manager**.

The backend uses **Flask**. The database is **PostgreSQL**. The frontend is **TypeScript**.

## What The App Does

1. The user enters a job title.
2. The TypeScript frontend sends the title to the Flask API.
3. Flask builds a role-specific AI prompt.
4. Flask calls the TinyFish Agent API.
5. Flask saves the generated question set in PostgreSQL.
6. The frontend displays the three interview questions.

## Project Structure

```text
SmartHireTime/
├── backend/
│   ├── app.py              # Flask entry point and HTTP routes
│   ├── ai_api.py           # TinyFish API request
│   ├── config.py           # Environment loading
│   ├── database.py         # PostgreSQL setup and inserts
│   └── question_builder.py # Prompt creation and response parsing
├── frontend/
│   ├── index.html          # Page markup
│   └── src/
│       ├── main.ts         # TypeScript form and API logic
│       └── styles.css      # Clean professional UI
├── .env.example            # Example environment variables
├── requirements.txt        # Flask and PostgreSQL Python dependencies
├── package.json            # Frontend build scripts
├── tsconfig.json           # TypeScript settings
├── vite.config.ts          # Frontend build config
└── README.md               # Documentation
```

## Core Layers

`backend/app.py`

This is the backend entry point. It creates the Flask app, exposes the API route, serves the built frontend, initializes PostgreSQL, and connects the helper layers together.

`backend/config.py`

Loads `.env` values:

- `TINYFISH_API_KEY`
- `DATABASE_URL`
- `PORT`

`backend/database.py`

Creates the PostgreSQL table if needed and saves each generated question set.

`backend/question_builder.py`

Builds the AI prompt and parses the AI JSON response into a clean list of questions.

`backend/ai_api.py`

Calls the TinyFish Agent API using the synchronous `/v1/automation/run` endpoint. TinyFish receives a `goal`, a `url`, an optional `output_schema`, and the API key in the `X-API-Key` header.

`frontend/src/main.ts`

Handles the browser logic. It reads the job title, calls the Flask API, and renders the returned questions.

## Simple Wiring

The backend helper files do not call each other. `backend/app.py` is the one place that hooks them together:

```text
app.py -> config.py
app.py -> question_builder.py
app.py -> ai_api.py
app.py -> database.py
```

## Database Table

When `DATABASE_URL` is set, the app creates this PostgreSQL table automatically on startup:

```sql
CREATE TABLE IF NOT EXISTS interview_question_sets (
    id SERIAL PRIMARY KEY,
    job_title TEXT NOT NULL,
    questions JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## Setup

Install frontend tools:

```bash
npm install
```

Create a Python virtual environment and install backend dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Create your environment file:

```bash
cp .env.example .env
```

Update `.env`:

```text
TINYFISH_API_KEY=your_tinyfish_api_key_here
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/smart_hire_time
PORT=3000
```

Create the PostgreSQL database if it does not exist yet:

```bash
createdb smart_hire_time
```

Build the TypeScript frontend:

```bash
npm run build
```

Start Flask:

```bash
npm start
```

Open the app:

```text
http://localhost:3000
```

## Development

Run TypeScript and Python syntax checks:

```bash
npm run check
```

For frontend-only development:

```bash
npm run dev
```

The Vite dev server proxies `/api` requests to Flask on port `3000`, so keep Flask running in another terminal.

## API Example

Request:

```http
POST /api/interview-questions
Content-Type: application/json

{
  "jobTitle": "Customer Success Manager"
}
```

Response:

```json
{
  "id": 1,
  "jobTitle": "Customer Success Manager",
  "questions": [
    "How do you identify whether a customer is at risk before they explicitly say they are unhappy?",
    "Tell me about a time you turned product feedback from a customer into a useful internal recommendation.",
    "How would you balance a customer's urgent request with the company's product roadmap and support boundaries?"
  ]
}
```
