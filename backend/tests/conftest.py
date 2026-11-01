import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import pytest
from backend.config import settings
@pytest.fixture(autouse=True)
def no_real_keys(monkeypatch):
    for key in ('gemini_key','openai_key','groq_key','sarvam_key','tavily_key','brave_key','safe_browsing_key','benchmark_token'):monkeypatch.setattr(settings,key,'')
    monkeypatch.setattr(settings,'provider','gemini');monkeypatch.setattr(settings,'model','');monkeypatch.setattr(settings,'require_live',False);monkeypatch.setattr(settings,'rate_limit',10000)
    from backend.main import requests
    requests.clear()
    from backend.services import official_fetcher,official_search,llm_client
    official_fetcher._CACHE.clear();official_search._CACHE.clear();llm_client._cooldown_until=0
    import tempfile
    from backend import operations
    monkeypatch.setattr(operations,'DB',str(Path(tempfile.mkdtemp())/'ops.sqlite'))
