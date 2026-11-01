"""Refresh public official-source snapshots; no provider credentials needed."""
import hashlib,json,httpx
from datetime import datetime,timezone
from pathlib import Path
SOURCES=[('digital_arrest','https://www.pib.gov.in/PressReleasePage.aspx?PRID=2110809&lang=1&reg=3','2025-03-12'),('banking','https://rbikehtahai.rbi.org.in/safeguards-for-digital-banking.html',None),('task_jobs','https://www.pib.gov.in/PressReleasePage.aspx?PRID=1982936&lang=2&reg=48','2023-12-06'),('credentials','https://cyber.delhipolice.gov.in/netbanking.html',None)]
out=Path('backend/data/evaluation');out.mkdir(exist_ok=True);manifest=[]
for ident,url,date in SOURCES:
 try:
  r=httpx.get(url,follow_redirects=True,trust_env=False,timeout=25);r.raise_for_status();data=r.content
  if 'captcha' in r.text[:2000].lower() or 'support ID' in r.text[:2000]:raise ValueError('challenge page')
  if len(data)>2_000_000:raise ValueError('oversize')
  if url.endswith('.pdf') and not data.startswith(b'%PDF-'):raise ValueError('expected PDF, received HTML')
  suffix='.pdf' if url.endswith('.pdf') else '.html'; (out/(ident+suffix)).write_bytes(data)
  manifest.append(dict(id=ident,url=url,publication_date=date,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),status='downloaded',retrieved_at=datetime.now(timezone.utc).isoformat()))
 except Exception as e:manifest.append(dict(id=ident,url=url,status='unavailable',reason=type(e).__name__))
(out/'sources.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
