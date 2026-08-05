import {AppPage} from "@/components/AppPage";

export default function Page(){return <AppPage eyebrow="PRICING" title="Simple plans for teams that score loan risk." copy="Start with the public demo, then move into authenticated audit trails, exports and portfolio analytics when your team is ready." cta={{label:"Run assessment",href:"/predict"}} cards={[
 {title:"Starter",body:"Free demo scoring for validating applicant risk flows and model explainability."},
 {title:"Team",body:"JWT accounts, prediction history, PDF/Excel reports and portfolio dashboards."},
 {title:"Enterprise",body:"Private deployment, SSO-ready architecture, monitoring, model governance and API access."}
]}/>}
