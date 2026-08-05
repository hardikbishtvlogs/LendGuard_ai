"use client";
import {useEffect, useState} from "react";
import {api} from "@/lib/api";

export default function Page(){
 const [embedUrl,setEmbedUrl]=useState(""); const [message,setMessage]=useState("Sign in to load your secure Power BI workspace.");
 useEffect(()=>{if(!localStorage.getItem("token"))return;api("/api/v1/powerbi/config").then((data)=>{if(data.configured)setEmbedUrl(data.embed_url);else setMessage("Power BI is not configured yet. Set POWERBI_PUSH_URL and POWERBI_EMBED_URL in the backend secrets, then publish the secure report.")}).catch((error)=>setMessage(error.message))},[]);
 return <main className="mx-auto max-w-7xl px-6 py-14"><p className="text-cyan">POWER BI</p><h1 className="text-4xl font-black">Executive risk intelligence</h1><div className="glass mt-9 min-h-[520px] overflow-hidden rounded-3xl">{embedUrl?<iframe title="LendGuard Power BI dashboard" className="min-h-[520px] w-full border-0" src={embedUrl} allowFullScreen/>:<div className="grid min-h-[520px] place-items-center p-8 text-center"><div><div className="text-6xl">◫</div><h2 className="mt-4 text-2xl font-bold">Secure Power BI workspace</h2><p className="mx-auto mt-2 max-w-lg text-slate-400">{message}</p></div></div>}</div></main>
}
