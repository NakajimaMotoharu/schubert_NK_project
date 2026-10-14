"""New-only corrected graph stage/finite prepare; preserve failed2954 slot."""
import inspect
import pg2954_current_cold_resume_dispatch as prior
from pg2970_current_resume_sources import namespace, sources, TOOLS, CLASS, SOURCE, BOM
from pg2972_current_resume_compile import TARGET

REMOTE = '/home/ubuntu/pg2974-fixed-stage-v1'
GUEST = '/var/lib/pgpt-s1-preservation/' + TOOLS


def bind(raw):
    return namespace(raw).replace('pg2954', 'pg2974').replace('pg2952', 'pg2972')


STAGE = bind(prior.STAGE)


def source():
    return bind(prior.source())


def main():
    raw = inspect.getsource(prior.prior.main)
    ns = {**prior.prior.__dict__, 'bind': bind, 'sources': sources, 'TOOLS': TOOLS, 'CLASS': CLASS, 'SOURCE': SOURCE, 'BOM': BOM, 'TARGET': TARGET, 'REMOTE': REMOTE, 'GUEST': GUEST, 'STAGE': STAGE, 'source': source}
    exec(compile(raw, '<corrected current closed stage dispatch>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
