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
