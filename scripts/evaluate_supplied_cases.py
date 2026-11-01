"""Supplied-case evaluation: isolated fallback by default, paced real Gemini with --live. No model/config changes."""
import sys,json,asyncio,time,logging,argparse
from contextlib import ExitStack
import httpx
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.schemas import AnalyzeInput
from backend.services import investigation_agent as agent,claim_extractor
from backend.services.llm_client import ProviderError
logging.getLogger('nivaar.operations').setLevel(logging.ERROR)
async def disabled_ai(*args,**kwargs):raise ProviderError('gemini','evaluation_disabled_no_call')
async def main():
 parser=argparse.ArgumentParser();parser.add_argument('output',nargs='?',default='docs/validation/supplied-cases-before.json');parser.add_argument('--live',action='store_true');parser.add_argument('--gap-seconds',type=float,default=33);args=parser.parse_args()
 from backend.config import settings
 calls=[];original_send=httpx.AsyncClient.send
 async def monitored_send(client,request,**kwargs):
  if request.url.host!='generativelanguage.googleapis.com':return await original_send(client,request,**kwargs)
  started=time.perf_counter()
  try:
   response=await original_send(client,request,**kwargs);calls.append({'status':response.status_code,'duration_ms':round((time.perf_counter()-started)*1000)});return response
  except httpx.HTTPError as exc:
   calls.append({'error':type(exc).__name__,'duration_ms':round((time.perf_counter()-started)*1000)});raise
 cases=json.loads(Path('backend/data/evaluation/user_supplied_2026_11_01.json').read_text(encoding='utf-8'));rows=[]
 with ExitStack() as stack:
  if args.live:stack.enter_context(patch.object(httpx.AsyncClient,'send',monitored_send))
  else:
   stack.enter_context(patch.object(claim_extractor,'json_call',disabled_ai));stack.enter_context(patch.object(agent,'json_call',disabled_ai))
  previous_start=None
  for c in cases:
   if args.live and previous_start is not None:await asyncio.sleep(max(0,args.gap_seconds-(time.perf_counter()-previous_start)))
   start=time.perf_counter();previous_start=start;call_start=len(calls);r=await agent.investigate(AnalyzeInput(text=c['text']))
   row={**c,'actual_verdict':r['verdict'],'actual_risk':r['risk_level'],'verdict_match':r['verdict']==c['expected_verdict'],'risk_match':r['risk_level'] in c['expected_risks'],'checks':r['checks'],'urls':r['extracted']['urls'],'upi_findings':r['identifiers']['upi_ids'],'tactics':sorted({t['tactic'] for t in r['tactics']}),'provider_status':r['provider_status'],'provider_errors':r['provider_errors'],'gemini_http_calls':calls[call_start:],'llm_trace':[t['output_summary'] for t in r['trace'] if t['tool_name'] in ('extract_claims','verify_evidence')],'sources':[{'id':e['source_id'],'url':e['url'],'date':e['document_date'],'relation':e['relation'],'cached':e['cached']} for e in r['evidence']],'duration_ms':round((time.perf_counter()-start)*1000)}
   rows.append(row);Path(args.output+'.partial').write_text(json.dumps({'model':settings.model_name,'results':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:row[k] for k in ('id','actual_verdict','actual_risk','verdict_match','checks','provider_status','gemini_http_calls')}) ,flush=True)
 output={'mode':'Real configured Gemini + Tavily/official retrieval; paced, with all safeguards enabled. No model/config changes.' if args.live else 'Gemini deliberately disabled in evaluation process only; real Tavily/official fetches. Not a full-provider or accuracy benchmark. No application configuration changed.','model':settings.model_name,'gemini_http_calls':calls,'total':len(rows),'verdict_matches':sum(r['verdict_match'] for r in rows),'risk_matches':sum(r['risk_match'] for r in rows),'results':rows}
 target=args.output
 Path(target).write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
asyncio.run(main())
