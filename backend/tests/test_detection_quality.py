"""Action-risk regressions; this set is deliberately not a population benchmark."""
import json
from pathlib import Path
import pytest
from backend.services.claim_extractor import local_extract
from backend.services.verdict_engine import action_checks,choose_verdict
from backend.schemas import AnalyzeInput,DimensionChecks
DATA=json.loads(Path('backend/data/evaluation/action_quality_2026_11_01.json').read_text())
@pytest.mark.parametrize('case',DATA['cases'],ids=lambda c:c['id'])
def test_multilingual_action_quality(case):
    x=local_extract(case['text'],'voice',False);action,high=action_checks(x)
    verdict,risk=choose_verdict(DimensionChecks(authority='UNVERIFIED',requested_action=action,destination='NOT_PROVIDED'),high)
    assert (verdict=='SCAM')==case['scam']
    if case['scam']:assert risk=='HIGH'

@pytest.mark.asyncio
@pytest.mark.parametrize('llm_status',['ok','fallback'])
async def test_exact_user_transcript_without_official_documents_or_ai_verdict(monkeypatch,llm_status):
    from backend.services import investigation_agent as agent
    text=next(c['text'] for c in DATA['cases'] if c['id']=='user-kn-customs')
    async def extract(text,input_type,loss):return local_extract(text,input_type,loss),'',llm_status,'Controlled extraction fixture'
    async def search(*args):return [],'fallback','No documents in this controlled regression.'
    monkeypatch.setattr(agent,'extract_claims',extract);monkeypatch.setattr(agent,'search_sources',search)
    report=await agent.investigate(AnalyzeInput(text=text,input_type='voice'))
    assert report['verdict']=='SCAM';assert report['risk_level']=='HIGH'
    assert report['checks']['requested_action']=='DANGEROUS'
    assert 'personal or private account' in report['assessments']['requested_action']['reason']
    assert report['evidence']==[] # Never fabricate a source match to justify the action warning.

def test_conflicting_public_claims_cannot_neutralise_dangerous_payment():
    checks=DimensionChecks(authority='UNVERIFIED',requested_action='DANGEROUS',destination='NOT_PROVIDED')
    assert choose_verdict(checks,conflict=True)==('SCAM','HIGH')

@pytest.mark.parametrize('text',[
    'Customs never asks you to pay into a personal account. Pay customs duty using the official portal.',
    'Pay the loan processing fee through the official bank portal to release your loan.',
    'Do not worry. Share your OTP with me to verify the account.',
])
def test_additional_unseen_wording(text):
    action,_=action_checks(local_extract(text,'voice',False))
    expected='DANGEROUS' if text.startswith('Do not worry') else 'SUSPICIOUS'
    assert action==expected
