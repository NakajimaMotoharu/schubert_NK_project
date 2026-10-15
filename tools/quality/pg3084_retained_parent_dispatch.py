"""New-only corrected retained-parent finite prepare, no Root/business start."""
import types
import pg3064_browser_resume_dispatch as previous
from pg3080_retained_parent_resume_sources import bind as normal_bind, sources, TOOLS, CLASS, SOURCE, BOM
from pg3082_retained_parent_compile import TARGET

REMOTE = '/home/ubuntu/pg3084-fixed-stage-v1'
GUEST = '/var/lib/pgpt-s1-preservation/' + TOOLS


def bind(raw):
    return normal_bind(raw).replace('pg3064', 'pg3084').replace('pg3062', 'pg3082')


STAGE = bind(previous.STAGE)


def source():
    return bind(previous.source())


def main():
    fn = previous.main
    return types.FunctionType(fn.__code__, {**fn.__globals__, 'bind': bind, 'sources': sources, 'TOOLS': TOOLS, 'CLASS': CLASS, 'SOURCE': SOURCE, 'BOM': BOM, 'TARGET': TARGET, 'REMOTE': REMOTE, 'GUEST': GUEST, 'STAGE': STAGE, 'source': source}, 'retained_parent_fixed_dispatch')()


if __name__ == '__main__':
    raise SystemExit(main())
