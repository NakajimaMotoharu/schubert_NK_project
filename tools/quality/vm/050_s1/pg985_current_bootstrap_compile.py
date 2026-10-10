"""Freeze current ABI/existingADMIN profile only; no actual Unit operation."""
import ast
from pathlib import Path
from pg894_compile_v3 import source as previous
R=Path(__file__).resolve().parent
def source():
    raw=previous()
    for a,b in (('from pg894_sources_v3 import files,SOURCE','from pg983_current_bootstrap_sources import files,SOURCE'),('pg894_source_test.py','pg984_current_bootstrap_sources_test.py'),('Pg894','Pg983'),('pg894','pg983'),('pg895-bootstrap-before-v1','pg978-bootstrap-before-v2'),('pg862-release-v1','pg932-release-v1')):
        assert a in raw,a;raw=raw.replace(a,b)
    ast.parse(raw);return raw
if __name__=='__main__':exec(compile(source(),'<985 source40ef compile freeze only>','exec'),{'__file__':str(R/'pg985_current_bootstrap_compile.py'),'__name__':'__main__'})
