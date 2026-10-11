"""Independent read-only full post after current corrected preparation.

Checks actual kernel/runtime/resources and literal expected roles/receipt; never
repairs, starts, re-prepares, or derives expected data from Production methods.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1450_current_cold_retry import observer,W
from pg1446_current_cold_stage import SSH


def payload():
    prefix=observer().split('import dbus,time,sys,types\n',1)[0]
    raw=prefix+'\n'+BODY;ast.parse(raw);return raw


BODY=r'''
import dbus,types
os.umask(0o077)
ROOT=pathlib.Path('/run/schubert-nk')
SAVE=BASE/'pg1453-current-cold-independent-post-v1';SAVE.mkdir(mode=0o700)
prepared=BASE/'pg1452-current-cold-prepared-v1'
complete=(prepared/'complete.private').read_bytes()
require(complete==b'allScopesReturnedNormally=true\nfinitePreparation=true\nepochDbBusinessWrites=0\n')
before_raw=(prepared/'after.private.json').read_bytes();before=json.loads(before_raw)
require(set(before)=={'current','runtime','parent'})
contract=types.ModuleType('contract');exec(INVENTORY_SOURCE,contract.__dict__)
ROLE_IDS={'backup':(992,977),'cleanup':(0,0),'expiry':(0,0),'inspector':(991,976),
 'ordinary-api193':(999,981),'ordinary-bootstrap196':(999,981),'ordinary-inspector196':(991,976),
 'ordinary-web193':(997,980),'parent':(0,0),'root-api':(0,0),'root-api193':(0,0),'root-web193':(0,0)}
def runtime_check():
 names={'startup','backup-request','cleanup-request','expiry-request','pt-coverage','maintenance.lock','startup-admission.lock','maintenance'}
 require(set(os.listdir(ROOT))==names and metadata(ROOT)[2:6]==[0,0,stat.S_IFDIR|0o755,8] and not os.listxattr(ROOT))
 runtime={n:metadata(ROOT/n)for n in names};runtime['@root']=metadata(ROOT)
 runtime['children']={n:metadata(ROOT/'pt-coverage'/n)for n in ROLE_IDS}
 require(runtime==before['runtime'])
 for n in ['startup','backup-request','cleanup-request','expiry-request','maintenance']:
  require(runtime[n][2:6]==[0,0,stat.S_IFDIR|0o700,2] and not os.listdir(ROOT/n) and not os.listxattr(ROOT/n))
 coverage=ROOT/'pt-coverage';require(runtime['pt-coverage'][2:6]==[0,0,stat.S_IFDIR|0o755,14] and set(os.listdir(coverage))==set(ROLE_IDS) and not os.listxattr(coverage))
 for n,(uid,gid)in ROLE_IDS.items():
  require(runtime['children'][n][2:6]==[uid,gid,stat.S_IFDIR|0o700,2] and not os.listdir(coverage/n) and not os.listxattr(coverage/n))
 metas={n:runtime[n]for n in['maintenance.lock','startup-admission.lock']}
 require(contract.free_flocks(pathlib.Path('/proc/locks').read_text().splitlines(),metas))
 require(not pathlib.Path('/proc/'+str(before['parent']['pid'])).exists())
 return runtime
def peer_check():
 sql=contract.all_client_sql(0)+"select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and granted;"
 require(command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',sql],4096).splitlines()==[b'0',b'0'])
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for n in UNITS:manager.LoadUnit(n);manager.RefUnit(n);refs.append(n)
 first=snapshot();require(first==before['current'] and first==snapshot());runtime=runtime_check();require(runtime==runtime_check())
 opts=command(['findmnt','--target','/opt/schubert-nk/releases/0.1.0-PG1292','--noheadings','--output','VFS-OPTIONS'],4096).decode().strip().split(',');require('ro'in opts and 'rw'not in opts)
 done=pathlib.Path('/var/lib/schubert-nk/maintenance/attempts/841b507c-2713-4ffe-8882-68f5fb3f87f5.done')
 require(hashlib.sha256(done.read_bytes()).hexdigest()=='59f3b40104a9ea940779caac6aad6be6873e87f465a626e6f7860833c02d70a2')
finally:
 errors=[]
 for n in reversed(refs):
  try:manager.UnrefUnit(n)
  except Exception as e:errors.append(type(e).__name__)
 try:bus.close()
 except Exception as e:errors.append(type(e).__name__)
 require(not errors)
encoded=json.dumps({'current':first,'runtime':runtime},sort_keys=True).encode()
with(SAVE/'after.private.json').open('xb')as f:f.write(encoded);f.flush();os.fsync(f.fileno())
result={'run':'PG1453-current-cold-independent-post-v1','actualExit':0,'source':SOURCE,'boot':BOOT,'fullCurrentDbOriginalBackupSignatureTwice':True,'tenCold18Full32':True,'twelveRolesEmptyCorrectIdsModesAcl':True,'releaseReadonly':True,'parentBackendAdvisoryFlocksGone':True,'metadataScopesClosedNormally':True,'oldDoneUnchanged':True,'businessWrites':0,'permissionIssued':False,'formalAccepted':False,'prepareAfterSha256':hashlib.sha256(before_raw).hexdigest(),'afterSha256':hashlib.sha256(encoded).hexdigest()}
with(SAVE/'result.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
print(json.dumps(result,sort_keys=True))
'''


def main():
    prior=json.loads((W/'pg1452-current-cold-owned-prepare-v1/manifest.safe.json').read_bytes())
    assert prior['actualExit']==0
    os.umask(0o077);out=W/'pg1453-current-cold-independent-post-v1';out.mkdir(mode=0o700)
    raw=payload().encode()
    with(out/'payload.private.py').open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    with(out/'observer.private.log').open('xb')as f:r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
    safe={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'formalAccepted':False}
    if r.returncode==0:safe['guest']=json.loads((out/'observer.private.log').read_bytes())
    with(out/'manifest.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe,sort_keys=True));return r.returncode


if __name__=='__main__':raise SystemExit(main())
