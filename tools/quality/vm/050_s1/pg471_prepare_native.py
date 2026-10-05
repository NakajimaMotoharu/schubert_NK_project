"""SSC193194 new-only PT directories/dropins inside the Java owner's stopped M/A/DB scope.
No start, permit, existing file replacement, old exec removal, original/DB mutation or default-unit edit.
Partial preparation is retained and the enclosing owner isolates on every failure.
"""
import hashlib,json,os,pathlib,pwd,stat,subprocess,sys
from pg471_owned_stop import holder,kernel_empty,show,ORDER,ROOT,BOOT
BASE=pathlib.Path('/run/schubert-nk/pt-coverage')
AGENT='/opt/pgpt-tools-pg390/jacoco-agent.jar'
PIN='fb5b0036a0899ea97edfa0fc2c7985b55f3f7c5695028163e5e60d4f3cf6075d'
ROLES={'root-api193':(0,0),'root-web193':(0,0),'ordinary-api193':(999,981),'ordinary-web193':(997,980)}
def meta(p):
 s=p.lstat();return (s.st_dev,s.st_ino,s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)
def identity_ok(observed,uid,gid,mode,directory):
 return isinstance(observed,tuple) and len(observed)==7 and all(type(v) is int for v in observed) and observed[0]>0 and observed[1]>0 and observed[2:5]==(uid,gid,mode) and observed[5]>=(2 if directory else 1) and (directory or observed[5]==1) and observed[6]==(stat.S_IFDIR if directory else stat.S_IFREG)
def parent_after(before,after):
 return isinstance(before,tuple) and isinstance(after,tuple) and len(before)==len(after)==6 and before[:4]==after[:4] and before[4]==0o711 and after[4]==0o755 and type(before[5]) is int and type(after[5]) is int and before[5]>=2 and after[5]==before[5]+4
def checked(p,uid,gid,mode,directory):
 s=p.lstat();v=(*meta(p),stat.S_IFMT(s.st_mode))
 assert not p.is_symlink() and identity_ok(v,uid,gid,mode,directory)
 assert 'system.posix_acl_access' not in os.listxattr(p,follow_symlinks=False) and 'system.posix_acl_default' not in os.listxattr(p,follow_symlinks=False)
 return v
def sync(p):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
def create_file(p,data,mode):
 fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,mode)
 try:
  os.fchmod(fd,mode)
  with os.fdopen(fd,'wb',closefd=False) as f:f.write(data);f.flush();os.fsync(fd)
 finally:os.close(fd)
 assert p.read_bytes()==data;checked(p,0,0,mode,False);sync(p.parent)
def configuration(role,base):
 assert role in ['api','web'] and isinstance(base,str) and base.startswith('!/usr/bin/java --enable-native-access=ALL-UNNAMED ')
 assert base.endswith(' dev.codex.schubert.nk.batch.file.RootServiceLauncher '+role.upper()) and '-javaagent:' not in base and '\n' not in base
 agent='-javaagent:'+AGENT+'=output=none,append=false,dumponexit=false,sessionid='+role.upper()+'-${INVOCATION_ID}-root'
 line=base.replace('!/usr/bin/java ','!/usr/bin/java '+agent+' ',1)
 rw=('/srv/schubert-nk/data/transfer ' if role=='api' else '')+str(BASE/('root-'+role+'193'))+' '+str(BASE/('ordinary-'+role+'193'))
 return ('# SSC193194 isolated PT only; default signed base unchanged, no vendor pathname writer\n[Service]\nExecStart=\nExecStart='+line+'\nReadWritePaths=\nReadWritePaths='+rw+'\n').encode('ascii')
