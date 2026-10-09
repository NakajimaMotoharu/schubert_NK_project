"""New-only old-current ABI/Werror/CLI compilation with nine private preservation roots."""
from pathlib import Path
from pg752_sources import bind

R=Path(__file__).resolve().parent


if __name__=='__main__':
    raw=bind((R/'pg717_compile.py').read_text()).replace('pg717_sources','pg752_sources')
    raw=raw.replace('pg716-completed-baseline-v1','pg751-completed-baseline-v1')
    exec(compile(raw,'<current completed21/next8d immutable compilation>','exec'),{'__file__':str(R/'pg752_compile.py'),'__name__':'__main__'})
