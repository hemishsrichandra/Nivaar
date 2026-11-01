import type {Status,Verdict} from '../types';
export function decide(checks:{authority:Status;requested_action:Status;destination:Status},highRisk:boolean):{verdict:Verdict;risk_level:'HIGH'|'MEDIUM'|'LOW'}{
 if(checks.authority==='CONTRADICTED'||checks.destination==='DANGEROUS'||checks.requested_action==='DANGEROUS')return {verdict:'SCAM',risk_level:'HIGH'};
 if(checks.authority==='VERIFIED'&&checks.requested_action==='VERIFIED'&&['VERIFIED','NOT_PROVIDED'].includes(checks.destination)&&!highRisk)return {verdict:'GENUINE',risk_level:'LOW'};
 return {verdict:'UNSURE',risk_level:checks.destination==='SUSPICIOUS'||highRisk?'HIGH':'MEDIUM'};
}
export function inspectDestination(urls:string[],text:string):Status{
 if(!urls.length)return 'NOT_PROVIDED';
 let allOfficial=true;
 for(const url of urls){try{const u=new URL(url),h=u.hostname.toLowerCase();const official=/(?:^|\.)(?:gov\.in|nic\.in)$/.test(h)||['rbi.org.in','www.rbi.org.in'].includes(h);
 if((/India Post|police|CBI|Cabinet Secretariat|Ministry|court|tax department|सरकार|पुलिस|ಸರ್ಕಾರ|ಪೊಲೀಸ್/i.test(text)&&!official)||/\.apk(?:$|\?)/i.test(u.pathname)||u.username||u.password)return 'DANGEROUS';
 if(!official||u.protocol!=='https:')allOfficial=false;
 }catch{return 'SUSPICIOUS';}}
 return allOfficial?'VERIFIED':'SUSPICIOUS';
}
