"""Current baseline unchanged; current758 sameRoot A01 only, noL01 approval."""
from pathlib import Path
from pg726_a01_current import code as previous
from pg761_current_binding import bind

R=Path(__file__).resolve().parent


def code():return bind(previous())


if __name__=='__main__':
    env={'__file__':str(R/'pg762_a01_current.py'),'__name__':'current758_A01'}
    exec(compile(code(),'<unchangedCurrent actual750>','exec'),env);env['main']()
