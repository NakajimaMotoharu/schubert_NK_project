"""Shared unchanged Current A01 oracle on PG722 sameRoot/source; QA051 not A01."""
from pathlib import Path
from pg694_a01_current import code as previous
from pg724_retention_sources import bind
from pg662_sources import replace

R=Path(__file__).resolve().parent


def code():
    return replace(bind(previous()), (
        ('PG694-native-a01-v1','PG726-native-a01-v1'),
        ('pg694-chr-a01-native-v1','pg726-chr-a01-native-v1'),
    ))


if __name__=='__main__':
    env={'__file__':str(R/'pg726_a01_current.py'),'__name__':'new_sameRoot_a01'}
    exec(compile(code(),'<Current unchanged A01>', 'exec'),env);env['main']()
