"""In-process HTTP load/abuse test; upstream analysis is deliberately stubbed."""
import sys,asyncio,time,json,tempfile,statistics
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import httpx
from backend import main,operations
from backend.config import settings
async def run():
 operations.DB=str(Path(tempfile.mkdtemp())/'load.sqlite');settings.require_live=False
 import os
 os.environ['GLOBAL_REQUESTS_PER_MINUTE']='60';os.environ['GLOBAL_REQUESTS_PER_DAY']='500'
 async def fake(value,emit=None):await asyncio.sleep(.02);return {'load_test_stub':True}
 main.investigate=fake
 times=[];statuses=[];gate=asyncio.Semaphore(20)
 async with httpx.AsyncClient(transport=httpx.ASGITransport(app=main.app),base_url='http://test') as client:
  async def one(i):
   async with gate:
    t=time.perf_counter();r=await client.post('/api/analyze',json={'text':'A public notice for testing.','language':'en'});times.append((time.perf_counter()-t)*1000);statuses.append(r.status_code)
  await asyncio.gather(*(one(i) for i in range(120)))
 result={'scope':'ASGI integration: 120 requests, 20 clients; stubbed analysis, no provider calls; not Render network throughput','requests':len(times),'p50_ms':round(statistics.median(times),2),'p95_ms':round(sorted(times)[int(len(times)*.95)-1],2),'statuses':{str(s):statuses.count(s) for s in set(statuses)},'budget_enforced':429 in statuses,'server_errors':sum(s>=500 for s in statuses)}
 Path('docs/load-test.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
 assert result['budget_enforced'] and not result['server_errors']
asyncio.run(run())
