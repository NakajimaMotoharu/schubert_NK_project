"""Fresh-only983 stage/verify/execute transport; actual currentRoot/before/ownedstop required."""
import ast,sys
from pathlib import Path
from pg894_native import source as previous
R=Path(__file__).resolve().parent
def source():
    raw=previous()
    for a,b in (('Pg894','Pg983'),('pg894','pg983'),('pg895-bootstrap-before-v1','pg978-bootstrap-before-v2'),('pg983-bootstrap-tools-v1','pg983-bootstrap-tools-v3'),('pg983-frozen-v1','pg983-frozen-v3'),('pg983-fixed-stage-v1','pg983-fixed-stage-v3'),("'pg983-'+action+'-v1'","'pg983-'+action+'-v3'"),('pg983-stage-v1.exit','pg983-stage-v3.exit'),('pg983-verify-v1.exit','pg983-verify-v3.exit'),('PG862','PG932')):
        assert a in raw,a;raw=raw.replace(a,b)
    marker="    action=sys.argv[1];assert not subprocess.check_output(['git','status','--porcelain'])";assert raw.count(marker)==1
    raw=raw.replace(marker,marker+"\n    assert(W/'pg963-stop-v1.exit').read_bytes()==(W/'pg968-terminal-final-v1.exit').read_bytes()==b'0\\n'\n    proof=json.loads((W/'pg960-completed-readonly-v1.safe.json').read_bytes());assert proof['productionSource']=='40ef6e894573d2ffab1d1732124960f9c98d5f97'and proof['genuineCompletion']['genuineRootDone']and proof['genuineCompletion']['genuinePid1StartDone']")
    ast.parse(raw);return raw
if __name__=='__main__':
    assert sys.argv[1:]in (['stage'],['verify'],['execute'])
    exec(compile(source(),'<986 current existingADMIN normal only>','exec'),{'__file__':str(R/'pg986_current_bootstrap_native.py'),'__name__':'__main__'})
