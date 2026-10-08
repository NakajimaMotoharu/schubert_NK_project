"""Once-only real TLS/body/cookie -> encrypted DB session oracle after A01; secrets memory-only."""
import datetime
import hashlib
import json
import os
import pathlib
import subprocess
import time
from pg607_a01_when_ready import GUARD

R=pathlib.Path(__file__).resolve().parent
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
PAYLOAD=r'''
import base64,datetime,hashlib,http.client,json,os,pathlib,stat,ssl,subprocess,time
os.umask(0o077)
def require(value):
 if not value:raise ValueError('independent TLS cookie/session capture refused')
def probe():
 e={'__name__':'sealed_current_generation_guard'};exec(compile(GUARD,'<current same-parent guard>','exec'),e);return e['units']
def query(sql):
 r=subprocess.run(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],capture_output=True,timeout=15)
 require(r.returncode==0 and not r.stderr and 0<len(r.stdout)<=1048576);return r.stdout
def main():
 require(os.geteuid()==0)
 oracle={'__name__':'independent_client_oracle'};exec(compile(CLIENT,'<literal Cookie/DOM oracle>','exec'),oracle)
 crypto={'__name__':'independent_crypto_oracle'};exec(compile(CRYPTO,'<literal UI/SS AES-GCM oracle>','exec'),crypto)
 before=probe()
 start=datetime.datetime.now(datetime.timezone.utc)
 ca=pathlib.Path('/var/lib/caddy/.local/share/caddy/pki/authorities/local/root.crt');ca_before=ca.lstat();context=ssl.create_default_context(cafile=str(ca))
 root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg608-client-v1');require(not os.path.lexists(root));root.mkdir(mode=0o700)
 with(root/'request-reserved.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump({'at':start.isoformat(),'once':True,'path':'/login','rawValuesStored':False},f);f.flush();os.fsync(f.fileno())
 connection=http.client.HTTPSConnection('10.0.2.15',55160,timeout=5,context=context)
 try:
  connection.request('GET','/login');response=connection.getresponse();body=response.read(65537)
  headers=response.getheaders();require(response.status==200 and 0<len(body)<=65536)
 finally:connection.close()
 end=datetime.datetime.now(datetime.timezone.utc);require(ca.lstat()==ca_before)
 cookie_values=[v for k,v in headers if k.lower()=='set-cookie'];lookup=oracle['cookie_identity'](cookie_values)
 require(len(lookup)==64 and all(c in '0123456789abcdef'for c in lookup))
 row=json.loads(query("begin isolation level repeatable read read only;select coalesce(jsonb_agg(to_jsonb(t)),'[]'::jsonb)from schubert_web_session.web_http_sessions t where session_id_hash='"+lookup+"';commit;"))
 require(type(row)is list and len(row)==1);row=row[0]
 keypath=pathlib.Path('/etc/schubert-nk/credentials/web-session-aes-current');metadata=keypath.lstat()
 require(stat.S_ISREG(metadata.st_mode)and metadata.st_uid==metadata.st_gid==0 and stat.S_IMODE(metadata.st_mode)==0o600 and metadata.st_nlink==1)
 key=None;plaintext=None
 try:
  fd=os.open(keypath,os.O_RDONLY|os.O_NOFOLLOW)
  with os.fdopen(fd,'rb')as f:parts=f.read(4097).split(b'\n')
  require(len(parts)==4 and parts[0]==b'NKKEY1'and parts[1]==b'v1'and parts[3]==b''and keypath.lstat()==metadata)
  key=bytearray(base64.b64decode(parts[2],validate=True));require(len(key)==32)
  plaintext,nonce=crypto['decrypt'](row['attributes_ciphertext'],row['key_version'],key,crypto['session_aad'](row),16384)
  crypto['anonymous_session'](row,plaintext)
  value=crypto['closed_json'](plaintext)
  result=oracle['body_identity'](body,value,row['session_id_hash'],lookup)
 finally:
  if key is not None:key[:]=b'\0'*len(key)
  if plaintext is not None:plaintext[:]=b'\0'*len(plaintext)
 sql="select coalesce(jsonb_agg(to_jsonb(t)),'[]'::jsonb)from schubert.app_logs t where request_uri='/login'and http_method='GET'and logged_at>='"+start.isoformat()+"'::timestamptz and logged_at<='"+end.isoformat()+"'::timestamptz;"
 deadline=time.monotonic()+45
 while time.monotonic()<deadline:
  logs=json.loads(query(sql))
  if logs:break
  time.sleep(.1)
 require(type(logs)is list and len(logs)==1 and logs[0]['status_code']==200 and logs[0]['details']['responseBytes']==len(body))
 after=probe()
 require(all(before[u]['MainPID']==after[u]['MainPID']and before[u]['InvocationID']==after[u]['InvocationID']and before[u]['ExecMainStartTimestampMonotonic']==after[u]['ExecMainStartTimestampMonotonic']for u in before))
 result.update(actualExit=0,run='PG608-client-v1',productionSource='23b14a44b10504172e030bbd6625926bf049fb5c',startedUTC=start.isoformat(),endedUTC=end.isoformat(),ordinarySameParentApiWebCaddyBeforeAfter=True,tlsPublicCaValidated=True,cookieFlagsVerified=True,logResponseBytesEqualsReceivedBody=True,anonymousFormat2EmptyOperationsEightHoursVerified=True,rawCookieCsrfKeyStored=False,formalAccepted=False)
 with(root/'result.safe.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
 print(json.dumps(result))
try:main()
except Exception as error:
 import traceback
 print(json.dumps({'actualExit':1,'exceptionType':type(error).__name__,'frames':[{'method':f.name,'line':f.lineno}for f in traceback.extract_tb(error.__traceback__)],'privateValuesOutput':False}));raise SystemExit(1)
'''


def main():
    os.umask(0o077)
    assert not os.path.lexists(W/'pg608-client-v1.private.log')
    deadline=time.monotonic()+1860
    while not (W/'pg607-chr-a01-native-v1.safe.json').exists():
        assert time.monotonic()<deadline
        if (W/'pg607-chr-a01-native-v1.exit').exists():
            assert (W/'pg607-chr-a01-native-v1.exit').read_bytes()==b'0\n'
        time.sleep(.2)
    assert json.loads((W/'pg607-chr-a01-native-v1.safe.json').read_bytes())['actualExit']==0
    assert GUARD.endswith('print(json.dumps(units))\n')
    guard=GUARD[:-len('print(json.dumps(units))\n')]
    prefix='GUARD='+repr(guard)+'\nCLIENT='+repr((R/'pg576_client_oracle.py').read_text())+'\nCRYPTO='+repr((R/'pg564_log_session_oracle.py').read_text())+'\n'
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    result=subprocess.run(ssh,input=(prefix+PAYLOAD).encode(),capture_output=True,timeout=80)
    with(W/'pg608-client-v1.private.log').open('xb')as f:f.write(result.stderr);f.write(result.stdout);f.flush();os.fsync(f.fileno())
    with(W/'pg608-client-v1.exit').open('x')as f:f.write(str(result.returncode)+'\n')
    if result.returncode==0:
        value=json.loads(result.stdout);value.update(hostStartedUTC=started,operatorSource=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip())
        with(W/'pg608-client-v1.safe.json').open('x')as f:json.dump(value,f,sort_keys=True)
    print(json.dumps({'actualExit':result.returncode,'rawValuesExported':False,'privateLogSha256':hashlib.sha256((W/'pg608-client-v1.private.log').read_bytes()).hexdigest()}));raise SystemExit(result.returncode)


if __name__=='__main__':main()
