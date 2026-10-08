"""Fresh finite admission and durable one-use start, prepared same e492 original only."""
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
SOURCE='36fe7a0b938489d61d17d49c1c30a6fbbef699d5'
DIGEST='57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe'
PAYLOAD=r'''
import ast,datetime,dbus,hashlib,json,os,pathlib,re,shutil,stat,subprocess,sys,time
os.umask(0o077)
def require(v):
 if not v:raise ValueError('fresh prepared resume admission rejected')
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441')
base=pathlib.Path('/var/lib/pgpt-s1-preservation');root=base/'pg637-fresh-resume-v2'
raw=(base/'pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes();require(hashlib.sha256(raw).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
parsed=ast.parse(raw);wanted={'command','metadata','strict','show','tree','configuration_fields','kernel'}
nodes=[n for n in parsed.body if isinstance(n,ast.FunctionDef)and n.name in wanted]
constants=[n for n in parsed.body if isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)and t.id in {'UNITS','FIELDS'}for t in n.targets)]
require(len(nodes)==7 and len(constants)==2);exec(compile(ast.Module(body=constants+nodes,type_ignores=[]),'<pinned readonly capture>','exec'),globals())
sealed=strict(base/'pg635-resume-preparation-v1/after.private.json',0o600,67108864);require(hashlib.sha256(sealed).hexdigest()=='c946eaae7147aff0fb328bfabda0d779133f7c04cc30a9a0427d58ae7da76d2e');expected=json.loads(sealed)
require(len(expected)==19 and len(expected['rows'])==24 and len(expected['rows']['schubert.batch_runs'])==494)
require(strict(base/'pg635-resume-preparation-v1/complete.private',0o600,4096)==b'onceResumePrepared=true\nallNewScopesReturnedNormally=true\noriginalRunCutoffUnchanged=true\ndatabaseUpdates0=true\nstarts0=true\n')
def capture():
 require(not pathlib.Path('/proc/1511808').exists())
 release=pathlib.Path('/opt/schubert-nk/current');require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG631'and hashlib.sha256((release/'RELEASE-MANIFEST.json').read_bytes()).hexdigest()==DIGEST)
 for u in UNITS:
  require(show(u,FIELDS)==expected['units'][u]and show(u,configuration_fields())==expected['configuration'][u]);kernel(u)
  require({k:sorted(v.split())for k,v in show(u,{'Requires','Before','After','PartOf','BindsTo'}).items()}==expected['dependencies'][u])
 require(show('caddy.service',{'ExecStartPre'})['ExecStartPre']==expected['caddyPre'])
 journal=command(['/usr/bin/journalctl','--boot=cc9ed8747f4f450ea1888de1e42c8441','_PID=1','UNIT=schubert-nk-morning-controller.service','INVOCATION_ID=3a2de24f931544c0a2fd83556a659cd0','-o','json','--no-pager'])
 require([json.loads(row)for row in journal.splitlines()]==expected['parentPid1'])
 for k,p in {'credentials':'/etc/schubert-nk/credentials','startup':'/run/schubert-nk/startup','originals':'/var/lib/schubert-nk/maintenance','backup':'/srv/schubert-nk/backup','native':'/run/schubert-nk/pt-coverage','oldProofs':str(base/'pg611-native-stop-v1'),'bootstrapOldProofs':str(base/'pg570-bootstrap-existing-v1'),'bootstrapTools':str(base/'pg570-bootstrap-tools-v1')}.items():require(tree(pathlib.Path(p))==expected[k])
 for p,v in expected['unitFiles'].items():require(metadata(pathlib.Path(p))==v['metadata']and hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()==v['sha256'])
 approval=pathlib.Path('/etc/schubert-nk/release-approval/current');require(metadata(approval)==expected['approval']['metadata']and hashlib.sha256(strict(approval,0o400,192)).hexdigest()==expected['approval']['sha256'])
 runtime=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d');require({p.name for p in runtime.iterdir()}=={'pg635-once-resume.conf'})
 require(strict(pathlib.Path('/var/lib/schubert-nk/maintenance/active'),0o600,109)==b'NKACT1\ne49243d5-de84-4714-8612-6912ddc17e9e\n2026-10-08T18:32:42.140966Z\n7d381b67-b37b-48c6-99ac-e04a336f887d\n')
 q="begin isolation level repeatable read read only;set local timezone='UTC';";rows={}
 for t in expected['rows']:
  require(re.fullmatch(r'schubert(?:_web_session)?\.[a-z_]+',t)is not None)
  q+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+t+" t)q;"
 q+="select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;commit;"
 lines=command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines();require(len(lines)==26 and lines[-2:]==[b'0',b'0'])
 for line in lines[:-2]:
  v=json.loads(line);require(v['table']not in rows);rows[v['table']]=v['rows']
 require(rows==expected['rows'])
 for name in ('maintenance.lock','startup-admission.lock'):
  s=pathlib.Path('/run/schubert-nk',name).lstat()
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)>=8 and f[1]=='FLOCK':
    d=f[5].split(':');require((int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))
 for name in ('backup-request','cleanup-request','expiry-request'):require(not list(pathlib.Path('/run/schubert-nk',name).iterdir()))
 return expected
def persist(name,value):
 with(root/name).open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 for p in (root,root.parent):
  fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for unit in UNITS:manager.RefUnit(unit);refs.append(unit)
 if MODE=='prepare':
  require(not os.path.lexists(root));before=capture();require(before==capture());root.mkdir(mode=0o700);persist('before.private.json',before)
  native=root/'native-before';shutil.copytree('/run/schubert-nk/pt-coverage',native,symlinks=False)
  for p in (native,*native.rglob('*')):
   require(not p.is_symlink());os.chmod(p,0o700 if p.is_dir()else 0o600)
   fd=os.open(p,os.O_RDONLY|(os.O_DIRECTORY if p.is_dir()else 0));os.fsync(fd);os.close(fd)
  now=datetime.datetime.now(datetime.timezone.utc);persist('admission.private.json',{'lower':now.isoformat(),'upper':(now+datetime.timedelta(minutes=2)).isoformat(),'source':SOURCE,'starts0':True})
  print(json.dumps({'prepared':True,'starts0':True,'source':SOURCE,'sameOriginalRun':True,'sameCutoffActivation':True,'originalBudgetSeconds':1800}))
 else:
  require(MODE=='start'and root.is_dir()and not os.path.lexists(root/'external-start-guard.private.json'))
  capture();require(json.loads(strict(root/'before.private.json',0o600,67108864))==expected)
  admitted=json.loads(strict(root/'admission.private.json',0o600,4096));now=datetime.datetime.now(datetime.timezone.utc)
  require(datetime.datetime.fromisoformat(admitted['lower'])<=now<=datetime.datetime.fromisoformat(admitted['upper'])and admitted['source']==SOURCE)
  persist('external-start-guard.private.json',{'at':now.isoformat(),'source':SOURCE,'run':'e49243d5-de84-4714-8612-6912ddc17e9e','originalBudgetSeconds':1800,'attemptReserved':True,'repeatForbidden':True})
  r=subprocess.run(['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service'],capture_output=True,timeout=15)
  d=show('schubert-nk-morning-controller.service',{'InvocationID','MainPID','Job','ExecMainStartTimestampMonotonic'});d.update(clientExit=r.returncode,clientSuccessIsNotParentSuccess=True)
  persist('external-start-issued.private.json',d);print(json.dumps(d));raise SystemExit(r.returncode)
finally:
 for unit in reversed(refs):manager.UnrefUnit(unit)
 bus.close()

'''


