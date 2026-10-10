"""BUG1000: one Morning yields Backup2+Cleanup8 batch rows; fresh-only readonly v2."""
import ast
from pathlib import Path
from pg978_current_bootstrap_before import source as previous
R=Path(__file__).resolve().parent
def source():
    raw=previous();assert raw.count('==594')==1
    raw=raw.replace('pg978-bootstrap-before-v1','pg978-bootstrap-before-v2').replace('PG978-bootstrap-before-v1','PG978-bootstrap-before-v2')
    ast.parse(raw);return raw
if __name__=='__main__':
    exec(compile(source(),'<981 independent current before v2>','exec'),{'__file__':str(R/'pg981_current_bootstrap_before_v2.py'),'__name__':'__main__'})
