"""Sealed PG554 readonly Log/HTTP-session evidence; private keys never leave guest.

New-only output. Reads current Unit/DB twice, original snapshots/journal; no Unit
action, credentials restoration, SQL write, payload export or Production call.
"""
import hashlib
import json
import os
import pathlib
import subprocess
import sys

os.umask(0o077)
HERE = pathlib.Path(__file__).parent
W = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P = pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
ssh = ['ssh', '-i', str(P / 'vm-access'), '-oBatchMode=yes', '-oIdentitiesOnly=yes',
       '-oStrictHostKeyChecking=yes', '-oUserKnownHostsFile=' + str(P / 'known_hosts'),
       '-p', '22222', 'ubuntu@127.0.0.1', 'sudo -n python3 -B -']
PAYLOAD = r'''
import base64,datetime,hashlib,json,os,pathlib,stat,subprocess,sys
os.umask(0o077)
def check(v):
 if not v:raise ValueError('readonly current cohort proof refused')
def sealed(path,sha):
 p=pathlib.Path(path);s=p.lstat();check(stat.S_ISREG(s.st_mode)and s.st_uid==s.st_gid==0 and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600)
 raw=p.read_bytes();check(hashlib.sha256(raw).hexdigest()==sha and p.lstat()==s);return json.loads(raw)
def main():
 check(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441')
 check(str(pathlib.Path('/opt/schubert-nk/current').readlink())=='/opt/schubert-nk/releases/0.1.0-PG548')
 old=sealed('/var/lib/pgpt-s1-preservation/pg553-newrun-preflight-v2/before.private.json','b9a70c2635febf3893b17369af3ddfdf721f040b3d6782423790ee63353bac87')
 after=sealed('/var/lib/pgpt-s1-preservation/pg559-terminal-readback-v2/after.private.json','23263d00948c5df5aca9aa4741a4d0266d9b8d20ebe400c7d180f89bb9ce6677')
 check(old['source']=='969d8ded10c0bf5841d9e3a5c531e922caf4a24a')
 def unchanged():
  for unit,v in after['units'].items():
   args=['systemctl','show',unit]+['-p'+f for f in v]
   lines=subprocess.run(args,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout.decode().splitlines()
   actual=dict(l.split('=',1)for l in lines);check(actual==v and actual['MainPID']==actual['ControlPID']=='0'and actual['Job']=='')
  check(not os.path.lexists('/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf'))
  query="begin isolation level repeatable read read only;set local timezone='UTC';";check(len(after['rows'])==24)
  import re
  for table in after['rows']:
   check(re.fullmatch(r'schubert(?:_web_session)?\.[a-z_]+',table)is not None)
   query+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from(select to_jsonb(t)j from "+table+" t)q;"
  result=subprocess.run(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',query+'commit;'],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  rows={}
  for line in result.stdout.splitlines():
   value=json.loads(line);check(value['table']not in rows);rows[value['table']]=value['rows']
  check(rows==after['rows'])
 unchanged()
 events=[]
 journal=subprocess.run(['journalctl','--boot=cc9ed8747f4f450ea1888de1e42c8441','_SYSTEMD_INVOCATION_ID=3bcfbad981e64d8fadda66f27d1994fa','-o','json','--no-pager'],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
 for line in journal.splitlines():
  record=json.loads(line);message=record.get('MESSAGE','');start=message.find('{')
  if start<0:continue
  try:event=json.loads(message[start:])
  except ValueError:continue
  if event.get('category')=='REQUEST':events.append(event)
 check(len(events)==114)
 namespace={};exec(compile(ORACLE_SRC,'<independent UI/SS oracle>','exec'),namespace)
 keys=[]
 try:
  for name in ('web-log-aes-current','web-session-aes-current'):
   path=pathlib.Path('/etc/schubert-nk/credentials')/name;s=path.lstat()
   check(stat.S_ISREG(s.st_mode)and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1)
   fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
   with os.fdopen(fd,'rb')as f:raw=f.read(4097)
   check(len(raw)<=4096 and path.lstat()==s);parts=raw.split(b'\n')
   check(len(parts)==4 and parts[0]==b'NKKEY1'and parts[1]==b'v1'and parts[3]==b'')
   key=bytearray(base64.b64decode(parts[2],validate=True));check(len(key)==32);keys.append(key)
  result=namespace['verify'](old['rows'],after['rows'],events,keys[0],keys[1])
  check(all(e['appVersion']=='0.1.0-SNAPSHOT'for e in events))
 finally:
  for key in keys:key[:]=b'\0'*len(key)
 unchanged()
 result.update({'productionSource':old['source'],'run':'PG554-ordinary-newrun-v1','all24CurrentRowsUnchangedTwice':True,'allTenUnitsUnchangedTwice':True,'bootCurrent':True,'requestJournalSha256':hashlib.sha256(journal).hexdigest(),'sealedBeforeSha256':'b9a70c2635febf3893b17369af3ddfdf721f040b3d6782423790ee63353bac87','sealedAfterSha256':'23263d00948c5df5aca9aa4741a4d0266d9b8d20ebe400c7d180f89bb9ce6677','keysExported':False,'startsStopsReloadsSqlWrites':0,'qa051FinalPass':False})
 save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg564-independent-log-session-v1');check(not save.exists());save.mkdir(mode=0o700)
 with(save/'result.safe.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
 print(json.dumps(result,sort_keys=True))
try:main()
except Exception as error:
 print(json.dumps({'actualExit':1,'exceptionType':type(error).__name__,'privateDataOutput':False}),file=sys.stderr);sys.exit(1)
'''


def main():
    log = W / 'pg564-log-session-capture-v1.private.log'
    code = W / 'pg564-log-session-capture-v1.exit'
    receipt = W / 'pg564-log-session-capture-v1.safe.json'
    assert not any(p.exists() for p in (log, code, receipt))
    subprocess.run(['python3', '-B', str(HERE / 'pg564_log_session_oracle_test.py')], check=True)
    oracle = (HERE / 'pg564_log_session_oracle.py').read_text()
    with log.open('xb') as stream:
        result = subprocess.run(ssh, input=('ORACLE_SRC=' + repr(oracle) + '\n' + PAYLOAD).encode(),
                                stdout=subprocess.PIPE, stderr=stream)
        stream.flush(); os.fsync(stream.fileno())
    with code.open('x') as stream:
        stream.write(str(result.returncode) + '\n'); stream.flush(); os.fsync(stream.fileno())
    if result.returncode == 0:
        safe = json.loads(result.stdout)
        assert safe['actualExit'] == 0 and safe['plaintextExported'] is False
        with receipt.open('x') as stream:
            json.dump(safe, stream, sort_keys=True); stream.flush(); os.fsync(stream.fileno())
    print(json.dumps({'run': 'PG564-independent-log-session-v1', 'actualExit': result.returncode,
                      'privateLogSha256': hashlib.sha256(log.read_bytes()).hexdigest(),
                      'independentOracleSha256': hashlib.sha256(oracle.encode()).hexdigest(),
                      'productionPT0': True, 'rawExported': False}))
    sys.exit(result.returncode)


if __name__ == '__main__':
    main()
