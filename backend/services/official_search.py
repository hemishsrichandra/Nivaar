import json, time, hashlib
_CACHE={}
from urllib.parse import urlparse
import httpx
from backend.config import settings,ROOT,OFFICIAL_DOMAINS
from backend.services.official_fetcher import allowed_url
from backend.services.input_parser import search_safe
REGISTRY=json.loads((ROOT/'data/verified_advisories.json').read_text(encoding="utf-8"))
async def search_sources(extracted,query=''):
    from backend.services.source_ranking import rank_sources
    seeds=[s for s in REGISTRY if s['family']==extracted.script_family or any(urlparse(u).path==urlparse(s['url']).path and urlparse(u).query.split('&')[0]==urlparse(s['url']).query for u in extracted.urls)]
    results=[];status='fallback';note='No search key; matching official registry entries only.'
    from backend.services.query_builder import build_queries
    query=build_queries(extracted)[0]
    cache_key=(query,hashlib.sha256('\n'.join(extracted.urls).encode()).hexdigest())
    cached=_CACHE.get(cache_key)
    if cached and time.monotonic()-cached[0]<900:return cached[1][0],'cached','Cached discovery results; documents are fetched or individually marked cached.'
    from backend.services.llm_client import reserve_operation
    if query and (settings.tavily_key or settings.brave_key) and reserve_operation():
        try:
            async with httpx.AsyncClient(timeout=12,trust_env=False) as client:
                if settings.tavily_key:
                    response=await client.post('https://api.tavily.com/search',headers={'Authorization':'Bearer '+settings.tavily_key},json={'query':query,'include_domains':list(OFFICIAL_DOMAINS),'max_results':4,'search_depth':'basic','include_answer':False,'include_raw_content':False})
                    response.raise_for_status();items=response.json().get('results',[])
                else:
                    restricted=query[:150]+' ('+' OR '.join('site:'+d for d in OFFICIAL_DOMAINS)+')'
                    response=await client.get('https://api.search.brave.com/res/v1/web/search',params={'q':restricted[:400],'count':5},headers={'X-Subscription-Token':settings.brave_key,'Accept':'application/json'})
                    response.raise_for_status();items=response.json().get('web',{}).get('results',[])
                for item in items:
                    if allowed_url(item.get('url','')):results.append({'url':item['url'],'title':item.get('title',''),'publisher':urlparse(item['url']).hostname,'description':item.get('content','')[:1000],'date':item.get('published_date')})
                status='ok';note=f'Live {"Tavily" if settings.tavily_key else "Brave"} search returned {len(results)} allowlisted URLs. Search snippets are not evidence.'
        except (httpx.HTTPError,ValueError,KeyError):note='Live search failed or was rate limited; matching registry entries retained.'
    explicit=[{'url':u,'title':'Supplied official reference'} for u in extracted.urls if allowed_url(u)]
    result=(rank_sources(explicit+seeds+results,query,extracted.urls),status,note)
    if status=='ok':
        if len(_CACHE)>=256:_CACHE.pop(next(iter(_CACHE)))
        _CACHE[cache_key]=(time.monotonic(),result)
    return result
