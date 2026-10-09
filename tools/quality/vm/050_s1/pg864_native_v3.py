"""New-only actual dispatch uses v3 complete profile; failed v2 never reused."""
import ast
from pathlib import Path
R=Path(__file__).resolve().parent
def source():
    raw=(R/'pg864_native.py').read_text()
    for old,new in (('pg864-completed-tools-v2','pg864-completed-tools-v3'),('pg864-frozen-v2','pg864-frozen-v3'),('PG864-compile-v2','PG864-compile-v3'),('pg864-stage-v2','pg864-stage-v3'),('PG864-stage-v2','PG864-stage-v3'),("'-v2'","'-v3'"),('pg864-prepare-ro-v2','pg864-prepare-ro-v3'),('pg864-verify-v2','pg864-verify-v3')):raw=raw.replace(old,new)
    ast.parse(raw);return raw
if __name__=='__main__':
    exec(compile(source(),'<864 v3 complete actual dispatch>','exec'),{'__file__':str(R/'pg864_native_v3.py'),'__name__':'__main__'})
