"""BUG923: new readonly receipt slot; preserve v1, never replay deployment."""
from pathlib import Path
from pg719_completed_post import source as previous
from pg662_sources import replace

R = Path(__file__).resolve().parent


def source():
    return replace(previous(), (("'batchRows':514", "'batchRows':524"),
                               ("'pg719-'+mode+'-post-v1'", "'pg719-'+mode+'-post-v2'")))


if __name__ == '__main__':
    env = {'__file__': str(R / 'pg719_post_v2.py'), '__name__': 'readonly_post_v2'}
    exec(compile(source(), '<new readonly reported count consistency>', 'exec'), env)
    env['main']()
