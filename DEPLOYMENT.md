# Deployment Guide

## GitHub

```bash
cd "/Users/hardikbisht/Documents/LOAN"
git remote add origin https://github.com/YOUR_USERNAME/secure-loan-risk-ai.git
git branch -M main
git push -u origin main
```

If the remote already exists, use:

```bash
git remote set-url origin https://github.com/YOUR_USERNAME/secure-loan-risk-ai.git
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
