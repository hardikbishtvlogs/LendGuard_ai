# Deployment Guide

## GitHub

```bash
cd "/Users/hardikbisht/Documents/LOAN"
git remote add origin https://github.com/hardikbishtvlogs/LendGuard_ai.git
git branch -M main
git push -u origin main
```

## Public Link With Render

Use Render Blueprint to deploy both services from this repository:

1. Open `https://dashboard.render.com/blueprints`
2. Click `New Blueprint Instance`
3. Connect the GitHub repo: `https://github.com/hardikbishtvlogs/LendGuard_ai`
4. Select the `main` branch and apply the detected `render.yaml`
5. Wait for both services to finish deploying

Expected public URLs:

- Web app: `https://lendguard-ai-web.onrender.com`
- API: `https://lendguard-ai-api.onrender.com`
- API docs: `https://lendguard-ai-api.onrender.com/docs`

After deployment, share the web app URL with anyone. They do not need to be on the same Wi-Fi.

Note: the Render free plan can sleep after inactivity, so the first request after a pause may take a little longer.

## Temporary Public Link From Your Laptop

For a quick shareable link without same Wi-Fi:

```bash
cd "/Users/hardikbisht/Documents/LOAN"
./run-public-tunnel.sh
```

Copy the printed `https://...trycloudflare.com` URL and send it to anyone. Keep the terminal open while people are using it. If the laptop sleeps, shuts down, or the terminal is closed, the temporary link stops working.

If the remote already exists, use:

```bash
git remote set-url origin https://github.com/hardikbishtvlogs/LendGuard_ai.git
git push -u origin main
```

## Local Production Run

```bash
cd "/Users/hardikbisht/Documents/LOAN"
./run-built.sh
```

Open `http://localhost:3100`.

## Single-host Docker deployment

1. Copy `.env.example` to `.env`; set `ENVIRONMENT=production`, a cryptographically random `SECRET_KEY`, `POSTGRES_PASSWORD`, `CORS_ORIGINS`, and `TRUSTED_HOSTS`.
2. Point your DNS A/AAAA record to the server.
3. Start the complete PostgreSQL, FastAPI, Next.js and Nginx stack:

```bash
docker compose -f docker-compose.production.yml up -d --build
docker compose -f docker-compose.production.yml ps
```

Nginx is the only public service and listens on port 80. Put a managed HTTPS load balancer in front of it, or terminate TLS with your hosting provider. Set `CORS_ORIGINS` and `TRUSTED_HOSTS` to the final HTTPS domain before going live.

## Continuous integration

`.github/workflows/ci.yml` installs the pinned dependencies, runs the backend tests, builds the frontend, and builds containers on each pull request and push to `main`. Configure a deployment hook (Render deploy hook, Railway service token, or AWS OIDC role) as a GitHub Actions secret; keep that provider-specific credential out of the repository.

## Cloud Hosting

Recommended split:

- Frontend: Vercel
- Backend: Render, Railway, Fly.io, or AWS
- Database: Managed PostgreSQL
- Model artifact: committed compressed `ml/artifacts/model.joblib`, or move to object storage for larger future models

Required backend environment variables:

```env
SECRET_KEY=replace-with-a-long-random-secret
DATABASE_URL=postgresql://...
MODEL_PATH=ml/artifacts/model.joblib
CORS_ORIGINS=https://your-frontend-domain.com
POWERBI_PUSH_URL=
POWERBI_EMBED_URL=
```

Required frontend environment variable:

```env
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
```
