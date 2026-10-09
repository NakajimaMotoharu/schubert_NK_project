"""Fresh proof-bound owned-stop tools: one ordered TERM after DONE and current A01."""
from pathlib import Path
from pg696_native_stop import source as previous
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():
    return replace(previous(), (
        ('pg696','pg728'),('Pg696','Pg728'),('PG696','PG728'),
        ('pg693','pg725'),('PG693','PG725'),('pg694','pg726'),
        ('0.1.0-PG682','0.1.0-PG715'),
    ))


if __name__=='__main__':
    exec(compile(source(),'<current source ownedstop>', 'exec'),
         {'__file__':str(R/'pg728_native_stop.py'),'__name__':'__main__'})
