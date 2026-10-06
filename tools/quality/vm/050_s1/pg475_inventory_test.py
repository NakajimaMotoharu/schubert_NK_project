"""Independent 21 exec + 2 private heap fixture; executes only extracted read-only inventory.
No actual Root helper body, archive, service or credential operation.
"""
import pathlib
import stat
import types

source=pathlib.Path(__file__).with_name('pg475_stopped_native.py').read_text()
exec_block=source[source.index('all_files=list('):source.index('legacy=json.loads')]
heap_block=source[source.index('heaps=['):source.index('before={')]
roles=['parent','backup','cleanup','expiry','root-api193','root-web193','ordinary-api193','ordinary-web193']
names=['parent.exec','backup.exec','cleanup.exec','expiry.exec',
       '354cbffa0db149ae88dd59c02a98f157.before-exec.exec','9cfb59cef62d4a0498a3702172803ca2.before-exec.exec',
       '354cbffa0db149ae88dd59c02a98f157.terminal.exec','9cfb59cef62d4a0498a3702172803ca2.terminal.exec']
literal=[
 'parent/parent.exec','backup/backup.exec','cleanup/cleanup.exec','expiry/expiry.exec','root-api/root-api.exec',
 'root-api193/8d6e47b48a58468aaac34643bbeddb16.before-exec.exec',
 'root-web193/a0e695e907204a7eaf84ae16013493ad.before-exec.exec',
 'ordinary-api193/8d6e47b48a58468aaac34643bbeddb16.terminal.exec',
 'ordinary-web193/a0e695e907204a7eaf84ae16013493ad.terminal.exec',
 'root-api193/f7560ea108ae4e7aaca9246602194143.before-exec.exec',
 'root-web193/fc1cec99569542298175864fcc8b6daf.before-exec.exec',
 'ordinary-api193/f7560ea108ae4e7aaca9246602194143.terminal.exec',
 'ordinary-web193/fc1cec99569542298175864fcc8b6daf.terminal.exec',
 'root-api193/e93ae37bc6b54a24abd2c62e0e8c431e.before-exec.exec',
 'root-web193/4504c595204d47f4a110059e71c13c63.before-exec.exec',
 'ordinary-api193/e93ae37bc6b54a24abd2c62e0e8c431e.terminal.exec',
 'ordinary-web193/4504c595204d47f4a110059e71c13c63.terminal.exec',
 'root-api193/354cbffa0db149ae88dd59c02a98f157.before-exec.exec',
 'root-web193/9cfb59cef62d4a0498a3702172803ca2.before-exec.exec',
 'ordinary-api193/354cbffa0db149ae88dd59c02a98f157.terminal.exec',
 'ordinary-web193/9cfb59cef62d4a0498a3702172803ca2.terminal.exec',
 'parent/pg463-private-diagnostic/parent.private.hprof','parent/diagnostic-private/parent-private.hprof']
checks=0
files={}
class File:
 def __init__(self,name):self.name=name
 def __truediv__(self,name):return File(self.name+'/'+name if self.name else name)
 def __eq__(self,other):return isinstance(other,File) and self.name==other.name
 def __hash__(self):return hash(self.name)
 def is_file(self):return self.name in files
 def lstat(self):return types.SimpleNamespace(**files[self.name])
 def rglob(self,pattern):
  assert self.name==''
  return [File(n) for n in files if pattern=='*' or n.endswith(pattern[1:])]
def reset():
 files.clear()
 for name in literal:files[name]={'st_mode':stat.S_IFREG|0o600,'st_nlink':1,'st_uid':0,'st_gid':0,'st_size':3}
def run():
 scope={'coverage':File(''),'roles':roles,'current_names':names,'stat':stat}
 exec(compile(exec_block+'\n'+heap_block,'<read-only inventory>','exec'),scope)
 assert {p.name for p in scope['all_files']}==set(literal[:21])
 assert {p.name for p in scope['heaps']}==set(literal[21:])
 assert len(scope['all_material'])==23
def reject():
 global checks
 try:run()
 except (AssertionError,KeyError):checks+=1;return
 raise AssertionError('malformed inventory granted')
reset();run();checks+=1
for name in literal:
 reset();del files[name];reject()
for extra in ['foreign.exec','parent/foreign.hprof','ordinary-web193/foreign.terminal.exec','foreign.private']:
 reset();files[extra]=dict(files[literal[0]]);reject()
for name in literal[21:]:
 for key,value in [('st_uid',999),('st_gid',999),('st_mode',stat.S_IFLNK|0o600),('st_mode',stat.S_IFREG|0o640),('st_nlink',2),('st_size',0)]:
  reset();files[name][key]=value;reject()
reset();run();checks+=1
print('PG475_INVENTORY_TEST independentAssertions='+str(checks)+' exec21=true heaps2=true nativeMutation0=true productionPT0=true')
