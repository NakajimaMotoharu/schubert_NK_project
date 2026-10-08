"""One new immutable stage + owned stop for new normal cohort, not old replay."""
from pathlib import Path

R=Path(__file__).resolve().parent


def source():
    raw=(R/'pg642_native_stop.py').read_text()
    for old,new in (('PG640','PG653'),('pg640','pg653'),('pg641','pg654'),('pg642','pg655'),('Pg642','Pg655'),('PG642','PG655')):
        assert old in raw;raw=raw.replace(old,new)
    return raw


if __name__=='__main__':
    exec(compile(source(),str(R/'pg655_native_stop.py'),'exec'),{'__file__':str(R/'pg655_native_stop.py'),'__name__':'__main__'})
