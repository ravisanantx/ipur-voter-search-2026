import json, os, re, unicodedata
from pathlib import Path
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

BASE = Path(__file__).resolve().parent
ROWS = json.loads((BASE/'voters.json').read_text(encoding='utf-8'))
HTML = (BASE/'index.html').read_bytes()
BASKET = (BASE/'basket.png').read_bytes()

def normalize(s):
    return ' '.join(unicodedata.normalize('NFKC', str(s or '')).casefold().split())

INDEX = [(r, normalize(r[2]), normalize(r[3]), normalize(r[5])) for r in ROWS]
PAGE_SIZE = 25

def search(name='', surname='', page=1, hno=''):
    name, surname, hno = normalize(name), normalize(surname), normalize(hno)
    if not name and not surname and not hno:
        raise ValueError('Enter NAME, SURNAME, or H NO.')
    if any(len(v)>120 for v in (name, surname, hno)):
        raise ValueError('Search text is too long.')
    def match(value, query):
        return not query or value == query or (len(query) >= 3 and value.startswith(query))
    # Each populated search field must match the same record. Blank fields are optional.
    # House number accepts exact input (including 1–2 characters), or a prefix of 3+.
    # Present NAME before SURNAME; preserve original source ordering.
    result = [[r[0], r[1], r[3], r[2], *r[4:]] for r,s,n,h in INDEX
              if match(n, name) and match(s, surname) and match(h, hno)]
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
    elif path=='/basket.png':
        body=BASKET; typ='image/png'
    elif path=='/api/search':
        params=parse_qs(environ.get('QUERY_STRING',''))
        get=lambda k,d:params.get(k,[d])[0]
        try:
            result=search(get('name',''),get('surname',''),int(get('page','1')),get('hno',''))
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