def main():
 assert os.geteuid()==0 and sys.argv==[sys.argv[0],'prepare'] and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT
 owner=holder();assert pathlib.Path('/opt/schubert-nk/current').readlink()==pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG469')
 for unit in ORDER:
  state=show(unit);assert state['MainPID']==state['ControlPID']=='0' and not state['Job'] and state['ActiveState'] in ['inactive','failed']
  assert (ROOT/(unit+'.stopped.private')).is_file();kernel_empty(unit)
 for p in [pathlib.Path('/run'),pathlib.Path('/run/schubert-nk')]:checked(p,0,0,0o755,True)
 original=checked(BASE,0,0,0o711,True)
 assert subprocess.check_output(['/usr/bin/findmnt','-n','-o','FSTYPE','--target',str(BASE)],text=True).strip()=='tmpfs'
 a=pathlib.Path(AGENT);checked(a,0,0,0o644,False);assert a.stat().st_size==307843 and hashlib.sha256(a.read_bytes()).hexdigest()==PIN
 for name,uid,gid in [('schubert-api',999,981),('schubert-web',997,980)]:
  record=pwd.getpwnam(name);assert (record.pw_uid,record.pw_gid)==(uid,gid)
 planned={};missing=[]
 checked(pathlib.Path('/etc/systemd/system'),0,0,0o755,True)
 for role in ['api','web']:
  unit=pathlib.Path('/etc/systemd/system/schubert-nk-'+role+'.service');base=unit.read_text()
  assert base.encode()==(pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG469/systemd')/unit.name).read_bytes()
  lines=[s[len('ExecStart='):] for s in base.splitlines() if s.startswith('ExecStart=')];assert len(lines)==1
  checked(unit,0,0,0o644,False)
  parent=unit.with_name(unit.name+'.d')
  if parent.exists():checked(parent,0,0,0o755,True)
  else:assert not parent.is_symlink();missing.append(parent)
  dest=parent/'zz-pg471-native193.conf';assert not dest.exists() and not dest.is_symlink();planned[dest]=configuration(role,lines[0])
 for name in ROLES:assert not (BASE/name).exists() and not (BASE/name).is_symlink()
 old={p:(meta(p),hashlib.sha256(p.read_bytes()).hexdigest()) for p in BASE.rglob('*.exec')};assert len(old)==5
 create_file(ROOT/'native-before.private.json',json.dumps({str(p):[m,h] for p,(m,h) in old.items()},sort_keys=True).encode(),0o600)
 assert owner==holder() and checked(BASE,0,0,0o711,True)==original
 fd=os.open(BASE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  st=os.fstat(fd);assert (st.st_dev,st.st_ino)==original[:2];os.fchmod(fd,0o755);os.fsync(fd);checked(BASE,0,0,0o755,True)
 finally:os.close(fd)
 for name,(uid,gid) in ROLES.items():
  p=BASE/name;p.mkdir(mode=0o700);os.chown(p,uid,gid);os.chmod(p,0o700);checked(p,uid,gid,0o700,True);assert not list(p.iterdir());sync(p)
 sync(BASE)
 for p in missing:p.mkdir(mode=0o755);os.chmod(p,0o755);checked(p,0,0,0o755,True);sync(p.parent)
 for p,data in planned.items():create_file(p,data,0o644)
 assert {p:(meta(p),hashlib.sha256(p.read_bytes()).hexdigest()) for p in BASE.rglob('*.exec')}==old
 assert parent_after(original[:6],meta(BASE)) and owner==holder()
 subprocess.run(['/usr/bin/systemctl','daemon-reload'],check=True,timeout=10,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 for role in ['api','web']:
  unit='schubert-nk-'+role+'.service';state=show(unit);assert state['MainPID']==state['ControlPID']=='0' and not state['Job'];kernel_empty(unit)
  effective=subprocess.check_output(['/usr/bin/systemctl','show',unit,'--property=ExecStart,ReadWritePaths'],text=True)
  assert 'output=none,append=false,dumponexit=false,sessionid='+role.upper()+'-${INVOCATION_ID}-root' in effective and 'destfile=' not in effective
  assert str(BASE/('root-'+role+'193')) in effective and str(BASE/('ordinary-'+role+'193')) in effective
 assert owner==holder();create_file(ROOT/'native-preparation.complete.private',b'fourPrivateRoles=true\nparent755=true\noldFiveExecUnchanged=true\nclosedProfile=true\nstarts0=true\n',0o600)
 print('PG471_NATIVE_PREPARED fourPrivateRoles=true parent755=true oldFiveExecUnchanged=true closedProfile=true starts0=true',flush=True)
if __name__=='__main__':main()
