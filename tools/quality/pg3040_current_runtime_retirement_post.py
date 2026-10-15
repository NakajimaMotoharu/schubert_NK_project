"""Independent exact runtime-only/config delta plus all raw data/native/resources post."""
import inspect
import pg2398_current_runtime_retirement_post as previous
import pg3012_current_resume_owned_post as stopped
from pg3034_current_runtime_retirement_sources import contract_source, SOURCE, TOOLS, SHA, BASE

SLOT = 'pg3040-current-runtime-retirement-post-v1'


def namespace():
    ns = {**previous.__dict__, 'previous': stopped, 'contract_source': contract_source, 'SOURCE': SOURCE, 'TOOLS': TOOLS, 'SHA': SHA, 'BASE': BASE, 'SLOT': SLOT}
    for fn in [previous.payload, previous.main]:
        raw = inspect.getsource(fn)
        for a, b in [('pg2374', 'pg3006'), ('Pg2374', 'Pg3006'), ('pg2392', 'pg3034'), ('Pg2392', 'Pg3034'), ('PG2380-current-resume-owned-post-v1', 'PG3012-current-resume-owned-post-v1'), ('PG2398-current-runtime-retirement-post-v1', 'PG3040-current-runtime-retirement-post-v1'), ('pg2394', 'pg3038'), ('pg2393', 'pg3036')]:
            raw = raw.replace(a, b)
        exec(compile(raw, '<current exact independent runtime post>', 'exec'), ns)
    return ns


def payload(seals):
    return namespace()['payload'](seals)


def main():
    return namespace()['main']()


if __name__ == '__main__':
    raise SystemExit(main())
