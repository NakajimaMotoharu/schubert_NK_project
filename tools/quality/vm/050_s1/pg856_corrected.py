"""One dispatch only for distinct immutable compile/stage/verify/recover v2 profile."""
import sys
from pathlib import Path
import pg856_compile as compiler
import pg856_sources_v2 as p
import pg813_native as native
R=Path(__file__).resolve().parent
def refs_source():return p.bind(compiler.refs_source())
if __name__=='__main__':
    assert len(sys.argv)==2 and sys.argv[1]in ('compile','stage','verify','recover')
    mode=sys.argv[1]
    raw=compiler.source() if mode=='compile' else __import__('pg856_sources').bind(native.source())
    raw=p.bind(raw).replace('import pg856_sources as p','import pg856_sources_v2 as p').replace('pg856_contract_test.py','pg856_contract_test_v2.py')
    exec(compile(raw,'<856v2 one actual dispatch>', 'exec'),{'__file__':str(R/'pg856_corrected.py'),'__name__':'__main__','refs_source':refs_source})
