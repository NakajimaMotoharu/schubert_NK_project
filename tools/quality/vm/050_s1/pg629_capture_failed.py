"""Fresh normal30 pre-permit failure baseline, read-only; no oldclose normalization."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

R=Path('/home/mini/codex/project1/work/pgpt-foundation/tools/quality/vm/050_s1')
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
RECEIPT=Path(__file__).with_name('pg629_failed_receipt.py').read_bytes()
PAYLOAD=r'''
import ast,datetime,dbus,hashlib,json,os,pathlib,re,stat,subprocess,sys,time
os.umask(0o077)
def require(v):
 if not v:raise ValueError('current failed-parent readonly proof rejected')
boot='cc9ed874-7f4f-450e-a188-8de1e42c8441';inv='3a2de24f931544c0a2fd83556a659cd0'
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==boot)
base=pathlib.Path('/var/lib/pgpt-s1-preservation');save=base/'pg629-failed-parent-baseline-v1';require(not os.path.lexists(save))
raw=(base/'pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes();require(hashlib.sha256(raw).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
parsed=ast.parse(raw);wanted={'command','metadata','strict','show','tree','configuration_fields','kernel'}
nodes=[n for n in parsed.body if isinstance(n,ast.FunctionDef)and n.name in wanted]
constants=[n for n in parsed.body if isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)and t.id in {'UNITS','FIELDS'}for t in n.targets)]
require(len(nodes)==7 and len(constants)==2);exec(compile(ast.Module(body=constants+nodes,type_ignores=[]),'<pinned readonly metadata>','exec'),globals())
prior_raw=strict(base/'pg626-fresh-parent-v2/before.private.json',0o600,67108864);require(hashlib.sha256(prior_raw).hexdigest()=='07e81e443f5b78f09ce6e3d5e2f754308b8911c67990fd015fb143130c8704dc');prior=json.loads(prior_raw)
run='e49243d5-de84-4714-8612-6912ddc17e9e';cutoff='2026-10-08T18:32:42.140966Z';act='7d381b67-b37b-48c6-99ac-e04a336f887d'
root=pathlib.Path('/var/lib/schubert-nk/maintenance');anchor=strict(root/'runs'/(run+'.run'),0o600,72);active=strict(root/'active',0o600,109)
require(anchor==('NKRUN1\n'+run+'\n'+cutoff+'\n').encode()and active==('NKACT1\n'+run+'\n'+cutoff+'\n'+act+'\n').encode())
require(active==strict(root/'attempts'/(act+'.begin'),0o600,109)and not os.path.lexists(root/'attempts'/(act+'.done')))
journal=command(['journalctl','--boot='+boot.replace('-',''),'_PID=1','UNIT=schubert-nk-morning-controller.service','INVOCATION_ID='+inv,'-o','json','--no-pager']);pid1=[json.loads(l)for l in journal.splitlines()];require(failed30(pid1)['status']==30)
release=pathlib.Path('/opt/schubert-nk/current');manifest=(release/'RELEASE-MANIFEST.json').read_bytes();require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG621'and hashlib.sha256(manifest).hexdigest()=='4a2c35463b37956632b6586dfe18f07320777ea863696b25c1e14e913dd3fa1e')
data=json.loads(manifest);require(data['source']['commit']=='72fb7440697ee1048a5c0145055dc1cc3c577914'and len(data['artifacts'])==187)
for v in data['artifacts']:
 p=release/v['path'];require(p.stat().st_size==v['size']and hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256'])
command(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(release/'RELEASE-MANIFEST.json'),'-sigfile',str(base/'pg621-manifest.sig')],4096)
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for u in UNITS:manager.RefUnit(u);refs.append(u)
 def snapshot():
  units={u:show(u,FIELDS)for u in UNITS};configuration={u:show(u,configuration_fields())for u in UNITS}
  for u,v in units.items():require(v['MainPID']==v['ControlPID']=='0'and not v['Job']);kernel(u)
  parent=units['schubert-nk-morning-controller.service'];require(parent['InvocationID']==inv and parent['Result']=='exit-code'and parent['ExecMainCode']=='1'and parent['ExecMainStatus']=='30'and parent['ExecMainStartTimestampMonotonic']=='97060184910'and parent['ExecMainExitTimestampMonotonic']=='97094171993')
  require(not pathlib.Path('/proc/1511808').exists())
  q="begin isolation level repeatable read read only;set local timezone='UTC';";rows={}
  for t in prior['rows']:
   require(re.fullmatch(r'schubert(?:_web_session)?\.[a-z_]+',t)is not None)
   q+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+t+" t)q;"
  q+="select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;commit;"
  lines=command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines();require(len(lines)==26 and lines[-2:]==[b'0',b'0'])
  for line in lines[:-2]:
   v=json.loads(line);require(v['table']not in rows);rows[v['table']]=v['rows']
  require(len(rows)==24 and len(rows['schubert.batch_runs'])==494)
  for t in rows.keys()-{'schubert.batch_runs'}:require(rows[t]==prior['rows'][t])
  old={r['id']:r for r in prior['rows']['schubert.batch_runs']};current={r['id']:r for r in rows['schubert.batch_runs']};require(all(current.get(k)==v for k,v in old.items()))
  new=[r for k,r in current.items()if k not in old];require(len(new)==2 and {r['step']for r in new}=={'BACKUP_DB','BACKUP_CONFIG'}and all(r['run_id']==run and r['status']=='SUCCESS'and r['attempt']==2 for r in new))
  values={k:tree(pathlib.Path(p))for k,p in [('startup','/run/schubert-nk/startup'),('originals','/var/lib/schubert-nk/maintenance'),('backup','/srv/schubert-nk/backup')]}
  require(all(values['backup'].get(p)==v for p,v in prior['backup'].items()if p!='/srv/schubert-nk/backup'))
  require(not any('intent' in p for p in values['startup']))
  for name in ('backup-request','cleanup-request','expiry-request'):require(not list(pathlib.Path('/run/schubert-nk',name).iterdir()))
  for name in ('maintenance.lock','startup-admission.lock'):
   s=pathlib.Path('/run/schubert-nk',name).lstat()
   for line in pathlib.Path('/proc/locks').read_text().splitlines():
    f=line.split()
    if len(f)>=8 and f[1]=='FLOCK':
     d=f[5].split(':');require((int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))
  require(not os.path.lexists('/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf'))
  return {'rows':rows,'units':units,'configuration':configuration,**values,'pid1':pid1}
 after=snapshot();require(after==snapshot()and strict(root/'active',0o600,109)==active)
 save.mkdir(mode=0o700)
 with(save/'after.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(after,f,sort_keys=True);f.flush();os.fsync(f.fileno())
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
safe={'run':'PG629-failed-parent-baseline-v1','actualExit':0,'source':'72fb7440697ee1048a5c0145055dc1cc3c577914','parentFailed30':True,'parentElapsedSeconds':failed30(pid1)['elapsedSeconds'],'noLaterWorkExecuted':True,'full24Twice':True,'batchRows':494,'prior492RowsPreserved':True,'oldBackupAllUnchanged':True,'newBackupBothSuccess':True,'allTenUnitsKernelEmpty':True,'resources0':True,'newMetadataScopesNormal':True,'oldScopesNormalized':False,'afterSha256':hashlib.sha256((save/'after.private.json').read_bytes()).hexdigest(),'afterBytes':(save/'after.private.json').stat().st_size,'sourceSignature187':True,'operationAuthority':False,'formalAccepted':False}
with(save/'result.safe.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
for p in (save,save.parent):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print(json.dumps(safe))
'''


def main():
    os.umask(0o077)
    assert subprocess.check_output(['git','status','--porcelain'],cwd=R.parents[3])==b''
    log=W/'pg629-failed-parent-baseline-v1.private.log';target=W/'pg629-failed-parent-baseline-v1.safe.json'
    assert not log.exists()and not target.exists()
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    payload=RECEIPT+b'\n'+PAYLOAD.encode()
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();result=subprocess.run(ssh,input=payload,capture_output=True,timeout=90)
    with log.open('xb')as f:f.write(result.stderr);f.flush();os.fsync(f.fileno())
    safe={'actualExit':result.returncode,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R.parents[3],text=True).strip(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'privateLogSha256':hashlib.sha256(result.stderr).hexdigest(),'helperSha256':hashlib.sha256(RECEIPT).hexdigest(),'payloadSha256':hashlib.sha256(payload).hexdigest(),'formalAccepted':False}
    if result.returncode==0:safe['proof']=json.loads(result.stdout)
    with target.open('x')as f:json.dump(safe,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':result.returncode,'readOnly':True,'oldScopesNormalized':False}))
    raise SystemExit(result.returncode)


if __name__=='__main__':main()
