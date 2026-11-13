import sys,time,statistics,json,tempfile,os,platform
from pathlib import Path
ROOT=Path(__file__).resolve().parent
import app,ot
f=tempfile.NamedTemporaryFile(delete=False);f.close();app.DB=f.name;c=app.app.test_client();v=[]
for i in range(110):
 t=time.perf_counter();x=c.post('/api/session').json;A=bytes.fromhex(x['A']);b=ot.scalar();B=ot.base(b);B=ot.add(A,B) if i%2 else B;r=c.post('/api/transfer',json={'sid':x['sid'],'B':B.hex()});assert r.status_code==200
 if i>=10:v.append((time.perf_counter()-t)*1000)
res={'samples':100,'warmup':10,'median_ms':round(statistics.median(v),3),'p95_ms':round(sorted(v)[94],3),'min_ms':round(min(v),3),'max_ms':round(max(v),3),'method':'Flask in-process test client; session + receiver public point + server transfer, excludes browser decryption, TLS and network','python':platform.python_version(),'ciphertext_bytes_each':4112,'nonce_bytes_each':12}
open(ROOT/'benchmark.json','w').write(json.dumps(res,indent=2));print(res);os.unlink(app.DB)
