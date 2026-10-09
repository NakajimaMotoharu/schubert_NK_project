"""Separate stage/verify/recover new-only. Failed old scope never normalized."""
from pathlib import Path
import ast
import pg813_native as previous
from pg856_sources import bind
R=Path(__file__).resolve().parent
if __name__=='__main__':
    raw=bind(previous.source());ast.parse(raw)
    exec(compile(raw,'<856 exact completed-failed recovery>','exec'),{'__file__':str(R/'pg856_native.py'),'__name__':'__main__'})
