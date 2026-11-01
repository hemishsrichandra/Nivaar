import time
_CACHE={}
import asyncio, hashlib, ipaddress, re, socket
from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin
import httpx
from bs4 import BeautifulSoup
from backend.config import OFFICIAL_DOMAINS
from backend.schemas import EvidenceItem

def utcnow(): return datetime.now(timezone.utc).isoformat()
def sha256(value): return hashlib.sha256(value.encode() if isinstance(value,str) else value).hexdigest()
def allowed_url(url):
    try:
        u=urlparse(url);host=(u.hostname or '').lower().rstrip('.')
        return u.scheme=='https' and not u.username and not u.password and u.port in (None,443) and any(host==d or host.endswith('.'+d) for d in OFFICIAL_DOMAINS)
    except ValueError:return False

async def public_addresses(host):
    records=await asyncio.wait_for(asyncio.get_running_loop().getaddrinfo(host,443,type=socket.SOCK_STREAM),timeout=5)
    addresses=sorted(set(r[4][0] for r in records),key=lambda a:ipaddress.ip_address(a).version)
    if not addresses or any(not ipaddress.ip_address(a).is_global for a in addresses):raise ValueError('Non-public destination blocked')
    return addresses

async def fetch_document(url,source_id='',publisher='',title='',date=None):
    key=(url,source_id,publisher,title,date)
    cached=_CACHE.get(key)
    if cached and time.monotonic()-cached[0]<900:return cached[1]
    original=url
    if not allowed_url(url):return None
    try:
        async with asyncio.timeout(14):
            async with httpx.AsyncClient(timeout=10,follow_redirects=False,trust_env=False) as client:
                for _ in range(3):
                    if not allowed_url(url):return None
                    parsed=urlparse(url);host=parsed.hostname
                    addresses=await public_addresses(host)
                    ip=addresses[0];ip_host=f'[{ip}]' if ':' in ip else ip
                    pinned=parsed._replace(netloc=ip_host).geturl()
                    # Pin validated DNS resolution and retain the original Host/TLS name.
                    async with client.stream('GET',pinned,headers={'Host':host,'User-Agent':'Nivaar/1.0 (+official evidence checker)'},extensions={'sni_hostname':host}) as response:
                        if response.is_redirect:
                            location=response.headers.get('location')
                            if not location:return None
                            url=urljoin(url,location)
                            continue
                        if response.status_code!=200:return None
                        content_type=response.headers.get('content-type','').lower()
                        if not any(t in content_type for t in ('text/html','text/plain','application/pdf')):return None
                        data=bytearray()
                        async for chunk in response.aiter_bytes():
                            data.extend(chunk)
                            if len(data)>2_000_000:return None
                        if 'application/pdf' in content_type:
                            from pypdf import PdfReader
                            from io import BytesIO
                            doc=PdfReader(BytesIO(data))
                            text=' '.join(p.extract_text() or '' for p in doc.pages[:20])
                        else:
                            soup=BeautifulSoup(bytes(data),'html.parser')
                            for tag in soup(['script','style','nav','footer','header','noscript']):tag.decompose()
                            from backend.services.source_ranking import valid_date
                            meta=soup.select_one('meta[property="article:published_time"], meta[name="date"], meta[name="DC.date.issued"]')
                            date=valid_date(meta.get('content')) if meta else valid_date(date)
                            if not date:
                                posted=re.search(r'Posted On:\s*(\d{1,2} [A-Z]{3} \d{4})',soup.get_text(' ',strip=True),re.I)
                                if posted:
                                    try:date=valid_date(datetime.strptime(posted.group(1),'%d %b %Y').date().isoformat())
                                    except ValueError:pass
                            content=soup.select_one('#divContent, .innner-page-main-about-us-content-right-part, article, main') or soup
                            text=content.get_text(' ',strip=True)
                            if not title and soup.title:title=soup.title.get_text(' ',strip=True)[:200]
                        text=re.sub(r'\s+',' ',text).strip()
                        if len(text)<100 or re.search(r'captcha|access denied|request rejected|verify you are human',text[:500],re.I):return None
                        item=EvidenceItem(source_id=source_id or 'web-'+sha256(original)[:12],url=url,publisher=publisher or host,title=title or host,document_date=date,evidence_text=text[:700],sha256_hash=sha256(text),retrieved_at_utc=utcnow())
                        result={'evidence':item,'text':text[:40000]}
                        if len(_CACHE)>=128:_CACHE.pop(next(iter(_CACHE)))
                        _CACHE[key]=(time.monotonic(),result)
                        return result
    except Exception:
        # No provider response bodies, submitted text or credentials enter logs.
        return None
    return None
