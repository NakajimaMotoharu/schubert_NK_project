"""SSC202/205, BUG808: fixed pre-DB owner TERM, old close stays UNKNOWN."""
import hashlib,json,os,pathlib,signal,sys,time
assert os.geteuid()==0
os.umask(0o077)
PID=23861;TICKS=26474104
BOOT='e07aa706-1acd-4e65-b309-d7f330f79d54'
ARGV='544542ec3d53a17fcf9722d511ec40e80385117ad2c15f05d7f146aa561ffe5e'
SAVE=pathlib.Path('/var/lib/pgpt-s1-preservation/pg499-preflight-owned-handoff-v1')
assert not SAVE.exists()
sys.path.insert(0,'/var/lib/pgpt-s1-preservation/pg496-timeout-tools-v6')
import pg496_timeout_owned as h
h.load_definitions()
raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg498-pending-codeonly/refs-after.private.json').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='1ef541deba93311f167df38135930dd1a935fddb7cc54d9cf2b02bfb1b77fdc3'
before=json.loads(raw)
def owner():
 p=pathlib.Path('/proc')/str(PID)
 assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT
 assert int((p/'stat').read_text().rpartition(')')[2].split()[19])==TICKS
 assert hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()==ARGV
 assert (p/'status').read_text().split('Uid:\t')[1].splitlines()[0].split()==['0']*4
 assert {c for t in (p/'task').iterdir() for c in (t/'children').read_text().split()}==({'23890'} if pathlib.Path('/proc/23890').exists() else set())
 for name in ['maintenance.lock','startup-admission.lock']:
  path=pathlib.Path('/run/schubert-nk')/name;s=path.stat();matches=[]
  assert str(path) in {str(fd.readlink()) for fd in (p/'fd').iterdir()}
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)>=8 and f[1:5]==['FLOCK','ADVISORY','WRITE',str(PID)]:
    d=f[5].split(':')
    if (int(d[0],16),int(d[1],16),int(d[2]))==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):matches.append(line)
  assert len(matches)==1
def unchanged():
 assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT
 units={u:h.show(u) for u in h.ORDER+h.EXTRA}
 for u,v in units.items():
  assert v['MainPID']==v['ControlPID']=='0' and v['Job']=='';h.kernel_empty(u)
 now=dict(h.snapshot(),units=units,current=str(pathlib.Path('/opt/schubert-nk/current').readlink()))
 assert now==before
 assert not pathlib.Path('/var/lib/pgpt-s1-preservation/pg499-runtime-retirement').exists()
 sql="select count(*) from pg_stat_activity where datname='schubert_nk' and usename in ('schubert_batch','schubert_app','schubert_backup','schubert_inbox_inspector','schubert_web_session');select count(*) from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and granted;"
 assert h.command(['/usr/bin/sudo','-n','-u','postgres','/usr/bin/psql','-X','-qAt','-d','schubert_nk','-c',sql]).splitlines()==[b'0',b'0']
def save(name,value):
 with (SAVE/name).open('x') as f:
  os.fchmod(f.fileno(),0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
 fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
child=pathlib.Path('/proc/23890')
child_data=child.joinpath('stat').read_text().rpartition(')')[2].split()
assert int(child_data[19])==26474240 and int(child_data[1])==PID
assert hashlib.sha256(child.joinpath('cmdline').read_bytes()).hexdigest()=='2d97b752cf1848c49f32a4582409ff2d7c9085b190b8c432f159d6773ed0110b'
assert child.joinpath('status').read_text().split('Uid:\t')[1].splitlines()[0].split()==['0']*4
owner();unchanged();owner();unchanged()
fd=os.pidfd_open(PID);owner()
SAVE.mkdir(mode=0o700)
save('term-reservation.private.json',{'boot':BOOT,'pid':PID,'ticks':TICKS,'argvHash':ARGV,'oldNormalClose':False,'repeatForbidden':True})
child_fd=os.pidfd_open(23890)
owner();signal.pidfd_send_signal(child_fd,signal.SIGTERM);os.close(child_fd)
child_deadline=time.monotonic()+5
while child.exists() and time.monotonic()<child_deadline:time.sleep(.05)
assert not child.exists()
owner();signal.pidfd_send_signal(fd,signal.SIGTERM);os.close(fd)
deadline=time.monotonic()+15
while pathlib.Path('/proc/'+str(PID)).exists() and time.monotonic()<deadline:time.sleep(.05)
assert not pathlib.Path('/proc/'+str(PID)).exists()
unchanged();unchanged()
save('complete.private.json',{'ownedTerm':True,'allOriginalValuesUnchanged':True,'businessPeers0':True,'advisory0':True,'oldCloseUNKNOWN':True,'starts0':True,'freeze0':True})
print('PG499_PREFLIGHT_HANDOFF ownedTerm=true unchangedTwice=true oldCloseUNKNOWN=true starts0=true')
