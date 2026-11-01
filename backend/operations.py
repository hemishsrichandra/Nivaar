"""Persistent single-instance abuse budget and privacy-preserving operational telemetry."""
import os, sqlite3, time, secrets, hmac, hashlib, json, logging
from pathlib import Path
import tempfile
DB=os.getenv('OPERATIONS_DB', str(Path(tempfile.gettempdir()) / 'nivaar-operations.sqlite3'))
SECRET=os.getenv('REPORT_SIGNING_SECRET') or secrets.token_hex(32)
logger=logging.getLogger('nivaar.operations')
def connect():
    db=sqlite3.connect(DB,timeout=3)
    db.execute('CREATE TABLE IF NOT EXISTS budgets (key TEXT PRIMARY KEY, window INTEGER, count INTEGER)')
    db.execute('CREATE TABLE IF NOT EXISTS events (time REAL, kind TEXT, detail TEXT)')
    return db
def session(cookie):
    parts=(cookie or '').split('.')
    if len(parts)==2 and len(parts[0])==32 and hmac.compare_digest(parts[1],hmac.new(SECRET.encode(),parts[0].encode(),hashlib.sha256).hexdigest()):return cookie
    ident=secrets.token_hex(16)
    return ident+'.'+hmac.new(SECRET.encode(),ident.encode(),hashlib.sha256).hexdigest()
def admit(ident,limit):
    now=int(time.time()); checks=[('global-minute',60,int(os.getenv('GLOBAL_REQUESTS_PER_MINUTE','60'))),('global-day',86400,int(os.getenv('GLOBAL_REQUESTS_PER_DAY','500'))),('session-'+hashlib.sha256(ident.encode()).hexdigest(),60,limit)]
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        for key,period,cap in checks:
            row=db.execute('SELECT window,count FROM budgets WHERE key=?',(key,)).fetchone()
            if row and row[0]==now//period and row[1]>=cap:return False
        for key,period,cap in checks:
            db.execute('INSERT INTO budgets VALUES (?,?,1) ON CONFLICT(key) DO UPDATE SET count=CASE WHEN window=excluded.window THEN count+1 ELSE 1 END,window=excluded.window',(key,now//period))
        db.execute('DELETE FROM budgets WHERE window<? AND key LIKE ?',(now//60-2,'session-%'))
    return True
def record(kind,detail=''):
    # Only application-owned labels, never bodies, URLs, IPs or exception strings.
    with connect() as db:
        db.execute('INSERT INTO events VALUES (?,?,?)',(time.time(),kind,detail[:100]))
        db.execute('DELETE FROM events WHERE time<?',(time.time()-86400,))
        db.execute('DELETE FROM events WHERE rowid NOT IN (SELECT rowid FROM events ORDER BY rowid DESC LIMIT 20000)')
    if kind in ('error','provider_failure','abuse_block'):logger.warning(json.dumps({'event':kind,'label':detail[:100]}))
def snapshot():
    with connect() as db:
        counts=dict(db.execute('SELECT kind,count(*) FROM events GROUP BY kind'))
        timings=sorted(float(r[0]) for r in db.execute("SELECT detail FROM events WHERE kind='latency_ms'") if r[0].isdigit())
        alerts=[{'time':r[0],'type':r[1],'label':r[2]} for r in db.execute("SELECT time,kind,detail FROM events WHERE kind IN ('error','provider_failure','abuse_block') ORDER BY time DESC LIMIT 30")]
    return {'window':'last 24 hours, capped at 20000 events','counts':counts,'stage_latency_ms':{'samples':len(timings),'p50':timings[len(timings)//2] if timings else None,'p95':timings[min(len(timings)-1,int(len(timings)*.95))] if timings else None},'alerts':alerts}

def provider_budget():
    now=int(time.time())
    checks=[('llm-minute',60,int(os.getenv('LLM_CALLS_PER_MINUTE','4'))),('llm-day',86400,int(os.getenv('LLM_CALLS_PER_DAY','100')))]
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        for key,period,cap in checks:
            row=db.execute('SELECT window,count FROM budgets WHERE key=?',(key,)).fetchone()
            if row and row[0]==now//period and row[1]>=cap:return False
        for key,period,cap in checks:
            db.execute('INSERT INTO budgets VALUES (?,?,1) ON CONFLICT(key) DO UPDATE SET count=CASE WHEN window=excluded.window THEN count+1 ELSE 1 END,window=excluded.window',(key,now//period))
    return True
