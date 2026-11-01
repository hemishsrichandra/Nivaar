"""Relevance first; dates are metadata, never proof of validity."""
import re
from datetime import date,datetime,timezone
from urllib.parse import urlparse
STOP={'this','that','with','from','your','have','will','please','official','source','https','www','gov','com','the','and','for'}
def tokens(text):return {t for t in re.findall(r'[^\W_]{3,}',text.casefold()) if t not in STOP}
def valid_date(value):
    try:
        d=date.fromisoformat(str(value)[:10])
        return d.isoformat() if date(1990,1,1)<=d<=datetime.now(timezone.utc).date() else None
    except (ValueError,TypeError):return None
def rank_sources(items,query,urls=()):
    wanted=tokens(query); seen={}
    for item in items:
        url=item['url']; text=' '.join(str(item.get(k) or '') for k in ('title','family','description'))
        overlap=len(wanted & tokens(text))/max(1,len(wanted))
        score=overlap*10+(20 if url in urls else 0)
        # Generic collections commonly match keywords without addressing the claim.
        if re.search(r'roundup|newsletter|news clipping|monthly bulletin',text,re.I):score-=5
        d=valid_date(item.get('date')); item={**item,'date':d}
        if d:score+=max(0,1-(date.today()-date.fromisoformat(d)).days/3650)
        host=urlparse(url).hostname
        key=(host.removeprefix('www.') if host else '',urlparse(url).path,urlparse(url).query)
        if key not in seen or score>seen[key][0]:seen[key]=(score,item)
    return [v[1] for v in sorted(seen.values(),key=lambda v:v[0],reverse=True)][:3]
