"""Independent exact3697/542/1643/FES0/static6, not selected-count addition."""
import inspect
import pg3206_expiry_group_full_qualified as previous
from pg3248_cycle_group_full_six import SOURCE, validate


def server():
    raw = previous.server().replace('PG3204', 'PG3248').replace('3694', '3697').replace("'batch':(1294,173,568)", "'batch':(1297,173,568)")
    if "'batch':(1297,173,568)" not in raw: raise ValueError('exact independent batch1297 required')
    compile(raw, '<independent all3697 input/source/XML/static proof>', 'exec')
    return raw


def main():
    raw = inspect.getsource(previous.main).replace('pg3206-expiry-group-full-qualified-v1', 'pg3250-cycle-group-full-qualified-v1').replace('pg3204-server-six-v1', 'pg3248-server-six-v1').replace('PG3204', 'PG3248')
    ns = {**previous.__dict__, 'SOURCE': SOURCE, 'validate': validate, 'server': server}
    exec(compile(raw, '<independent whole3697 transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
