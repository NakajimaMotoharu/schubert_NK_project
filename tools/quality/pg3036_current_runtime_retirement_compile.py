"""Seventeen-source current held-FD retirement ABI; no guest action."""
import pg2393_current_runtime_retirement_compile as previous
from pg3034_current_runtime_retirement_sources import sources, SOURCE, SHA, TOOLS


def main():
    engine = previous.previous.previous.prior.prior.prior.old.prior.prior
    raw = engine.compiler_source().replace('Pg1609', 'Pg3034').replace('pg1610', 'pg3036').replace('pg1544-release-v1', 'pg2802-release-v1')
    ns = {**engine.prior.prior.__dict__, 'sources': sources, 'SOURCE': SOURCE, 'BEFORE': SHA, 'TARGET': engine.prior.prior.W / TOOLS}
    exec(compile(raw, '<actual current held-FD retirement ABI>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
