# System architecture

```mermaid
flowchart LR
  User["Browser / Next.js"] --> Proxy["Nginx TLS reverse proxy"]
  Proxy --> Web["Next.js application"]
  Proxy --> API["FastAPI / OpenAPI"]
  API --> DB[("PostgreSQL")]
  API --> Model["Joblib CatBoost model"]
  API --> BI["Power BI push dataset"]
```

FastAPI validates input, authenticates JWTs, applies role checks, persists a decision, and only then submits an asynchronous Power BI event. The saved model and its decision thresholds are versioned artifacts. The UI uses the REST API and no database credentials are sent to the browser.

# Data model

```mermaid
erDiagram
  USERS ||--o{ CUSTOMERS : owns
  USERS ||--o{ PREDICTIONS : creates
  CUSTOMERS ||--o{ PREDICTIONS : associated_with
  USERS { int id PK string email UK string role boolean is_active datetime created_at }
  CUSTOMERS { int id PK int owner_id FK string name string email string phone }
  PREDICTIONS { int id PK int user_id FK int customer_id FK json inputs float default_probability string risk_category string decision datetime created_at }
```
