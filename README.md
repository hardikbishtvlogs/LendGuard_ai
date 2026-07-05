# LendGuard AI

Enterprise loan-default intelligence platform built with FastAPI, PostgreSQL, Next.js, TypeScript, Tailwind, React Native/Expo, scikit-learn, and Power BI push integration.

The web app is responsive and usable across desktop, iPad/tablet, and mobile browser viewports.

## One-command local start

```bash
cd "/Users/hardikbisht/Documents/LOAN"
./run-local.sh
```

Open http://localhost:3100. Press `Ctrl+C` to stop both services. Port 3100 is used to avoid conflicts with other local Next.js projects.

## Run the built production app locally

If `npm run build` is already complete and you want the fully functional production build, use:

```bash
cd "/Users/hardikbisht/Documents/LOAN"
./run-built.sh
```

Open http://localhost:3100. This starts both the FastAPI backend and the Next.js standalone production server. Running `npm start` from `frontend/` only starts the website, so API-backed features such as login, dashboard, saved predictions and reports need the backend running too.

The training pipeline now enforces a **95% held-out accuracy quality gate** before replacing the deployed model. If candidates miss the gate, the current production artifact remains untouched and details are written to `ml/reports/metrics_failed_gate.json`.

## Fastest way to run (Docker)

Install Docker Desktop, open Terminal, then:

```bash
cd "/Users/hardikbisht/Documents/LOAN"
docker compose up --build
```

Open:

- Website: http://localhost:3000
- Interactive API documentation: http://localhost:8000/docs
- API health check: http://localhost:8000/health

Stop with `Ctrl+C`, then `docker compose down`.

## Run without Docker

Terminal 1 — backend:

```bash
cd "/Users/hardikbisht/Documents/LOAN"
source .venv/bin/activate
cd backend
uvicorn app.main:app --reload --port 8000
```

Terminal 2 — website:

```bash
cd "/Users/hardikbisht/Documents/LOAN/frontend"
npm install
npm run dev
```

This local mode uses SQLite automatically. Docker uses PostgreSQL.

## Mobile app

Start the backend first, then:

```bash
cd "/Users/hardikbisht/Documents/LOAN/mobile"
npm install
EXPO_PUBLIC_API_URL=http://YOUR-COMPUTER-IP:8000 npx expo start
```

Scan the QR code using Expo Go. A physical phone cannot use `localhost`; use the computer's LAN IP. The web app currently provides the complete authentication flow; the Expo client demonstrates shared-API prediction and is ready for additional screens.

## Retrain and verify the model

```bash
cd "/Users/hardikbisht/Documents/LOAN"
source .venv/bin/activate
python ml/train.py
```

Training compares Logistic Regression, Random Forest, gradient boosting and CatBoost when available. It evaluates accuracy, ROC AUC, precision, recall, F1, confusion matrix and five-fold cross-validation, then refuses to save a model below the 95% accuracy quality gate.

## Power BI

Follow `powerbi/README.md`. Set `POWERBI_PUSH_URL` to stream each saved prediction and `POWERBI_EMBED_URL` for the report. Never use Publish to Web for customer data.

## Tests

```bash
cd "/Users/hardikbisht/Documents/LOAN"
source .venv/bin/activate
PYTHONPATH=backend pytest backend/tests
cd frontend && npm run build
```

## Production checklist

- Replace `SECRET_KEY` and keep it in a secrets manager.
- Use managed PostgreSQL with backups, TLS, migrations, connection pooling, and least-privilege credentials.
- Add Microsoft Entra embed-token flow for Power BI.
- Put Nginx or a cloud load balancer in front of the services and enforce HTTPS.
- Add rate limiting, refresh-token rotation, email verification, MFA, audit-event retention, consent and jurisdiction-specific lending compliance.
- Deploy frontend to Vercel and backend/container to AWS or Render; the included Dockerfiles and CI workflow are starting points.

## Structure

`backend/` API, auth, RBAC, persistence, reports · `frontend/` responsive web app · `mobile/` Expo app · `ml/` training and artifacts · `powerbi/` BI setup · `deployment/` Nginx · `legacy_cpp/` supplied baseline · `data/` supplied dataset.
