"""Actual fresh fifteen-source owned-stop ABI after full current seal; no Main rebuild."""
import pg2459_question_current_owned_compile as previous
from pg2554_strict_current_owned_sources import sources, context, SOURCE, TOOLS


def main():
    before, _, _, _ = context()
    engine = previous.prior.previous.prior.prior.prior.old.prior.prior
    raw = engine.compiler_source().replace('Pg1609', 'Pg2554').replace('pg1610', 'pg2555').replace(
        'pg1544-release-v1', 'pg2512-release-v1')
    ns = {**engine.prior.prior.__dict__, 'sources':sources, 'SOURCE':SOURCE,
          'BEFORE':before, 'TARGET':engine.prior.prior.W / TOOLS}
    exec(compile(raw, '<fresh whole owned ABI>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
