![app_logo](https://github.com/452init/SmartHireTime/blob/main/public/assets/icon.png)

# SmartHireTime

SmartHireTime is a simple web app that turns a job title into three thoughtful interview questions. The frontend is TypeScript, the backend is Flask, the question set is stored in PostgreSQL, and Mistral generates the structured JSON response.

## What The App Does

1. The user enters a job title.
2. The TypeScript frontend sends the role details to the Flask API.
3. Flask builds a role-specific prompt.
4. Flask calls the Mistral API.
5. Flask validates the JSON response and saves the question set in PostgreSQL.
6. The frontend renders the interview questions.

## Project Structure

```text
SmartHireTime/
├── backend/
│   ├── app.py              # Flask entry point and HTTP routes
│   ├── ai_api.py           # Mistral API request
│   ├── config.py           # Environment loading
│   ├── database.py         # PostgreSQL setup and inserts
│   └── question_builder.py # Prompt creation and response parsing
├── frontend/
│   ├── index.html          # Page markup
│   └── src/
│       ├── main.ts         # TypeScript form and API logic
│       └── styles.css      # Clean hiring-focused UI
├── render.yaml             # Render production service definition
├── vercel.json             # Vercel production build and SPA routing config
├── requirements.txt        # Flask and PostgreSQL Python dependencies
├── package.json            # Frontend build scripts
├── tsconfig.json           # TypeScript settings
├── vite.config.ts          # Frontend build config
└── README.md               # Documentation
```

## Core Layers

`backend/app.py`

This is the backend entry point. It exposes the API route, serves health checks, initializes PostgreSQL, and connects the helper layers together.

`backend/config.py`

Loads `.env` values:

- `MISTRAL_API_KEY`
- `DATABASE_URL`
- `FRONTEND_ORIGIN`
- `PORT`

`backend/database.py`

Creates the PostgreSQL table if needed and saves each generated question set.

`backend/question_builder.py`

Builds the AI prompt and parses the Mistral JSON response into a clean list of questions.

`backend/ai_api.py`

Calls the Mistral chat completions endpoint and extracts the returned text payload.

`frontend/src/main.ts`

Handles the browser logic. It reads the job title, role level, and focus area, then calls the Flask API and renders the returned questions.

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
MISTRAL_API_KEY=your_mistral_api_key_here
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/smart_hire_time
FRONTEND_ORIGIN=http://localhost:5173,https://smart-hire-time.vercel.app
VITE_API_BASE_URL=http://127.0.0.1:3000
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

## Production Architecture

- Frontend: Vercel
- Backend API: Render
- Database: Supabase (PostgreSQL)
- CI/CD: GitHub Actions workflow in `.github/workflows/deploy-production.yml`

## Production Hosting (Step-by-Step)

### 1) Create Supabase database

1. Create a Supabase project.
2. In Supabase, copy the PostgreSQL connection string.
3. Use that value as `DATABASE_URL` in Render.
4. Ensure the password is URL-safe in the final `DATABASE_URL` when needed.

### 2) Deploy backend to Render

1. In Render, create a new **Blueprint** service from this repository (uses `render.yaml`) or create a Web Service manually with:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn --chdir backend --bind 0.0.0.0:$PORT app:app`
2. Set backend environment variables in Render:
   - `MISTRAL_API_KEY`
   - `DATABASE_URL` (Supabase PostgreSQL URL)
   - `FRONTEND_ORIGIN` (comma-separated list of allowed frontend origins, for example `https://your-app.vercel.app`)
3. Confirm health check works:
   - `GET https://<your-render-service>/api/health` returns `{"status":"ok"}`

### 3) Deploy frontend to Vercel

1. Import this repository into Vercel.
2. Framework preset should be Vite (also configured in `vercel.json`).
3. Set frontend environment variable in Vercel:
   - `VITE_API_BASE_URL=https://<your-render-service>`
4. Deploy, then verify frontend can call backend successfully.

### 4) Enable automatic production deploy on every push

This repo includes `.github/workflows/deploy-production.yml`, which:

1. Runs checks/build on pushes to `main`.
2. Triggers Render deploy hook.
3. Triggers Vercel deploy hook.

Add these GitHub repository secrets:

- `RENDER_DEPLOY_HOOK_URL`
- `VERCEL_DEPLOY_HOOK_URL`

How to get the hook URLs:

- Render: Service Settings → Deploy Hook.
- Vercel: Project Settings → Git / Deploy Hooks.

After adding secrets, every push to `main` will auto-validate and auto-deploy both frontend and backend.

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
    {
      "question": "How do you identify whether a customer is at risk before they explicitly say they are unhappy?",
      "difficulty": "Easy"
    },
    {
      "question": "Tell me about a time you turned product feedback from a customer into a useful internal recommendation.",
      "difficulty": "Medium"
    },
    {
      "question": "How would you balance a customer's urgent request with the company's roadmap and support boundaries?",
      "difficulty": "Hard"
    }
  ]
}
```
