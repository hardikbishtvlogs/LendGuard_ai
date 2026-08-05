import Link from "next/link";

type Card = {title:string; body:string; href?:string};

export function AppPage({eyebrow,title,copy,cards,cta}:{eyebrow:string;title:string;copy:string;cards:Card[];cta?:{label:string;href:string}}){
 return <main className="mx-auto max-w-6xl px-5 py-14 md:py-20">
  <p className="eyebrow">{eyebrow}</p>
  <div className="mt-3 flex flex-col justify-between gap-5 md:flex-row md:items-end">
   <div>
    <h1 className="max-w-3xl text-4xl font-black tracking-tight md:text-6xl">{title}</h1>
    <p className="muted mt-5 max-w-2xl text-base leading-7 md:text-lg">{copy}</p>
   </div>
   {cta&&<Link className="button shrink-0 text-center" href={cta.href}>{cta.label}</Link>}
  </div>
  <section className="mt-10 grid gap-4 md:grid-cols-3">
   {cards.map((card,i)=>{const content=<><span className="text-xs font-bold text-cyan">0{i+1}</span><h2 className="mt-4 text-xl font-bold">{card.title}</h2><p className="muted mt-3 text-sm leading-6">{card.body}</p></>;return card.href?<Link key={card.title} href={card.href} className="glass rounded-2xl p-6 transition hover:-translate-y-1 hover:border-cyan/40">{content}</Link>:<article key={card.title} className="glass rounded-2xl p-6">{content}</article>})}
  </section>
 </main>
}
