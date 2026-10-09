"""Observer-first sameRoot route on current PG715; never start a second parent."""
from pathlib import Path
from pg691_observer import source as previous, watch as previous_watch
from pg662_sources import replace

R = Path(__file__).resolve().parent


def watch():
    return replace(previous_watch(), (('PG682','PG715'),))


def source():
    return replace(previous(), (
        ('pg691','pg723'), ('PG690','PG722'), ('pg690','pg722'), ('PG682','PG715'),
        ('9bd50536f692610036a0ed8b83e0a8b35fe2a66f','1ec19782a1afe22d1de75b05f4cd12b8a8a8a172'),
        ('076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480','74d35361865a32a6b992f93d78d42844e20a5bb286fa4fc4b5e74520fa6305d5'),
    ))


if __name__ == '__main__':
    exec(compile(source(), '<new current source observer>', 'exec'),
         {'__file__': str(R / 'pg723_observer.py'), '__name__': '__main__','watch':watch})
