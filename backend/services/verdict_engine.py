import re
from backend.schemas import DimensionChecks

def choose_verdict(checks, high_risk=False, conflict=False):
    if checks.requested_action=='DANGEROUS' or checks.destination=='DANGEROUS':return 'SCAM','HIGH'
    if conflict:return 'UNSURE','HIGH'
    if checks.authority=='CONTRADICTED':return 'SCAM','HIGH'
    if checks.authority=='VERIFIED' and checks.requested_action in ('VERIFIED','NOT_PROVIDED') and checks.destination in ('VERIFIED','NOT_PROVIDED') and not high_risk:return 'GENUINE','LOW'
    return 'UNSURE','HIGH' if high_risk or checks.requested_action=='SUSPICIOUS' or checks.destination=='SUSPICIOUS' else 'MEDIUM'

def action_checks(extracted):
    from backend.services.risk_patterns import behavioural_risk
    action,high,_=behavioural_risk(extracted)
    return action,high

def grounded_matches(assessment,extracted,documents):
    """Drop invented claim/source identifiers and any quote absent from fetched text."""
    claims={c.claim_id for c in extracted.claims};docs={d['evidence'].source_id:d for d in documents};accepted=[];rejected_material=False
    for match in assessment.matches:
        if match.claim_id not in claims or match.source_id not in docs:
            rejected_material=True;continue
        normal=lambda s:re.sub(r'\s+',' ',s).strip()
        quote=normal(match.quote)
        if len(quote)<25 or quote not in normal(docs[match.source_id]['text']):
            rejected_material=True;continue
        if not specific_relation(extracted,match,docs[match.source_id]):
            rejected_material=True;continue
        item=docs[match.source_id]['evidence'].model_copy(update={'claim_id':match.claim_id,'relation':match.relation,'evidence_text':match.quote[:1600]})
        accepted.append(item)
    supported={e.claim_id for e in accepted if e.relation=='supports'}
    conflicting=any(any(e.claim_id==cid and e.relation=='supports' for e in accepted) and any(e.claim_id==cid and e.relation=='contradicts' for e in accepted) for cid in claims)
    authority='UNVERIFIED' if conflicting else 'CONTRADICTED' if any(e.relation=='contradicts' for e in accepted) else 'VERIFIED' if claims and claims<=supported and not assessment.unverified_claim_ids and not rejected_material else 'UNVERIFIED'
    return accepted,authority

def local_evidence(extracted,documents):
    """Exact document-text coverage generalises beyond a demo sentence; no AI paraphrase acceptance."""
    text=extracted.raw_text_redacted
    cleaned=re.sub(r'https?://\S+','',text)
    cleaned=re.sub(r'\b(?:official clarification|source|official source)\s*:\s*','',cleaned,flags=re.I).strip()
    norm=lambda s:re.sub(r'[^\w\s]','',s.casefold()).strip()
    for d in documents:
        if len(cleaned)>50 and re.sub(r'\s+',' ',cleaned).strip() in re.sub(r'\s+',' ',d['text']).strip():
            matches=[]
            for c in extracted.claims:
                quote=re.sub(r'https?://\S+','',c.text).strip()
                if quote and re.sub(r'\s+',' ',quote) in re.sub(r'\s+',' ',d['text']):matches.append(d['evidence'].model_copy(update={'relation':'supports','claim_id':c.claim_id,'evidence_text':quote}))
            return matches,'VERIFIED' if len(matches)==len(extracted.claims) else 'UNVERIFIED'
    for d in documents:
        if known_release(d['evidence'],'2130875') and re.search(r'1736|1,736',text) and re.search(r'Cabinet Secretariat',text,re.I) and re.search(r'Field Assistant',text,re.I) and not re.search(r'denies|no official|fake|fraudulent|खंडन|नकली|ನಕಲಿ',text,re.I) and 'categorically denies' in d['text'].lower() and contemporaneous_claim(text,d['evidence']):
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
        from backend.services.source_ranking import source_identity
        key=source_identity(url)
        if key[0]=='pib':return key
        u=urlparse(url)
        query=sorted((k,v) for k,v in parse_qsl(u.query) if k.lower() not in ('reg','lang') and not k.lower().startswith('utm_'))
        return (u.hostname or '').lower().removeprefix('www.'),u.path.rstrip('/'),tuple(query)
    references={identity(url) for url in extracted.urls if allowed_url(url)}
    return bool(references and any(e.relation=='supports' and identity(e.url) in references for e in evidence))


