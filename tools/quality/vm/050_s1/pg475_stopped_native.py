"""SSC190191/PG-D379: authenticate stopped receipt; archive old exec only under actual enclosing M/A owner. No start/stop/permit/DDL/namespace repair."""
import os,pathlib,subprocess,json,hashlib,stat,sys
os.umask(0o077)
assert len(sys.argv)==2 and sys.argv[1] in ['verify','archive','after']
action=sys.argv[1]
assert os.geteuid()==0
boot=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()
assert boot=='e07aa706-1acd-4e65-b309-d7f330f79d54'
release=pathlib.Path('/opt/schubert-nk/releases/0.1.0-'+('PG475' if action=='after' else 'PG474'))
assert pathlib.Path('/opt/schubert-nk/current').readlink()==release
raw=(release/'RELEASE-MANIFEST.json').read_bytes()
assert hashlib.sha256(raw).hexdigest()==('9183662292299cc86412c31a551bf140c8b32ccd9b2d6dcdd414b14e4bcd4806' if action=='after' else '3f6b837c12282baca8b2c5fc79c85916421b6940471cca5d544381072120af18')
assert json.loads(raw)['source']['commit']==('979c5ac3e9c28ae76363adacdf9f0736f5a59df1' if action=='after' else '09b448644cfe70c87df9c89aa5c0c1bf6efdeeea')
for name,expected in [('complete.private','allNewScopesReturnedNormally=true\noldUnknownNormalized=false\n')]:
 p=pathlib.Path('/var/lib/pgpt-s1-preservation/pg474-native-stop-v1')/name
 s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_uid==0 and stat.S_IMODE(s.st_mode)==0o600
 assert p.read_text()==expected
import sys
sys.path.insert(0,'/var/lib/pgpt-s1-preservation/pg474-native-tools-v1')
from pg474_native_owned_stop import show,kernel_empty,ORDER,tick,require
def holder():
 pid=os.getppid();p=pathlib.Path('/proc')/str(pid);argv=(p/'cmdline').read_bytes().split(b'\0')
 require(argv[-3:] in ([b'Pg475StoppedDeployment',b'verify',b''],[b'Pg475StoppedDeployment',b'activate',b'']) and argv[0]==b'/opt/jdk-25.0.4/bin/java')
 fds=[]
 for fd in (p/'fd').iterdir():
  try:fds.append(str(fd.readlink()))
  except FileNotFoundError:continue
 for name in ('maintenance.lock','startup-admission.lock'):
  target=pathlib.Path('/run/schubert-nk')/name;st=target.stat()
  require(st.st_uid==st.st_gid==0 and stat.S_IMODE(st.st_mode)==0o600 and st.st_nlink==1 and str(target) in fds)
  matches=[]
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)>=8 and f[1:5]==['FLOCK','ADVISORY','WRITE',str(pid)]:
    dev=f[5].split(':')
    if len(dev)==3 and (int(dev[0],16),int(dev[1],16),int(dev[2]))==(os.major(st.st_dev),os.minor(st.st_dev),st.st_ino):matches.append(line)
  require(len(matches)==1)
 return (pid,tick(pid))

owner=holder()
if action in ['archive','after']:assert (pathlib.Path('/proc')/str(owner[0])/'cmdline').read_bytes().split(b'\0')[-2]==b'activate'
from pg471_native_term_witness import witness
from pg466_term_witness import unique
def current(unit):
 if unit in ORDER:return show(unit)
 assert unit=='schubert-nk-morning-controller.service'
 from pg466_term_witness import FIELDS
 raw=subprocess.check_output(['systemctl','show',unit,'--property='+','.join(sorted(FIELDS))])
 assert len(raw.decode('ascii').splitlines())==len(FIELDS)
 result=dict(line.split('=',1) for line in raw.decode('ascii').splitlines())
 assert set(result)==FIELDS and result['Id']==unit and result['LoadState']=='loaded'
 return result
units=['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service','schubert-nk-morning-controller.service']
assert units[:-1]==ORDER
saved=pathlib.Path('/var/lib/pgpt-s1-preservation/pg474-native-stop-v1')
def material(p):
 s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_uid==0 and stat.S_IMODE(s.st_mode)==0o600
 return p.read_bytes()
prior=json.loads(material(saved/'stops-before.private'),object_pairs_hook=unique)
states=[]
for unit in units:
 state=current(unit)
 assert state['Id']==unit and state['LoadState']=='loaded' and state['MainPID']==state['ControlPID']=='0' and state['Job']==''
 if unit in ORDER:
  receipt=json.loads(material(saved/(unit+'.stopped.private')),object_pairs_hook=unique)
  assert state==receipt
  if unit in ('schubert-nk-api.service','schubert-nk-web.service'):
   result=witness('API' if 'api' in unit else 'WEB',prior[unit],state,material(saved/(unit+'.full-journal.private.jsonl')),prior[unit]['MainPID'],'999' if 'api' in unit else '997')
   assert result['ordinaryStopData'] and result['nativeCaptureComplete'] and result['unitSuccess'] is False
 else:
  assert state['ActiveState']=='inactive' and state['SubState']=='dead' and state['Result']=='success'
 kernel_empty(unit)
 assert state==current(unit)
 assert state['KillMode']=='control-group' and state['SendSIGKILL']=='no'
 group=pathlib.Path('/sys/fs/cgroup/system.slice')/unit
 if group.exists():
  assert all(not p.read_text().strip() for p in group.rglob('cgroup.procs'))
 states.append(state)
