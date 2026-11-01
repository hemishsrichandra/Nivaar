import re
from urllib.parse import urlparse
import httpx, tldextract
from backend.config import settings
extract_domain=tldextract.TLDExtract(suffix_list_urls=(),cache_dir=None)
async def check_urls(urls,text):
    status='NOT_PROVIDED' if not urls else 'VERIFIED'
    notes=[]
    gov_claim=bool(re.search(r'India Post|police|CBI|Cabinet Secretariat|Ministry|court|tax department|सरकार|पुलिस|ಸರ್ಕಾರ|ಪೊಲೀಸ್',text,re.I))
    for url in urls:
        u=urlparse(url);host=(u.hostname or '').lower()
        from backend.services.identifiers import PLATFORMS
        platform=host in PLATFORMS
        official=host.endswith(('.gov.in','.nic.in')) or host in ('rbi.org.in','www.rbi.org.in','sebi.gov.in','www.sebi.gov.in')
        registered=extract_domain(host).top_domain_under_public_suffix
        short_kyc=host in ('bit.ly','tinyurl.com','t.co','cutt.ly','is.gd','rb.gy') and bool(re.search(r'KYC|challan',text,re.I))
        if short_kyc or (gov_claim and not official and not platform and bool(re.search(r'indiapost|rbi|cbi|gov|police',host,re.I))) or re.search(r'\.apk(?:$|\?)',u.path,re.I) or u.username or u.password:
            status='DANGEROUS';notes.append(f'{registered or host}: government mismatch, credential-bearing URL or APK destination.')
        elif platform:
            risky=gov_claim or bool(re.search(r'pay|transfer|deposit|OTP|password|arrest',text,re.I))
            if status not in ('DANGEROUS','SUSPICIOUS'):
                status='SUSPICIOUS' if risky else 'UNVERIFIED'
            notes.append(f'{host}: messaging platform; recipient/group identity is unverified. The platform alone is not a scam signal.')
        elif not official or u.scheme!='https' or 'xn--' in host or not host.isascii():
            risky=bool(re.search(r'pay|transfer|deposit|OTP|password|arrest|KYC',text,re.I))
            structural=u.scheme!='https' or 'xn--' in host or not host.isascii()
            if status not in ('DANGEROUS','SUSPICIOUS'):status='SUSPICIOUS' if risky or structural else 'UNVERIFIED'
            notes.append(f'{registered or host}: unverified destination.')
    provider='not_configured'
    from backend.services.llm_client import reserve_operation
    if settings.safe_browsing_key and urls and reserve_operation():
        try:
            async with httpx.AsyncClient(timeout=8,trust_env=False) as client:
                response=await client.post('https://safebrowsing.googleapis.com/v4/threatMatches:find',params={'key':settings.safe_browsing_key},json={'client':{'clientId':'nivaar','clientVersion':'1.0'},'threatInfo':{'threatTypes':['MALWARE','SOCIAL_ENGINEERING','UNWANTED_SOFTWARE'],'platformTypes':['ANY_PLATFORM'],'threatEntryTypes':['URL'],'threatEntries':[{'url':u} for u in urls]}})
                response.raise_for_status()
                if response.json().get('matches'):status='DANGEROUS';notes.append('Google Safe Browsing returned a threat-list match.')
                provider='live_checked'
        except (httpx.HTTPError,ValueError):provider='unavailable'
    return status,notes,provider
