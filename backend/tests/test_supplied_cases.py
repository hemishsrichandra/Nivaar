"""Regression cases provided by the owner; fixtures, not real-world accuracy."""
import json
from pathlib import Path
import pytest
from backend.services.claim_extractor import local_extract
from backend.services.url_checker import check_urls
from backend.services.verdict_engine import action_checks,choose_verdict,local_evidence
from backend.services.source_ranking import rank_sources,source_identity
from backend.schemas import DimensionChecks,EvidenceItem
CASES={c['id']:c for c in json.loads(Path('backend/data/evaluation/user_supplied_2026_11_01.json').read_text(encoding='utf-8'))}
@pytest.mark.parametrize('ident',[1,2,4,5,7,9,10,11])
@pytest.mark.asyncio
async def test_owner_cases_local_rules(ident):
 c=CASES[ident];x=local_extract(c['text'],'text',False)
 destination,_,_=await check_urls(x.urls,c['text']);action,high=action_checks(x)
 verdict,risk=choose_verdict(DimensionChecks(authority='UNVERIFIED',requested_action=action,destination=destination),high)
 assert verdict==c['expected_verdict'];assert risk in c['expected_risks']

def test_pib_variants_are_one_source_and_keep_registry_metadata():
 registry={'id':'pib-2130875','url':'https://www.pib.gov.in/PressReleasePage.aspx?PRID=2130875','title':'Recruitment denial','date':'2025-05-23','anchor':'categorically denies'}
 web={'url':'https://pib.gov.in/Pressreleaseshare.aspx?lang=2&reg=48&PRID=2130875','title':'Cabinet Secretariat Field Assistant recruitment official denial'}
 results=rank_sources([registry,web],'Cabinet Secretariat Field Assistant recruitment')
 assert len(results)==1;assert results[0]['id']=='pib-2130875';assert results[0]['anchor']=='categorically denies'
 assert source_identity('https://evil.com/?PRID=2130875')!=source_identity(registry['url'])

def test_old_denial_does_not_disprove_newly_dated_notice():
 quote='The Cabinet Secretariat categorically denies any such recruitment advertisement about 1736 Field Assistant posts.'
 e=EvidenceItem(source_id='web-random',url='https://pib.gov.in/Pressreleaseshare.aspx?PRID=2130875&lang=2',publisher='PIB',title='Unit fixture',document_date='2025-05-23',evidence_text=quote,sha256_hash='fixture',retrieved_at_utc='2026-11-01T00:00:00+00:00')
 x=local_extract(CASES[3]['text'],'text',False)
 assert local_evidence(x,[{'evidence':e,'text':quote}])[1]=='UNVERIFIED'
 old=local_extract('Cabinet Secretariat recruitment: 1736 Field Assistant posts open in 2025.','text',False)
 assert local_evidence(old,[{'evidence':e,'text':quote}])[1]=='CONTRADICTED'

@pytest.mark.parametrize('text',['Never share your bank PIN.','Do not share your banking password.'])
def test_extended_credential_patterns_still_honor_negation(text):assert action_checks(local_extract(text,'text',False))[0]=='NOT_PROVIDED'

@pytest.mark.parametrize('url',['https://example.org/','https://t.me/community','https://www.pib.gov.in/'])
@pytest.mark.asyncio
async def test_bare_link_is_not_proof_of_scam_or_authenticity(url):
 from backend.services.input_parser import is_link_only
 x=local_extract(url,'link',False);assert is_link_only(url,x.urls)
 dest,_,_=await check_urls(x.urls,url)
 assert dest in ('VERIFIED','UNVERIFIED')
 assert choose_verdict(DimensionChecks(authority='UNVERIFIED',requested_action='NOT_PROVIDED',destination=dest))==('UNSURE','MEDIUM')

def test_verified_pib_reference_survives_official_page_share_redirect():
 from backend.services.verdict_engine import can_verify_public_content
 x=local_extract(CASES[8]['text'],'text',False)
 e=EvidenceItem(source_id='pib-2130875',url='https://pib.gov.in/Pressreleaseshare.aspx?lang=2&reg=48&PRID=2130875',publisher='PIB',title='Fixture',evidence_text='Verified exact quotation fixture.',sha256_hash='fixture',retrieved_at_utc='2026-11-01T00:00:00+00:00',relation='supports')
 assert can_verify_public_content(x,[e])
 e.url='https://pib.gov.in/PressReleasePage.aspx?PRID=9999999'
 assert not can_verify_public_content(x,[e])
