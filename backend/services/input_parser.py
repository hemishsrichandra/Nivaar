import re
from backend.schemas import ExtractionResult

def redact(text: str) -> str:
    preserved=[]
    def protect(m):
        if not 8<=len(re.sub(r'\D','',m.group()))<=15:return m.group()
        preserved.append(m.group());return '[PHONE_TOKEN_'+str(len(preserved)-1)+']'
    text=re.sub(r'\+\d[\d -]{6,20}\d(?!\d)',protect,text)
    text = re.sub(r'\b(?:\d[ -]?){13,19}\b','[REDACTED_CARD]',text)
    text = re.sub(r'\b\d{4}[ -]?\d{4}[ -]?\d{4}\b','[REDACTED_ID]',text)
    text = re.sub(r'\b\d{6}\b','[REDACTED_OTP]',text)
    for i,raw in enumerate(preserved):text=text.replace('[PHONE_TOKEN_'+str(i)+']',raw)
    return text

def entities(text: str):
    from backend.services.identifiers import phone_tokens,upi_tokens,messaging_links
    urls = list(dict.fromkeys((m if re.match(r'https?://',m,re.I) else 'https://'+m).rstrip('.,;!?)') for m in re.findall(r'https?://[^\s<>"\']+|\b(?:[a-z0-9-]+\.)+(?:top|xyz|click|com|in|org|net)(?:/[^\s<>"\']*)?',text,re.I)))
    urls=list(dict.fromkeys(urls+[m.normalized for m in messaging_links(text)]))
    return {'urls':urls[:20],'upi_ids':upi_tokens(text),'phone_numbers':phone_tokens(text),'amounts':re.findall(r'(?:₹|Rs\.?|INR)\s?[\d,]+',text,re.I),'deadlines':re.findall(r'within \d+ (?:minutes|hours|days)|आज ही|ತಕ್ಷಣ',text,re.I)}

def detect_language(text):
    return 'kn' if re.search(r'[\u0c80-\u0cff]',text) else 'hi' if re.search(r'[\u0900-\u097f]',text) else 'en'

def search_safe(text):
    text=redact(text)
    text=re.sub(r'https?://\S+|\b\S+@\S+|\+?\d[\d -]{7,}\d',' ',text)
    return re.sub(r'\s+',' ',text).strip()[:350]
