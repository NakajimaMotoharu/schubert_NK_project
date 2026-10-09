"""Actual generated held-FD body with literal independent named/fstat fault oracle."""
import ast,copy,stat,types
from pg864_completed_sources import refs
p=ast.parse(refs());cls=next(n for n in p.body if isinstance(n,ast.ClassDef)and n.name=='NamespaceFDs');md=next(n for n in ast.walk(p)if isinstance(n,ast.FunctionDef)and n.name=='metadata')
fields=['st_dev','st_ino','st_uid','st_gid','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns']
named={};opened={};events=[]
def props(values):return types.SimpleNamespace(**dict(zip(fields,values)))
class FakePath:
 def __init__(self,name):self.name=name
 def __str__(self):return self.name
 def lstat(self):return props(named[self.name])
 def is_symlink(self):return False
def open_(p,flags):
 name=str(p);values=[1,len(named)+2,0,0,stat.S_IFDIR|0o700,2,4096,8,9]
 if name=='/opt/schubert-nk':values[3:6]=[986,stat.S_IFDIR|0o750,3]
 named[name]=values;fd=len(opened)+20;opened[fd]=name;events.append(('open',fd));return fd
def fstat_(fd):
 if fd not in opened:raise OSError('closed FD')
 return props(named[opened[fd]])
def close_(fd):events.append(('close',fd));del opened[fd]
fake=types.SimpleNamespace(O_RDONLY=0,O_DIRECTORY=1,O_NOFOLLOW=2,open=open_,fstat=fstat_,listxattr=lambda p:[],close=close_)
ns={'os':fake,'pathlib':types.SimpleNamespace(Path=FakePath),'stat':stat};exec(compile(ast.Module(body=[md,cls],type_ignores=[]),'<actual held FD>','exec'),ns)
obj=ns['NamespaceFDs']();assert len(opened)==8;obj.check();saved=copy.deepcopy(named)
for name in saved:
 for index in (0,1,2,3,4,5):
  named[name][index]+=1
  caught=False
  try:obj.check()
  except AssertionError:caught=True
  assert caught;named[name]=saved[name].copy()
fd=next(iter(opened));name=opened.pop(fd);caught=False
try:obj.check()
except OSError:caught=True
assert caught;opened[fd]=name
obj.close();assert opened=={} and [e[1]for e in events if e[0]=='close']==list(reversed([e[1]for e in events if e[0]=='open']))
print('DEP864003 actual held eight FD/named identity+48 field faults/early-close/reverse-close PASS; mutation0')
