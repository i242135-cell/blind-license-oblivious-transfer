import unittest,time,statistics,json,tempfile,os
import app,ot
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
class SecurityTests(unittest.TestCase):
 def setUp(self):
  f=tempfile.NamedTemporaryFile(delete=False);f.close();app.DB=f.name;self.c=app.app.test_client()
 def tearDown(self):os.unlink(app.DB)
 def flow(self,c):
  x=self.c.post('/api/session').json;A=bytes.fromhex(x['A']);b=ot.scalar();B=ot.base(b);B=ot.add(A,B) if c else B
  body={'sid':x['sid'],'B':B.hex()};r=self.c.post('/api/transfer',json=body);return x,A,b,B,body,r
 def test_both_choices(self):
  for c in [0,1]:
   x,A,b,B,_,r=self.flow(c);k=ot.key(ot.mul(b,A),x['sid'],A,B,c);v=r.json['items'][c];p=AESGCM(k).decrypt(bytes.fromhex(v['nonce']),bytes.fromhex(v['ciphertext']),ot.aad(x['sid'],c));n=int.from_bytes(p[:4],'big');self.assertEqual(p[4:4+n],app.ASSETS[c])
 def test_wrong_branch(self):
  x,A,b,B,_,r=self.flow(0);k=ot.key(ot.mul(b,A),x['sid'],A,B,1);v=r.json['items'][1]
  with self.assertRaises(Exception):AESGCM(k).decrypt(bytes.fromhex(v['nonce']),bytes.fromhex(v['ciphertext']),ot.aad(x['sid'],1))
 def test_tamper(self):
  x,A,b,B,_,r=self.flow(0);v=r.json['items'][0];ct=bytearray.fromhex(v['ciphertext']);ct[20]^=1
  with self.assertRaises(Exception):AESGCM(ot.key(ot.mul(b,A),x['sid'],A,B,0)).decrypt(bytes.fromhex(v['nonce']),bytes(ct),ot.aad(x['sid'],0))
 def test_replay(self):
  *_,body,r=self.flow(0);self.assertEqual(r.status_code,200);self.assertEqual(self.c.post('/api/transfer',json=body).status_code,409)
 def test_invalid_point(self):
  x=self.c.post('/api/session').json;self.assertEqual(self.c.post('/api/transfer',json={'sid':x['sid'],'B':'00'*32}).status_code,400)
 def test_expiry(self):
  x=self.c.post('/api/session').json
  with app.db() as d:d.execute('UPDATE sessions SET created=0')
  self.assertEqual(self.c.post('/api/transfer',json={'sid':x['sid'],'B':ot.base(ot.scalar()).hex()}).status_code,409)
 def test_padding(self):
  *_,r=self.flow(0);self.assertEqual([len(bytes.fromhex(i['ciphertext'])) for i in r.json['items']],[4112,4112])
 def test_no_sender_secret_after_use(self):
  x,*_=self.flow(0)
  with app.db() as d:self.assertIsNone(d.execute('SELECT secret FROM sessions WHERE id=?',(x['sid'],)).fetchone()[0])
if __name__=='__main__':unittest.main(verbosity=2)
