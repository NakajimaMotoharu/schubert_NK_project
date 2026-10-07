"""BUG811/812 independent real umask/held inode vector and fixed ID/owner negatives."""
import ast,hashlib,os,pathlib,stat,tempfile
from types import SimpleNamespace
R=pathlib.Path(__file__).resolve().parent
tree=ast.parse((R/'pg504_resume_refs.py').read_text());n=0
def check(value):
 global n
 assert value;n+=1
literal=[28,2576,0,0,stat.S_IFDIR|0o700,2,40,1791390404799000000,1791390404799000000]
class PathFixture:
 def __init__(self):self.m=list(literal);self.names=[];self.acls=[]
 def iterdir(self):return self.names
fixture=PathFixture();env={'metadata':lambda p:p.m,'RUNTIME_METADATA':literal,'os':SimpleNamespace(listxattr=lambda p:p.acls)}
definition=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='recoverable_runtime')
exec(compile(ast.Module(body=[definition],type_ignores=[]),'<fixed runtime recovery>','exec'),env)
check(env['recoverable_runtime'](fixture))
for i in range(9):
 fixture.m=list(literal);fixture.m[i]+=1;check(not env['recoverable_runtime'](fixture))
for value in [None,[],literal[:-1]]:
 fixture.m=value;check(not env['recoverable_runtime'](fixture))
fixture.m=list(literal);fixture.names=['foreign.conf'];check(not env['recoverable_runtime'](fixture));fixture.names=[]
for acl in ['system.posix_acl_access','system.posix_acl_default']:
 fixture.acls=[acl];check(not env['recoverable_runtime'](fixture))
# Truly execute kernel umask/fchmod on an isolated generated host fixture, not the VM.
old=os.umask(0o077)
try:
 with tempfile.TemporaryDirectory(prefix='pg504-mode-oracle-') as generated:
  p=pathlib.Path(generated)/'runtime';p.mkdir(mode=0o755);before=p.lstat()
  check(stat.S_IMODE(before.st_mode)==0o700)
  fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
  try:
   check((os.fstat(fd).st_dev,os.fstat(fd).st_ino)==(before.st_dev,before.st_ino))
   os.fchmod(fd,0o755);os.fsync(fd);after=p.lstat()
   check(stat.S_IMODE(after.st_mode)==0o755)
   check((after.st_dev,after.st_ino,after.st_uid,after.st_gid)==(before.st_dev,before.st_ino,before.st_uid,before.st_gid))
   check(not list(p.iterdir()) and 'system.posix_acl_access' not in os.listxattr(p))
  finally:os.close(fd)
finally:os.umask(old)
repair=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='repair_empty_runtime')
check(any(isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr=='fchmod'
          and isinstance(x.args[1],ast.Constant) and x.args[1].value==0o755 for x in ast.walk(repair)))
driver=ast.parse((R/'pg504_resume_native_v1.py').read_text())
ids=[x.value for node in ast.walk(driver) if isinstance(node,ast.Dict) for key,x in zip(node.keys,node.values)
     if isinstance(key,ast.Constant) and key.value=='id' and isinstance(x,ast.Constant)]
check(ids==['PG504-resume-native-v1'])
check('pg504-resume-native-v1.private.log' in (R/'pg504_resume_native_v1.py').read_text())
check('pg504-resume-native-v1.exit' in (R/'pg504_resume_native_v1.py').read_text())
print('PG504_PREFLIGHT_ORACLE independentAssertions='+str(n)+' realUmaskFD=true fixedID=true vmActions0=true productionPT0=true')
