import json, os, re, unicodedata
from pathlib import Path
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

BASE = Path(__file__).resolve().parent
ROWS = json.loads((BASE/'voters.json').read_text(encoding='utf-8'))
HTML = (BASE/'index.html').read_bytes()

def normalize(s):
    return ' '.join(unicodedata.normalize('NFKC', str(s or '')).casefold().split())

INDEX = [(r, normalize(r[2]), normalize(r[3])) for r in ROWS]
PAGE_SIZE = 25

def search(query, field='both', mode='prefix', page=1):
    q = normalize(query)
    if not q or (mode == 'prefix' and len(q) < 4):
        raise ValueError('Enter at least 4 characters for a prefix search, or select Full name for a shorter exact name.')
    if len(q)>120: raise ValueError('Search text is too long.')
    if field not in ('both','surname','name') or mode not in ('prefix','exact'):
        raise ValueError('Invalid search options.')
    def match(v): return v == q if mode=='exact' else v.startswith(q)
    result = [r for r,s,n in INDEX if (field in ('both','surname') and match(s)) or (field in ('both','name') and match(n))]
    pages = max(1,(len(result)+PAGE_SIZE-1)//PAGE_SIZE)
    page = max(1,min(page,pages))
    return {'rows':result[(page-1)*PAGE_SIZE:page*PAGE_SIZE], 'total':len(result),'page':page,'pages':pages,'pageSize':PAGE_SIZE}

def application(environ, start_response):
    path=environ.get('PATH_INFO','/')
    status='200 OK'; typ='application/json; charset=utf-8'
    if environ.get('REQUEST_METHOD')!='GET':
        status='405 Method Not Allowed'; body=b'{"error":"Method not allowed"}'
    elif path=='/':
        body=HTML; typ='text/html; charset=utf-8'
    elif path=='/api/search':
        params=parse_qs(environ.get('QUERY_STRING',''))
        get=lambda k,d:params.get(k,[d])[0]
        try:
            result=search(get('q',''),get('field','both'),get('mode','prefix'),int(get('page','1')))
        except ValueError as e:
            result={'error':str(e)};status='400 Bad Request'
        body=json.dumps(result,ensure_ascii=False).encode('utf-8')
    elif path=='/health': body=b'{"status":"ok"}'
    else: status='404 Not Found'; body=b'{"error":"Not found"}'
    start_response(status,[('Content-Type',typ),('Content-Length',str(len(body))),('Cache-Control','no-store'),('X-Content-Type-Options','nosniff'),('Referrer-Policy','no-referrer'),('X-Robots-Tag','noindex, nofollow'),('X-Frame-Options','DENY'),('Content-Security-Policy',"default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'")])
    return [body]

if __name__=='__main__':
    port=int(os.environ.get('PORT','8000'))
    print(f'Open http://127.0.0.1:{port} in your browser.')
    with make_server('127.0.0.1',port,application) as server: server.serve_forever()
