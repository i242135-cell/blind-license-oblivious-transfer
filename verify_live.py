"""Run a few simulated purchases against the public teaching demo; save summary evidence."""
from pathlib import Path
import urllib.request,urllib.error,json,datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import ot
ROOT=Path(__file__).resolve().parent
BASE='https://kashan.pythonanywhere.com'
def request(path,data=None):
 req=urllib.request.Request(BASE+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json','User-Agent':'Blind-License-Deployment-Verification'})
 try:
  with urllib.request.urlopen(req,timeout=35) as r:return r.status,r.read()
 except urllib.error.HTTPError as e:return e.code,e.read()
def post(path,data):
 status,body=request(path,data);return status,json.loads(body)
results=[]
for path in ['/','/health','/static/libsodium-sumo.js','/static/libsodium-wrappers.js']:
 status,body=request(path);assert status==200
 if path=='/health':assert json.loads(body)=={'status':'ok'}
 results.append({'check':path,'status':status,'bytes':len(body)})
for choice,label in [(0,b'NORTH / Studio'),(1,b'FORM / Atelier')]:
 status,x=post('/api/session',{});assert status==200
 A=bytes.fromhex(x['A']);ot.validate(A);b=ot.scalar();B=ot.base(b)
 if choice:B=ot.add(B,A)
 body={'sid':x['sid'],'B':B.hex()};status,r=post('/api/transfer',body);assert status==200
 key=ot.key(ot.mul(b,A),x['sid'],A,B,choice);v=r['items'][choice];plain=AESGCM(key).decrypt(bytes.fromhex(v['nonce']),bytes.fromhex(v['ciphertext']),ot.aad(x['sid'],choice));length=int.from_bytes(plain[:4],'big');svg=plain[4:4+length]
 assert svg.startswith(b'<svg') and label in svg
 assert all(len(bytes.fromhex(i['ciphertext']))==4112 for i in r['items'])
 results.append({'check':'choice '+str(choice),'result':'expected SVG decrypted locally','ciphertext_bytes_each':4112})
 replay,_=post('/api/transfer',body);assert replay==409;results.append({'check':'replay choice '+str(choice),'status':replay})
status,x=post('/api/session',{});assert status==200
status,_=post('/api/transfer',{'sid':x['sid'],'B':'00'*32});assert status==400
results.append({'check':'identity point rejected','status':status})
evidence={'url':BASE+'/','verified_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'HTTPS page/assets/health and end-to-end API transfers with local decryption; not a proof of cryptographic security','results':results}
(ROOT/'deployment_verification.json').write_text(json.dumps(evidence,indent=2))
print(json.dumps(evidence,indent=2))
