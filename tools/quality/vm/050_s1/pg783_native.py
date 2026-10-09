"""Actual new783 existing-only stage/verify/retire under fresh ownership, never old recovery."""
from pathlib import Path
from pg783_sources import bind

R=Path(__file__).resolve().parent


if __name__=='__main__':
    raw=(R/'pg778_native.py').read_text().replace('Pg778FailedRecovery','Pg779FailedRecovery').replace('pg778','pg779').replace('PG778','PG779')
    raw=bind(raw).replace('pg783-failed758-tools-v1','pg783-existing-pair-tools-v1')
    exec(compile(raw,'<new783 existing-only normal scopes>','exec'),{'__file__':str(R/'pg783_native.py'),'__name__':'__main__'})
