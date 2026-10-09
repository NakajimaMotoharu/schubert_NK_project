"""Immutable new proof-bound tools and one ordered owned stop, no reissue."""
from pathlib import Path
from pg692_retention_sources import replace

R=Path(__file__).resolve().parent


def source():
    return replace((R/'pg642_native_stop.py').read_text(),(
        ('PG640','PG693'),('pg640','pg693'),('pg641','pg694'),
        ('pg642','pg696'),('Pg642','Pg696'),('PG642','PG696'),
        ('0.1.0-PG631','0.1.0-PG682'),
    ))


if __name__=='__main__':
    exec(compile(source(),'<new current proof owned stop>','exec'),
         {'__file__':str(R/'pg696_native_stop.py'),'__name__':'__main__'})
