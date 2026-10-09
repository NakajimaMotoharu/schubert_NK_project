"""New-only full installed832 ABI, independent source/owned failure and DB lifetime tests."""
from pathlib import Path
import ast
import pg813_compile as previous
import pg856_sources as p
R=Path(__file__).resolve().parent
def refs_source():return p.bind(previous.refs_source())
def source():
    raw=p.bind(previous.source()).replace('pg856_compile.py','pg856_compile.py')
    raw=raw.replace('pg856-database-oracle-v2','pg856-database-oracle-v1')
    ast.parse(raw);return raw
if __name__=='__main__':
    exec(compile(source(),'<856 immutable complete source compiler>','exec'),{'__file__':str(R/'pg856_compile.py'),'__name__':'__main__','refs_source':refs_source})
