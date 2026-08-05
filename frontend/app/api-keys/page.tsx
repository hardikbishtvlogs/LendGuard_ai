import {AppPage} from "@/components/AppPage";

export default function Page(){return <AppPage eyebrow="API KEYS" title="Developer access, designed for the next release." copy="The current platform exposes JWT-secured REST APIs. API-key management is scaffolded as a product page for enterprise developer onboarding." cta={{label:"Read API docs",href:"/docs"}} cards={[
 {title:"REST first",body:"Versioned /api/v1 endpoints support auth, predictions, dashboard data and reports."},
 {title:"Bearer security",body:"Today, API calls use JWT tokens issued by register/login."},
 {title:"Roadmap ready",body:"Dedicated key rotation, scopes and usage metering can be added without changing the UI structure."}
]}/>}
