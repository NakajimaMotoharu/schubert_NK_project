"""Independent SS324/352 big-endian length-prefixed public-metadata vectors, no Java production call."""
from pathlib import Path
import json,struct,uuid
b=Path('evidence/01_PT/018_NK-OPS-001');o=b/'evidence/PG35629-snapshot-identity-independent-goldens-v1';o.mkdir();vectors={}
for label,owner in [('anonymous',None),('minimum',1),('maximum',999999999999)]:
 pieces=[b'api-inbox-response',b'schubert.request_inbox',uuid.UUID('00112233-4455-6677-8899-aabbccddeeff').bytes,b'\x01',b'v1',b'QSSRSP01',b'001',b'' if owner is None else struct.pack('>q',owner)];value=b''.join(struct.pack('>I',len(x))+x for x in pieces);vectors[label]=dict(owner=owner,length=len(value),pieceLengths=[len(x) for x in pieces],hex=value.hex())
def signed(n):return (n+2**31)%2**32-2**31
def string_hash(s):
 value=0
 for ch in s:value=signed(31*value+ord(ch))
 return value
value=0
for h in [0,string_hash('QSSRSP01'),string_hash('001'),1]:value=signed(31*value+h)
v=dict(schema='SS324_AAD_INDEPENDENT_LP8',vectors=vectors,recordHashAuthenticatedMinimum=value,hashRecipe='UUID001122..eeff hash0; Java String polynomial for QSSRSP01 and001; OptionalLong1 hash1; record ordered polynomial with signed32 arithmetic',productionCalls=0,secretInputs=False);(o/'goldens.json').open('x').write(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
