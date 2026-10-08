"""Compile immutable new normal owned-stop tools only after genuine PG653."""
from pathlib import Path

R=Path(__file__).resolve().parent


def source():
    raw=(R/'pg642_compile.py').read_text()
    for old,new in (('PG640','PG653'),('pg640','pg653'),('pg642','pg655'),('Pg642','Pg655')):
        assert old in raw;raw=raw.replace(old,new)
    return raw


if __name__=='__main__':
    exec(compile(source(),str(R/'pg655_compile.py'),'exec'),{'__file__':str(R/'pg655_compile.py'),'__name__':'__main__'})
