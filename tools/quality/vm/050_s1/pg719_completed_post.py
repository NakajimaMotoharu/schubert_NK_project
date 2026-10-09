"""Independent full21 readonly after new717 finite update; no operation authority."""
from pathlib import Path
from pg687_completed_post import source as previous
from pg717_sources import bind
from pg662_sources import replace

R = Path(__file__).resolve().parent


def source():
    return replace(bind(previous()), (
        ('pg687', 'pg719'),
        ("'PG631'if MODE=='verify'else'PG682'", "'PG682'if MODE=='verify'else'PG715'"),
        ("'pg664-bootstrap-existing-v1')", "'pg664-bootstrap-existing-v1','pg702-bootstrap-tools-v1','pg702-bootstrap-verify-v1','pg702-bootstrap-existing-v1')"),
    ))


if __name__ == '__main__':
    env = {'__file__': str(R / 'pg719_completed_post.py'), '__name__': 'new_completed_post_only'}
    exec(compile(source(), '<independent new finite21 post>', 'exec'), env); env['main']()
