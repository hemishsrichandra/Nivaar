import base64
import io
import wave
import httpx
import pytest
import respx
from backend.config import settings
from backend.services import speech
from backend.services.llm_client import ProviderError

@pytest.mark.asyncio
@respx.mock
async def test_auto_language_is_not_forced_to_report_language(monkeypatch):
    monkeypatch.setattr(settings,'sarvam_key','test-key')
    route=respx.post('https://api.sarvam.ai/speech-to-text').mock(return_value=httpx.Response(200,json={'transcript':'नमस्ते','language_code':'hi-IN'}))
    result=await speech.transcribe(b'audio','clip.webm','audio/webm','auto')
    assert result['language_code']=='hi-IN'
    assert b'unknown' in route.calls[0].request.content

@pytest.mark.asyncio
@pytest.mark.parametrize('payload',[[],{'transcript':None},{'transcript':7}])
@respx.mock
async def test_invalid_transcript_is_a_provider_error(monkeypatch,payload):
    monkeypatch.setattr(settings,'sarvam_key','test-key')
    respx.post('https://api.sarvam.ai/speech-to-text').mock(return_value=httpx.Response(200,json=payload))
    with pytest.raises(ProviderError):await speech.transcribe(b'audio','clip.wav','audio/wav','en')

def wav(frames):
    output=io.BytesIO()
    with wave.open(output,'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(22050);f.writeframes(b'\0\0'*frames)
    return output.getvalue()

def test_all_tts_segments_are_preserved():
    joined=speech.join_audio([base64.b64encode(wav(n)).decode() for n in (100,200)])
    with wave.open(io.BytesIO(joined),'rb') as f:assert f.getnframes()==300

@pytest.mark.parametrize('audios',[[],['!invalid!'],[base64.b64encode(b'').decode()]])
def test_empty_or_corrupt_audio_rejected(audios):
    with pytest.raises((ProviderError,ValueError)):speech.join_audio(audios)

@pytest.mark.parametrize('audio_language,expected', [('auto','auto'),('kn','kn'),(None,'en')])
def test_transcribe_endpoint_language_and_unlabelled_m4a(monkeypatch,audio_language,expected):
    from fastapi.testclient import TestClient
    from backend.main import app
    captured={}
    async def fake(data,filename,content_type,language):
        captured.update(mime=content_type,language=language)
        return {'text':'A transcript','language_code':'kn-IN','provider':'sarvam','redacted':True}
    monkeypatch.setattr(speech,'transcribe',fake)
    form={'consent':'true','language':'en'}
    if audio_language is not None:form['audio_language']=audio_language
    with TestClient(app) as client:
        response=client.post('/api/transcribe',files={'file':('note.m4a',b'audio','application/octet-stream')},data=form)
    assert response.status_code==200
    assert captured=={'mime':'audio/mp4','language':expected}

def test_empty_audio_rejected_before_provider_call():
    from fastapi.testclient import TestClient
    from backend.main import app
    with TestClient(app) as client:
        response=client.post('/api/transcribe',files={'file':('note.wav',b'','audio/wav')},data={'consent':'true'})
    assert response.status_code==400
