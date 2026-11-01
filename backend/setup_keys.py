"""Run locally: python3 backend/setup_keys.py. Values are never echoed."""
from getpass import getpass
from pathlib import Path
import os
path = Path(__file__).with_name('.env')
values = {}
if path.exists():
    for line in path.read_text().splitlines():
        if '=' in line and not line.startswith('#'):
            k,v=line.split('=',1);values[k]=v
values['LLM_PROVIDER']='gemini'
values.setdefault('LLM_MODEL','gemini-2.5-flash')
print('Enter keys locally. Press Enter to keep an existing value or skip an optional key.')
for name in ('GEMINI_API_KEY','SARVAM_API_KEY','BRAVE_API_KEY','GOOGLE_SAFE_BROWSING_KEY'):
    value=getpass(f'{name}'+(' (already set)' if values.get(name) else '')+': ').strip()
    if value:values[name]=value
values.setdefault('SARVAM_STT_MODEL','saaras:v3')
values.setdefault('SARVAM_TTS_MODEL','bulbul:v3')
values.setdefault('SARVAM_SPEAKER','shubh')
fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
with os.fdopen(fd,'w') as stream:
    for k,v in values.items():stream.write(k+'='+v+'\n')
os.chmod(path,0o600)
print('Saved backend/.env. Restart the backend after changes. No keys were printed.')
