"""Independent literal error wire and NIST AES256-GCM vector; no real keys or DB."""
import copy,json,pathlib,struct,uuid,zlib
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pg478_inbox_oracle import aad,plaintext,validate
checks=0
def check(v):
 global checks
 checks+=1;assert v
key=bytes(32);nonce=bytes(12)
# NIST AES-256-GCM, zero key/IV, empty plaintext/AAD, fixed published tag.
check(AESGCM(key).decrypt(nonce,bytes.fromhex('530f8afbc74536b9a963b4f1c4cb738b'),b'')==b'')
row={'message_id':'11111111-2222-4333-8444-555555555555','request_layout_id':'UDTREQ01','request_version':'001','response_layout_id':'UDTRSP01','response_version':'001','owner_user_id':1,'response_key_version':'v1','fingerprint_key_version':'v1','request_fingerprint_hmac':'a'*64,'processing_state':'ERROR','result_ref_type':'NONE','result_ref_id':None,'result_ref_uuid':None,'operation_token':None,'created_at':'2026-10-05T06:00:00Z','completed_at':'2026-10-05T06:00:01.123456Z','expires_at':'2026-10-06T06:00:01.123456Z'}
layout=json.loads(pathlib.Path(__file__).with_name('pg478_independent_layouts.json').read_text())['UDTRSP01']
# Literal 576-byte error wire, N fields zero/X fields space, all offsets from UI232/236.
wire=bytearray(b' '*576)
for start,value in [(0,b'SCHBNK01001UDTRSP01001SS'),(24,b'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee'),(60,row['message_id'].encode()),(96,b'20261005150001123'),(113,b'1'*64),(177,b'0256000320000000000000000000576'),(208,b'0104')]:wire[start:start+len(value)]=value
for start,length in [(256,12),(379,17),(396,17),(413,17),(430,3),(433,9)]:wire[start:start+length]=b'0'*length
validate(row,wire,layout);checks+=1
parts=[b'api-inbox-response',b'schubert.request_inbox',bytes.fromhex('11111111222243338444555555555555'),b'\1',b'v1',b'UDTRSP01',b'001',bytes.fromhex('0000000000000001')]
check(aad(row)==b''.join(struct.pack('>I',len(p))+p for p in parts))
encrypted=AESGCM(key).encrypt(nonce,zlib.compress(bytes(wire),3),aad(row));stored=b'NKENC1\1\2v1'+nonce+encrypted;row['response_body_encrypted']='\\x'+stored.hex()
check(plaintext(row,key)==wire)
for start in [0,11,22,23,60,96,113,177,181,187,193,199,208,212,256,300]:
 bad=bytearray(wire);bad[start]=ord('!')
 try:validate(row,bad,layout)
 except (ValueError,UnicodeDecodeError):checks+=1
 else:raise AssertionError('mutated literal wire accepted')
for change in [{'owner_user_id':2},{'message_id':'99999999-2222-4333-8444-555555555555'},{'response_layout_id':'USRRSP01'},{'response_key_version':'v2'}]:
 wrong=copy.deepcopy(row);wrong.update(change)
 try:plaintext(wrong,key)
 except (ValueError,InvalidTag):checks+=1
 else:raise AssertionError('AAD mutation accepted')
for index in [0,6,7,8,-1]:
 wrong=copy.deepcopy(row);value=bytearray(stored);value[index]^=1;wrong['response_body_encrypted']='\\x'+value.hex()
 try:plaintext(wrong,key)
 except (ValueError,InvalidTag,UnicodeDecodeError):checks+=1
 else:raise AssertionError('envelope mutation accepted')
print('PG478_INBOX_ORACLE_TEST independentAssertions='+str(checks)+' privateDataRead0=true productionPT0=true')
