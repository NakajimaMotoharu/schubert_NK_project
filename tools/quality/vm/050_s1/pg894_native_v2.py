"""Fresh v2 immutable new stage/verify/execute only after owned v1 handoff, no replay."""
import ast,sys
from pathlib import Path
from pg894_native import source as previous
R=Path(__file__).resolve().parent
def source():
 raw=previous().replace('pg894-bootstrap-tools-v1','pg894-bootstrap-tools-v2').replace('pg894-frozen-v1','pg894-frozen-v2').replace('pg894-fixed-stage-v1','pg894-fixed-stage-v2').replace("'pg894-'+action+'-v1'","'pg894-'+action+'-v2'").replace('pg894-stage-v1.exit','pg894-stage-v2.exit').replace('pg894-verify-v1.exit','pg894-verify-v2.exit')
 marker="    action=sys.argv[1];assert not subprocess.check_output(['git','status','--porcelain'])";assert raw.count(marker)==1
 raw=raw.replace(marker,marker+"\n    assert(W/'pg896-handoff-execute-v1.exit').read_bytes()==b'0\\n'")
 ast.parse(raw);return raw
if __name__=='__main__':
 assert sys.argv[1:]in(['stage'],['verify'],['execute'])
 exec(compile(source(),'<894 v2 separate new runtime>','exec'),{'__file__':str(R/'pg894_native_v2.py'),'__name__':'__main__'})
