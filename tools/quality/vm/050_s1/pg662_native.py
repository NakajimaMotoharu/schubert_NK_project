"""SSC231 new immutable verify then one existing-only ADMIN execute."""
from pathlib import Path
from pg662_sources import native

R=Path(__file__).resolve().parent
if __name__=='__main__':
    exec(compile(native(),str(R/'pg662_native.py'),'exec'),{'__file__':str(R/'pg662_native.py'),'__name__':'__main__'})
