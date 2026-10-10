"""BUG1000: one Morning yields Backup2+Cleanup8 batch rows; fresh-only readonly v2."""
import ast
from pathlib import Path
from pg978_current_bootstrap_before import source as previous
R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
def namespace():
    env={'__file__':str(R/'pg981_current_bootstrap_before_v2.py'),'__name__':'current_readonly_before_definitions'}
    exec(compile(source(),'<981 composed before definitions>','exec'),env);return env
def payload(proof,seals):return namespace()['payload'](proof,seals)
def source():
    raw=previous();assert raw.count('==594')==1
    raw=raw.replace('pg978-bootstrap-before-v1','pg978-bootstrap-before-v2').replace('PG978-bootstrap-before-v1','PG978-bootstrap-before-v2')
    ast.parse(raw);return raw
if __name__=='__main__':
    exec(compile(source(),'<981 independent current before v2>','exec'),{'__file__':str(R/'pg981_current_bootstrap_before_v2.py'),'__name__':'__main__'})
