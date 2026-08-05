import type {NextConfig} from "next";
import {PHASE_DEVELOPMENT_SERVER} from "next/constants";

export default function config(phase:string):NextConfig{
 const defaultApiUrl=phase===PHASE_DEVELOPMENT_SERVER?"http://localhost:8000":"https://lendguard-ai-api.onrender.com";
 return {
  // Keep dev chunks isolated so a production build cannot corrupt a running server.
  distDir: phase===PHASE_DEVELOPMENT_SERVER?".next-dev":".next",
  output:"standalone",
  // An explicitly empty value uses the same-origin /api/v1 proxy in production.
  // Local development keeps the override below; production defaults to the
  // deployed FastAPI service so browser requests never point at localhost.
  env:{NEXT_PUBLIC_API_URL:process.env.NEXT_PUBLIC_API_URL??defaultApiUrl}
 };
}
