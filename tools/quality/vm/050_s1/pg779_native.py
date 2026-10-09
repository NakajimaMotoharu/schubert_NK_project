"""Distinct actual779 stage/verify/recover, old778 stage/failure are never replayed."""
from pathlib import Path
from pg779_sources import bind

R=Path(__file__).resolve().parent


if __name__=='__main__':
    exec(compile(bind((R/'pg778_native.py').read_text()),'<new779 actual transport>','exec'),{'__file__':str(R/'pg779_native.py'),'__name__':'__main__'})
