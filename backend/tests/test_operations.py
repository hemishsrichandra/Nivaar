import pytest,time
from backend import operations
from backend.services.source_ranking import rank_sources,valid_date

def test_signed_session_and_persistent_global_limit(monkeypatch):
 monkeypatch.setenv('GLOBAL_REQUESTS_PER_MINUTE','2')
 s=operations.session(None)
 assert operations.session(s)==s
 assert operations.session(s+'x')!=s+'x'
 assert operations.admit(s,10)
 assert operations.admit(operations.session(None),10)
 assert not operations.admit(operations.session(None),10) # Cookie reset does not bypass global budget.

def test_source_ranking_and_future_date():
 rows=rank_sources([{'url':'https://pib.gov.in/a','title':'monthly newsletter'},{'url':'https://pib.gov.in/b','title':'task job fraud deposit','date':'2999-01-01'}],'task job fraud')
 assert rows[0]['url'].endswith('/b');assert rows[0]['date'] is None
 assert valid_date('2025-03-06')=='2025-03-06'

def test_alerts_do_not_contain_inputs():
 operations.record('provider_failure','gemini_http_429')
 assert operations.snapshot()['alerts'][0]['label']=='gemini_http_429'

@pytest.mark.asyncio
async def test_quota_cooldown_prevents_network(monkeypatch):
 from backend.services import llm_client
 from backend.schemas import LLMExtraction
 monkeypatch.setattr(llm_client,'_cooldown_until',time.monotonic()+60)
 with pytest.raises(llm_client.ProviderError,match='quota_cooldown'):await llm_client.json_call('',{},LLMExtraction)

def test_monitor_endpoint_requires_token():
 from fastapi.testclient import TestClient
 from backend.main import app
 assert TestClient(app).get('/api/ops').status_code==403

def test_origin_rejection_and_proxy_origin_allowance():
 from fastapi.testclient import TestClient
 from backend.main import app
 c=TestClient(app)
 assert c.post('/api/analyze',headers={'origin':'https://attacker.example'},json={}).status_code==403
 assert c.post('/api/analyze',headers={'origin':'http://localhost:3000'},json={}).status_code==422

def test_free_tier_budget(monkeypatch):
 monkeypatch.setenv('LLM_CALLS_PER_MINUTE','1')
 assert operations.provider_budget()
 assert not operations.provider_budget()

def test_source_derived_regressions():
 import json
 from pathlib import Path
 from backend.services.claim_extractor import local_extract
 from backend.services.verdict_engine import action_checks,choose_verdict
 from backend.schemas import DimensionChecks
 for line in Path('backend/data/evaluation/cases.jsonl').read_text().splitlines():
  c=json.loads(line);action,risk=action_checks(local_extract(c['text'],'text',False))
  verdict,_=choose_verdict(DimensionChecks(authority='UNVERIFIED',requested_action=action,destination='NOT_PROVIDED'),risk)
  assert (verdict=='SCAM')==(c['label']=='scam'),c['id']
