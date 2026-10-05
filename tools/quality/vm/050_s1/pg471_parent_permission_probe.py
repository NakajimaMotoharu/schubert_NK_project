"""BUG754 independent real UID/OS syscall oracle in a new private fixture; apps/DB/current unchanged."""
import datetime,json,os,pathlib,subprocess
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
os.umask(0o077);log=W/'pg471-parent-permission-v1.private.log';assert not log.exists()
INNER=r'''import errno,json,os,pathlib,stat,sys
assert os.geteuid()==999 and os.getegid()==981
base=pathlib.Path(sys.argv[1]);flags=os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC
try:os.open(base/'711',flags);raise AssertionError('711 must refuse ordinary read FD')
except PermissionError as e:assert e.errno==errno.EACCES
fd=os.open(base/'755',flags)
try:
 child=os.open('ordinary-api193',flags,dir_fd=fd)
 try:
  f=os.open('literal.exec',os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=child)
  try:
   literal=b'independent O_RDONLY parent permission vector\n';assert os.write(f,literal)==len(literal);os.fsync(f)
   s=os.fstat(f);assert (s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(999,981,0o600,1)
   os.lseek(f,0,os.SEEK_SET);assert os.read(f,4096)==literal
  finally:os.close(f)
  os.fsync(child)
 finally:os.close(child)
finally:os.close(fd)
print(json.dumps({'uid':999,'gid':981,'parent711':'EACCES','parent755':'OPENED','roleMode':'0700','newFileMode':'0600','newFileBytes':46,'normalFileAndDirectoryClose':True,'sync':True,'appsMutated':False}))
'''
OUTER=r'''import os,pathlib,subprocess,stat
assert os.geteuid()==0
root=pathlib.Path('/var/tmp/pg471-parent-permission-v1');assert not root.exists() and not root.is_symlink();root.mkdir(mode=0o755);os.chmod(root,0o755)
for mode in [0o711,0o755]:
 p=root/format(mode,'o');p.mkdir(mode=mode);os.chmod(p,mode);child=p/'ordinary-api193';child.mkdir(mode=0o700);os.chown(child,999,981);os.chmod(child,0o700)
before={p:(p.stat().st_dev,p.stat().st_ino,p.stat().st_uid,p.stat().st_gid,stat.S_IMODE(p.stat().st_mode)) for p in [root,root/'711',root/'755']}
subprocess.run(['/usr/bin/sudo','-n','-u','schubert-api','-g','schubert-api','/usr/bin/python3','-B','-c',INNER,str(root)],check=True)
assert before=={p:(p.stat().st_dev,p.stat().st_ino,p.stat().st_uid,p.stat().st_gid,stat.S_IMODE(p.stat().st_mode)) for p in before}
'''
ssh=['ssh','-i',str(P/'vm-access'),'-p','22222','-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'ubuntu@127.0.0.1','sudo -n python3 -B -']
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
r=subprocess.run(ssh,input=('INNER='+repr(INNER)+'\n'+OUTER).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
with log.open('xb') as f:f.write(r.stdout);f.write(r.stderr)
if r.returncode:print('PG471_PARENT_PROBE actualExit='+str(r.returncode)+' privateDiagnostics=true');raise SystemExit(r.returncode)
result=json.loads(r.stdout);assert result['parent711']=='EACCES' and result['parent755']=='OPENED' and result['normalFileAndDirectoryClose']
result.update({'actualExit':0,'started':start,'completed':datetime.datetime.now(datetime.timezone.utc).isoformat(),'fixturePreserved':True,'formal':False,'productionPT':0})
out=W/'pg471-parent-permission-v1.safe.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
