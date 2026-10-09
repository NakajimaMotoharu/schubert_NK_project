"""New-only stop compile only after actual current genuine DONE; VM mutations0."""
from pathlib import Path
from pg696_compile import source as previous
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():
    return replace(previous(), (
        ('pg696','pg728'),('Pg696','Pg728'),('pg693','pg725'),('PG693','PG725'),
        ('pg680-owner-six-host-v1','pg713-expiry-six-host-v1'),('pg682-release-v1','pg715-release-v1'),
    ))


if __name__=='__main__':
    exec(compile(source(),'<new current ABI ownedstop>', 'exec'),
         {'__file__':str(R/'pg728_compile.py'),'__name__':'__main__'})
