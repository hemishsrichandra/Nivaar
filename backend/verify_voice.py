"""Manual Sarvam-only smoke test; uses configured quota and synthetic public text.

Run: .venv/bin/python -m backend.verify_voice
No Gemini/search calls. Temporary audio is deleted when the check finishes.
"""
import asyncio
import io
import json
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path
from backend.services.speech import speak,transcribe

SAMPLES={
    'en':'Do not share your password. Check the official website before sending money.',
    'hi':'अपना पासवर्ड किसी को न दें। पैसे भेजने से पहले आधिकारिक वेबसाइट की जाँच करें।',
    'kn':'ನಿಮ್ಮ ಪಾಸ್‌ವರ್ಡ್ ಯಾರಿಗೂ ನೀಡಬೇಡಿ. ಹಣ ಕಳುಹಿಸುವ ಮೊದಲು ಅಧಿಕೃತ ವೆಬ್‌ಸೈಟ್ ಪರಿಶೀಲಿಸಿ.',
}

async def check():
    results=[]
    with tempfile.TemporaryDirectory(prefix='nivaar-voice-') as directory:
        folder=Path(directory)
        for language,text in SAMPLES.items():
            try:
                audio=await speak(text,language)
                (folder/f'{language}.wav').write_bytes(audio)
                with wave.open(io.BytesIO(audio),'rb') as f:duration=round(f.getnframes()/f.getframerate(),2)
                result=await transcribe(audio,f'{language}.wav','audio/wav','auto')
                results.append({'language':language,'codec':'wav','seconds':duration,'detected':result['language_code'],'transcript':result['text'],'ok':result['language_code']=={'en':'en-IN','hi':'hi-IN','kn':'kn-IN'}[language] and bool(result['text'])})
            except Exception as exc:results.append({'language':language,'ok':False,'error':str(exc)})
        ffmpeg=shutil.which('ffmpeg')
        if ffmpeg and (folder/'en.wav').exists():
            for ext,codec,mime in [('webm','libopus','audio/webm'),('m4a','aac','audio/mp4'),('ogg','libopus','audio/ogg')]:
                path=folder/f'en.{ext}'
                try:
                    subprocess.run([ffmpeg,'-y','-v','error','-i',str(folder/'en.wav'),'-c:a',codec,str(path)],check=True,capture_output=True)
                    result=await transcribe(path.read_bytes(),path.name,mime,'auto')
                    results.append({'language':'en','codec':ext,'detected':result['language_code'],'transcript':result['text'],'ok':result['language_code']=='en-IN' and bool(result['text'])})
                except Exception as exc:results.append({'codec':ext,'ok':False,'error':str(exc)})
        else:results.append({'codec':'webm/m4a/ogg','skipped':'ffmpeg or English WAV unavailable'})
    print(json.dumps(results,ensure_ascii=False,indent=2))
    return all(item.get('ok',True) for item in results)

if __name__=='__main__':raise SystemExit(0 if asyncio.run(check()) else 1)
