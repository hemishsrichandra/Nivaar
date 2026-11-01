"""Deterministic report projections; evidence coverage never participates in verdict selection."""
import re,hashlib
from backend.schemas import ClaimFinding,DimensionAssessment,EvidenceCoverage,CoverageComponent
from backend.services.identifiers import analyze_identifiers

def private_claim(text):
    return bool(re.search(r'\b(?:your|my)\s+(?:application|account|payment|transaction|parcel|delivery|appointment|refund|claim|loan|SIM)\b|(?:आपका|आपकी|मेरा|मेरी)\s*(?:आवेदन|खाता|भुगतान|पार्सल|सिम)|(?:ನಿಮ್ಮ|ನನ್ನ)\s*(?:ಅರ್ಜಿ|ಖಾತೆ|ಪಾವತಿ|ಪಾರ್ಸೆಲ್|ಸಿಮ್)',text,re.I))

def evidence_id(e):return 'e-'+hashlib.sha256((e.source_id+'|'+str(e.claim_id)+'|'+e.relation+'|'+e.evidence_text).encode()).hexdigest()[:20]

def findings(extracted,evidence,checks,statuses,url_notes):
    for e in evidence:e.evidence_id=evidence_id(e)
    ledger=[];conflicts=[]
    for c in extracted.claims:
        items=[e for e in evidence if e.claim_id==c.claim_id and e.relation in ('supports','contradicts')]
        relations={e.relation for e in items}
        conflict=len(relations)>1
        if conflict:conflicts.append(c.claim_id)
        private=private_claim(c.text)
        status='UNVERIFIABLE' if private or conflict else 'CONTRADICTED' if 'contradicts' in relations else 'SUPPORTED' if 'supports' in relations else 'NOT_FOUND'
        reason='Public sources cannot establish this private event.' if private else 'Official passages disagree; both are shown. No precedence rule resolves this conflict.' if conflict else 'Relevant fetched passage directly addresses this claim.' if items else 'No sufficiently specific matching passage was located. This does not mean the claim is false.'
        ledger.append(ClaimFinding(claim_id=c.claim_id,text=c.text,category=c.claim_type,status=status,explanation=reason,evidence_ids=[e.evidence_id for e in items],limitations=['Sender identity is not authenticated.']+(['Checks may be incomplete; inspect provider availability.'] if statuses.get('llm')!='ok' else [])))
    authority_ids=[e.evidence_id for e in evidence if e.relation in ('supports','contradicts')]
    assessments={
     'authority':DimensionAssessment(status=checks.authority,reason='Exact public content is corroborated by the cited official material.' if checks.authority=='VERIFIED' else 'Specific official evidence contradicts a material claim.' if checks.authority=='CONTRADICTED' else 'The precise issuer/content relationship has not been established.',evidence_ids=authority_ids,limitation='A document match does not authenticate the sender or a private account.'),
     'requested_action':DimensionAssessment(status=checks.requested_action,reason='A credential/remote access request or coercive payment pattern was found.' if checks.requested_action=='DANGEROUS' else 'Requested action remains unverified.' if checks.requested_action!='NOT_PROVIDED' else 'No actionable instruction was identified.',limitation='Pattern inference is separate from an issuer-confirmed process.'),
     'destination':DimensionAssessment(status=checks.destination,reason=' '.join(url_notes) or ('No destination was supplied.' if checks.destination=='NOT_PROVIDED' else 'Official-domain syntax was checked; purpose and recipient identity remain unverified.'),limitation='No phone subscriber or UPI ownership lookup. Absence from a threat list does not establish safety.')}
    ids=analyze_identifiers(extracted.raw_text_redacted)
    from backend.services.identifiers import compare_official_contact
    compare_official_contact(extracted.raw_text_redacted,ids.phone_numbers,evidence)
    # Exact customs/private-account contradiction is the only newly supported payment mismatch.
    for upi in ids.upi_ids:
        matches=[e for e in evidence if e.source_id=='pib-2025648' and e.relation in ('contradicts','context_only') and 'private account' in e.evidence_text.lower()]
        if matches and re.search(r'private account|personal account',extracted.raw_text_redacted,re.I):
            upi.status='MISMATCH';upi.reason='The submitted private-account duty instruction conflicts with CBIC guidance; recipient ownership remains unknown.';upi.evidence_ids=[e.evidence_id for e in matches]
    action_ids=[e.evidence_id for e in evidence if e.source_id=='pib-2025648' and e.evidence_text.startswith('Indian Customs officers never contact') and e.evidence_text.endswith('private accounts.') and checks.requested_action=='DANGEROUS']
    if action_ids:
        assessments['requested_action'].evidence_ids=action_ids
        assessments['requested_action'].reason='This private-account customs-duty demand conflicts with the cited CBIC process warning.'
    # Coverage only credits scoped fetched relations, never rule-only danger flags.
    completed=sum(bool(c.evidence_ids) and (c.status in ('SUPPORTED','CONTRADICTED') or c.claim_id in conflicts) for c in ledger)/len(ledger) if ledger else 0
    authority=1.0 if authority_ids and (checks.authority in ('VERIFIED','CONTRADICTED') or bool(conflicts)) else .5 if authority_ids else 0
    dest_app=bool(extracted.urls or ids.upi_ids or ids.phone_numbers)
    action_app=checks.requested_action!='NOT_PROVIDED' or bool(extracted.requested_actions)
    if statuses.get('llm')!='ok' or statuses.get('evidence_comparison')!='ok':completed=min(completed,.5)
    components=[CoverageComponent(name='Material claims',weight=30,applicable=True,completed=completed,explanation='Fraction with relevant validated source relations; capped at partial if AI extraction/comparison was unavailable.'),CoverageComponent(name='Authority',weight=25,applicable=True,completed=authority,explanation='Scoped source relation; document identity does not authenticate a caller.'),CoverageComponent(name='Requested action',weight=25,applicable=action_app,completed=1 if action_ids else 0,explanation='Cited CBIC guidance contradicts this exact requested process.' if action_ids else 'Local risk patterns do not establish the issuer’s actual procedure.'),CoverageComponent(name='Destination',weight=20,applicable=dest_app,completed=0,explanation='Syntax/reputation checks do not verify the recipient or purpose.')]
    denominator=sum(c.weight for c in components if c.applicable)
    score=round(100*sum(c.weight*c.completed for c in components if c.applicable)/denominator) if denominator else None
    return ledger,assessments,ids,EvidenceCoverage(score=score,components=components),conflicts
