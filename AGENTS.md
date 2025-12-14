# Repository Guidelines

## Project Structure & Module Organization

- `src/`: Flask backend (routes in `app.py`, DB helpers in `database.py`, AI clients/prompts in `doubao_api.py`, `prompts*.py`).
- `frontend/`: UI assets (`templates/` Jinja2 HTML, `static/css/`, `static/js/`, `static/images/`).
- `tests/`: runnable test scripts and placeholders (`tests/api/` is the primary integration test area).
- `config/`: environment templates (copy `config/.env.example` to `src/.env`).
- `data/`: runtime state (`uploads/`, `sessions/`; tracked with `.gitkeep`).
- `docs/`: architecture and setup notes; `.claude/` contains repo-automation scripts.

## Build, Test, and Development Commands

- Install deps (recommended): `python scripts/install_all.py`
- Install deps (manual): `pip install -r src/requirements.txt`
- Configure env: `cp config/.env.example src/.env` (fill `DEEPSEEK_API_KEY`, `DOUBAO_API_KEY`, DB vars as needed)
- Run locally: `python start.py` (runs `src/app.py` on `http://localhost:5000`)
- Run production-style: `cd src; python run_production.py` (Waitress)
- Validate repo structure: `python .claude/scripts/validate.py`

## Coding Style & Naming Conventions

- Python: 4-space indentation, `snake_case` for functions/vars, `UPPER_SNAKE_CASE` for constants, keep route handlers small and delegate logic to helpers.
- Frontend: keep templates in `frontend/templates/` and shared JS/CSS in `frontend/static/`; avoid inline JS for new features unless it’s truly page-specific.
- Secrets: never hardcode API keys; use `src/.env` (excluded from git).

## Testing Guidelines

- Current tests are script-style (not `pytest`). Keep new API tests as executable scripts under `tests/api/` named `test_<feature>.py`.
- Prefer tests that hit local endpoints and write outputs to `tests/api/test_results/` when needed.

## Commit & Pull Request Guidelines

- Commit messages in history are short and imperative (e.g., `Fix ...`, `Add ...`, `Improve ...`); `feat:`/`fix:`/`docs:` prefixes are also used—match nearby commits.
- PRs: include a brief summary, reproduction/verification steps, and screenshots for UI/template changes; link issues when applicable.

## Agent-Specific Notes

- Treat `data/` as runtime-only; don’t commit generated sessions/uploads.
- If you change structure, re-run `python .claude/scripts/validate.py` before shipping.
