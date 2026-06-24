## Getting Started

## Local development

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn main:app --reload
```

API docs: http://localhost:8000/docs

Create an admin user:

```bash
python3 scripts/make_admin.py admin@example.com 'SecurePass123' 'Admin Name'
```

## Staging with Docker

Build and run the API in staging mode:

```bash
cp .env.example .env
# edit .env with real Supabase credentials

docker compose up --build
```

Health checks:

- Liveness: `GET /health`
- Readiness (includes Supabase): `GET /health/ready`

## Deploy to Render

1. Connect this repo to [Render](https://render.com).
2. Use the included `render.yaml` blueprint, or create a **Web Service** with Docker runtime.
3. Set environment variables in the Render dashboard:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`
   - `GROQ_API_KEY`
   - `CORS_ORIGINS` (your frontend URL)
   - `ENVIRONMENT=staging`
4. Set the health check path to `/health`.

## Production notes

- Set `ENVIRONMENT=production` to disable `/docs` and OpenAPI.
- Use `CORS_ORIGINS` to restrict frontend access.
- The service role key bypasses Supabase RLS — keep authorization checks in route handlers.
- Run behind HTTPS with a reverse proxy or platform load balancer.

## Tests and CI

```bash
pytest
```

GitHub Actions runs tests on push/PR to `main`.

## API routes

| Prefix | Description |
|--------|-------------|
| `/api/auth` | Signup, login, current user |
| `/api/quotes` | User quotes |
| `/api/line-items` | Quote line items |
| `/api/estimator` | Cost estimation |
| `/api/pdf` | PDF upload and parsing |
| `/api/suppliers` | Supplier directory and referrals |
