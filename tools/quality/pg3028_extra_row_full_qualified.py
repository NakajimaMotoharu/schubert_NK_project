"""Exact new3685/542/1643 independent qualification, old3684 remains historical."""
import inspect
import pg2932_format_fixed_full_qualified as previous
from pg3026_extra_row_full_six import SOURCE, validate


def server():
    raw = previous.server().replace('PG2930', 'PG3026').replace('3684', '3685').replace("'batch':(1284,173,568)", "'batch':(1285,173,568)")
    if "'batch':(1285,173,568)" not in raw:
        raise ValueError('exact one additional batch method required')
    return raw


def main():
    raw = inspect.getsource(previous.prior.main).replace('pg2920-db-failure-group-full-qualified-v1', 'pg3028-extra-row-full-qualified-v1').replace('pg2918-server-six-v1', 'pg3026-server-six-v1').replace('PG2918', 'PG3026')
    ns = {**previous.prior.__dict__, 'SOURCE': SOURCE, 'validate': validate, 'server': server}
    exec(compile(raw, '<actual new whole3685 independent qualification>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
