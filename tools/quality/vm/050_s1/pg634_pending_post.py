"""Independent readonly complete-source postconditions, no start/stop/publication."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
PAYLOAD=r'''
import ast,datetime,dbus,hashlib,json,os,pathlib,re,stat,subprocess,sys,time
os.umask(0o077)
def require(ok):
 if not ok:raise ValueError('independent pending post rejected')
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441')
base=pathlib.Path('/var/lib/pgpt-s1-preservation');root=base/('pg633-pending-'+MODE+'-v2')
raw=(base/'pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes()
require(hashlib.sha256(raw).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
parsed=ast.parse(raw);wanted={'command','metadata','strict','show','tree','configuration_fields','kernel'}
nodes=[n for n in parsed.body if isinstance(n,ast.FunctionDef)and n.name in wanted]
constants=[n for n in parsed.body if isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)and t.id in {'UNITS','FIELDS'}for t in n.targets)]
require(len(nodes)==7 and len(constants)==2)
exec(compile(ast.Module(body=constants+nodes,type_ignores=[]),'<independent readonly metadata>','exec'),globals())
before_raw=strict(root/'before.private.json',0o600,67108864);after_raw=strict(root/'after.private.json',0o600,67108864)
before=json.loads(before_raw);after=json.loads(after_raw)
fields=set('backup bootstrapOldProofs bootstrapTools configuration credentials dependencies native oldProofs originals parentPid1 pid1Stop rows runtime startup units current approval unitFiles caddyPre'.split())
require(set(before)==set(after)==fields and len(after['rows'])==24 and len(after['rows']['schubert.batch_runs'])==494)
complete=strict(root/'complete.private',0o600,4096)
require(complete==('pendingCurrentVerified=true\nmode='+MODE+'\nallNewScopesReturnedNormally=true\nrequestsUnchanged=true\ndatabaseUpdates0=true\nstarts0=true\n').encode())
require(finite(before,after,MODE))
if MODE=='activate':require(before==json.loads(strict(base/'pg633-pending-verify-v2/after.private.json',0o600,67108864)))
approval=pathlib.Path('/etc/schubert-nk/release-approval/current');release=pathlib.Path('/opt/schubert-nk/current')
require(str(release.readlink())==after['current'])
version='PG621'if MODE=='verify'else'PG631'
digest='4a2c35463b37956632b6586dfe18f07320777ea863696b25c1e14e913dd3fa1e'if MODE=='verify'else'57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe'
require(strict(approval,0o400,192)==('NKRELEASEAPPROVAL1\nversion=0.1.0-'+version+'\nmanifest_sha256='+digest+'\n').encode())
manifest=(release/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(manifest).hexdigest()==digest)
data=json.loads(manifest);require(len(data['artifacts'])==187 and data['versions']['schema']=='028')
require(data['source']['commit']==('72fb7440697ee1048a5c0145055dc1cc3c577914'if MODE=='verify'else'36fe7a0b938489d61d17d49c1c30a6fbbef699d5'))
for v in data['artifacts']:
 p=release/v['path'];require(p.stat().st_size==v['size']and hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256'])
command(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(release/'RELEASE-MANIFEST.json'),'-sigfile',str(base/(version.lower()+'-manifest.sig'))],4096)
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for u in UNITS:manager.RefUnit(u);refs.append(u)
 for repeat in range(2):
  require(not pathlib.Path('/proc/1511808').exists())
  fresh_sources=[]
  for u in UNITS:
   require(show(u,FIELDS)==after['units'][u]and show(u,configuration_fields())==after['configuration'][u]);kernel(u)
   require({k:sorted(v.split())for k,v in show(u,{'Requires','Before','After','PartOf','BindsTo'}).items()}==after['dependencies'][u])
   source_fields=show(u,{'FragmentPath','DropInPaths'});require(set(source_fields)=={'FragmentPath','DropInPaths'})
   fresh_sources.append(source_fields['FragmentPath']);fresh_sources.extend(source_fields['DropInPaths'].split())
  approval_before=metadata(approval);approval_raw=strict(approval,0o400,192);require(approval_before==metadata(approval))
  require(fresh_join(after,str(release.readlink()),{'metadata':approval_before,'sha256':hashlib.sha256(approval_raw).hexdigest()},[p.name for p in pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d').iterdir()],fresh_sources))
  require(show('caddy.service',{'ExecStartPre'})['ExecStartPre']==after['caddyPre'])
  pid1=command(['/usr/bin/journalctl','--boot=cc9ed8747f4f450ea1888de1e42c8441','_PID=1','UNIT=schubert-nk-morning-controller.service','INVOCATION_ID=3a2de24f931544c0a2fd83556a659cd0','-o','json','--no-pager'])
  require([json.loads(row)for row in pid1.splitlines()]==after['parentPid1'])
  for u,v in after['pid1Stop'].items():
   p=base/'pg611-native-stop-v1'/(u+'.stopped.private');require(metadata(p)==v['metadata']and hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256'])
  for k,p in {'credentials':'/etc/schubert-nk/credentials','startup':'/run/schubert-nk/startup','originals':'/var/lib/schubert-nk/maintenance','backup':'/srv/schubert-nk/backup','native':'/run/schubert-nk/pt-coverage','oldProofs':str(base/'pg611-native-stop-v1'),'bootstrapOldProofs':str(base/'pg570-bootstrap-existing-v1'),'bootstrapTools':str(base/'pg570-bootstrap-tools-v1')}.items():require(tree(pathlib.Path(p))==after[k])
  for p,v in after['unitFiles'].items():require(metadata(pathlib.Path(p))==v['metadata']and hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()==v['sha256'])
  q="begin isolation level repeatable read read only;set local timezone='UTC';";rows={}
  for t in after['rows']:
   require(re.fullmatch(r'schubert(?:_web_session)?\.[a-z_]+',t)is not None)
   q+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+t+" t)q;"
  q+="select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;commit;"
  lines=command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines();require(len(lines)==26 and lines[-2:]==[b'0',b'0'])
  for line in lines[:-2]:
   v=json.loads(line);require(v['table']not in rows);rows[v['table']]=v['rows']
  require(rows==after['rows'])
  for name in ('maintenance.lock','startup-admission.lock'):
   s=pathlib.Path('/run/schubert-nk',name).lstat()
   for line in pathlib.Path('/proc/locks').read_text().splitlines():
    f=line.split()
    if len(f)>=8 and f[1]=='FLOCK':
     d=f[5].split(':');require((int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))
  require(not os.path.lexists('/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf'))
  for name in ('backup-request','cleanup-request','expiry-request'):require(not list(pathlib.Path('/run/schubert-nk',name).iterdir()))
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
print(json.dumps({'mode':MODE,'beforeSha256':hashlib.sha256(before_raw).hexdigest(),'afterSha256':hashlib.sha256(after_raw).hexdigest(),'completeSha256':hashlib.sha256(complete).hexdigest(),'fields':19,'full24Twice':True,'batchRows':494,'tenUnitsKernel0':True,'whole187Signature':True,'resources0':True,'allNewMetadataNormal':True,'formalAccepted':False,'startsStopsWrites0':True}))
'''


def main():
    os.umask(0o077)
    assert sys.argv[1:]in (['verify'],['activate'])
    mode=sys.argv[1]
    assert subprocess.check_output(['git','status','--porcelain'],cwd=R.parents[3])==b''
    assert (W/('pg633-'+mode+'-v2.exit')).read_bytes()==b'0\n'
    slot=W/('pg634-'+mode+'-post-v1')
    assert not slot.with_suffix('.private.log').exists()and not slot.with_suffix('.safe.json').exists()
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    result=subprocess.run(ssh,input=('MODE='+repr(mode)+'\n'+(R/'pg634_post_contract.py').read_text()+'\n'+PAYLOAD).encode(),capture_output=True,timeout=90)
    with slot.with_suffix('.private.log').open('xb')as f:f.write(result.stderr);f.flush();os.fsync(f.fileno())
    safe={'actualExit':result.returncode,'startedUTC':started,'endedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R.parents[3],text=True).strip(),'privateLogSha256':hashlib.sha256(result.stderr).hexdigest(),'formalAccepted':False}
    if result.returncode==0:safe['proof']=json.loads(result.stdout)
    with slot.with_suffix('.safe.json').open('x')as f:json.dump(safe,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':result.returncode,'mode':mode,'rawExported':False}))
    raise SystemExit(result.returncode)


if __name__=='__main__':main()
