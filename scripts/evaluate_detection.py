"""No-cost local detection evaluation. Does not measure AI or live retrieval accuracy."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.services.claim_extractor import local_extract
from backend.services.verdict_engine import action_checks,choose_verdict
from backend.schemas import DimensionChecks
from backend.services.url_checker import check_urls
import asyncio
async def run():
 rows=[]
 for line in Path('backend/data/evaluation/cases.jsonl').read_text().splitlines():
  c=json.loads(line);e=local_extract(c['text'],'text',False);action,risk=action_checks(e)
  # Offline URL rules only; never call optional reputation API.
  from backend.config import settings
  settings.safe_browsing_key=''
  dest,_,_=await check_urls(e.urls,e.raw_text_redacted)
  actual,_=choose_verdict(DimensionChecks(authority='UNVERIFIED',requested_action=action,destination=dest),risk)
  rows.append({**c,'actual':actual})
 tp=sum(r['label']=='scam' and r['actual']=='SCAM' for r in rows);fp=sum(r['label']!='scam' and r['actual']=='SCAM' for r in rows);fn=sum(r['label']=='scam' and r['actual']!='SCAM' for r in rows)
 result={'scope':'Source-derived development regression; local rules only; not independent real-world accuracy','total':len(rows),'scam_precision':tp/(tp+fp) if tp+fp else None,'scam_recall':tp/(tp+fn) if tp+fn else None,'scam_f1':2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None,'false_scam':fp,'missed_scams':fn,'abstention_rate':sum(r['actual']=='UNSURE' for r in rows)/len(rows),'false_genuine':sum(r['actual']=='GENUINE' and r['label']!='genuine' for r in rows),'confusion':{label:{v:sum(r['label']==label and r['actual']==v for r in rows) for v in ('SCAM','UNSURE','GENUINE')} for label in ('scam','benign','ambiguous')},'results':rows}
 Path('docs/detection-evaluation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='results'},indent=2))
asyncio.run(run())
