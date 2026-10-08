"""Fresh PG672v2 qualification; no repeated failure slot or quality skip."""
from pathlib import Path
import sys
from pg673_collect_full import source as prior

R=Path(__file__).resolve().parent


def source():
    raw=prior();assert 'pg672-entry-six-host-v1' in raw
    return raw.replace('pg672-entry-six-host-v1','pg672-entry-six-host-v2')


if __name__=='__main__':
    assert len(sys.argv)==2
    env={'__name__':'current_frozen_full','__file__':str(R/'pg674_collect_full.py')}
    exec(compile(source(),'<six reactor v2 independent qualification>','exec'),env);env['main'](sys.argv[1],'PG630')
