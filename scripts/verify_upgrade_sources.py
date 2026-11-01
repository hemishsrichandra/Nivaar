"""Curated source leads only, no crawling. Store normalized snapshots for audit, not runtime evidence."""
import sys,json,hashlib,asyncio
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader
from io import BytesIO
LEADS={
'assam_lottery':'https://police.assam.gov.in/sites/default/files/swf_utility_folder/departments/assampolice_webcomindia_org_oid_8/menu/document/cyber_secure.pdf',
'alt_lottery':'https://elurupolice.ap.gov.in/lotteryscam.html',
'alt_sim':'https://cyber.delhipolice.gov.in/netbanking.html',
'alt_loan':'https://www.pib.gov.in/PressReleasePage.aspx?PRID=1749169&lang=2&reg=48',
'lottery':'https://cybercrime.gov.in/pdf/Cyber%20Security%20Awareness%20Booklet%20for%20Citizens.pdf',
'sim':'https://cybercrime.gov.in/webform/crimecatdes.aspx',
'customs':'https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=2025648&lang=2&reg=48',
'loan':'https://www.rbi.org.in/commonman/images/FAME202426022024.pdf',
'lending':'https://systemhealth.rbi.org.in/Scripts/NotificationUser.aspx_Id%3D12382%26Mode%3D0.html',
'phone':'https://www.dot.gov.in/static/uploads/2025/07/8df49d5b579439471bb8e506906d913a.pdf',
'helpline':'https://www.pib.gov.in/PressReleasePage.aspx?PRID=2290377&lang=1&reg=22',
'upi':'https://www.npci.org.in/PDF/npci/upi/Product-Booklet.pdf'}
async def main():
 out=Path('backend/data/source_inventory');out.mkdir(exist_ok=True)
 async def fetch(ident,url):
  item=dict(id=ident,url=url,retrieved_at=datetime.now(timezone.utc).isoformat())
  try:
   async with httpx.AsyncClient(trust_env=False,follow_redirects=True,timeout=25) as c:r=await c.get(url);r.raise_for_status()
   if url.lower().endswith('.pdf'):
    if not r.content.startswith(b'%PDF-'):raise ValueError('PDF lead returned HTML')
    text=' '.join(p.extract_text() or '' for p in PdfReader(BytesIO(r.content)).pages[:100])
   else:
    soup=BeautifulSoup(r.content,'html.parser')
    for tag in soup(['script','style','nav','footer']):tag.decompose()
    text=soup.get_text(' ',strip=True)
   if len(text)<200 or any(t in text[:1200].lower() for t in ('captcha','support id','access denied','enable javascript','request rejected')):raise ValueError('challenge or empty')
   text=' '.join(text.split());(out/(ident+'.txt')).write_text(text,encoding='utf-8')
   item.update(status='retrieved',sha256=hashlib.sha256(text.encode()).hexdigest(),characters=len(text),canonical_url=str(r.url))
  except Exception as e:item.update(status='unavailable',reason=type(e).__name__)
  return item
 rows=await asyncio.gather(*(fetch(i,u) for i,u in LEADS.items()));(out/'manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');print(json.dumps(rows,indent=2))
asyncio.run(main())
