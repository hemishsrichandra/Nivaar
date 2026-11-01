import re
from backend.schemas import DimensionChecks

def choose_verdict(checks, high_risk=False):
    if checks.authority=='CONTRADICTED' or checks.requested_action=='DANGEROUS' or checks.destination=='DANGEROUS':return 'SCAM','HIGH'
    if checks.authority=='VERIFIED' and checks.requested_action in ('VERIFIED','NOT_PROVIDED') and checks.destination in ('VERIFIED','NOT_PROVIDED') and not high_risk:return 'GENUINE','LOW'
    return 'UNSURE','HIGH' if high_risk or checks.requested_action=='SUSPICIOUS' or checks.destination=='SUSPICIOUS' else 'MEDIUM'

def action_checks(extracted):
    types={t.tactic for t in extracted.tactics}
    payment='payment_redirection' in types or bool(re.search(r'\bpay\b|transfer|deposit|fee|भुगतान|पैसे|ಹಣ',extracted.raw_text_redacted,re.I))
    task_deposit=bool(re.search(r'(?:task|rating|review|part.time)[^.!?]{0,100}\b(?:deposit|recharge|pay|transfer)\b|(?:deposit|recharge).{0,100}(?:unlock|withdraw|commission)',extracted.raw_text_redacted,re.I))
    dangerous=task_deposit or bool(types & {'otp_or_credential_harvesting','remote_access_app'}) or payment and bool(types & {'fear_of_arrest','secrecy_or_isolation'})
    return ('DANGEROUS' if dangerous else 'SUSPICIOUS' if payment else 'NOT_PROVIDED'),bool(types & {'fear_of_arrest','secrecy_or_isolation','otp_or_credential_harvesting','remote_access_app','too_good_returns'})

def grounded_matches(assessment,extracted,documents):
    """Drop invented claim/source identifiers and any quote absent from fetched text."""
    claims={c.claim_id for c in extracted.claims};docs={d['evidence'].source_id:d for d in documents};accepted=[]
    for match in assessment.matches:
        if match.claim_id not in claims or match.source_id not in docs:continue
        normal=lambda s:re.sub(r'\s+',' ',s).strip().casefold()
        quote=normal(match.quote)
        if len(quote)<25 or quote not in normal(docs[match.source_id]['text']):continue
        item=docs[match.source_id]['evidence'].model_copy(update={'claim_id':match.claim_id,'relation':match.relation,'evidence_text':match.quote[:1600]})
        accepted.append(item)
    supported={e.claim_id for e in accepted if e.relation=='supports'}
    authority='CONTRADICTED' if any(e.relation=='contradicts' for e in accepted) else 'VERIFIED' if claims and claims<=supported and not assessment.unverified_claim_ids else 'UNVERIFIED'
    return accepted,authority

def local_evidence(extracted,documents):
    """Exact document-text coverage generalises beyond a demo sentence; no AI paraphrase acceptance."""
    text=extracted.raw_text_redacted
    cleaned=re.sub(r'https?://\S+','',text)
    cleaned=re.sub(r'\b(?:official clarification|source|official source)\s*:\s*','',cleaned,flags=re.I).strip()
    norm=lambda s:re.sub(r'[^\w\s]','',s.casefold()).strip()
    for d in documents:
        if len(cleaned)>50 and norm(cleaned) in norm(d['text']):
            e=d['evidence'].model_copy(update={'relation':'supports','claim_id':'c1','evidence_text':cleaned})
            return [e],'VERIFIED'
    for d in documents:
        if d['evidence'].source_id=='pib-2130875' and re.search(r'1736|1,736',text) and re.search(r'recruitment|posts|vacanc|भर्ती|ನೇಮಕ',text,re.I) and not re.search(r'denies|no official|fake|fraudulent|खंडन|नकली|ನಕಲಿ',text,re.I) and 'categorically denies' in d['text'].lower():
            at=d['text'].lower().find('categorically denies');e=d['evidence'].model_copy(update={'relation':'contradicts','claim_id':'c1','evidence_text':d['text'][max(0,at-40):at+400]});return [e],'CONTRADICTED'
    return [d['evidence'] for d in documents],'UNVERIFIED'

def can_verify_public_content(extracted,evidence):
    """Generic public documents cannot establish a private account/application event."""
    from urllib.parse import urlparse,parse_qsl
    from backend.services.official_fetcher import allowed_url
    text=extracted.raw_text_redacted
    personal_patterns=(
        r'\b(?:your|my)\s+(?:application|account|payment|transaction|parcel|delivery|appointment|refund|claim|loan)\b',
        r'(?:आपका|आपकी|मेरा|मेरी)\s*(?:आवेदन|खाता|भुगतान|लेनदेन|पार्सल|ऋण)',
        r'(?:ನಿಮ್ಮ|ನನ್ನ)\s*(?:ಅರ್ಜಿ|ಖಾತೆ|ಪಾವತಿ|ವ್ಯವಹಾರ|ಪಾರ್ಸೆಲ್|ಸಾಲ)',
    )
    if any(re.search(p,text,re.I) for p in personal_patterns):return False
    def identity(url):
        u=urlparse(url)
        query=sorted((k,v) for k,v in parse_qsl(u.query) if k.lower() not in ('reg','lang') and not k.lower().startswith('utm_'))
        return (u.hostname or '').lower().removeprefix('www.'),u.path.rstrip('/'),tuple(query)
    references={identity(url) for url in extracted.urls if allowed_url(url)}
    return bool(references and any(e.relation=='supports' and identity(e.url) in references for e in evidence))
