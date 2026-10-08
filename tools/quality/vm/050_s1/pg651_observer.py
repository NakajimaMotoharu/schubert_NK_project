"""Readonly current observer in new immutable campaign slot; no unit action."""
from pathlib import Path

R=Path(__file__).resolve().parent


def source():
    raw=(R/'pg638_observer.py').read_text()
    for old,new in (('PG637','PG650'),('pg638','pg651'),('pg637-prepare-v2','pg650-prepare-v1'),('pg637-fresh-resume-v2','pg650-fresh-parent-v1')):
        assert old in raw;raw=raw.replace(old,new)
    old="files={name:(R/name).read_bytes()for name in ('pg651_watch_parent.py','pg554_stable_actor.py','pg462_observer_identity.py')}"
    new="files={name:(R/('pg638_watch_parent.py'if name=='pg651_watch_parent.py'else name)).read_bytes()for name in ('pg651_watch_parent.py','pg554_stable_actor.py','pg462_observer_identity.py')}"
    assert raw.count(old)==1;raw=raw.replace(old,new)
    return raw


if __name__=='__main__':
    exec(compile(source(),str(R/'pg651_observer.py'),'exec'),{'__file__':str(R/'pg651_observer.py'),'__name__':'__main__'})
