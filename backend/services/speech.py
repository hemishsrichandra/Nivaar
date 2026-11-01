import base64
import io
import wave
import httpx
from backend.config import settings
from backend.services.llm_client import ProviderError
from backend.services.input_parser import redact
LANG={'en':'en-IN','hi':'hi-IN','kn':'kn-IN','auto':'unknown'}

async def transcribe(data,filename,content_type,language):
    if not settings.sarvam_key:raise ProviderError('sarvam','not_configured')
    # MediaRecorder includes codec parameters; Sarvam validates an exact MIME allowlist.
    content_type=content_type.split(';',1)[0].strip().lower()
    try:
        async with httpx.AsyncClient(timeout=60,trust_env=False) as client:
            r=await client.post('https://api.sarvam.ai/speech-to-text',headers={'api-subscription-key':settings.sarvam_key},files={'file':(filename,data,content_type)},data={'model':settings.stt_model,'mode':'transcribe','language_code':LANG[language]})
            if r.status_code>=400:raise ProviderError('sarvam',f'http_{r.status_code}')
            result=r.json()
            text=result.get('transcript','')
            if not isinstance(text,str) or not text.strip():raise ProviderError('sarvam','empty_transcript')
            return {'text':redact(text),'language_code':result.get('language_code',LANG[language]),'provider':'sarvam','redacted':True}
    except httpx.HTTPError:raise ProviderError('sarvam','timeout_or_connection_error') from None
    except (ValueError,AttributeError,TypeError):raise ProviderError('sarvam','invalid_response') from None

def join_audio(audios):
    if not isinstance(audios,list) or not audios:raise ProviderError('sarvam','empty_audio')
    chunks=[base64.b64decode(chunk,validate=True) for chunk in audios]
    if any(len(chunk)<44 or not chunk.startswith(b'RIFF') for chunk in chunks):raise ValueError('Invalid WAV')
    if len(chunks)==1:return chunks[0]
    output=io.BytesIO()
    with wave.open(output,'wb') as target:
        expected=None
        for chunk in chunks:
            with wave.open(io.BytesIO(chunk),'rb') as source:
                params=source.getparams()
                signature=(params.nchannels,params.sampwidth,params.framerate,params.comptype)
                if expected is None:expected=signature;target.setparams(params)
                elif signature!=expected:raise ValueError('Inconsistent WAV segments')
                target.writeframes(source.readframes(params.nframes))
    return output.getvalue()

async def speak(text,language):
    if not settings.sarvam_key:raise ProviderError('sarvam','not_configured')
    try:
        async with httpx.AsyncClient(timeout=45,trust_env=False) as client:
            r=await client.post('https://api.sarvam.ai/text-to-speech',headers={'api-subscription-key':settings.sarvam_key},json={'text':redact(text),'language_code':LANG[language],'model':settings.tts_model,'speaker':settings.speaker,'speech_sample_rate':22050,'output_audio_codec':'wav'})
            if r.status_code>=400:raise ProviderError('sarvam',f'http_{r.status_code}')
            return join_audio(r.json().get('audios',[]))
    except (httpx.HTTPError,ValueError,TypeError,AttributeError,wave.Error,EOFError):raise ProviderError('sarvam','invalid_response_or_timeout') from None
