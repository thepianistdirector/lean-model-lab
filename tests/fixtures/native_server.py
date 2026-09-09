"""TEST FIXTURE ONLY: emulates HTTP records; performs no model inference."""
import json
import re
import sys
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer


def argument(name,default):
    return sys.argv[sys.argv.index(name)+1] if name in sys.argv else default


if '--version' in sys.argv:
    print('TEST_FIXTURE_ONLY native server protocol bb4caa7; no model inference')
    raise SystemExit(0)

CONCURRENCY=int(argument('--parallel','1'))
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def send_json(self,value):
        raw=json.dumps(value).encode();self.send_response(200)
        self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)))
        self.end_headers();self.wfile.write(raw)
    def do_GET(self):
        if self.path=='/health':self.send_json({'status':'ok'})
        elif self.path=='/slots':self.send_json([{'id':i,'n_ctx':2048,'is_processing':False} for i in range(CONCURRENCY)])
        else:self.send_error(404)
    def do_POST(self):
        request=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        if self.path=='/tokenize':
            self.send_json({'tokens':[ord(c) for c in request['content']]});return
        if self.path!='/completion':self.send_error(404);return
        prompt=''.join(chr(t) for t in request['prompt'])
        match=re.search(r'KEY: ([A-Z]{5})',prompt)
        if match:
            key=match.group(1)
        else:
            # Independent tiny interpreter for the INERT v3 protocol fixture.
            # No production candidate/evaluator imports or model execution.
            table={}
            for kind,name,value in re.findall(r'^(VALUE|REF) ([A-Z]{5}) ([A-Z]{5})$',prompt,re.M):
                table[name]=(kind,value)
            name=re.search(r'^ASK ([A-Z]{5})$',prompt,re.M).group(1)
            seen=set();key='ERROR'
            while name in table and name not in seen:
                seen.add(name);kind,value=table[name]
                if kind=='VALUE':key=value;break
                name=value
        fields={'id_slot':request['id_slot'],'tokens_evaluated':len(request['prompt'])}
        settings={k:request[k] for k in ('samplers','temperature','seed','n_predict','ignore_eos','stop','stream')}
        settings.update(grammar='',lora=[],backend_sampling=False)
        cache=100 if request['cache_prompt'] else 0
        records=[{**fields,'id_slot':-1,'stop':False,'tokens':[0],'content':'','tokens_predicted':0,
                  'prompt_progress':{'total':len(request['prompt']),'cache':cache,'processed':cache,'time_ms':0}},
                 {**fields,'id_slot':-1,'stop':False,'tokens':[ord(c) for c in key],'content':key},
                 {**fields,'stop':True,'tokens':[],'content':'','tokens_predicted':len(key)+1,
                  'truncated':False,'stop_type':'eos','stopping_word':'','generation_settings':settings,
                  'timings':{'cache_n':cache,'prompt_n':len(request['prompt'])-cache,'predicted_n':len(key)+1}}]
        self.send_response(200);self.send_header('Content-Type','text/event-stream');self.end_headers()
        for record in records:
            self.wfile.write(b'data: '+json.dumps(record).encode()+b'\n\n');self.wfile.flush()


if __name__=='__main__':
    ThreadingHTTPServer(('127.0.0.1',int(argument('--port','0'))),Handler).serve_forever()
