"""Independent current-state parser/Root material and read-only authority vectors.
Extract definitions only: never executes the helper's Root body or archives/stops a VM.
"""
import ast,pathlib,stat,types,os
from pg466_term_witness import FIELDS
from pg471_native_owned_stop import require

source=pathlib.Path(__file__).with_name('pg477_stopped_native.py').read_text()
parsed=ast.parse(source)
functions=[node for node in parsed.body if isinstance(node,ast.FunctionDef) and node.name in ['holder','current','material']]
assert len(functions)==3
imports={alias.asname or alias.name for node in parsed.body if isinstance(node,(ast.Import,ast.ImportFrom)) for alias in node.names}
assert {'require','tick','show','kernel_empty','ORDER','os','pathlib','stat'} <= imports
paths=[node for node in ast.walk(parsed) if isinstance(node,ast.Constant) and isinstance(node.value,str)]
assert '/var/lib/pgpt-s1-preservation/pg475-native-tools-v1' in [node.value for node in paths]
assert any(isinstance(node,ast.ImportFrom) and node.module=='pg475_native_owned_stop' for node in parsed.body)
assert not any(isinstance(node,ast.ImportFrom) and node.module=='pg474_native_owned_stop' for node in parsed.body)
parent='schubert-nk-morning-controller.service'
literal={'Id':parent,'LoadState':'loaded','ActiveState':'inactive','SubState':'dead','Job':'','MainPID':'0','ControlPID':'0','InvocationID':'2cb76b9c627e430ebc4dbec0761f9ebb','Type':'oneshot','Restart':'no','RemainAfterExit':'no','Result':'success','ExecMainCode':'1','ExecMainStatus':'0','ExecMainStartTimestampMonotonic':'187523371433','ExecMainExitTimestampMonotonic':'188500000000','KillMode':'control-group','SendSIGKILL':'no'}
assert set(literal)==FIELDS
checks=0
def check(value):
 global checks
 checks+=1
 assert value,'literal stopped helper vector'
raw=('\n'.join(k+'='+v for k,v in literal.items())+'\n').encode()
class Commands:
 def __init__(self):self.data=raw;self.calls=[]
 def check_output(self,args):
  self.calls.append(args)
  check(args==['systemctl','show',parent,'--property='+','.join(sorted(literal))])
  return self.data
commands=Commands();observed=[]
namespace={'subprocess':commands,'ORDER':['caddy.service'],'show':lambda unit:observed.append(unit) or {'fixed':'receipt'},'stat':stat,'require':require}
exec(compile(ast.Module(body=functions,type_ignores=[]),'<independent helper definitions>','exec'),namespace)
current=namespace['current'];material=namespace['material']
check(current(parent)==literal);check(current('caddy.service')=={'fixed':'receipt'});check(observed==['caddy.service'])
def reject(function,*args):
 global checks
 try:function(*args)
 except (AssertionError,ValueError,UnicodeDecodeError):checks+=1;return
 raise AssertionError('must reject malformed fixed observation')
reject(current,'foreign.service')
for key in literal:
 commands.data=('\n'.join(k+'='+v for k,v in literal.items() if k!=key)+'\n').encode();reject(current,parent)
 commands.data=raw+(key+'=duplicate\n').encode();reject(current,parent)
for key,value in [('Id','foreign.service'),('LoadState','not-found')]:
 data=dict(literal);data[key]=value;commands.data=('\n'.join(k+'='+v for k,v in data.items())+'\n').encode();reject(current,parent)
commands.data=b'\xff';reject(current,parent)
class File:
 def __init__(self,**changes):
  values={'st_mode':stat.S_IFREG|0o600,'st_uid':0,'st_nlink':1};values.update(changes);self.info=types.SimpleNamespace(**values)
 def lstat(self):return self.info
 def read_bytes(self):return b'literal-private-fixture'
check(material(File())==b'literal-private-fixture')
for change in [{'st_mode':stat.S_IFLNK|0o600},{'st_mode':stat.S_IFDIR|0o600},{'st_mode':stat.S_IFREG|0o640},{'st_uid':999},{'st_nlink':2}]:reject(material,File(**change))
class Proc:
 def __init__(self):
  self.argv=b'/opt/jdk-25.0.4/bin/java\0-cp\0fixed\0Pg477StoppedDeployment\0verify\0'
  self.links=['/run/schubert-nk/maintenance.lock','/run/schubert-nk/startup-admission.lock']
  self.meta={name:types.SimpleNamespace(st_dev=os.makedev(0,1),st_ino=42+index,st_uid=0,st_gid=0,st_mode=stat.S_IFREG|0o600,st_nlink=1) for index,name in enumerate(self.links)}
  self.locks='1: FLOCK ADVISORY WRITE 100 00:01:42 0 EOF\n2: FLOCK ADVISORY WRITE 100 00:01:43 0 EOF\n'
proc=Proc()
class Path:
 def __init__(self,*parts):self.name='/'.join(str(value).rstrip('/') for value in parts)
 def __truediv__(self,value):return Path(self.name,value)
 def __str__(self):return self.name
 def read_bytes(self):check(self.name=='/proc/100/cmdline');return proc.argv
 def read_text(self):check(self.name=='/proc/locks');return proc.locks
 def stat(self):return proc.meta[self.name]
 def iterdir(self):
  check(self.name=='/proc/100/fd')
  return [types.SimpleNamespace(readlink=lambda value=value:value) for value in proc.links]
namespace.update({'pathlib':types.SimpleNamespace(Path=Path),'os':types.SimpleNamespace(getppid=lambda:100,major=os.major,minor=os.minor),'tick':lambda pid:123})
holder=namespace['holder'];check(holder()==(100,123))
proc.argv=proc.argv.replace(b'verify',b'activate');check(holder()==(100,123))
proper=proc.argv
for wrong in [proper.replace(b'Pg477StoppedDeployment',b'ForeignOwner'),proper.replace(b'activate',b'stop'),proper.replace(b'/opt/jdk-25.0.4/bin/java',b'/arbitrary/java')]:
 proc.argv=wrong;reject(holder)
proc.argv=proper
for field,value in [('st_uid',999),('st_gid',981),('st_mode',stat.S_IFREG|0o640),('st_nlink',2),('st_ino',99)]:
 original=getattr(proc.meta[proc.links[0]],field);setattr(proc.meta[proc.links[0]],field,value);reject(holder);setattr(proc.meta[proc.links[0]],field,original)
all_locks=proc.locks
for wrong in ['',all_locks.splitlines()[0]+'\n',all_locks+all_locks.splitlines()[0]+'\n',all_locks.replace('WRITE','READ'),all_locks.replace(' 100 ',' 101 ')]:proc.locks=wrong;reject(holder)
proc.locks=all_locks
saved_links=proc.links;proc.links=saved_links[:1];reject(holder);proc.links=saved_links
check(holder()==(100,123))
# No hidden stop/start/reset/freeze/permit path in this helper. Mutation is only fixed SAVE archive.
calls=[node for node in ast.walk(parsed) if isinstance(node,ast.Call)]
check(not any(isinstance(node.func,ast.Attribute) and node.func.attr in ['run','Popen','unlink','rename','replace','chmod','chown'] for node in calls))
check("PG477_STOPPED_NATIVE action=" in source and "'archive'" in source and "oldTwentySevenUnchanged=true" in source)
print('PG477_STOPPED_NATIVE_TEST independentAssertions='+str(checks)+' nativeMutation0=true productionPT0=true')
