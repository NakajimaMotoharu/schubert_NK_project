"""SSC202 one reserved ordinary same-run start after normal runtime preparation."""
import datetime,hashlib,json,os,pathlib,subprocess
os.umask(0o077)
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
SOURCE='a2e98ce9e96c42425921e3686e8ae7a94bff9e6c';DIGEST='f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44'
assert (W/'pg495-six-full-v1.source').read_text().strip()==SOURCE and (W/'pg495-six-full-v1.exit').read_text().strip()=='0'
assert (W/'pg504-resume-native-v1.exit').read_text().strip()=='0'
assert (W/'pg505-parent-observer-v1.started').exists() and not (W/'pg505-parent-observer-v1.exit').exists()
assert (W/'pg505-parent-watch-private-v1.jsonl').stat().st_size>0
assert not (W/'pg505-external-resume-v1.private.log').exists()
SSH=['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1']
PAYLOAD=r'''import ast,datetime,hashlib,json,os,pathlib,shutil,stat,subprocess
assert os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
prep=pathlib.Path('/var/lib/pgpt-s1-preservation/pg504-resume-preparation-v1')
assert hashlib.sha256((prep/'complete.private').read_bytes()).hexdigest()=='ac7a0eb9af359638ed84bab5951afe69cfc2636e2b460233f82029560aa762ad'
raw=(prep/'refs-after.private.json').read_bytes();assert hashlib.sha256(raw).hexdigest()=='67fa28ad6f289589994af0be7022a20fe12b673685d0c151ffb791dd91fec52e';before=json.loads(raw)
current=pathlib.Path('/opt/schubert-nk/current');assert str(current.readlink())==before['current']=='/opt/schubert-nk/releases/0.1.0-PG495'
manifest=(current/'RELEASE-MANIFEST.json').read_bytes();assert hashlib.sha256(manifest).hexdigest()==DIGEST and json.loads(manifest)['source']['commit']==SOURCE
raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg480-backup-tools-v3/pg480_backup_refs.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='0dd9ded789de2205ecb7f60080f3f57c2d489e28c0436d4a309a4dab386d0eb7'
names={'require','command','metadata','tree','show','kernel'};defs=[n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef) and n.name in names];assert len(defs)==len(names)
exec(compile(ast.Module(body=defs,type_ignores=[]),'<immutable readonly prestart>','exec'),globals());UNITS=list(before['units']);assert len(UNITS)==10
def unchanged():
 for unit in UNITS:
  assert show(unit,set(before['units'][unit]))==before['units'][unit];kernel(unit)
  assert show(unit,set(before['configuration'][unit]))==before['configuration'][unit]
 for root,values in before['trees'].items():assert tree(pathlib.Path(root))==values
 q="begin isolation level repeatable read read only;set local timezone='UTC';";rows={}
 for table in before['rows']:q+="select json_build_object('table','"+table+"','rows',coalesce(jsonb_agg(j order by j::text),'[]'::jsonb)) from (select to_jsonb(t) j from "+table+" t) q;"
 q+='commit;'
 for line in command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-v','ON_ERROR_STOP=1','-d','schubert_nk','-c',q]).splitlines():
  v=json.loads(line);assert v['table'] not in rows;rows[v['table']]=v['rows']
 assert rows==before['rows']
 assert command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-d','schubert_nk','-c',"select count(*) from pg_stat_activity where datname='schubert_nk' and usename in ('schubert_batch','schubert_app','schubert_web_session','schubert_inbox_inspector','schubert_backup'); select count(*) from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and granted;"],4096).splitlines()==[b'0',b'0']
 for line in pathlib.Path('/proc/locks').read_text().splitlines():
  parts=line.split()
  if len(parts)>=8 and parts[1]=='FLOCK':
   dev=parts[5].split(':')
   for name in ['maintenance.lock','startup-admission.lock']:
    item=pathlib.Path('/run/schubert-nk',name).lstat();assert (int(dev[0],16),int(dev[1],16),int(dev[2]))!=(os.major(item.st_dev),os.minor(item.st_dev),item.st_ino)
 for name in ['backup-request','cleanup-request','expiry-request']:assert not list(pathlib.Path('/run/schubert-nk',name).iterdir())
 runtime=pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d');assert {p.name for p in runtime.iterdir()}=={'pg492-once-resume.conf'}
 s=(runtime/'pg492-once-resume.conf').lstat();assert stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o644 and s.st_nlink==1 and 'system.posix_acl_access' not in os.listxattr(runtime/'pg492-once-resume.conf')
 conf=(runtime/'pg492-once-resume.conf').read_bytes();assert conf.count(b' --resume ')==1 and conf.endswith(b' --resume 91a748b4-1abe-484c-9682-44f46429b324\n')
unchanged();save=pathlib.Path('/var/lib/pgpt-s1-preservation/pg505-external-resume');assert not save.exists();save.mkdir(mode=0o700)
shutil.copytree('/run/schubert-nk/pt-coverage',save/'native-before',symlinks=False)
for p in (save/'native-before').rglob('*'):
 assert not p.is_symlink()
 if p.is_file():
  os.chmod(p,0o600)
  with p.open('rb') as f:os.fsync(f.fileno())
 elif p.is_dir():os.chmod(p,0o700)
 else:raise AssertionError('unknown native artifact')
os.chmod(save/'native-before',0o700)
def persist(name,data):
 fd=os.open(save/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
 with os.fdopen(fd,'w') as f:json.dump(data,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
activation=pathlib.Path('/var/lib/schubert-nk/maintenance/active').read_bytes().decode('ascii').splitlines();assert len(activation)==4 and activation[0]=='NKACT1' and activation[1]=='91a748b4-1abe-484c-9682-44f46429b324'
unchanged();persist('external-start-guard.private.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':SOURCE,'manifestSha256':DIGEST,'run':'91a748b4-1abe-484c-9682-44f46429b324','cutoff':activation[2],'originalBudgetSeconds':1800,'attemptReserved':True,'repeatForbidden':True})
r=subprocess.run(['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=15)
raw=subprocess.check_output(['/usr/bin/systemctl','show','schubert-nk-morning-controller.service','--property=InvocationID,MainPID,Job,ExecMainStartTimestampMonotonic'],text=True,timeout=5)
d=dict(line.split('=',1) for line in raw.splitlines());d.update(clientExit=r.returncode,at=datetime.datetime.now(datetime.timezone.utc).isoformat(),clientSuccessIsNotParentSuccess=True)
persist('external-start-issued.private.json',d);print(json.dumps(d));raise SystemExit(r.returncode)
'''
r=subprocess.run(SSH+['sudo -n python3 -B -'],input=('SOURCE='+repr(SOURCE)+'\nDIGEST='+repr(DIGEST)+'\n'+PAYLOAD).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with (W/'pg505-external-resume-v1.private.log').open('xb') as f:f.write(r.stdout);f.write(r.stderr)
print(r.stdout.decode(),end='')
if r.returncode:print('PG505_RESUME_REFUSED actual='+str(r.returncode)+' priorGuardRequiresReattachment=true privateDiagnostics=true')
raise SystemExit(r.returncode)
