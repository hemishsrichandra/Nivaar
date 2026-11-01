import asyncio, base64, json, os, secrets, time
from collections import defaultdict,deque
from contextlib import asynccontextmanager
from fastapi import FastAPI,HTTPException,UploadFile,File,Form,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse,Response,StreamingResponse
from backend.config import settings,ROOT
from backend.schemas import AnalyzeInput,SpeakInput,BenchmarkInput,PdfInput
from backend.services.investigation_agent import investigate
from backend.services.llm_client import ProviderError
from backend.services import speech
from backend.services.vision import read_image
from backend.services.report_integrity import verify
from backend.services.evidence_pdf import build_pdf

semaphore=asyncio.Semaphore(settings.concurrency)
@asynccontextmanager
async def lifespan(app):
    yield
app=FastAPI(title='Nivaar API',version='1.0.0',lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=os.getenv('ALLOWED_ORIGINS','http://localhost:3000,http://127.0.0.1:3000').split(','),allow_methods=['GET','POST'],allow_headers=['Content-Type','X-Benchmark-Token'])

class BodyLimitMiddleware:
    def __init__(self,app):self.app=app
    async def __call__(self,scope,receive,send):
        if scope['type']!='http':return await self.app(scope,receive,send)
        # Limit before parsing or spooling an upload; supports chunked bodies.
        chunks=[];size=0
        while True:
            message=await receive()
            if message['type']=='http.disconnect':return
            size+=len(message.get('body',b''))
            if size>12*1024*1024:
                await JSONResponse({'error':'Request exceeds 12 MB.'},status_code=413)(scope,receive,send);return
            chunks.append(message)
            if not message.get('more_body'):break
        index=0
        async def replay():
            nonlocal index
            if index<len(chunks):item=chunks[index];index+=1;return item
            return await receive()
        await self.app(scope,replay,send)
app.add_middleware(BodyLimitMiddleware)
requests=defaultdict(deque)
@app.middleware('http')
async def limits(request,call_next):
    if request.url.path.startswith('/api/'):
        from backend.operations import session,admit,record
        identity=session(request.cookies.get('nivaar_session'))
        if request.method=='POST':
            origin=request.headers.get('origin')
            allowed=set(os.getenv('ALLOWED_ORIGINS','http://localhost:3000,http://127.0.0.1:3000').split(',')) | {os.getenv('RENDER_EXTERNAL_URL','')}
            if origin and origin not in allowed and __import__('urllib.parse',fromlist=['urlparse']).urlparse(origin).netloc!=request.headers.get('host'):
                return JSONResponse({'error':'Cross-origin submission blocked.'},status_code=403)
            if not admit(identity,settings.rate_limit):
                record('abuse_block','request_budget')
                return JSONResponse({'error':'Request budget reached. Please retry later.'},status_code=429,headers={'Retry-After':'60'})
    try:
        response=await call_next(request)
    except Exception:
        from backend.operations import record
        record('error','unhandled_request')
        raise
    if request.url.path.startswith('/api/'):
        from backend.operations import record
        record('request',str(response.status_code))
        if response.status_code>=500:record('error','http_5xx')
        response.set_cookie('nivaar_session',identity,httponly=True,samesite='strict',secure=bool(os.getenv('RENDER')),max_age=86400)

    response.headers['Cache-Control']='no-store'
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Referrer-Policy']='no-referrer'
    return response

@app.exception_handler(ProviderError)
async def provider_error(request,exc):return JSONResponse({'error':str(exc),'provider':exc.provider,'reason':exc.reason,'error_code':exc.code},status_code=503 if exc.reason=='not_configured' else 502)

@app.get('/api/health')
async def health():return {'status':'ok','application':'Nivaar','version':'1.0.0','runtime':'fastapi','stores_messages':False,'providers':settings.public_status()}
@app.get('/api/ready')
async def ready():
    missing=[]
    if not settings.llm_key:missing.append('LLM_API_KEY')
    if not settings.sarvam_key:missing.append('SARVAM_API_KEY')
    if not (settings.brave_key or settings.tavily_key):missing.append('SEARCH_API_KEY')
    return JSONResponse({'ready':not missing,'configured_only':True,'missing':missing,'providers':settings.public_status()},status_code=503 if missing else 200)
@app.get('/api/config')
async def config():return {'providers':settings.public_status(),'require_live':settings.require_live,'benchmark_requires_token':True,'max_upload_mb':10,'max_voice_seconds':30,'mode':'live_configured' if settings.llm_key else 'fallback','credentials_verified':False}

def require_provider():
    if settings.require_live and not settings.llm_key:raise HTTPException(503,'AI provider is not configured. Set the provider key before enabling full analysis.')

async def limited_analyze(value,emit=None):
    try:await asyncio.wait_for(semaphore.acquire(),timeout=2)
    except TimeoutError:raise HTTPException(429,'All investigation slots are busy. Try again shortly.')
    try:return await investigate(value,emit)
    finally:semaphore.release()

@app.post('/api/analyze')
async def analyze(value:AnalyzeInput):
    require_provider();return await limited_analyze(value)
