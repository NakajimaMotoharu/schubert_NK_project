"""One new772 readonly failure capture after full namespace tests; old771 remainsfailed."""
from pathlib import Path
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():
    raw=(R/'pg771_failure_capture.py').read_text().replace('pg771-failure-current758-v1','pg772-failure-current758-v1')
    return replace(raw,(('import ast,hashlib,json,os,pathlib,subprocess,time','import ast,hashlib,json,os,pathlib,stat,subprocess,time\ndef require(value):\n if not value:raise ValueError("current failure readonly namespace refused")'),))


if __name__=='__main__':
    exec(compile(source(),'<newreadonly772 fullnamespace>','exec'),{'__file__':str(R/'pg772_failure_capture.py'),'__name__':'__main__'})
