import registry from '../../data/verified_advisories.json';
import type {Evidence} from '../types';
export {registry};
export async function hash(text:string){return [...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(text)))].map(x=>x.toString(16).padStart(2,'0')).join('');}
export function allowedOfficial(url:string) {
 try {const u=new URL(url); return u.protocol==='https:'&&!u.username&&!u.password&&!u.port&&registry.some(x=>new URL(x.url).hostname===u.hostname); } catch {return false;}
}
function plain(html:string){return html.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,' ').replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi,' ').replace(/<[^>]+>/g,' ').replace(/&nbsp;|&#160;/g,' ').replace(/&amp;/g,'&').replace(/&#39;/g,"'").replace(/&quot;/g,'"').replace(/\s+/g,' ').trim();}
// Only exact registry URLs are requested. Submitted links never reach fetch().
export async function fetchOfficial(source:typeof registry[number], relation:Evidence['relation']):Promise<Evidence|null>{
 if(!registry.some(s=>s.url===source.url)||!allowedOfficial(source.url))return null;
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),6000);
 try {
  let current=source.url;
  let res:Response|undefined;
  for(let redirects=0;redirects<=2;redirects++){
   res=await fetch(current,{redirect:'manual',signal:controller.signal,headers:{'User-Agent':'Nivaar/1.0 Evidence Verification'}});
   if(![301,302,303,307,308].includes(res.status))break;
   const location=res.headers.get('location');if(!location)return null;
   const target=new URL(location,current),original=new URL(source.url);
   // PIB adds locale parameters. Only this same document, same origin and numeric locales may redirect.
   if(!allowedOfficial(target.href)||target.origin!==original.origin||target.pathname!==original.pathname||target.searchParams.get('PRID')!==original.searchParams.get('PRID')||[...target.searchParams].some(([key,value])=>!['PRID','reg','lang'].includes(key)||!/^\d+$/.test(value)))return null;
   current=target.href;
  }
  if(!res)return null;
  if(!res.ok||!res.headers.get('content-type')?.includes('text/html')) return null;
  const reader=res.body?.getReader(); if(!reader)return null;
  let body='',bytes=0;const decoder=new TextDecoder();
  while(true){const {value,done}=await reader.read();if(done)break;bytes+=value.length;if(bytes>1500000){await reader.cancel();return null;}body+=decoder.decode(value,{stream:true});}
  const text=plain(body),at=text.toLowerCase().indexOf(source.anchor.toLowerCase());
  if(at<0||/captcha|access denied|request rejected/i.test(text.slice(0,300)))return null;
  return {source_id:source.id,url:source.url,publisher:source.publisher,document_date:source.date,title:source.title,evidence_text:text.slice(Math.max(0,text.lastIndexOf('.',at)+1),at+source.anchor.length+260).trim(),relation,retrieval_status:'live_fetched',sha256_hash:await hash(text),retrieved_at_utc:new Date().toISOString()};
 }catch{return null;}finally{clearTimeout(timer);}
}
