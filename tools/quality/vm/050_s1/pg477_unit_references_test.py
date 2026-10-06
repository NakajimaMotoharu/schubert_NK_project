"""Independent fixed drop-in and duplicate-free metadata vectors; no D-Bus/VM body."""
import ast,pathlib,types
from pg466_term_witness import FIELDS
source=pathlib.Path(__file__).with_name('pg477_unit_references.py').read_text()
tree=ast.parse(source)
selected=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['require','dropin_preview','show','effective_rw']]
assert len(selected)==4
checks=0
def check(value):
 global checks
 checks+=1
 if not value:raise AssertionError('fixed references oracle')
unit='schubert-nk-morning-controller.service';inspector='schubert-nk-inbox-inspector.service'
old=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG475')
prefix=b'# PGPT only: same entry/byte/owners; JaCoCo and explicit same-run resume.\n[Service]\nExecStart=\nExecStart='
base=b'[Unit]\nDescription=literal\n[Service]\nExecStart=/usr/bin/java --enable-native-access=ALL-UNNAMED LiteralEntry\n'
morning=prefix+b'/usr/bin/java -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=destfile=/run/schubert-nk/pt-coverage/parent/parent.exec,append=false --enable-native-access=ALL-UNNAMED LiteralEntry --resume 31100027-2222-4333-8444-555555555555\nReadWritePaths=/run/schubert-nk/pt-coverage/parent\n'
inspector_raw=prefix+b'/opt/pgpt-tools-pg390/schubert-nk-inbox-inspector\nReadWritePaths=/run/schubert-nk/pt-coverage/inspector\n'
data={old/'systemd'/unit:base,pathlib.Path('/etc/systemd/system')/(unit+'.d')/'pg390-native-coverage.conf':morning,pathlib.Path('/etc/systemd/system')/(inspector+'.d')/'pg390-native-coverage.conf':inspector_raw}
namespace={'pathlib':pathlib,'OLD':old,'FIELDS':FIELDS,'material':lambda p:(data[p],types.SimpleNamespace(st_dev=1,st_ino=2,st_uid=0,st_gid=0,st_mode=0o100644,st_nlink=1))}
exec(compile(ast.Module(body=selected,type_ignores=[]),'<independent fixed references>','exec'),namespace)
preview=namespace['dropin_preview']
p,raw,s,next_data=preview(unit)
check(raw==morning)
check(next_data==prefix+b'/usr/bin/java -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=destfile=/run/schubert-nk/pt-coverage/parent/parent.exec,append=false --enable-native-access=ALL-UNNAMED LiteralEntry\nReadWritePaths=/run/schubert-nk/pt-coverage/parent\n')
check(preview(inspector)[3] is None)
def reject(fn,*args):
 global checks
 try:fn(*args)
 except (ValueError,UnicodeDecodeError):checks+=1;return
 raise AssertionError('malformed fixed references accepted')
for u,good in [(unit,morning),(inspector,inspector_raw)]:
 path=pathlib.Path('/etc/systemd/system')/(u+'.d')/'pg390-native-coverage.conf'
 for bad in [good+b'Environment=EXTRA=1\n',good[:-1],good.replace(b'pg390',b'pg391'),good.replace(b'ExecStart=\n',b'ExecStart=/foreign\n'),good.replace(b'ReadWritePaths=',b'ReadOnlyPaths=')]:
  data[path]=bad;reject(preview,u)
 data[path]=good
literal={key:'literal' for key in FIELDS};literal.update(Id=unit,LoadState='loaded')
raw=('\n'.join(k+'='+v for k,v in literal.items())+'\n').encode()
current=[raw]
def command(args):
 check(args==['/usr/bin/systemctl','show',unit,'--property='+','.join(sorted(FIELDS))])
 return current[0]
namespace.update(UNITS=[unit],FIELDS=FIELDS,command=command)
# The original default binding was declared against literal FIELDS before compile.
namespace['show'].__defaults__=(FIELDS,)
check(namespace['show'](unit)==literal)
for key in literal:
 current[0]=raw+(key+'=foreign\n').encode();reject(namespace['show'],unit)
 current[0]=('\n'.join(k+'='+v for k,v in literal.items() if k!=key)+'\n').encode();reject(namespace['show'],unit)
current[0]=b'\xff';reject(namespace['show'],unit)
rw=namespace['effective_rw']
old='/run/schubert-nk /var/lib/schubert-nk/maintenance /srv/schubert-nk/backup /run/schubert-nk/pt-coverage/parent'
check(rw(unit,old,old))
for wrong in ['/run/schubert-nk/pt-coverage/parent',old+' /foreign',' '.join(old.split()[::-1]),old.replace('/srv/schubert-nk/backup','/foreign'),'']:
 check(not rw(unit,old,wrong))
for actor,expected in [(inspector,'/run/schubert-nk/pt-coverage/ordinary-inspector196'),('schubert-nk-bootstrap-admin.service','/run/schubert-nk/pt-coverage/ordinary-bootstrap196')]:
 check(rw(actor,'',expected))
 for wrong in [expected+' /foreign',expected+'/',old,'',None]:check(not rw(actor,'',wrong))
for actor in [None,'foreign.service']:
 check(not rw(actor,old,old))
check(not rw(unit,None,old));check(not rw(unit,old,None))
print('PG477_UNIT_REFERENCES_TEST independentAssertions='+str(checks)+' nativeMutation0=true productionPT0=true')
