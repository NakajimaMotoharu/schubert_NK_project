"""New observer-first PG682 campaign, unchanged generation/identity/readiness logic."""
from pathlib import Path

R=Path(__file__).resolve().parent


def watch():
    raw=(R/'pg638_watch_parent.py').read_text();assert 'PG631'in raw
    return raw.replace('PG631','PG682')


def source():
    raw=(R/'pg638_observer.py').read_text()
    for old,new in (
        ('pg638','pg691'),('PG637','PG690'),('pg637-prepare-v2','pg690-prepare-v1'),
        ('pg637-fresh-resume-v2','pg690-fresh-parent-v1'),('PG631','PG682'),
        ('36fe7a0b938489d61d17d49c1c30a6fbbef699d5','9bd50536f692610036a0ed8b83e0a8b35fe2a66f'),
        ('57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe','076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480'),
    ):
        assert old in raw,old;raw=raw.replace(old,new)
    old="files={name:(R/name).read_bytes()for name in ('pg691_watch_parent.py','pg554_stable_actor.py','pg462_observer_identity.py')}"
    assert raw.count(old)==1
    return raw.replace(old,"files={name:(watch().encode()if name=='pg691_watch_parent.py'else(R/name).read_bytes())for name in ('pg691_watch_parent.py','pg554_stable_actor.py','pg462_observer_identity.py')}")


if __name__=='__main__':
    exec(compile(source(),'<new source observer>','exec'),
         {'__file__':str(R/'pg691_observer.py'),'__name__':'__main__','watch':watch})
