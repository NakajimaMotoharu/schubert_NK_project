"""Immutable current751/next750 transport and distinct code-only verify/activate, no startup."""
from pathlib import Path
from pg752_sources import bind

R=Path(__file__).resolve().parent


def source():
    from pg717_native import source as previous
    return bind(previous()).replace('pg752-frozen-v1.safe.json','pg752-frozen-v2.safe.json')


if __name__=='__main__':
    exec(compile(source(),'<current751/new750 immutable transport>', 'exec'),{'__file__':str(R/'pg752_native.py'),'__name__':'__main__'})
