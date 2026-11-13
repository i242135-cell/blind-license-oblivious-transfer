import os,secrets,sqlite3,time
from flask import Flask,request,jsonify,send_from_directory
import ot
from contextlib import contextmanager
app=Flask(__name__,static_folder='static');app.config['MAX_CONTENT_LENGTH']=2048
DB=os.environ.get('OT_DB','sessions.sqlite3')
@contextmanager
def db():
 c=sqlite3.connect(DB,timeout=10);c.execute('CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY,secret BLOB,public BLOB,created REAL,used INTEGER DEFAULT 0)')
 try:
  with c:yield c
 finally:c.close()
ASSETS=[b'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="500"><rect width="800" height="500" fill="#112b46"/><text x="70" y="230" font-size="64" fill="#6ce5c2">NORTH / Studio</text></svg>',b'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="500"><rect width="800" height="500" fill="#f7dfb8"/><text x="70" y="230" font-size="64" fill="#883c45">FORM / Atelier</text></svg>']
@app.after_request
def headers(r):
 r.headers['Cache-Control']='no-store';r.headers['X-Content-Type-Options']='nosniff';r.headers['Referrer-Policy']='no-referrer';return r
@app.get('/')
def index(): return send_from_directory('static','index.html')
@app.get('/health')
def health():return {'status':'ok'}
@app.post('/api/session')
def start():
 a=ot.scalar();A=ot.base(a);sid=secrets.token_hex(16)
 with db() as c:
  c.execute('DELETE FROM sessions WHERE created < ?',(time.time()-300,))
  if c.execute('SELECT COUNT(*) FROM sessions').fetchone()[0]>=1000:return {'error':'Capacity reached'},429
  c.execute('INSERT INTO sessions VALUES(?,?,?,?,0)',(sid,a,A,time.time()))
 return {'sid':sid,'A':A.hex(),'expires_in':300,'payment':'simulated; not a real purchase'}
@app.post('/api/transfer')
def transfer():
 try:
  data=request.get_json()
  if not isinstance(data,dict) or not isinstance(data.get('sid'),str) or not isinstance(data.get('B'),str):raise ValueError()
  sid=data['sid'];B=bytes.fromhex(data['B'])
  if len(sid)!=32:raise ValueError()
  ot.validate(B)
  with db() as c:
   c.execute('BEGIN IMMEDIATE');row=c.execute('SELECT secret,public,created,used FROM sessions WHERE id=?',(sid,)).fetchone()
   if not row or row[3] or time.time()-row[2]>300:return {'error':'Unavailable session'},409
   a,A,_,_=row;result=ot.encrypt(a,A,B,sid,ASSETS)
   c.execute('UPDATE sessions SET used=1,secret=NULL WHERE id=?',(sid,))
  return {'items':result}
 except (ValueError,KeyError,TypeError):return {'error':'Invalid request'},400
if __name__=='__main__':app.run(host='127.0.0.1',port=5000)
