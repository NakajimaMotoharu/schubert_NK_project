"""Current completed+owned-stopped readonly nineteen-field capture. No operation authority."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

R = Path(__file__).resolve().parent
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P = Path('/home/mini/codex/project1/work/pgpt-vm/private')
PAYLOAD = r'''
import ast,datetime,dbus,hashlib,json,os,pathlib,re,stat,subprocess
os.umask(0o077)
def require(v):
 if not v:raise ValueError('current completed readonly nineteen-field capture rejected')
require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441')
base=pathlib.Path('/var/lib/pgpt-s1-preservation');root=base/'pg646-completed-baseline-v1';require(not os.path.lexists(root))
raw=(base/'pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes();require(hashlib.sha256(raw).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7')
parsed=ast.parse(raw);wanted={'command','metadata','strict','show','tree','configuration_fields','kernel'}
defs=[n for n in parsed.body if isinstance(n,ast.FunctionDef)and n.name in wanted]
constants=[n for n in parsed.body if isinstance(n,ast.Assign)and all(isinstance(t,ast.Name)and t.id in {'UNITS','FIELDS'}for t in n.targets)]
require(len(defs)==7 and len(constants)==2);exec(compile(ast.Module(body=constants+defs,type_ignores=[]),'<pinned readonly functions>','exec'),globals())
sealed=strict(base/'pg642-native-stop-v1/after.private.json',0o600,67108864);require(hashlib.sha256(sealed).hexdigest()=='011d96090bac12c58f0a9531455e72bb79a23a413d5b16fa886c9df8dac4bf3c');old=json.loads(sealed)
require(strict(base/'pg642-native-stop-v1/complete.private',0o600,4096)==b'genuineParentDone=true\nallEightOwnedTerminal=true\nallNewScopesReturnedNormally=true\noriginalBackupStartupRowsPreserved=true\nstarts0=true\noldUnknownNormalized=false\n')
def file(p):
 before=metadata(p);raw=p.read_bytes();require(before==metadata(p));return{'metadata':before,'sha256':hashlib.sha256(raw).hexdigest()}
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]
try:
 for u in UNITS:manager.RefUnit(u);refs.append(u)
 def capture():
  release=pathlib.Path('/opt/schubert-nk/current');require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG631'and hashlib.sha256((release/'RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe')
  v={}
  for k,p in {'credentials':'/etc/schubert-nk/credentials','startup':'/run/schubert-nk/startup','originals':'/var/lib/schubert-nk/maintenance','backup':'/srv/schubert-nk/backup','native':'/run/schubert-nk/pt-coverage','oldProofs':str(base/'pg611-native-stop-v1'),'bootstrapOldProofs':str(base/'pg570-bootstrap-existing-v1'),'bootstrapTools':str(base/'pg570-bootstrap-tools-v1')}.items():v[k]=tree(pathlib.Path(p))
  for k in ('startup','originals','backup'):require(v[k]==old[k])
  v['units']={u:show(u,FIELDS)for u in UNITS};v['configuration']={u:show(u,configuration_fields())for u in UNITS}
  require(v['units']==old['units']and v['configuration']==old['configuration'])
  for u,s in v['units'].items():require(s['MainPID']==s['ControlPID']=='0'and not s['Job']);kernel(u)
  v['dependencies']={u:{k:sorted(x.split())for k,x in show(u,{'Requires','Before','After','PartOf','BindsTo'}).items()}for u in UNITS}
  journal=command(['journalctl','--boot=cc9ed8747f4f450ea1888de1e42c8441','_PID=1','UNIT=schubert-nk-morning-controller.service','INVOCATION_ID=293d218b06454bd1a8ff350bb93de2d5','-o','json','--no-pager'])
  v['parentPid1']=[json.loads(line)for line in journal.splitlines()];require(v['parentPid1']==old['pid1'])
  stopped=('caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service')
  v['pid1Stop']={u:file(base/'pg642-native-stop-v1'/(u+'.stopped.private'))for u in stopped}
  q="begin isolation level repeatable read read only;set local timezone='UTC';";rows={}
  for t in old['rows']:
   require(re.fullmatch(r'schubert(?:_web_session)?\.[a-z_]+',t)is not None)
   q+="select json_build_object('table','"+t+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb))from(select to_jsonb(t)j from "+t+" t)q;"
  q+="select count(*)from pg_stat_activity where datname='schubert_nk'and backend_type='client backend'and pid<>pg_backend_pid();select count(*)from pg_locks where locktype='advisory'and classid=0 and objid=71419602 and objsubid=1 and granted;commit;"
  lines=command(['sudo','-n','-u','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines();require(len(lines)==26 and lines[-2:]==[b'0',b'0'])
  for line in lines[:-2]:
   item=json.loads(line);require(item['table']not in rows);rows[item['table']]=item['rows']
  require(rows==old['rows']and len(rows['schubert.batch_runs'])==504);v['rows']=rows
  runtime=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d');require({p.name for p in runtime.iterdir()}=={'pg635-once-resume.conf'})
  v['runtime']=file(runtime/'pg635-once-resume.conf');v['current']=str(release.readlink());v['approval']=file(pathlib.Path('/etc/schubert-nk/release-approval/current'))
  paths=[]
  for u in UNITS:
   fields=show(u,{'FragmentPath','DropInPaths'});paths.append(fields['FragmentPath']);paths.extend(fields['DropInPaths'].split())
  require(len(set(paths))==19 and all(pathlib.Path(p).is_absolute()for p in paths));v['unitFiles']={p:file(pathlib.Path(p))for p in sorted(set(paths))}
  require(v['unitFiles'][str(runtime/'pg635-once-resume.conf')]==v['runtime']);v['caddyPre']=show('caddy.service',{'ExecStartPre'})['ExecStartPre']
  for name in('backup-request','cleanup-request','expiry-request'):require(not list(pathlib.Path('/run/schubert-nk',name).iterdir()))
  for name in('maintenance.lock','startup-admission.lock'):
   s=pathlib.Path('/run/schubert-nk',name).lstat()
   for line in pathlib.Path('/proc/locks').read_text().splitlines():
    f=line.split()
    if len(f)>=8 and f[1]=='FLOCK':
     d=f[5].split(':');require((int(d[0],16),int(d[1],16),int(d[2]))!=(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino))
  require(len(v)==19);return v
 before=capture();require(before==capture());root.mkdir(mode=0o700)
 with(root/'before.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(before,f,sort_keys=True);f.flush();os.fsync(f.fileno())
finally:
 for u in reversed(refs):manager.UnrefUnit(u)
 bus.close()
for d in(root,root.parent):
 fd=os.open(d,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'full19Fields':True,'all24UnchangedTwice':True,'batchRows':504,'all10KernelAndResources0':True,'newMetadataScopesNormal':True,'operationAuthority':False,'source':'36fe7a0b938489d61d17d49c1c30a6fbbef699d5','beforeSha256':hashlib.sha256((root/'before.private.json').read_bytes()).hexdigest(),'runtimeFiles':1}))
'''


def main():
    os.umask(0o077)
    assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=R.parents[3]) == b''
    assert (W/'pg643-terminal-final-v2.exit').read_bytes() == b'0\n'
    ssh = ['ssh', '-i', str(P/'vm-access'), '-oBatchMode=yes', '-oIdentitiesOnly=yes',
           '-oStrictHostKeyChecking=yes', '-oUserKnownHostsFile='+str(P/'known_hosts'),
           '-p', '22222', 'ubuntu@127.0.0.1', 'sudo -n python3 -B -']
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = subprocess.run(ssh, input=PAYLOAD.encode(), capture_output=True, timeout=90)
    with (W/'pg646-completed-baseline-v1.private.log').open('xb') as f:
        f.write(result.stderr); f.flush(); os.fsync(f.fileno())
    with (W/'pg646-completed-baseline-v1.exit').open('x') as f: f.write(str(result.returncode)+'\n')
    if result.returncode == 0:
        safe = json.loads(result.stdout); safe.update(startedUTC=started, endedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),operatorSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
        with (W/'pg646-completed-baseline-v1.safe.json').open('x') as f: json.dump(safe, f, sort_keys=True)
        print(json.dumps(safe))
    else: print(json.dumps({'actualExit': result.returncode, 'privateLogSha256': hashlib.sha256(result.stderr).hexdigest()}))
    raise SystemExit(result.returncode)


if __name__ == '__main__': main()
