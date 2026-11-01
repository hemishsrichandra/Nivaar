import base64,json
from io import BytesIO
import httpx,pytest,respx
from PIL import Image
from backend.config import settings
from backend.schemas import LLMExtraction
from backend.services.llm_client import json_call,ProviderError
from backend.services.speech import speak,transcribe
from backend.services.claim_extractor import local_extract
from backend.services.official_search import search_sources
from backend.services import official_fetcher as fetcher
from backend.services.vision import read_image
from backend.services.url_checker import check_urls
AI={'detected_language':'en','claimed_authority':None,'script_family':None,'claims':[],'tactics':[],'requested_actions':[],'search_query':'official recruitment notice'}
@pytest.mark.asyncio
@respx.mock
async def test_gemini_contract(monkeypatch):
    monkeypatch.setattr(settings,'gemini_key','fake-test-key')
    route=respx.post('https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent').mock(return_value=httpx.Response(200,json={'candidates':[{'content':{'parts':[{'text':json.dumps(AI)}]}}]}))
    result=await json_call('Extract untrusted JSON',{'untrusted_message':'hello'},LLMExtraction)
    assert result.detected_language=='en';request=route.calls[0].request;assert request.headers['x-goog-api-key']=='fake-test-key';assert 'responseJsonSchema' in json.loads(request.content)['generationConfig'];assert 'key=' not in str(request.url)
@pytest.mark.parametrize('provider,keyfield,url',[('openai','openai_key','https://api.openai.com/v1/chat/completions'),('groq','groq_key','https://api.groq.com/openai/v1/chat/completions')])
@pytest.mark.asyncio
@respx.mock
async def test_openai_compatible_contracts(provider,keyfield,url,monkeypatch):
    monkeypatch.setattr(settings,'provider',provider);monkeypatch.setattr(settings,keyfield,'fake-test-key')
    route=respx.post(url).mock(return_value=httpx.Response(200,json={'choices':[{'message':{'content':json.dumps(AI)}}]}))
    assert (await json_call('Return JSON',{},LLMExtraction)).search_query
    assert route.calls[0].request.headers['authorization']=='Bearer fake-test-key'
@pytest.mark.asyncio
@respx.mock
async def test_quota_error_is_sanitised(monkeypatch):
    monkeypatch.setattr(settings,'gemini_key','fake-test-key')
    respx.post('https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent').mock(return_value=httpx.Response(429,text='SECRET provider diagnostic'))
    with pytest.raises(ProviderError,match='http_429') as exc:await json_call('Return JSON',{},LLMExtraction)
    assert 'SECRET' not in str(exc.value)
@pytest.mark.asyncio
@respx.mock
async def test_invalid_model_json_rejected(monkeypatch):
    monkeypatch.setattr(settings,'gemini_key','fake-test-key')
    respx.post('https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent').mock(return_value=httpx.Response(200,json={'candidates':[{'content':{'parts':[{'text':'{"verdict":"GENUINE"}'}]}}]}))
    with pytest.raises(ProviderError):await json_call('Return JSON',{},LLMExtraction)
@pytest.mark.asyncio
@respx.mock
async def test_brave_filters_unapproved_results(monkeypatch):
    monkeypatch.setattr(settings,'brave_key','fake-test-key')
    route=respx.get('https://api.search.brave.com/res/v1/web/search').mock(return_value=httpx.Response(200,json={'web':{'results':[{'url':'https://evil.com/','title':'Untrusted'},{'url':'https://www.pib.gov.in/new-notice','title':'Official'}]}}))
    sources,status,note=await search_sources(local_extract('A new ministry notice.','text',False),'official ministry notice')
    assert status=='ok';assert len(sources)==1;assert 'site:pib.gov.in' in route.calls[0].request.url.params['q'];assert route.calls[0].request.headers['X-Subscription-Token']=='fake-test-key'
@pytest.mark.asyncio
@respx.mock
async def test_tavily_allowlist_contract(monkeypatch):
    monkeypatch.setattr(settings,'tavily_key','fake-test-key')
    route=respx.post('https://api.tavily.com/search').mock(return_value=httpx.Response(200,json={'results':[]}))
    await search_sources(local_extract('A notice.','text',False),'notice')
    assert 'pib.gov.in' in json.loads(route.calls[0].request.content)['include_domains']
@pytest.mark.asyncio
@respx.mock
async def test_sarvam_both_directions(monkeypatch):
    monkeypatch.setattr(settings,'sarvam_key','fake-test-key')
    audio=b'RIFF'+b'\0'*40
    tts=respx.post('https://api.sarvam.ai/text-to-speech').mock(return_value=httpx.Response(200,json={'audios':[base64.b64encode(audio).decode()]}))
    stt=respx.post('https://api.sarvam.ai/speech-to-text').mock(return_value=httpx.Response(200,json={'transcript':'OTP 123456','language_code':'en-IN'}))
    assert await speak('Hello','en')==audio
    result=await transcribe(audio,'clip.wav','audio/wav','en');assert result['text']=='OTP [REDACTED_OTP]'
    assert json.loads(tts.calls[0].request.content)['language_code']=='en-IN';assert stt.calls[0].request.headers['api-subscription-key']=='fake-test-key'
