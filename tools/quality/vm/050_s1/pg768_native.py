"""Current source newimmutable ADMIN verify then oneexecute, pairmarkerrequired."""
from pathlib import Path
from pg768_sources import native

R=Path(__file__).resolve().parent


if __name__=='__main__':
    exec(compile(native(),'<current pairADMIN immutable>','exec'),{'__file__':str(R/'pg768_native.py'),'__name__':'__main__'})
