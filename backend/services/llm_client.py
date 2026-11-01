import json, asyncio, time
from contextvars import ContextVar
investigation_budget=ContextVar('investigation_budget',default=None)
def reserve_operation():
    budget=investigation_budget.get()
    if budget is None:return True
    if budget['remaining']<=0:return False
    budget['remaining']-=1
    return True
_cooldown_until=0.0
import httpx
from pydantic import BaseModel
from backend.config import settings
class ProviderError(Exception):
    def __init__(self, provider, reason):
        self.provider, self.reason = provider, reason
        self.code=('MISSING_KEY' if reason=='not_configured' else 'RATE_LIMITED' if reason in ('http_429','quota_cooldown','local_free_tier_budget') else 'TIMEOUT' if 'timeout' in reason else 'UPSTREAM_ERROR' if reason.startswith('http_') or 'connection' in reason else 'NOT_CONFIGURED' if 'unsupported' in reason else 'INVALID_RESPONSE')
        super().__init__(f'{provider}: {reason}')

def strict_schema(schema):
    if isinstance(schema,dict):
        schema={k:strict_schema(v) for k,v in schema.items() if k not in ('default','title')}
        if schema.get('type')=='object':
            schema['additionalProperties']=False
            schema['required']=list(schema.get('properties',{}))
        return schema
    if isinstance(schema,list): return [strict_schema(x) for x in schema]
    return schema

async def json_call(system: str, payload: dict, schema: type[BaseModel]):
    global _cooldown_until
    if time.monotonic()<_cooldown_until:raise ProviderError(settings.provider,'quota_cooldown')
    if not settings.llm_key: raise ProviderError(settings.provider,'not_configured')
    if not reserve_operation():raise ProviderError(settings.provider,'operation_budget_exhausted')
    from backend.operations import provider_budget
    if not provider_budget():raise ProviderError(settings.provider,'local_free_tier_budget')
    provider=settings.provider
    spec=strict_schema(schema.model_json_schema())
    try:
        async with httpx.AsyncClient(timeout=35,trust_env=False) as client:
            if provider=='gemini':
                url=f'https://generativelanguage.googleapis.com/v1beta/models/{settings.model_name}:generateContent'
                data={'systemInstruction':{'parts':[{'text':system}]},'contents':[{'role':'user','parts':[{'text':json.dumps(payload,ensure_ascii=False)}]}], 'generationConfig':{'temperature':0,'responseMimeType':'application/json','responseJsonSchema':spec,'maxOutputTokens':6000}}
                r=await client.post(url,headers={'x-goog-api-key':settings.llm_key},json=data)
            elif provider in ('openai','groq'):
                url='https://api.openai.com/v1/chat/completions' if provider=='openai' else 'https://api.groq.com/openai/v1/chat/completions'
                fmt={'type':'json_schema','json_schema':{'name':schema.__name__,'strict':True,'schema':spec}} if provider=='openai' else {'type':'json_object'}
                data={'model':settings.model_name,'messages':[{'role':'system','content':system+' Return only JSON conforming to this schema: '+json.dumps(spec)},{'role':'user','content':json.dumps(payload,ensure_ascii=False)}], 'temperature':0,'response_format':fmt,'max_tokens':6000}
                if provider=='openai':data['store']=False
                r=await client.post(url,headers={'Authorization':'Bearer '+settings.llm_key},json=data)
            else: raise ProviderError(provider,'unsupported_provider')
            if r.status_code in (502,503,504) and reserve_operation() and provider_budget():
                await asyncio.sleep(.25)
                r=await client.send(client.build_request(r.request.method,r.request.url,headers=r.request.headers,content=r.request.content))
            if r.status_code>=400:
                from backend.operations import record
                record('provider_failure',provider+'_http_'+str(r.status_code))
                if r.status_code==429:_cooldown_until=time.monotonic()+60
                raise ProviderError(provider,f'http_{r.status_code}')
            body=r.json()
            content=''.join(p.get('text','') for p in body['candidates'][0]['content']['parts']) if provider=='gemini' else body['choices'][0]['message']['content']
            return schema.model_validate_json(content)
    except ProviderError: raise
    except httpx.TimeoutException:raise ProviderError(provider,'timeout') from None
    except httpx.HTTPError:raise ProviderError(provider,'upstream_connection_error') from None
    except (KeyError,IndexError,ValueError,TypeError):raise ProviderError(provider,'invalid_response') from None
