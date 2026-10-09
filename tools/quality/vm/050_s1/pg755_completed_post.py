"""Independent fresh full21 post for current751/next750, no mutation/operation replay."""
from pathlib import Path
from pg752_sources import bind
from pg719_post_v2 import source as previous
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():
    return replace(bind(previous()),(
        ('pg719','pg755'),("'PG682'if MODE=='verify'else'PG715'", "'PG715'if MODE=='verify'else'PG750'"),
        ("'batchRows':524","'batchRows':534"),
    ))


if __name__=='__main__':
    env={'__file__':str(R/'pg755_completed_post.py'),'__name__':'fresh_full21_readonly'}
    exec(compile(source(),'<current751/next750 independent post>','exec'),env);env['main']()
