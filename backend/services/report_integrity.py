import hashlib, hmac, json, os, secrets
SECRET=os.getenv('REPORT_SIGNING_SECRET') or secrets.token_hex(32)
def canonical(report):
    value=report.model_dump(mode='json') if hasattr(report,'model_dump') else dict(report)
    value['report_hash']=''
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def report_hash(report):return hashlib.sha256(canonical(report).encode()).hexdigest()
def sign(report):return hmac.new(SECRET.encode(),report_hash(report).encode(),hashlib.sha256).hexdigest()
def verify(report,signature):return hmac.compare_digest(report.report_hash,report_hash(report)) and hmac.compare_digest(sign(report),signature)
