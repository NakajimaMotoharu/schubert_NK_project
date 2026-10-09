"""New only ADMIN compile after current736, no VM action or changed production."""
from pathlib import Path
from pg737_sources import current

R=Path(__file__).resolve().parent
if __name__=='__main__':
    raw=current((R/'pg662_compile.py').read_text().replace('pg662','pg664').replace('Pg662','Pg664'))
    exec(compile(raw,'<new current signed ADMIN tooling>', 'exec'),
         {'__file__':str(R/'pg737_compile.py'),'__name__':'__main__'})
