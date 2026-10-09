"""Fresh tools only after truecurrentDONE; frozen current748 ABI, VM mutation0."""
from pathlib import Path
from pg728_compile import source as previous
from pg761_current_binding import bind
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():return replace(bind(previous()),(('pg713-expiry-six-host-v1','pg748-closing-six-host-v1'),('pg715-release-v1','pg750-release-v1')))


if __name__=='__main__':
    exec(compile(source(),'<newcurrent stopcompile>','exec'),{'__file__':str(R/'pg764_compile.py'),'__name__':'__main__'})
