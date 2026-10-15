"""New-only all11-key corrected finite preparation, no external Root start."""
import types
import pg3084_retained_parent_dispatch as previous
from pg3100_full_native_resume_sources import bind as source_bind, sources, TOOLS, CLASS, SOURCE, BOM
from pg3102_full_native_resume_compile import TARGET

REMOTE = '/home/ubuntu/pg3104-fixed-stage-v1'
GUEST = '/var/lib/pgpt-s1-preservation/' + TOOLS


def bind(raw):
    return source_bind(raw).replace('pg3084', 'pg3104').replace('pg3082', 'pg3102')


STAGE = bind(previous.STAGE)


def source():
    return bind(previous.source())


def main():
    fn = previous.main
    return types.FunctionType(fn.__code__, {**fn.__globals__, 'bind': bind, 'sources': sources, 'TOOLS': TOOLS, 'CLASS': CLASS, 'SOURCE': SOURCE, 'BOM': BOM, 'TARGET': TARGET, 'REMOTE': REMOTE, 'GUEST': GUEST, 'STAGE': STAGE, 'source': source}, 'full_native_fixed_dispatch')()


if __name__ == '__main__':
    raise SystemExit(main())