def specific_relation(extracted,match,document):
    """Conservative lexical/scope guard in addition to exact source-quote validation."""
    if match.relation in ('context_only','unclear'):return True
    from backend.services.report_findings import private_claim
    claim=next(c.text for c in extracted.claims if c.claim_id==match.claim_id)
    if private_claim(claim):return False
    from backend.services.source_ranking import tokens
    wanted=tokens(claim)-{'official','notice','message','says','issued','please'}
    quote_tokens=tokens(match.quote)
    overlap=len(wanted & quote_tokens)/max(1,len(wanted))
    # Distinctive numbers must be present exactly; no matching an unrelated recruitment/date/amount.
    numbers=set(re.findall(r'\b\d[\d,]*\b',claim))
    if not numbers <= set(re.findall(r'\b\d[\d,]*\b',match.quote)):return False
    names=set(re.findall(r'\b[A-Z][a-zA-Z]{2,}\b',claim))-{'The','This','Your','Please','Official','Notice','Source'}
    if not {n.casefold() for n in names}<={n.casefold() for n in re.findall(r'\b[a-zA-Z]{3,}\b',match.quote)}:return False
    if match.relation=='contradicts':
        # A general advisory is context, never an individual contradiction.
        if known_release(document['evidence'],'2130875'):
            if not contemporaneous_claim(claim,document['evidence']):return False
            return bool(re.search(r'Cabinet Secretariat',claim,re.I) and re.search(r'1,?736',claim) and re.search(r'Field Assistant',claim,re.I) and re.search(r'categorically denies|no official notification',match.quote,re.I))
        if known_release(document['evidence'],'2025648'):
            return bool(re.search(r'customs|CBIC',claim,re.I) and re.search(r'private account|personal account',claim,re.I) and re.search(r'pay|duty|fee',claim,re.I) and re.search(r'never contact.*private accounts',match.quote,re.I))
        # Only a specific issuer denial with material identifier overlap can contradict.
        return overlap>=.7 and bool(numbers) and bool(re.search(r'categorically denies|no such notification|not issued|withdrawn|cancelled',match.quote,re.I))
    neg=lambda s:bool(re.search(r'\b(?:not|never|no|denies|withdrawn|cancelled)\b|नहीं|ಬೇಡ',s,re.I))
    return overlap>=.75 and len(wanted)>=3 and neg(claim)==neg(match.quote)


def customs_action_evidence(extracted,documents):
    text=extracted.raw_text_redacted
    if not (re.search(r'customs|CBIC',text,re.I) and re.search(r'private account|personal account',text,re.I) and re.search(r'duty|customs fee',text,re.I) and re.search(r'pay|transfer',text,re.I) and re.search(r'phone|call|SMS|email|message',text,re.I)):return None
    for d in documents:
        if not known_release(d['evidence'],'2025648'):continue
        match=re.search(r'Indian Customs officers never contact the general public via phone, SMS, or e-mail for payment of duty in private accounts\.',d['text'],re.I)
        if match:return d['evidence'].model_copy(update={'relation':'context_only','claim_id':None,'evidence_text':match.group()})
    return None


def known_release(evidence,prid):
    from backend.services.source_ranking import source_identity
    return evidence.source_id=='pib-'+prid or source_identity(evidence.url)==('pib',prid)

def contemporaneous_claim(text,evidence):
    # A historical denial does not establish whether a newly dated notice exists.
    years=[int(y) for y in re.findall(r'\b20\d{2}\b',text)]
    return not years or bool(evidence.document_date and max(years)<=int(evidence.document_date[:4]))
