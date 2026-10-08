"""Independent Python AES-GCM/zlib + published UI byte tables, not production codec calls.
Only current seven query/NONE fixtures; broader routes require a separate independent oracle.
"""
import base64,datetime,hashlib,json,os,pathlib,re,stat,struct,sys,unicodedata,uuid,zlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pg478_cleanup_oracle import instant,candidates
def require(value):
 if not value:raise ValueError('independent snapshot proof refused')
def bounded_candidates(rows,bounds,cutoff):
 low=candidates(rows,bounds['lower']);high=candidates(rows,bounds['upper'])
 require(instant(bounds['lower'])<=instant(cutoff)<=instant(bounds['upper']))
 expected=candidates(rows,cutoff)
 require(all(set(low[k])<=set(expected[k])<=set(high[k]) for k in low))
 require(all(low[k]==high[k] for k in low if k!='web_http_sessions'))
 require(all(not v for k,v in expected.items()if k not in ['auth_sessions','login_ip_attempts','web_http_sessions','inbox_scan_candidates']))
 return low,expected,high
def aad(row):
 parts=[b'api-inbox-response',b'schubert.request_inbox',uuid.UUID(row['message_id']).bytes,b'\1',row['response_key_version'].encode('ascii'),row['response_layout_id'].encode('ascii'),b'001',struct.pack('>q',row['owner_user_id'])]
 return b''.join(struct.pack('>I',len(p))+p for p in parts)
def plaintext(row,key):
 encoded=row['response_body_encrypted'];require(encoded.startswith('\\x'));raw=bytes.fromhex(encoded[2:])
 require(raw[:7]==b'NKENC1\1' and 1<=raw[7]<=16 and len(raw)>=8+raw[7]+12+16)
 k=8+raw[7];require(raw[8:k].decode('ascii')==row['response_key_version'])
 compressed=AESGCM(key).decrypt(raw[k:k+12],raw[k+12:],aad(row))
 z=zlib.decompressobj();wire=z.decompress(compressed,1000001)
 require(z.eof and not z.unused_data and not z.unconsumed_tail and 256<=len(wire)<=1000000);return bytearray(wire)
def fields(block,definition,success):
 require(sum(f[2] for f in definition)==len(block))
 for name,start,length,kind,required in definition:
  raw=bytes(block[start:start+length]);require(len(raw)==length)
  if not success:require(raw==(b'0' if kind=='N' else b' ')*length);continue
  if kind=='N':
   require(re.fullmatch(b'[0-9]+',raw) is not None)
   if length==17:datetime.datetime.strptime(raw.decode('ascii'),'%Y%m%d%H%M%S%f')
  elif kind=='B':require(raw in [b'0',b'1'])
  else:
   text=raw.rstrip(b' ').decode('utf8');require(unicodedata.normalize('NFC',text)==text and not any(c in text for c in '\r\n\t\0'))
   if required=='M':require(bool(text))
   if name=='Reserved':require(raw==b' '*length)
   if name=='Role':require(text in ['USER','ADMIN'])
   if name=='State':require(text in ['ACTIVE','DISABLED','LOCKED'])
   if name=='Game code':require(text in ['NUKITASHI1','NUKITASHI2'])
   if name=='Entry type':require(text in ['dialogue','narration'])
   if name=='Level':require(text in ['INFO','WARN','ERROR'])
   if length==17 and text:datetime.datetime.strptime(text,'%Y%m%d%H%M%S%f')
