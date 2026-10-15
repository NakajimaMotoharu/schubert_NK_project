"""Independent all3691/542/1643/static6 qualification; old3685 remains historical."""
import inspect
import pg2800_jdbc_null_fixed_full_qualified as engine
import pg3028_extra_row_full_qualified as previous
from pg3054_boundary_group_full_six import SOURCE, validate


def server():
    raw = previous.server().replace('PG3026', 'PG3054').replace('3685', '3691').replace("'batch':(1285,173,568)", "'batch':(1291,173,568)")
    if "'batch':(1291,173,568)" not in raw:
        raise ValueError('exact batch1285 plus six method count required')
    compile(raw, '<all3691 exact independent qualification>', 'exec')
    return raw


def main():
    raw = inspect.getsource(engine.main).replace('pg2800-jdbc-null-fixed-full-qualified-v1', 'pg3056-boundary-group-full-qualified-v1').replace('pg2798-server-six-v1', 'pg3054-server-six-v1').replace('PG2798', 'PG3054')
    ns = {**engine.__dict__, 'SOURCE': SOURCE, 'validate': validate, 'server': server}
    exec(compile(raw, '<whole3691 independent XML/source/static>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
