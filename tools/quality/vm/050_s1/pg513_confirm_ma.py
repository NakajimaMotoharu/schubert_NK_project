"""SSC209 fail-closed restore permission ONLY: fresh real M/A, no DB/Ref authority claimed."""
import os,pathlib,stat

def require(v):
 if not v:raise ValueError('current M/A unavailable')
def actor_arguments(args):
 return isinstance(args,list) and len(args)>=4 and args[0]==b'/opt/jdk-25.0.4/bin/java' and args[-3:]==[b'Pg513SingleApiRecovery',b'recover',b'']
def lock_match(parts,pid,dev,inode):
 if not isinstance(parts,list) or len(parts)<8 or parts[1:5]!=['FLOCK','ADVISORY','WRITE',str(pid)]:return False
 try:
  value=parts[5].split(':')
  return len(value)==3 and (int(value[0],16),int(value[1],16),int(value[2]))==(os.major(dev),os.minor(dev),inode)
 except ValueError:return False
def execute():
 require(os.geteuid()==0 and pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441')
 pid=os.getppid();proc=pathlib.Path('/proc')/str(pid)
 args=(proc/'cmdline').read_bytes().split(b'\0');require(actor_arguments(args))
 ticks=(proc/'stat').read_text().rpartition(')')[2].split()[19]
 require((proc/'status').read_text().split('Uid:')[1].splitlines()[0].split()==['0']*4)
 for name in ['maintenance.lock','startup-admission.lock']:
  path=pathlib.Path('/run/schubert-nk')/name;s=path.lstat()
  require(s.st_uid==s.st_gid==0 and s.st_mode==stat.S_IFREG|0o600 and s.st_nlink==1 and s.st_size==0 and not os.listxattr(path))
  links=[]
  for fd in (proc/'fd').iterdir():
   try:links.append(str(fd.readlink()))
   except FileNotFoundError:continue
  require(str(path) in links)
  rows=pathlib.Path('/proc/locks').read_text().splitlines();require(sum(lock_match(r.split(),pid,s.st_dev,s.st_ino) for r in rows)==1)
  after=path.lstat();require((s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_uid,after.st_gid,after.st_mode,after.st_nlink,after.st_size,after.st_mtime_ns,after.st_ctime_ns))
 require(ticks==(proc/'stat').read_text().rpartition(')')[2].split()[19] and args==(proc/'cmdline').read_bytes().split(b'\0'))
 print('PG513_CURRENT_MA confirmed=true databaseOrRefsClaimed=false')
if __name__=='__main__':execute()
