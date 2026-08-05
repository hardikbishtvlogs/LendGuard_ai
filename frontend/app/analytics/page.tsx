import {AppPage} from "@/components/AppPage";

export default function Page(){return <AppPage eyebrow="ANALYTICS" title="Portfolio trends without the spreadsheet fog." copy="Track approval rate, default probability, risk mix, monthly movement and operational reporting from one command center." cta={{label:"Open dashboard",href:"/dashboard"}} cards={[
 {title:"Risk distribution",body:"Low, medium and high-risk segments summarized for fast portfolio review.",href:"/dashboard"},
 {title:"Trend reporting",body:"Monthly application movement and approval ratios are ready for production chart expansion."},
 {title:"Executive exports",body:"Download clean PDF and Excel reports for reviews, audits and credit committees.",href:"/reports"}
]}/>}
