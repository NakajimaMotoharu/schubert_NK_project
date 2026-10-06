"""Independent stopped metadata/command parser vectors; no Root/VM authority."""
import ast,pathlib,types
from pg466_term_witness import FIELDS
base=pathlib.Path(__file__).parent
tree=ast.parse((base/'pg477_completed_refs.py').read_text())
defs=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ['require','show']]
assert len(defs)==2
checks=0
unit='schubert-nk-bootstrap-admin.service'
literal={k:'literal' for k in FIELDS};literal.update(Id=unit,LoadState='loaded')
raw=('\n'.join(k+'='+v for k,v in literal.items())+'\n').encode()
value=[raw]
def command(args):
 global checks
 checks+=1;assert args==['/usr/bin/systemctl','show',unit,'--property='+','.join(sorted(FIELDS))]
 return value[0]
env={'command':command,'FIELDS':FIELDS,'UNITS':[unit]}
exec(compile(ast.Module(body=defs,type_ignores=[]),'<independent completed metadata>','exec'),env)
assert env['show'](unit)==literal;checks+=1
for key in literal:
 for data in [raw+(key+'=duplicate\n').encode(),('\n'.join(k+'='+v for k,v in literal.items() if k!=key)+'\n').encode()]:
  value[0]=data
  try:env['show'](unit)
  except ValueError:checks+=1
  else:raise AssertionError('malformed metadata accepted')
for filename in ['pg477_completed_refs.py','pg477_completed_native.py']:
 source=(base/filename).read_text();parsed=ast.parse(source)
 assert "Pg477CompletedAcceptance" in source and 'os.getppid()' in source
 assert not any(isinstance(x,ast.Attribute) and x.attr in ['unlink','rename','replace','kill','pidfd_send_signal'] for x in ast.walk(parsed));checks+=1
 assert 'start' not in [x.value for x in ast.walk(parsed) if isinstance(x,ast.Constant) and isinstance(x.value,str)];checks+=1
print('PG477_COMPLETED_METADATA_TEST independentAssertions='+str(checks)+' productionPT0=true nativeMutation0=true')
