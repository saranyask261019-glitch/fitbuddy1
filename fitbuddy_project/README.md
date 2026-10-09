# FitBuddy — AI Fitness Plan Generator

A complete FastAPI + Jinja2 + SQLAlchemy + SQLite application. Gemini creates workout plans, nutrition/recovery tips, and feedback-based revisions. Without a Gemini API key, the app uses a clearly identified starter-plan/demo fallback so the UI and database can be tested locally.

## Features
- Responsive form and 7-day workout result page
- Gemini integration using the current `google-genai` SDK
- Nutrition and recovery tips
- Feedback-based plan revision; original plan remains stored
- SQLite persistence
- Admin dashboard at `/view-all-users`
- JSON endpoints `/api/health` and `/api/users`
- Swagger API documentation at `/docs`

## Requirements
- Python 3.11 or newer recommended
- Visual Studio Code
- Optional Gemini API key from Google AI Studio

## Windows / VS Code setup
1. Extract/open this project folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Create a virtual environment:
   ```powershell
   py -m venv .venv
   ```
4. Activate it:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, use Command Prompt terminal and run:
   ```bat
   .venv\Scripts\activate.bat
   ```
5. Install dependencies:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
6. Copy `.env.example` to `.env`. Add your key to `GEMINI_API_KEY=` if you have one. Keep `.env` private and never commit it.
7. Start the server from the project root:
   ```powershell
   uvicorn app.main:app --reload
   ```
8. Open:
   - Website: http://127.0.0.1:8000
   - API docs: http://127.0.0.1:8000/docs
   - Admin dashboard: http://127.0.0.1:8000/view-all-users
   - Health check: http://127.0.0.1:8000/api/health

## Test
Keep the server running in one terminal. In a second terminal, activate `.venv` and run:
```powershell
pytest -q
```
Manual test: create a plan with a user ID of your choice; then submit feedback on the result page; then open the admin dashboard to inspect the original and updated plans.

## API
- `GET /api/health` — health check
- `GET /api/users` — registered user summaries
- `POST /generate-workout` — HTML form endpoint
- `POST /submit-feedback` — HTML feedback form endpoint

## Important security and safety notes
- The admin page is intentionally a local-development dashboard and has no authentication. Do not expose it publicly until authentication and authorization are added.
- User ID is a convenience identifier, not authentication.
- Fitness content is general wellness information, not medical advice. Users should adapt activity to their abilities and seek qualified advice for health concerns.
- Do not put API keys into source code. Configure `.env`; do not commit it.
- For a real production deployment, add authentication, rate limiting, logging, privacy controls, database migrations, and stronger validation.

## Project structure
```text
fitbuddy_project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── ai.py
│   ├── templates/
│   │   ├── index.html
│   │   ├── result.html
│   │   └── all_users.html
│   └── static/
│       └── style.css
├── tests/
│   └── test_app.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```
