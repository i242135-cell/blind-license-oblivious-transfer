"""Educational DH OT composition using libsodium Ristretto255; not a production audit."""
import ctypes,ctypes.util,secrets,hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
s=ctypes.CDLL(ctypes.util.find_library('sodium'));s.sodium_init()
s.crypto_core_ristretto255_scalar_random.restype=None
def call(name,*args):
 out=ctypes.create_string_buffer(32)
 rc=getattr(s,name)(out,*args)
 if rc not in (0,None): raise ValueError('Invalid group operation')
 return out.raw

def scalar(): return call('crypto_core_ristretto255_scalar_random')
def base(x): return call('crypto_scalarmult_ristretto255_base',x)
def mul(x,p):
 validate(p);return call('crypto_scalarmult_ristretto255',x,p)
def add(p,q): return call('crypto_core_ristretto255_add',p,q)
def sub(p,q): return call('crypto_core_ristretto255_sub',p,q)
def validate(p):
 if len(p)!=32 or p==bytes(32) or s.crypto_core_ristretto255_is_valid_point(p)!=1: raise ValueError('Invalid point')
def key(shared,sid,A,B,i):
 return hashlib.sha256(b'OT-LICENSE-v1'+bytes.fromhex(sid)+A+B+bytes([i])+shared).digest()
def aad(sid,i):return bytes.fromhex(sid)+bytes([i])
def encrypt(a,A,B,sid,messages):
 validate(B);validate(sub(B,A));out=[]
 for i,m in enumerate(messages):
  shared=mul(a,B if i==0 else sub(B,A));nonce=secrets.token_bytes(12)
  padded=len(m).to_bytes(4,'big')+m
  if len(padded)>4096:raise ValueError('Asset too large')
  padded=padded.ljust(4096,b'\0')
  ct=AESGCM(key(shared,sid,A,B,i)).encrypt(nonce,padded,aad(sid,i))
  out.append({'nonce':nonce.hex(),'ciphertext':ct.hex()})
 return out
