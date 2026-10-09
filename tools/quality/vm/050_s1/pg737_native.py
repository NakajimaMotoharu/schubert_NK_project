"""Separate verify then durable existing-only execute once; old inputs never replayed."""
from pathlib import Path
from pg737_sources import native

R=Path(__file__).resolve().parent
if __name__=='__main__':
    exec(compile(native(),'<current ADMIN new-only transport>','exec'),
         {'__file__':str(R/'pg737_native.py'),'__name__':'__main__'})
