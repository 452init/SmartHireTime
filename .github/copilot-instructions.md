# SmartHireTime Instructions

Treat authentication as removed from this codebase unless the user explicitly asks to restore it.

- Do not add or preserve auth UI, auth API routes, session or token handling, password reset flows, refresh cookies, Google sign-in, or auth-specific environment variables.
- Remove auth-dependent guards, headers, redirects, storage, and backend branching rather than stubbing them.
- Use the free Gemini API for interview-question generation instead of TinyFish.
- Keep the AI response format structured as JSON and parse or validate it defensively.
- Update docs, examples, scripts, and environment samples whenever auth or AI flow changes so no TinyFish or auth references remain.