def validate(row,wire,layout):
 rid=row['response_layout_id'];require(row['request_layout_id']==rid[:3]+'REQ01' and row['request_version']==row['response_version']=='001')
 require(row['result_ref_type']=='NONE' and row['result_ref_id'] is row['result_ref_uuid'] is row['operation_token'] is None)
 require(1<=row['owner_user_id']<=999999999999 and row['fingerprint_key_version']=='v1' and re.fullmatch('[0-9a-f]{64}',row['request_fingerprint_hmac']) is not None)
 require(instant(row['created_at'])<=instant(row['completed_at']) and instant(row['expires_at'])>=instant(row['completed_at'])+datetime.timedelta(hours=24))
 require(wire[:11]==b'SCHBNK01001' and wire[11:22]==(rid+'001').encode() and wire[22:24]==b'SS')
 mid=bytes(wire[24:60]).decode('ascii');require(str(uuid.UUID(mid))==mid and uuid.UUID(mid).int!=0)
 require(wire[60:96]==row['message_id'].encode() and re.fullmatch(b'[0-9a-f]{64}',bytes(wire[113:177])) is not None)
 time=instant(row['completed_at']).astimezone(datetime.timezone(datetime.timedelta(hours=9)))
 require(wire[96:113]==(time.strftime('%Y%m%d%H%M%S')+f'{time.microsecond//1000:03}').encode() and wire[177:181]==b'0256' and wire[212:256]==b' '*44)
 for a,b in [(181,187),(187,193),(193,199),(199,208)]:require(re.fullmatch(b'[0-9]+',bytes(wire[a:b])) is not None)
 dl,rl,count,total=[int(bytes(wire[a:b])) for a,b in [(181,187),(187,193),(193,199),(199,208)]]
 require(dl==layout['dataLength'] and rl==layout['recordLength'] and count<=layout['maximumRecords'] and total==len(wire)==256+dl+rl*count)
 code=bytes(wire[208:212]);require(code in ([b'0000',b'0104'] if rid=='UDTRSP01' else [b'0000',b'9001']))
 success=code==b'0000';require(success==(row['processing_state']=='COMPLETED') and (success or count==0))
 data=wire[256:256+dl];fields(data,layout['dataFields'],success)
 if success and dl==9:require(int(data)==count)
 if success and dl==48:
  page,size,amount,pages,first,last=[int(data[a:b]) for a,b in [(0,6),(6,9),(9,18),(18,24),(24,33),(33,42)]]
  require(page>=1 and size==(50 if rid=='USRRSP01' else 100) and pages==max(1,(amount+size-1)//size) and page<=pages)
  expected=min(size,max(0,amount-(page-1)*size));require(count==expected and first==((page-1)*size+1 if count else 0) and last==(first+count-1 if count else 0))
 if success and rid=='UDTRSP01':require(1<=int(data[:12])<=999999999999 and int(data[174:177])<=2)
 for index in range(count):
  record=wire[256+dl+rl*index:256+dl+rl*(index+1)];fields(record,layout['recordFields'],True)
  if rid=='SRCRSP01':
   audio=record[4534:4535];require((audio==b'0' and record[4535:4547]==b' '*12 and record[5059:5571]==b' '*512) or (audio==b'1' and re.fullmatch(b'[0-9]{12}',bytes(record[4535:4547])) is not None and bytes(record[5059:5571]).strip()))
def main():
 require(os.geteuid()==0 and sys.argv[1:]==['capture'])
 root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg553-newrun-preflight-v2');data=json.loads((root/'before.private.json').read_text());layouts=json.loads(pathlib.Path(__file__).with_name('pg478_independent_layouts.json').read_text())
 require(data['source']=='969d8ded10c0bf5841d9e3a5c531e922caf4a24a' and data['manifestSha256']=='a224ea9cf421b06e7029b1f8845f2a7eb3d620b5ec2bdf90bfe64c731b99515b')
 low,_,high=bounded_candidates(data['rows'],data['bounds'],data['bounds']['lower'])
 keypath=pathlib.Path('/etc/schubert-nk/credentials/api-inbox-response-aes-current');before=keypath.lstat();require(stat.S_ISREG(before.st_mode) and before.st_uid==0 and before.st_nlink==1 and not keypath.is_symlink() and stat.S_IMODE(before.st_mode) in [0o400,0o600])
 raw=keypath.read_bytes();parts=raw.split(b'\n');require(len(parts)==4 and parts[0]==b'NKKEY1' and parts[1]==b'v1' and not parts[-1]);key=bytearray(base64.b64decode(parts[2],validate=True));require(len(key)==32 and before==keypath.lstat())
 deleted=[];proof=[]
 try:
  for row in data['rows']['schubert.request_inbox']:
   if row['message_id'] not in low['inbox_scan_candidates']:continue
   require(row['response_key_version']=='v1' and row['response_layout_id'] in layouts)
   wire=plaintext(row,key)
   try:validate(row,wire,layouts[row['response_layout_id']]);deleted.append(row['message_id']);proof.append({'messageId':row['message_id'],'plaintextSha256':hashlib.sha256(wire).hexdigest(),'byteLength':len(wire),'valid':True})
   finally:wire[:]=b'\0'*len(wire)
 finally:key[:]=b'\0'*len(key)
 require(sorted(deleted)==low['inbox_scan_candidates'])
 result={'source':data['source'],'manifestSha256':data['manifestSha256'],'beforeSha256':hashlib.sha256((root/'before.private.json').read_bytes()).hexdigest(),'bounds':data['bounds'],'expectedLower':low,'expectedUpper':high,'actualCutoffIndependentCalculationRequired':True,'varyingCategories':[k for k in low if low[k]!=high[k]],'inboxExpectedDeleted':sorted(deleted),'inboxExpectedProtected':sorted(r['message_id'] for r in data['rows']['schubert.request_inbox']if r['message_id']not in deleted),'inboxIndependentProof':proof,'starts0':True}
 with (root/'cleanup-oracle.private.json').open('x') as f:os.fchmod(f.fileno(),0o600);json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
 print(json.dumps({'independentCandidateCountsLower':{k:len(v) for k,v in low.items()},'independentCandidateCountsUpper':{k:len(v) for k,v in high.items()},'independentValidInboxCount':len(deleted),'actualCutoffIndependentCalculationRequired':True,'plaintextLogged':False,'starts0':True},sort_keys=True))
if __name__=='__main__':main()
