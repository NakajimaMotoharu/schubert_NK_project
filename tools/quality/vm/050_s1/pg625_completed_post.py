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
 if not ok:raise ValueError('independent completed post rejected')
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441')
base=pathlib.Path('/var/lib/pgpt-s1-preservation');root=base/('pg624-completed-'+MODE+'-v1')
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
require(set(before)==set(after)==fields and len(after['rows'])==24 and len(after['rows']['schubert.batch_runs'])==492)
complete=strict(root/'complete.private',0o600,4096)
require(complete==('completedCurrentVerified=true\nmode='+MODE+'\nallNewScopesReturnedNormally=true\nrequestsUnchanged=true\ndatabaseUpdates0=true\nstarts0=true\n').encode())
if MODE=='verify':require(before==after)
else:
 require(before==json.loads(strict(base/'pg624-completed-verify-v1/after.private.json',0o600,67108864)))
 require(all(before[k]==after[k]for k in fields-{'current','startup','approval'}))
 require(before['current']=='/opt/schubert-nk/releases/0.1.0-PG600'and after['current']=='/opt/schubert-nk/releases/0.1.0-PG621')
 old,new=before['startup'],after['startup'];epoch='/run/schubert-nk/startup/epoch.current';directory='/run/schubert-nk/startup'
 require(set(old)==set(new)and all(old[k]==new[k]for k in old.keys()-{epoch,directory}))
 require(old[directory]['metadata'][:7]==new[directory]['metadata'][:7]and old[directory]['sha256']==new[directory]['sha256'])
 require(hashlib.sha256(strict(root/'old-epoch.private',0o600,4096)).hexdigest()==old[epoch]['sha256'])
 epoch_raw=strict(pathlib.Path(epoch),0o600,4096);require(hashlib.sha256(epoch_raw).hexdigest()==new[epoch]['sha256'])
 e=epoch_raw.decode('ascii').splitlines();require(len(e)==8 and e[0]=='NKEPOCH1'and e[1]=='state=INVALID'and e[3].startswith('epoch_id=')and e[7]=='permit_sha256=-')
 require(e[2]=='boot_id=cc9ed874-7f4f-450e-a188-8de1e42c8441'and e[4]=='run_id=3a53b979-fa01-47dd-92a6-7b26affcfb5c'and e[5]=='cutoff_utc=2026-10-08T15:32:46.368375Z'and e[6]=='activation_id=970bbce1-6bba-4db0-ace1-680ee7dfde92')
approval=pathlib.Path('/etc/schubert-nk/release-approval/current');release=pathlib.Path('/opt/schubert-nk/current')
require(str(release.readlink())==after['current'])
version='PG600'if MODE=='verify'else'PG621'
digest='a6342b8a764565cdfea256a781029d419888c7b58c0c3f9b00685e30feaa786f'if MODE=='verify'else'4a2c35463b37956632b6586dfe18f07320777ea863696b25c1e14e913dd3fa1e'
require(strict(approval,0o400,192)==('NKRELEASEAPPROVAL1\nversion=0.1.0-'+version+'\nmanifest_sha256='+digest+'\n').encode())
manifest=(release/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(manifest).hexdigest()==digest)
data=json.loads(manifest);require(len(data['artifacts'])==187 and data['versions']['schema']=='028')
require(data['source']['commit']==('23b14a44b10504172e030bbd6625926bf049fb5c'if MODE=='verify'else'72fb7440697ee1048a5c0145055dc1cc3c577914'))
for v in data['artifacts']:
 p=release/v['path'];require(p.stat().st_size==v['size']and hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256'])
command(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(release/'RELEASE-MANIFEST.json'),'-sigfile',str(base/(version.lower()+'-manifest.sig'))],4096)
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for u in UNITS:manager.RefUnit(u);refs.append(u)
 for repeat in range(2):
  for u in UNITS:
   require(show(u,FIELDS)==after['units'][u]and show(u,configuration_fields())==after['configuration'][u]);kernel(u)
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
print(json.dumps({'mode':MODE,'beforeSha256':hashlib.sha256(before_raw).hexdigest(),'afterSha256':hashlib.sha256(after_raw).hexdigest(),'completeSha256':hashlib.sha256(complete).hexdigest(),'fields':19,'full24Twice':True,'batchRows':492,'tenUnitsKernel0':True,'whole187Signature':True,'resources0':True,'allNewMetadataNormal':True,'formalAccepted':False,'startsStopsWrites0':True}))
'''


def main():
    os.umask(0o077)
    assert sys.argv[1:]in (['verify'],['activate'])
    mode=sys.argv[1]
    assert subprocess.check_output(['git','status','--porcelain'],cwd=R.parents[3])==b''
    assert (W/('pg624-'+mode+'-v1.exit')).read_bytes()==b'0\n'
    slot=W/('pg625-'+mode+'-post-v1')
    assert not slot.with_suffix('.private.log').exists()and not slot.with_suffix('.safe.json').exists()
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    result=subprocess.run(ssh,input=('MODE='+repr(mode)+'\n'+PAYLOAD).encode(),capture_output=True,timeout=90)
    with slot.with_suffix('.private.log').open('xb')as f:f.write(result.stderr);f.flush();os.fsync(f.fileno())
    safe={'actualExit':result.returncode,'startedUTC':started,'endedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R.parents[3],text=True).strip(),'privateLogSha256':hashlib.sha256(result.stderr).hexdigest(),'formalAccepted':False}
    if result.returncode==0:safe['proof']=json.loads(result.stdout)
    with slot.with_suffix('.safe.json').open('x')as f:json.dump(safe,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':result.returncode,'mode':mode,'rawExported':False}))
    raise SystemExit(result.returncode)


if __name__=='__main__':main()
