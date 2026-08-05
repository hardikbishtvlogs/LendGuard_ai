import {AppPage} from "@/components/AppPage";

export default function Page(){return <AppPage eyebrow="SETTINGS" title="Configure the platform safely." copy="Production settings are environment-driven so secrets, API URLs, CORS and integrations stay outside source code." cards={[
 {title:"Environment variables",body:"Backend and frontend configuration is controlled through .env-compatible deployment settings."},
 {title:"Security posture",body:"Passwords are hashed, privileged roles cannot be self-assigned and protected APIs require JWT."},
 {title:"Integrations",body:"Power BI and deployment integrations are isolated behind configuration switches."}
]}/>}
