# Power BI setup

1. In Power BI Service, create a streaming/push semantic model with fields matching `predictionId`, `timestamp`, `default_probability`, `risk_score`, `confidence`, `risk_category`, `decision`, and the application fields.
2. Copy its push URL into `POWERBI_PUSH_URL`.
3. Build Executive, Risk Analytics, Business, and Live Prediction report pages from that model.
4. Publish the report and set its secure embed URL in `POWERBI_EMBED_URL`.

Predictions are persisted before the asynchronous push. A Power BI outage therefore never loses the lending decision. Production embedding should use Microsoft Entra ID and server-generated embed tokens rather than a public publish-to-web URL.

