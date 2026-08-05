import {AppPage} from "@/components/AppPage";

export default function Page(){return <AppPage eyebrow="PROFILE" title="Your lending workspace identity." copy="Manage account details, role context and secure access. Live user profile data is available through the authenticated backend API." cards={[
 {title:"Account",body:"Email, full name and assigned role are served from /api/v1/users/me."},
 {title:"Access",body:"JWT bearer auth protects saved predictions, dashboard data and report exports."},
 {title:"Activity",body:"Prediction history provides the operational trail for account activity."}
]}/>}
