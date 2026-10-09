"""Independent vectors against the actual v2 assembled source, not previous namespace."""
from pathlib import Path
R=Path(__file__).resolve().parent
if __name__=='__main__':
    raw=(R/'pg856_contract_test.py').read_text().replace('import pg856_sources as p','import pg856_sources_v2 as p')
    exec(compile(raw,'<856v2 actual namespace independent vectors>', 'exec'),globals())
