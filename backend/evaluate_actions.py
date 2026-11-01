"""Offline action-risk regression metrics; no API calls, not population accuracy."""
import json
from pathlib import Path
from backend.schemas import DimensionChecks
from backend.services.claim_extractor import local_extract
from backend.services.verdict_engine import action_checks,choose_verdict

def evaluate():
    fixture=json.loads((Path(__file__).parent/'data/evaluation/action_quality_2026_11_01.json').read_text())
    counts={'true_positive':0,'false_positive':0,'true_negative':0,'false_negative':0};results=[]
    for case in fixture['cases']:
        extraction=local_extract(case['text'],'voice',False)
        action,high=action_checks(extraction)
        verdict,risk=choose_verdict(DimensionChecks(authority='UNVERIFIED',requested_action=action,destination='NOT_PROVIDED'),high)
        positive=verdict=='SCAM';expected=case['scam']
        key=('true_' if positive==expected else 'false_')+('positive' if positive else 'negative')
        counts[key]+=1
        results.append({'id':case['id'],'expected_scam':expected,'verdict':verdict,'risk':risk,'matched':positive==expected})
    tp=counts['true_positive'];fp=counts['false_positive'];fn=counts['false_negative']
    return {'scope':fixture['provenance'],'count':len(results),**counts,'precision':tp/(tp+fp) if tp+fp else None,'recall':tp/(tp+fn) if tp+fn else None,'results':results}
if __name__=='__main__':
    result=evaluate();print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(0 if all(r['matched'] for r in result['results']) else 1)
