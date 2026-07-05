import type {NextConfig} from "next";
import {PHASE_DEVELOPMENT_SERVER} from "next/constants";

export default function config(phase:string):NextConfig{
 return {
  // Keep dev chunks isolated so a production build cannot corrupt a running server.
  distDir: phase===PHASE_DEVELOPMENT_SERVER?".next-dev":".next",
  output:"standalone",
  env:{NEXT_PUBLIC_API_URL:process.env.NEXT_PUBLIC_API_URL||"http://localhost:8000"}
 };
}
