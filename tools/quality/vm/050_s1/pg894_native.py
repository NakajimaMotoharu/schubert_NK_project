"""New-only immutable stage, then separate verify/existing20 execute once, never Morning start."""
import ast,sys
from pathlib import Path
from pg877_native_stop import source as previous
R=Path(__file__).resolve().parent
def source():
 raw=previous().replace('Pg877NativeStop','Pg894BootstrapExisting').replace('Pg877NativeArgumentTest','Pg894BootstrapArgumentTest').replace('pg877-native-tools-v1','pg894-bootstrap-tools-v1').replace('pg877-fixed-stage-v1','pg894-fixed-stage-v1').replace('pg877-frozen-v1.safe.json','pg894-frozen-v1.safe.json').replace('pg877-','pg894-').replace('PG877','PG894')
 raw=raw.replace("sys.argv[1]in ('stage','stop')","sys.argv[1]in ('stage','verify','execute')")
 raw=raw.replace("'Pg894BootstrapExisting stop'","'Pg894BootstrapExisting '+action")
 marker="    action=sys.argv[1];assert not subprocess.check_output(['git','status','--porcelain'])";assert raw.count(marker)==1
 raw=raw.replace(marker,marker+"\n    assert(W/'pg895-bootstrap-before-v1.exit').read_bytes()==b'0\\n'\n    if action=='execute':assert(W/'pg894-verify-v1.exit').read_bytes()==b'0\\n'")
 # All actual885/new93cb proof is enforced by generated Java/helper and full895 baseline.
 a=raw.index("    assert(W/'pg875-completed-readonly-v1.exit')");b=raw.index("    frozen=",a);raw=raw[:a]+raw[b:]
 ast.parse(raw);return raw
if __name__=='__main__':
 assert sys.argv[1:]in(['stage'],['verify'],['execute'])
 exec(compile(source(),'<894 current862 existing20 only>','exec'),{'__file__':str(R/'pg894_native.py'),'__name__':'__main__'})
