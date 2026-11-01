import type {Report} from '../types';
// Dependency-free paginated PDF. UTF-8 original report is embedded as an attachment.
export function evidencePdf(r:Report){
 const enc=new TextEncoder();const ascii=(s:string)=>s.replace(/[^\x20-\x7e\n]/g,'?');
 const lines=["NIVAAR | Evidence & reporting pack",`Generated: ${r.generated_at_utc}`,`Assessment: ${r.verdict} | Risk: ${r.risk_level}`,`Report SHA-256: ${r.report_hash}`,'','AUTOMATED GUIDANCE - not a legal certificate.','The hash detects changes to the canonical JSON report.','Original UTF-8 report is attached as report.json.','Non-Latin text appears in that attachment; use browser Print for a localized PDF.','', 'REDACTED MESSAGE',r.extracted.raw_text_redacted,'','DIMENSION CHECKS',...Object.entries(r.checks).map(([k,v])=>`${k}: ${v}`),'','RECOMMENDED ACTIONS',...r.recommended_actions,'','OFFICIAL EVIDENCE',...r.evidence.flatMap(e=>[e.publisher,e.url,e.evidence_text,`Content SHA-256: ${e.sha256_hash}`,`Fetched: ${e.retrieved_at_utc}`,'']),'LIMITATIONS',...r.limitations,'','COMPLAINT DRAFT (review before filing)',r.complaint].flatMap(s=>ascii(s).split('\n').flatMap(line=>line.match(/.{1,88}(?:\s|$)|.{1,88}/g)||['']));
 const objects:string[]=[];const add=(s:string)=>{objects.push(s);return objects.length;};
 const catalog=add(''),pages=add(''),font=add('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>');
 const ids:number[]=[];
 for(let i=0;i<lines.length;i+=48){const escape=(s:string)=>s.replace(/\\/g,'\\\\').replace(/\(/g,'\\(').replace(/\)/g,'\\)');const stream='BT /F1 10 Tf 44 790 Td 14 TL '+lines.slice(i,i+48).map(s=>`(${escape(s)}) Tj T*`).join('\n')+' ET';const content=add(`<< /Length ${enc.encode(stream).length} >>\nstream\n${stream}\nendstream`);ids.push(add(`<< /Type /Page /Parent ${pages} 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 ${font} 0 R >> >> /Contents ${content} 0 R >>`));}
 const json=JSON.stringify(r,null,2);const embedded=add(`<< /Type /EmbeddedFile /Subtype /application#2Fjson /Length ${enc.encode(json).length} >>\nstream\n${json}\nendstream`);const spec=add(`<< /Type /Filespec /F (report.json) /EF << /F ${embedded} 0 R >> >>`);
 objects[catalog-1]=`<< /Type /Catalog /Pages ${pages} 0 R /Names << /EmbeddedFiles << /Names [(report.json) ${spec} 0 R] >> >> >>`;
 objects[pages-1]=`<< /Type /Pages /Kids [${ids.map(id=>`${id} 0 R`).join(' ')}] /Count ${ids.length} >>`;
 let out='%PDF-1.7\n',offsets=[0];for(let i=0;i<objects.length;i++){offsets.push(enc.encode(out).length);out+=`${i+1} 0 obj\n${objects[i]}\nendobj\n`;}
 const xref=enc.encode(out).length;out+=`xref\n0 ${objects.length+1}\n0000000000 65535 f \n`+offsets.slice(1).map(n=>`${String(n).padStart(10,'0')} 00000 n \n`).join('')+`trailer << /Size ${objects.length+1} /Root ${catalog} 0 R >>\nstartxref\n${xref}\n%%EOF`;return enc.encode(out);
}
