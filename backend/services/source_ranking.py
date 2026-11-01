"""Relevance first; dates are metadata, never proof of validity."""
import re
from datetime import date,datetime,timezone
from urllib.parse import urlparse,parse_qsl
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
        key=source_identity(url)
        if key in seen:
            prior_score,prior=seen[key]
            registry=prior if prior.get('id') else item if item.get('id') else None
            winner=item if score>prior_score else prior
            if registry:
                winner={**winner,**{k:registry[k] for k in ('id','publisher','date','anchor','family','strength') if k in registry}}
            seen[key]=(max(score,prior_score),winner)
        else:seen[key]=(score,item)
    return [v[1] for v in sorted(seen.values(),key=lambda v:v[0],reverse=True)][:3]

def relevant_document(extracted,document):
    """Remove off-topic retrievals before they can become background evidence."""
    text=document['text'].casefold()
    rules={
      'customs_fraud':(r'customs|cbic',r'private account|\bdin\b|fraud|impersonat'),
      'sim_swap':(r'\bsim\b',r'swap|duplicate|replacement|fraud'),
      'loan_app_fraud':(r'lend|\bnbfc\b',r'digital|\bapp|\blsp\b|key fact'),
      'lottery_fraud':(r'lottery|prize',r'advance|fee|token|fraud'),
      'digital_arrest':(r'digital arrest',r'fraud|scam|police|payment'),
    }
    if extracted.script_family in rules:return all(re.search(p,text) for p in rules[extracted.script_family])
    return True


def source_identity(url):
    u=urlparse(url);host=(u.hostname or '').lower().removeprefix('www.')
    query={k.lower():v for k,v in parse_qsl(u.query)}
    if host=='pib.gov.in' and query.get('prid','').isdigit():return ('pib',query['prid'])
    return (host,u.path.rstrip('/'),tuple(sorted(parse_qsl(u.query))))