@app.post('/api/analyze/stream')
async def analyze_stream(value:AnalyzeInput,request:Request):
    require_provider()
    queue=asyncio.Queue()
    async def emit(event):await queue.put(event)
    async def run():
        try:await queue.put({'type':'report','report':await limited_analyze(value,emit)})
        except asyncio.CancelledError:raise
        except HTTPException as e:await queue.put({'type':'error','error':str(e.detail)})
        except Exception:await queue.put({'type':'error','error':'Investigation failed. Please retry.'})
        finally:await queue.put(None)
    async def stream():
        task=asyncio.create_task(run())
        try:
            while True:
                try:event=await asyncio.wait_for(queue.get(),timeout=10)
                except TimeoutError:
                    yield ': keepalive\n\n';continue
                if event is None:break
                yield 'data: '+json.dumps(event,ensure_ascii=False)+'\n\n'
        finally:
            task.cancel()
            try:await task
            except asyncio.CancelledError:pass
    return StreamingResponse(stream(),media_type='text/event-stream',headers={'X-Accel-Buffering':'no','Cache-Control':'no-cache, no-transform'})

@app.post('/api/transcribe')
async def transcribe(file:UploadFile=File(...),language:str=Form('en'),consent:bool=Form(False)):
    if language not in ('en','hi','kn'):raise HTTPException(422,'Unsupported language.')
    if not consent:raise HTTPException(400,'Explicit consent is required to send audio to Sarvam.')
    if not file.content_type or not file.content_type.startswith(('audio/','video/webm','video/mp4')):raise HTTPException(415,'Upload a supported audio file.')
    data=await file.read(10*1024*1024+1)
    if len(data)>10*1024*1024:raise HTTPException(413,'Audio must be under 10 MB and 30 seconds.')
    # Provider enforces duration/codecs; files are held only for this request.
    return await speech.transcribe(data,(file.filename or 'voice.webm')[:100],file.content_type,language)
@app.post('/api/speak')
async def speak(value:SpeakInput):return Response(await speech.speak(value.text,value.language),media_type='audio/wav')
@app.post('/api/ocr')
async def ocr(file:UploadFile=File(...),consent:bool=Form(False)):
    if not consent:raise HTTPException(400,'Explicit consent is required to send an image to the AI provider.')
    if file.content_type not in ('image/png','image/jpeg','image/webp'):raise HTTPException(415,'Choose PNG, JPG or WebP.')
    data=await file.read(8*1024*1024+1)
    if len(data)>8*1024*1024:raise HTTPException(413,'Image must be under 8 MB.')
    try:return await read_image(data)
    except ValueError as e:raise HTTPException(400,str(e)) from None
@app.post('/api/evidence-pdf')
async def evidence_pdf(value:PdfInput):
    if not verify(value.report,value.signature):raise HTTPException(400,'Report integrity check failed. Run a new investigation after server restarts or report edits.')
    try:data=await asyncio.to_thread(build_pdf,value.report)
    except Exception:raise HTTPException(500,'PDF generation failed. Please retry or print the displayed report.') from None
    return Response(data,media_type='application/pdf',headers={'Content-Disposition':'attachment; filename="nivaar-evidence.pdf"'})

@app.post('/api/benchmark')
async def benchmark(value:BenchmarkInput):
    if not settings.benchmark_token or not secrets.compare_digest(value.token,settings.benchmark_token):raise HTTPException(403,'A valid BENCHMARK_TOKEN is required for this deployment.')
    cases=[json.loads(line) for line in (ROOT/'data/benchmark_cases.jsonl').read_text(encoding="utf-8").splitlines() if line.strip()]
    started=time.perf_counter();results=[]
    # Bounded sequential evaluation avoids bursting provider quotas.
    for c in cases:
        case_started=time.perf_counter()
        result=await limited_analyze(AnalyzeInput(text=c['text'],language=c['language']))
        results.append({'id':c['id'],'language':c['language'],'expected':c['expected'],'actual':result['verdict'],'passed':c['expected']==result['verdict'],'source':c.get('source'),'evidence_count':len(result['evidence']),'provider_status':result['provider_status'],'group':c.get('group','unit_fixture'),'latency_ms':round((time.perf_counter()-case_started)*1000),'source_validation_failure':any(t['tool_name']=='fetch_official_documents' and t['status']=='fallback' for t in result['trace'])})
    return {'total':len(results),'correct':sum(r['passed'] for r in results),'abstention_count':sum(r['actual']=='UNSURE' for r in results),'false_scam':sum(r['actual']=='SCAM' and r['expected']!='SCAM' for r in results),'groups':{group:{'total':sum(r['group']==group for r in results),'correct':sum(r['group']==group and r['passed'] for r in results)} for group in {r['group'] for r in results}},'language_results':{lang:{'total':sum(r['language']==lang for r in results),'correct':sum(r['language']==lang and r['passed'] for r in results)} for lang in ('en','hi','kn')},'source_validation_failures':sum(r['source_validation_failure'] for r in results),'false_genuine':sum(r['actual']=='GENUINE' and r['expected']!='GENUINE' for r in results),'genuine_cases':sum(r['expected']=='GENUINE' for r in results),'duration_ms':round((time.perf_counter()-started)*1000),'results':results,'limitations':'Synthetic regression cases derived from official advisories, not a real-world accuracy estimate. Genuine cases require live official retrieval. Provider and source outages are visible in each result.'}

@app.get('/api/ops')
async def operations(request:Request):
    token=os.getenv('MONITORING_TOKEN','') or settings.benchmark_token
    if not token or not secrets.compare_digest(request.headers.get('authorization',''),'Bearer '+token):raise HTTPException(403,'Monitoring token required.')
    from backend.operations import snapshot
    return snapshot()
