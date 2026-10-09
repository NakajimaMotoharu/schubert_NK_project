"""Separate v3 only after899 cohort gone; no business operation replay."""
import ast,sys
from pathlib import Path
from pg894_native_v2 import source as previous
R=Path(__file__).resolve().parent
def source():
 raw=previous().replace('pg894-bootstrap-tools-v2','pg894-bootstrap-tools-v3').replace('pg894-frozen-v2','pg894-frozen-v3').replace('pg894-fixed-stage-v2','pg894-fixed-stage-v3').replace("'pg894-'+action+'-v2'","'pg894-'+action+'-v3'").replace('pg894-stage-v2.exit','pg894-stage-v3.exit').replace('pg894-verify-v2.exit','pg894-verify-v3.exit').replace('pg896-handoff-execute-v1.exit','pg899-handoff-execute-v1.exit')
 ast.parse(raw);return raw
if __name__=='__main__':
 assert sys.argv[1:]in(['stage'],['verify'],['execute'])
 exec(compile(source(),'<894 v3 standalone>','exec'),{'__file__':str(R/'pg894_native_v3.py'),'__name__':'__main__'})
