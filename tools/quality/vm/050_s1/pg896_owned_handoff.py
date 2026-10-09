"""Only retained894 Java; full895 unchanged before/after, owned pidfd TERM once, no unit action."""
import ast,datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
from pg895_bootstrap_before import payload as previous,W,P
R=Path(__file__).resolve().parent
IDENTITY='''
def actor():
 p=pathlib.Path('/proc/3832792');require(int((p/'stat').read_text().rpartition(')')[2].split()[19])==18878511)
 argv=(p/'cmdline').read_bytes();require(hashlib.sha256(argv).hexdigest()=='96e095662d125eaaae97b38a94010cdee4cfce7ca8ab0f0d8ab2aee14fab7e7e'and str((p/'exe').readlink())=='/opt/jdk-25.0.4/bin/java')
 status=dict(l.split(':',1)for l in(p/'status').read_text().splitlines()if ':'in l)
 require(status['Uid'].split()==status['Gid'].split()==['0']*4)
 require(not {int(c)for t in(p/'task').iterdir()for c in(t/'children').read_text().split()})
 return {'pid':3832792,'ticks':18878511,'argvSha256':hashlib.sha256(argv).hexdigest(),'cgroup':(p/'cgroup').read_text(),'authority':{k:status[k].strip()for k in ('Uid','Gid','Groups','NoNewPrivs','CapInh','CapPrm','CapEff','CapBnd','CapAmb')}}
def locks(owned):
 for name in ('maintenance.lock','startup-admission.lock'):
  p=pathlib.Path('/run/schubert-nk')/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1)
  hits=[]
  for line in pathlib.Path('/proc/locks').read_text().splitlines():
   f=line.split()
   if len(f)<8:continue
   d=f[5].split(':')
   if len(d)==3 and (int(d[0],16),int(d[1],16),int(d[2]))==(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino):hits.append(f)
  require(len(hits)==1 and hits[0][1:5]==['FLOCK','ADVISORY','WRITE','3832792'] if owned else not hits)
'''
def payload(proof,seals,pins,mode):
 raw=previous(proof,seals);a=raw.index("\nresult={'actualExit'");raw=raw[:a]
 marker="if len(f)>=8 and f[1]=='FLOCK':";assert raw.count(marker)==1
 raw=raw.replace(marker,"if len(f)>=8 and f[1]=='FLOCK'and not (OWNED and f[4]=='3832792'):")
 raw=raw.replace('bus=dbus.SystemBus(private=True);',IDENTITY+'\nOWNED=True\nbus=dbus.SystemBus(private=True);')
 marker="value={**after,";a=raw.index(marker);b=raw.index('\nfinally:',a)
 raw=raw[:b]+'''
 baseline_raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg895-bootstrap-before-v1/after.private.json').read_bytes();require(hashlib.sha256(baseline_raw).hexdigest()=='2a4f222e0d9759ac7c764f3e3c581a9774ad74de01971f15bf28e759dbc04e6e');require(value==json.loads(baseline_raw));locks(True);captured=actor()
 tool=pathlib.Path('/var/lib/pgpt-s1-preservation/pg894-bootstrap-tools-v1');require({p.name for p in tool.iterdir()}==set(PINS)|{'payload-sha256.json'})
 for name,digest in PINS.items():
  p=tool/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o400 and s.st_nlink==1 and hashlib.sha256(p.read_bytes()).hexdigest()==digest)
 require(json.loads((tool/'payload-sha256.json').read_bytes())==PINS)
 partial=pathlib.Path('/var/lib/pgpt-s1-preservation/pg894-bootstrap-verify-v1');require({p.name for p in partial.iterdir()}=={'refs-prepare.private.log'})
 save=pathlib.Path('/var/lib/pgpt-s1-preservation')/('pg896-handoff-'+MODE+'-v1');require(not os.path.lexists(save));save.mkdir(mode=0o700)
 def private(name,data):
  with(save/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(data);f.flush();os.fsync(f.fileno())
  fd=os.open(save,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
 private('before.private.json',json.dumps(value,sort_keys=True).encode());private('actor.private.json',json.dumps(captured,sort_keys=True).encode())
 if MODE=='execute':
  prior=pathlib.Path('/var/lib/pgpt-s1-preservation/pg896-handoff-preflight-v1');require(json.loads((prior/'before.private.json').read_bytes())==value and json.loads((prior/'actor.private.json').read_bytes())==captured)
  import signal,select,time
  fd=os.pidfd_open(3832792,0)
  try:
   require(actor()==captured);locks(True);private('term-reserved.private.json',json.dumps(captured,sort_keys=True).encode());require(actor()==captured)
   signal.pidfd_send_signal(fd,signal.SIGTERM,None,0);poll=select.poll();poll.register(fd,select.POLLIN);require(bool(poll.poll(15000)))
  finally:os.close(fd)
  deadline=time.monotonic()+15
  while pathlib.Path('/proc/3832792').exists()and time.monotonic()<deadline:time.sleep(.02)
  require(not pathlib.Path('/proc/3832792').exists());OWNED=False;locks(False);require(snapshot()==native==snapshot());locks(False)
  private('after.private.json',json.dumps(value,sort_keys=True).encode());private('complete.private',b'oldCloseUnknown=true\\nownedToolGone=true\\nallResources0=true\\noriginalsUnchanged=true\\nunitStarts0=true\\n')
'''+raw[b:]
 raw+="\nprint(json.dumps({'actualExit':0,'mode':MODE,'toolGone':MODE=='execute','allResources0':MODE=='execute','oldNormalClose':False,'originalsUnchanged':True,'unitStartsStopsReloads0':True}))\n"
 ast.parse(raw);return 'PINS='+repr(pins)+'\nMODE='+repr(mode)+'\n'+raw
