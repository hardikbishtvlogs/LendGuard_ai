import {AppPage} from "@/components/AppPage";

export default function Page(){return <AppPage eyebrow="DOCUMENTATION" title="Build, run and integrate LendGuard AI." copy="Use the local API docs for live schemas, then connect the responsive frontend to the FastAPI backend on port 8000." cards={[
 {title:"Local app",body:"Run ./run-local.sh from /Users/hardikbisht/Documents/LOAN and open http://localhost:3100.",href:"/predict"},
 {title:"OpenAPI",body:"FastAPI publishes live Swagger documentation at http://localhost:8000/docs."},
 {title:"Core flow",body:"Register or sign in, run predictions, review dashboard metrics and export reports."}
]}/>}
