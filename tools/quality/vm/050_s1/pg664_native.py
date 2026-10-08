"""New-only fixed SSC231 existing ADMIN verify→durable one execute."""
from pathlib import Path
from pg664_sources import native

R=Path(__file__).resolve().parent
if __name__=='__main__':
    exec(compile(native(),str(R/'pg664_native.py'),'exec'),{'__file__':str(R/'pg664_native.py'),'__name__':'__main__'})
