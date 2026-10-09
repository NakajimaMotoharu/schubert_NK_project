"""Current758 sameRootDONE/A01, one orderedTERM only; no oldstop reuse."""
from pathlib import Path
from pg728_native_stop import source as previous
from pg761_current_binding import bind

R=Path(__file__).resolve().parent


def source():return bind(previous())


if __name__=='__main__':
    exec(compile(source(),'<current758 ownedstop>','exec'),{'__file__':str(R/'pg764_native_stop.py'),'__name__':'__main__'})
