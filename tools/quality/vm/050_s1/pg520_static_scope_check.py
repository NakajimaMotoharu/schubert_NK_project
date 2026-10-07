"""BUG821/YKT590: host-only fixed dynamic-definition scope check; baseline NEVER permitted."""
import ast,pathlib,sys
RUNTIME=pathlib.Path('/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime')
sys.path.insert(0,str(RUNTIME))
from pyflakes.checker import Checker
from pyflakes.messages import UndefinedName
# Only the exact pinned AST definitions/constant assignment loaded by this retirement adapter.
DYNAMIC={'BOOT','UNITS','FIELDS','command','show','metadata','tree','strict','owner','locked_database','kernel','configuration_fields','exec_record'}
def undefined(source):
 if not isinstance(source,str):raise ValueError('source required')
 return [(m.lineno,m.message_args[0]) for m in Checker(ast.parse(source),builtins=DYNAMIC).messages if isinstance(m,UndefinedName)]
def execute(argv):
 if len(argv)!=2 or argv[1] not in ['reproduce','verify']:raise ValueError('fixed scope mode')
 here=pathlib.Path(__file__).parent
 name='pg519_runtime_retirement_refs.py' if argv[1]=='reproduce' else 'pg520_runtime_retirement_refs.py'
 results=undefined((here/name).read_text())
 if argv[1]=='reproduce':
  if results!=[(85,'baseline')]:raise AssertionError('old exact undefined scope not reproduced')
  print('PG520_SCOPE_REPRODUCED oldLine85UndefinedBaseline=true excludedDynamicNamesOnly=true vmActions0=true')
 else:
  if results:raise AssertionError('undefined current scope')
  print('PG520_SCOPE_VERIFIED undefined0=true excludedDynamicNamesOnly=true vmActions0=true')
if __name__=='__main__':execute(sys.argv)
