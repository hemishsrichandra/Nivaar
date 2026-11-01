import base64
import httpx
from backend.config import settings
from backend.services.llm_client import ProviderError
from backend.services.input_parser import redact
LANG={'en':'en-IN','hi':'hi-IN','kn':'kn-IN'}
async def transcribe(data,filename,content_type,language):
    if not settings.sarvam_key:raise ProviderError('sarvam','not_configured')
    try:
        async with httpx.AsyncClient(timeout=60,trust_env=False) as client:
            r=await client.post('https://api.sarvam.ai/speech-to-text',headers={'api-subscription-key':settings.sarvam_key},files={'file':(filename,data,content_type)},data={'model':settings.stt_model,'mode':'transcribe','language_code':LANG[language]})
            if r.status_code>=400:raise ProviderError('sarvam',f'http_{r.status_code}')
            text=r.json().get('transcript','')
            if not text.strip():raise ProviderError('sarvam','empty_transcript')
            return {'text':redact(text),'language_code':r.json().get('language_code',LANG[language]),'provider':'sarvam','redacted':True}
    except httpx.HTTPError:raise ProviderError('sarvam','timeout_or_connection_error') from None
async def speak(text,language):
    if not settings.sarvam_key:raise ProviderError('sarvam','not_configured')
    try:
        async with httpx.AsyncClient(timeout=45,trust_env=False) as client:
            r=await client.post('https://api.sarvam.ai/text-to-speech',headers={'api-subscription-key':settings.sarvam_key},json={'text':redact(text),'language_code':LANG[language],'model':settings.tts_model,'speaker':settings.speaker,'speech_sample_rate':22050})
            if r.status_code>=400:raise ProviderError('sarvam',f'http_{r.status_code}')
            audios=r.json().get('audios',[])
            if not audios:raise ProviderError('sarvam','empty_audio')
            return base64.b64decode(audios[0],validate=True)
    except (httpx.HTTPError,ValueError):raise ProviderError('sarvam','invalid_response_or_timeout') from None
