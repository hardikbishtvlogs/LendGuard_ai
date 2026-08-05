# Secure Power BI integration

The API pushes a row only after the prediction has committed to PostgreSQL. A Power BI outage therefore cannot discard or alter a lending decision.

## 1. Create the semantic model

In Power BI Service, create a push semantic model with these fields: `predictionId`, `timestamp`, `default_probability`, `risk_score`, `confidence`, `risk_category`, `decision`, `age`, `income`, `employment_length`, `loan_amount`, `interest_rate`, `credit_history_length`, `home_ownership`, `loan_intent`, `loan_grade`, and `previous_default`.

Copy the generated push URL into the secret `POWERBI_PUSH_URL`. The backend posts this exact shape after every authenticated `/predictions` request.

## 2. Build the report

Create cards for total predictions, approval/rejection rate and average default probability. Add a risk-category donut chart, timestamp month trend, loan-intent/grade comparison and a model-performance table using `ml/reports/metrics.json` as a governed manual refresh source. Publish the report to a workspace with only the lender’s authorized users.

## 3. Secure embedding

Use **Embed for your organization** or **Embed for your customers** with Microsoft Entra ID; do not use “Publish to web” for credit data. Register an Entra application, grant its service principal access to the Power BI workspace, then have a trusted backend service generate a short-lived embed token using the Power BI REST API. Store the returned report embed URL in `POWERBI_EMBED_URL` and the Entra client secret in your provider’s secret store.

The included `/api/v1/powerbi/config` API requires authentication before it returns configuration. A deployment with user-specific Power BI RLS must generate the embed token server-side and must never expose the Entra client secret to Next.js.

## 4. Verify

Make an authenticated prediction, confirm the Postgres row first, then verify the streaming model receives the same `predictionId`. Set an alert for a failed Power BI refresh separately; it is analytics, not the system of record.