def main():
 mode=sys.argv[1];assert mode in('preflight','execute');os.umask(0o077);assert subprocess.check_output(['git','status','--porcelain'])==b''
 if mode=='execute':assert (W/'pg896-handoff-preflight-v1.exit').read_bytes()==b'0\n'
 proof=json.loads((W/'pg885-completed-readonly-v1.safe.json').read_bytes());final=json.loads((W/'pg890-terminal-final-v1.safe.json').read_bytes());seals={k:v['sha256']for k,v in final['proofHashes'].items()if k in('before.private.json','after.private.json','parent.private.jsonl','complete.private')};frozen=json.loads((W/'pg894-frozen-v1.safe.json').read_bytes())
 prefix='HASHES='+repr(final['toolHashes'])+'\nRECEIPT='+repr((W/'pg887-native-tools-v1/pg887_parent_receipt.py').read_text())+'\n'
 code=prefix+payload(proof,seals,frozen['fileHashes'],mode);base=W/('pg896-handoff-'+mode+'-v1');assert not Path(str(base)+'.private.log').exists()
 ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -'];started=datetime.datetime.now(datetime.timezone.utc)
 r=subprocess.run(ssh,input=code.encode(),capture_output=True,timeout=90)
 with Path(str(base)+'.private.log').open('xb')as f:f.write(r.stderr);f.flush();os.fsync(f.fileno())
 with Path(str(base)+'.exit').open('x')as f:f.write(str(r.returncode)+'\n')
 safe={'actualExit':r.returncode,'mode':mode,'startedUTC':started.isoformat(),'elapsedSeconds':(datetime.datetime.now(datetime.timezone.utc)-started).total_seconds(),'privateLogSha256':hashlib.sha256(r.stderr).hexdigest(),'oldNormalClose':False,'formalAccepted':False}
 if r.returncode==0:safe.update(json.loads(r.stdout))
 with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
 print(json.dumps(safe));raise SystemExit(r.returncode)
if __name__=='__main__':main()
