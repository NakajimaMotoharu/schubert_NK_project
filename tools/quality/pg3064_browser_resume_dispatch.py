"""New-only finite Browser-run preparation; not permission to start Root before readiness."""
import types
import pg2974_current_resume_dispatch as previous
from pg3060_browser_resume_sources import bind as positive_bind, sources, TOOLS, CLASS, SOURCE, BOM
from pg3062_browser_resume_compile import TARGET

REMOTE = '/home/ubuntu/pg3064-fixed-stage-v1'
GUEST = '/var/lib/pgpt-s1-preservation/' + TOOLS


def bind(raw):
    return positive_bind(raw).replace('pg2974', 'pg3064').replace('pg2972', 'pg3062')


STAGE = bind(previous.STAGE)


def source():
    return bind(previous.source())


def main():
    fn = previous.main
    ns = {**fn.__globals__, 'bind': bind, 'sources': sources, 'TOOLS': TOOLS, 'CLASS': CLASS, 'SOURCE': SOURCE, 'BOM': BOM, 'TARGET': TARGET, 'REMOTE': REMOTE, 'GUEST': GUEST, 'STAGE': STAGE, 'source': source}
    return types.FunctionType(fn.__code__, ns, 'latest_browser_resume_dispatch')()


if __name__ == '__main__':
    raise SystemExit(main())
