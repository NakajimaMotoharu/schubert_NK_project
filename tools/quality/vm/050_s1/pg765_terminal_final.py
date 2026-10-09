"""Independent current758 fullpost/24rows/resources, no secondSTOP."""
from pathlib import Path
from pg729_terminal_final import source as previous
from pg761_current_binding import bind
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():return replace(bind(previous()),(('pg715-manifest.sig','pg750-manifest.sig'),))


if __name__=='__main__':
    exec(compile(source(),'<current750 independentpost>','exec'),{'__file__':str(R/'pg765_terminal_final.py'),'__name__':'__main__'})
