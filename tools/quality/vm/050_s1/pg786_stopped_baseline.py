"""Separate readonly capture after785 independent refusal vectors actually pass."""
from pathlib import Path
from pg785_stopped_baseline import source as prior

R=Path(__file__).resolve().parent


if __name__=='__main__':
    raw=prior().replace('pg785-stopped-current-v1','pg786-stopped-current-v1')
    exec(compile(raw,'<new786 stopped current fixedprofile>','exec'),{'__file__':str(R/'pg786_stopped_baseline.py'),'__name__':'__main__'})