@pytest.mark.asyncio
@respx.mock
async def test_cloud_vision_contract(monkeypatch):
    monkeypatch.setattr(settings,'gemini_key','fake-test-key')
    route=respx.post('https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent').mock(return_value=httpx.Response(200,json={'candidates':[{'content':{'parts':[{'text':'OTP 123456'}]}}]}))
    data=BytesIO();Image.new('RGB',(50,50),'white').save(data,'PNG')
    result=await read_image(data.getvalue());assert result['text']=='OTP [REDACTED_OTP]';assert 'inlineData' in json.loads(route.calls[0].request.content)['contents'][0]['parts'][1]
@pytest.mark.asyncio
@respx.mock
async def test_safe_browsing_threat(monkeypatch):
    monkeypatch.setattr(settings,'safe_browsing_key','fake-test-key')
    respx.post('https://safebrowsing.googleapis.com/v4/threatMatches:find').mock(return_value=httpx.Response(200,json={'matches':[{'threatType':'SOCIAL_ENGINEERING'}]}))
    result=await check_urls(['https://www.pib.gov.in/'],'hello');assert result[0]=='DANGEROUS';assert result[2]=='live_checked'
@pytest.mark.asyncio
async def test_private_dns_rejected(monkeypatch):
    async def private(host):raise ValueError('Private IP')
    monkeypatch.setattr(fetcher,'public_addresses',private)
    assert await fetcher.fetch_document('https://pib.gov.in/test') is None
@pytest.mark.asyncio
@respx.mock
async def test_pinned_fetch_and_redirect_boundary(monkeypatch):
    async def public(host):return ['93.184.216.34']
    monkeypatch.setattr(fetcher,'public_addresses',public)
    route=respx.get('https://93.184.216.34/test').mock(return_value=httpx.Response(200,text='<html><title>Official</title><main>'+('Official government content. '*10)+'</main></html>',headers={'content-type':'text/html'}))
    result=await fetcher.fetch_document('https://pib.gov.in/test')
    assert result is not None;request=route.calls[0].request;assert request.headers['host']=='pib.gov.in';assert request.extensions['sni_hostname']=='pib.gov.in'
    fetcher._CACHE.clear() # Force a new network request to exercise redirect validation.
    route.mock(return_value=httpx.Response(302,headers={'location':'https://127.0.0.1/private'}))
    assert await fetcher.fetch_document('https://pib.gov.in/test') is None
@pytest.mark.asyncio
async def test_kyc_shortener_and_punycode_are_not_verified():
    assert (await check_urls(['https://bit.ly/verify'],'Bank KYC update'))[0]=='DANGEROUS'
    assert (await check_urls(['https://xn--exmple-cua.com/'],'Unknown message'))[0]=='SUSPICIOUS'

@pytest.mark.asyncio
@respx.mock
async def test_upstream_timeout_becomes_provider_error(monkeypatch):
    monkeypatch.setattr(settings,'gemini_key','fake-test-key')
    respx.post('https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent').mock(side_effect=httpx.ReadTimeout('timeout'))
    with pytest.raises(ProviderError,match='timeout'):await json_call('Return JSON',{},LLMExtraction)

@pytest.mark.asyncio
@respx.mock
async def test_image_and_speech_endpoints_with_provider_success(monkeypatch):
    from fastapi.testclient import TestClient
    from backend.main import app
    monkeypatch.setattr(settings,'sarvam_key','fake-test-key');monkeypatch.setattr(settings,'gemini_key','fake-test-key')
    audio=b'RIFF'+b'\0'*40
    respx.post('https://api.sarvam.ai/text-to-speech').mock(return_value=httpx.Response(200,json={'audios':[base64.b64encode(audio).decode()]}))
    respx.post('https://api.sarvam.ai/speech-to-text').mock(return_value=httpx.Response(200,json={'transcript':'Do not share passwords.','language_code':'en-IN'}))
    respx.post('https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent').mock(return_value=httpx.Response(200,json={'candidates':[{'content':{'parts':[{'text':'OTP 123456'}]}}]}))
    data=BytesIO();Image.new('RGB',(50,50),'white').save(data,'PNG')
    with TestClient(app) as client:
        result=client.post('/api/speak',json={'text':'Hello','language':'kn'});assert result.status_code==200;assert result.content==audio
        result=client.post('/api/transcribe',files={'file':('clip.wav',audio,'audio/wav')},data={'consent':'true','language':'en'});assert result.status_code==200;assert result.json()['text']=='Do not share passwords.'
        result=client.post('/api/ocr',files={'file':('image.png',data.getvalue(),'image/png')},data={'consent':'true'});assert result.status_code==200;assert result.json()['text']=='OTP [REDACTED_OTP]'