def main():
    os.umask(0o077)
    assert sys.argv[1:]in (['prepare'],['start']);mode=sys.argv[1]
    assert subprocess.check_output(['git','status','--porcelain'],cwd=R.parents[3])==b''
    proof=json.loads((W/'pg636-prepare-post-v1.safe.json').read_bytes());assert proof['actualExit']==0
    if mode=='start':
        assert (W/'pg637-prepare-v2.exit').read_bytes()==b'0\n'
        assert (W/'pg638-observer-v1.started').exists()and not(W/'pg638-observer-v1.exit').exists()
        with(W/'pg638-watch-private-v1.jsonl').open()as f:first=json.loads(f.readline())
        assert first=={'observerPrepared':True,'source':SOURCE,'manifestSha256':DIGEST,'starts0':True}
    base=W/('pg637-'+mode+'-v2');assert not any(Path(str(base)+'.'+v).exists()for v in ('private.log','exit','safe.json'))
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();payload='MODE='+repr(mode)+'\nSOURCE='+repr(SOURCE)+'\nDIGEST='+repr(DIGEST)+'\n'+PAYLOAD
    result=subprocess.run(ssh,input=payload.encode(),capture_output=True,timeout=90)
    with Path(str(base)+'.private.log').open('xb')as f:f.write(result.stderr);f.flush();os.fsync(f.fileno())
    with Path(str(base)+'.exit').open('x')as f:f.write(str(result.returncode)+'\n')
    if result.returncode==0:
        d=json.loads(result.stdout);d.update(actualExit=0,operatorSource=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R.parents[3],text=True).strip(),startedUTC=started,endedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
        with Path(str(base)+'.safe.json').open('x')as f:json.dump(d,f,sort_keys=True)
    print(json.dumps({'actualExit':result.returncode,'mode':mode,'clientSuccessIsNotParentSuccess':True}));raise SystemExit(result.returncode)


if __name__=='__main__':main()
