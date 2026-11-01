"""Independent public SMS diagnostic; spam labels are NOT scam labels."""
import sys,json,zipfile,io,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import httpx
from backend.services.claim_extractor import local_extract
from backend.services.verdict_engine import action_checks,choose_verdict
from backend.schemas import DimensionChecks
out=Path('backend/data/evaluation');archive=out/'uci-sms.zip'
url='https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip'
if not archive.exists():
 r=httpx.get(url,follow_redirects=True,trust_env=False,timeout=30);r.raise_for_status();archive.write_bytes(r.content)
rows=zipfile.ZipFile(io.BytesIO(archive.read_bytes())).read('SMSSpamCollection').decode('utf-8-sig').splitlines()
counts={};total=0
for line in rows:
 if '\t' not in line:continue
 label,text=line.split('\t',1);e=local_extract(text,'text',False);action,risk=action_checks(e)
 verdict,_=choose_verdict(DimensionChecks(authority='UNVERIFIED',requested_action=action,destination='NOT_PROVIDED'),risk)
 counts.setdefault(label,{'SCAM':0,'UNSURE':0,'GENUINE':0})[verdict]+=1;total+=1
result={'scope':'Independent public English SMS diagnostic, local action rules only; spam is not a fraud ground-truth label. No model training or tuning on this corpus. URLs and live evidence excluded. No SMS text sent to providers.','source':url,'citation':'Almeida & Hidalgo (2011), SMS Spam Collection, UCI, DOI 10.24432/C5CC84','license':'CC BY 4.0 (UCI dataset page)','archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'total':total,'counts_by_original_label':counts,'ham_scam_flag_rate':counts['ham']['SCAM']/sum(counts['ham'].values()),'spam_scam_flag_rate':counts['spam']['SCAM']/sum(counts['spam'].values()),'limitations':'Historical largely non-Indian English SMS. Spam-flag coverage is NOT scam recall. Most spam can be advertising, and UNSURE is expected. Does not establish current Indian multilingual fraud accuracy.'}
Path('docs/public-sms-evaluation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
