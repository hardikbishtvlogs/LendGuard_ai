import {AppPage} from "@/components/AppPage";

export default function Page(){return <AppPage eyebrow="AUDIT LOGS" title="Traceable decisions for regulated teams." copy="Every authenticated prediction is persisted with inputs, model output, decision, user and timestamp so reviews can reconstruct what happened." cta={{label:"View history",href:"/history"}} cards={[
 {title:"Immutable records",body:"Prediction rows store inputs and generated risk output for audit-friendly review."},
 {title:"User ownership",body:"Customer users see their own records while admin-style roles can review broader portfolio data."},
 {title:"Exportable evidence",body:"PDF and Excel downloads convert stored predictions into committee-ready artifacts."}
]}/>}
