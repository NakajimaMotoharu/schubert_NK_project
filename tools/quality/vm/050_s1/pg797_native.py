"""New immutable stage and exactly one75s readonly verify; no recover/start/deploy mode."""
from pathlib import Path
from pg797_sources import bind

R=Path(__file__).resolve().parent


if __name__=='__main__':
    import sys
    assert sys.argv[1:]in (['stage'],['verify'])
    raw=bind((R/'pg778_native.py').read_text().replace('Pg778FailedRecovery','Pg783ExistingPairRetirement').replace('pg778','pg783').replace('PG778','PG783')).replace('pg797-failed758-tools-v1','pg797-liveness-tools-v1')
    exec(compile(raw,'<new797 readonly75s actual stage verify>','exec'),{'__file__':str(R/'pg797_native.py'),'__name__':'__main__'})
