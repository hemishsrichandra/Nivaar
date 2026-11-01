import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env')

@dataclass
class Settings:
    provider: str = os.getenv('LLM_PROVIDER', 'gemini').lower()
    model: str = os.getenv('LLM_MODEL', '')
    gemini_key: str = os.getenv('GEMINI_API_KEY', '')
    openai_key: str = os.getenv('OPENAI_API_KEY', '')
    groq_key: str = os.getenv('GROQ_API_KEY', '')
    tavily_key: str = os.getenv('TAVILY_API_KEY', '')
    brave_key: str = os.getenv('BRAVE_API_KEY', '')
    sarvam_key: str = os.getenv('SARVAM_API_KEY', '')
    stt_model: str = os.getenv('SARVAM_STT_MODEL', 'saaras:v3')
    tts_model: str = os.getenv('SARVAM_TTS_MODEL', 'bulbul:v3')
    speaker: str = os.getenv('SARVAM_SPEAKER', 'shubh')
    safe_browsing_key: str = os.getenv('GOOGLE_SAFE_BROWSING_KEY', '')
    require_live: bool = os.getenv('REQUIRE_LIVE_PROVIDERS', 'false').lower() == 'true'
    rate_limit: int = int(os.getenv('RATE_LIMIT_PER_MINUTE', '20'))
    concurrency: int = int(os.getenv('MAX_CONCURRENT_ANALYSES', '4'))
    report_ttl: int = int(os.getenv('REPORT_TTL_SECONDS', '3600'))
    benchmark_token: str = os.getenv('BENCHMARK_TOKEN', '')
    @property
    def llm_key(self):
        return {'gemini': self.gemini_key, 'openai': self.openai_key, 'groq': self.groq_key}.get(self.provider, '')
    @property
    def model_name(self):
        return self.model or {'gemini': 'gemini-2.5-flash', 'openai': 'gpt-4o-mini', 'groq': 'llama-3.3-70b-versatile'}.get(self.provider, '')
    def public_status(self):
        return {'llm': {'provider': self.provider, 'model': self.model_name, 'configured': bool(self.llm_key)}, 'search': {'provider': 'tavily' if self.tavily_key else 'brave' if self.brave_key else 'registry', 'configured': bool(self.tavily_key or self.brave_key)}, 'speech': {'provider': 'sarvam', 'configured': bool(self.sarvam_key)}, 'url_reputation': {'provider': 'google_safe_browsing', 'configured': bool(self.safe_browsing_key)}}
settings = Settings()
OFFICIAL_DOMAINS = ('pib.gov.in','rbi.org.in','sebi.gov.in','sancharsaathi.gov.in','cybercrime.gov.in','mha.gov.in','dot.gov.in','indiapost.gov.in','india.gov.in','cert-in.org.in','uidai.gov.in','npci.org.in','nic.gov.in','delhipolice.gov.in','megpolice.gov.in')
