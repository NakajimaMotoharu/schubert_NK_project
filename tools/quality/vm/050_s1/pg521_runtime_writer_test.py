"""Independent real-FD new-only writer/short writes/fault positions; synthetic Root, no VM."""
import ast,copy,os,pathlib,tempfile,types
source=ast.parse(pathlib.Path(__file__).with_name('pg521_runtime_resume_refs.py').read_text())
branches=[n for n in ast.walk(source) if isinstance(n,ast.If) and isinstance(n.test,ast.Compare) and isinstance(n.test.left,ast.Name) and n.test.left.id=='action' and any(isinstance(v,ast.Constant) and v.value=='prepare' for v in n.test.comparators)]
assert len(branches)==1
code=compile(ast.Module(body=branches[0].body,type_ignores=[]),'<actual exclusive held-parent writer>','exec')
count=0
def check(v):
 global count
 if not v:raise AssertionError('runtime writer independent oracle')
 count+=1
def require(v):
 if not v:raise ValueError('independent mismatch')
def exercise(fault=0,foreign=False,zero_write=False):
 events=[];fds=set()
 with tempfile.TemporaryDirectory(prefix='pg521-synthetic-root-') as tmp:
  root=pathlib.Path(tmp)/'runtime';root.mkdir(mode=0o755);root.chmod(0o755)
  prior=root.stat();expected=[prior.st_dev,prior.st_ino,0,0,prior.st_mode,prior.st_nlink,prior.st_size,prior.st_mtime_ns,prior.st_ctime_ns]
  name='pg492-once-resume.conf';target=root/name;dropin=b'# independent SS343 fixture\n[Service]\nExecStart=literal --resume public\n'
  if foreign:target.write_bytes(b'independent-old')
  def point(n):
   events.append(n)
   if len(events)==fault:raise OSError('injected public IO fault')
  class Ops:
   def __getattr__(self,n):return getattr(os,n)
   def open(self,*args,**kwargs):
    point('open');v=os.open(*args,**kwargs);fds.add(v);return v
   def fstat(self,v):
    point('fstat');s=os.fstat(v);return types.SimpleNamespace(st_dev=s.st_dev,st_ino=s.st_ino,st_uid=0,st_gid=0,st_mode=s.st_mode,st_nlink=s.st_nlink,st_size=s.st_size,st_mtime_ns=s.st_mtime_ns,st_ctime_ns=s.st_ctime_ns)
   def fchmod(self,*args):point('fchmod');return os.fchmod(*args)
   def write(self,fd,raw):
    point('write')
    return 0 if zero_write else os.write(fd,raw[:11])
   def fsync(self,*args):point('fsync');return os.fsync(*args)
   def close(self,fd):
    os.close(fd);fds.remove(fd);point('consumedClose')
  def strict(p,mode,bound):
   point('strict');check(p==target and mode==0o644 and bound==4096)
   check(p.stat().st_mode & 0o777==0o644)
   return p.read_bytes()
  def command(args):
   point('reload');check(args==['/usr/bin/systemctl','daemon-reload']);return b''
  def compare(*args):point('compare')
  env={'require':require,'target':target,'before':{'independent':'snapshot'},'snapshot':lambda:{'independent':'snapshot'},'compare':compare,'os':Ops(),'RUNTIME':root,'NAME':name,'runtime_directory':expected,'dropin':dropin,'strict':strict,'command':command,'changed':False}
  try:
   exec(code,env);check(target.read_bytes()==dropin);check(env['changed']);check(events.count('reload')==1);check(not fds)
   return events,None
  except (OSError,ValueError) as error:
   if foreign:check(target.read_bytes()==b'independent-old' and 'open' not in events)
   check('reload' not in events[:-1] or events.count('reload')==1)
   return events,error
  finally:
   for fd in list(fds):os.close(fd)
events,error=exercise();check(error is None)
positions=len(events)
for fault in range(1,positions+1):
 failed,error=exercise(fault=fault);check(isinstance(error,OSError));check(len(failed)==fault or failed[-1]=='consumedClose')
failed,error=exercise(foreign=True);check(isinstance(error,ValueError))
failed,error=exercise(zero_write=True);check(isinstance(error,ValueError) and 'reload' not in failed)
print('PG521_WRITER_ORACLE independentAssertions='+str(count)+' faultPositions='+str(positions)+' shortWritesHandled=true exclusiveHeldParentFD=true syntheticRoot=true vmActions0=true productionPT0=true')
