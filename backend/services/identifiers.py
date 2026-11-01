"""Limited syntax/context checks. No subscriber, carrier or payee ownership lookup."""
import re
from urllib.parse import urlparse
from backend.schemas import PhoneFinding,UpiFinding,MessagingLink,IdentifierFindings
PHONE=re.compile(r'(?<![\w])(?:\+\d(?:[\d ()-]{6,22}\d)|(?:[6-9]\d{9})|1930)(?!\w)')
UPI=re.compile(r'(?<![\w@])([a-zA-Z0-9][a-zA-Z0-9._-]{0,255}@[a-zA-Z][a-zA-Z0-9.-]{1,63})(?![\w@])')
PLATFORMS={'wa.me':'WhatsApp','chat.whatsapp.com':'WhatsApp','whatsapp.com':'WhatsApp','www.whatsapp.com':'WhatsApp','api.whatsapp.com':'WhatsApp','t.me':'Telegram','telegram.me':'Telegram','telegram.dog':'Telegram'}
PLATFORM_PATTERN=r'(?:(?:https?://)?(?:www\.)?(?:wa\.me|chat\.whatsapp\.com|api\.whatsapp\.com|whatsapp\.com|t\.me|telegram\.me|telegram\.dog)(?=[/?#\s,;!)]|$)(?:[/?#][^\s<>"\']*)?)'
AUTHORITY=r'\b(?:CBI|RBI|police|customs|government|DoT|TRAI|SEBI)\b|पुलिस|सरकार|ಸರ್ಕಾರ|ಪೊಲೀಸ್'
COUNTRY_LENGTHS={'91':{10},'1':{10},'44':{10},'61':{9},'971':{9},'65':{8},'92':{10},'49':set(range(7,12)),'33':{9},'81':{9,10},'86':{11}}
PAYMENT=r'\b(?:pay|payment|transfer|deposit|fee|collect|refund|safe account)\b|भुगतान|पैसे|ಹಣ|ಪಾವತಿ'
def phone_tokens(text):
    values=[m.group().rstrip(' -') for m in PHONE.finditer(text)]
    for m in re.finditer(r'\b(?:call|phone|contact|number)\s*[:=]?\s+(\+?[\d ()-]{3,25})(?!\d)',text,re.I):
        raw=m.group(1).strip()
        if raw and not any(raw in v for v in values):values.append(raw)
    return list(dict.fromkeys(values))
def upi_tokens(text):return list(dict.fromkeys(m.group().rstrip('.,;!?)') for m in UPI.finditer(text) if '.' not in m.group().rstrip('.,;!?)').split('@')[1]))
def messaging_links(text):
    result=[]
    for m in re.finditer(r'(?<![\w.@-])'+PLATFORM_PATTERN,text,re.I):
        raw=m.group().rstrip('.,;!?)');url=raw if re.match('https?://',raw,re.I) else 'https://'+raw
        host=(urlparse(url).hostname or '').lower()
        if host in PLATFORMS:
            result.append(MessagingLink(original=raw,normalized=url,platform=PLATFORMS[host],invite=host=='chat.whatsapp.com' or '/joinchat/' in url or '/+' in url,warning='Messaging destination; platform identity does not authenticate a person or group. Never opened or joined by Nivaar.'))
    return result

def analyze_identifiers(text):
    phones=[]
    for raw in phone_tokens(text):
        digits=re.sub(r'\D','',raw);normal=None;status='UNPARSED';foreign=False
        if raw=='1930':status='PUBLISHED_HELPLINE';normal='1930'
        elif raw.startswith('+') and 8<=len(digits)<=15 and digits[0]!='0':
            code=next((c for c in sorted(COUNTRY_LENGTHS,key=len,reverse=True) if digits.startswith(c) and len(digits)-len(c) in COUNTRY_LENGTHS[c]),None)
            if code and (code!='91' or digits[2] in '6789'):normal='+'+digits;status='PARSED';foreign=code!='91'
        # Bare national numbers remain ambiguous: never infer +91 from the app locale.
        warning='Format only. Caller ID can be spoofed; this does not authenticate an incoming caller.'
        if raw=='1930':warning='1930 is published for outgoing financial cyber-fraud reporting. An incoming caller displaying 1930 is not authenticated.'
        elif foreign and re.search(AUTHORITY,text,re.I):warning='An international displayed number appears with a claimed Indian authority. Verify independently; international calls alone are not fraud and caller ID can be spoofed.'
        elif status=='UNPARSED':warning='Ambiguous or malformed number; no country or identity inferred.'
        phones.append(PhoneFinding(original=raw,normalized=normal,status=status,international=foreign,warning=warning))
    upis=[]
    for raw in upi_tokens(text):
        local,handle=raw.split('@');valid=bool(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{1,255}',local) and re.fullmatch(r'[A-Za-z][A-Za-z0-9]{1,63}',handle))
        upis.append(UpiFinding(original=raw,local_part=local if valid else None,handle=handle if valid else None,status='PAYEE_NOT_VERIFIED' if valid else 'UNPARSED',payment_context=bool(re.search(PAYMENT,text,re.I)),reason='The handle is a routing namespace, not the recipient identity. No authorised ownership check is available.'))
    return IdentifierFindings(phone_numbers=phones,upi_ids=upis,messaging_links=messaging_links(text))

def compare_official_contact(text,phones,evidence):
    # Only an outgoing national financial-cyber-fraud helpline instruction has a
    # reviewed same-purpose/jurisdiction comparison. Never compare incoming IDs.
    if re.search(r'incoming|caller ID|called me|displayed|कॉलर|ಕರೆ ಬಂದ',text,re.I):return
    if not (re.search(r'call|contact',text,re.I) and re.search(r'national financial cyber.?fraud (?:reporting )?helpline',text,re.I)):return
    sources=[e for e in evidence if 'PRID=2290377' in e.url and '1930' in e.evidence_text and re.search(r'helpline',e.evidence_text,re.I)]
    if not sources:return
    for phone in phones:
        phone.official_comparison='MATCH_FORMAT' if phone.normalized=='1930' else 'MISMATCH'
        phone.evidence_ids=[e.evidence_id for e in sources]
        phone.warning='The requested outgoing national reporting helpline number '+('matches' if phone.normalized=='1930' else 'differs from')+' the fetched MHA publication of 1930. This does not identify a subscriber or authenticate an incoming caller.'
