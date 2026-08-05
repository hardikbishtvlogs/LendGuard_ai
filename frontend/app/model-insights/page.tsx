import {AppPage} from "@/components/AppPage";

export default function Page(){return <AppPage eyebrow="MODEL INSIGHTS" title="Explainable AI for lending decisions." copy="The platform uses a saved sklearn pipeline with engineered features, validation metrics and transparent risk drivers returned with every score." cta={{label:"Try explainability",href:"/predict"}} cards={[
 {title:"Best model selection",body:"Training compares candidate models and saves the strongest validated pipeline with Joblib."},
 {title:"Feature importance",body:"Risk drivers, strengths and score components make the decision understandable to users."},
 {title:"Governance ready",body:"Model artifacts and metrics live under the ML layer for reproducible deployment reviews."}
]}/>}