namespace=pathlib.Path('/run/schubert-nk/startup')
names={p.name for p in namespace.iterdir()};assert len(names)==61 and 'epoch.current' in names and not any('intent' in name for name in names)
coverage=pathlib.Path('/run/schubert-nk/pt-coverage')
roles=['parent','backup','cleanup','expiry','root-api193','root-web193','ordinary-api193','ordinary-web193']
streams=[]
current_names=['parent.exec','backup.exec','cleanup.exec','expiry.exec','354cbffa0db149ae88dd59c02a98f157.before-exec.exec','9cfb59cef62d4a0498a3702172803ca2.before-exec.exec','354cbffa0db149ae88dd59c02a98f157.terminal.exec','9cfb59cef62d4a0498a3702172803ca2.terminal.exec']
for role,name in zip(roles,current_names):
 d=coverage/role;p=d/name;s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600 and s.st_size>0
 streams.append({'role':role,'bytes':s.st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'uid':s.st_uid,'gid':s.st_gid})

all_files=list(coverage.rglob('*.exec'));assert len(all_files)==21
expected_files={coverage/r/n for r,n in zip(roles,current_names)} | {coverage/'root-api'/'root-api.exec'}
for inv_api,inv_web in [('8d6e47b48a58468aaac34643bbeddb16','a0e695e907204a7eaf84ae16013493ad'),('f7560ea108ae4e7aaca9246602194143','fc1cec99569542298175864fcc8b6daf'),('e93ae37bc6b54a24abd2c62e0e8c431e','4504c595204d47f4a110059e71c13c63')]:
 expected_files |= {coverage/'root-api193'/(inv_api+'.before-exec.exec'),coverage/'root-web193'/(inv_web+'.before-exec.exec'),coverage/'ordinary-api193'/(inv_api+'.terminal.exec'),coverage/'ordinary-web193'/(inv_web+'.terminal.exec')}
assert set(all_files)==expected_files
legacy=json.loads(material(pathlib.Path('/var/lib/pgpt-s1-preservation/pg471-completed-deploy/native-before.private.json')))['oldExec']
empty=[entry for entry in legacy if entry['bytes']==0];assert len(empty)==1
legacy_file=pathlib.Path(empty[0]['origin']);ls=legacy_file.lstat()
assert legacy_file in all_files and stat.S_ISREG(ls.st_mode) and ls.st_size==0
assert [ls.st_dev,ls.st_ino,ls.st_uid,ls.st_gid,stat.S_IMODE(ls.st_mode),ls.st_nlink]==empty[0]['originIdentity']
assert hashlib.sha256(legacy_file.read_bytes()).hexdigest()==empty[0]['sha256']
def metadata(p):
 st=p.lstat();assert stat.S_ISREG(st.st_mode) and st.st_nlink==1 and not p.is_symlink()
 return {'origin':str(p),'identity':[st.st_dev,st.st_ino,st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode),st.st_nlink],'bytes':st.st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
heaps=[coverage/'parent'/'pg463-private-diagnostic'/'parent.private.hprof',coverage/'parent'/'diagnostic-private'/'parent-private.hprof']
assert set(coverage.rglob('*.hprof'))==set(heaps)
for heap in heaps:
 hs=heap.lstat();assert stat.S_ISREG(hs.st_mode) and hs.st_nlink==1 and hs.st_uid==hs.st_gid==0 and stat.S_IMODE(hs.st_mode)==0o600 and hs.st_size>0
all_material=all_files+heaps
assert len(all_material)==23 and {p for p in coverage.rglob('*') if p.is_file()}==set(all_material)
before={str(p):metadata(p) for p in all_material}
archive=pathlib.Path('/var/lib/pgpt-s1-preservation/pg475-stopped-deploy')
def save(name,raw):
 st=archive.lstat();assert stat.S_ISDIR(st.st_mode) and st.st_uid==st.st_gid==0 and stat.S_IMODE(st.st_mode)==0o700
 fd=os.open(archive/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
 with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
 fd=os.open(archive,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
if action=='archive':
 copies=[]
 for index,p in enumerate(sorted(all_material)):
  assert holder()==owner and metadata(p)==before[str(p)]
  raw=p.read_bytes();dest='old-native-'+str(index)+'.private'+p.suffix;save(dest,raw)
  assert hashlib.sha256((archive/dest).read_bytes()).hexdigest()==before[str(p)]['sha256']
  copies.append({**before[str(p)],'archive':str(archive/dest)})
 assert before=={str(p):metadata(p) for p in all_material} and holder()==owner
 save('native-before.private.json',json.dumps({'oldExec':copies,'parentIdentity':[coverage.stat().st_dev,coverage.stat().st_ino]},sort_keys=True).encode())
 save('native-archive.complete.private',b'oldTwentyOneExecAndTwoHeapsActualBytesArchived=true\noldTwentyThreeUnchanged=true\nstarts0=true\n')
if action=='after':
 assert material(archive/'native-archive.complete.private')==b'oldTwentyOneExecAndTwoHeapsActualBytesArchived=true\noldTwentyThreeUnchanged=true\nstarts0=true\n'
 copies=json.loads(material(archive/'native-before.private.json'))['oldExec'];assert len(copies)==23
 assert {entry['origin']:{key:value for key,value in entry.items() if key!='archive'} for entry in copies}==before
 for entry in copies:assert hashlib.sha256(material(pathlib.Path(entry['archive']))).hexdigest()==entry['sha256']
assert holder()==owner
print('PG475_STOPPED_NATIVE action='+action+' sameSavedCohort=true allNineKernelEmpty=true ordinary143IsStopData=true currentMatched=true starts0=true stops0=true')
