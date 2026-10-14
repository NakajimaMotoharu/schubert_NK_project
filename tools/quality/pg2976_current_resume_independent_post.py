"""Independent new-only corrected preparation post; old failed family not accepted."""
import inspect
import pg2956_current_resume_independent_post as previous
from pg2970_current_resume_sources import SAVE, RUN

SLOT = 'pg2976-current-resume-independent-post-v1'
ORACLE = previous.ORACLE.replace('pg2950', 'pg2970')


def namespace():
    ns = {**previous.__dict__, 'SLOT': SLOT, 'ORACLE': ORACLE, 'SAVE': SAVE, 'RUN': RUN}
    for fn in [previous.payload, previous.entry]:
        raw = inspect.getsource(fn).replace('pg2950', 'pg2970').replace('pg2954', 'pg2974').replace('PG2956', 'PG2976')
        exec(compile(raw, '<corrected current literal post>', 'exec'), ns)
    return ns


def payload(seals):
    return namespace()['payload'](seals)


def entry():
    return namespace()['entry']()


if __name__ == '__main__':
    raise SystemExit(entry()())
