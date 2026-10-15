"""Independent exact3694/542/1643/static-six0, never selected-result addition."""
import inspect
import pg3056_boundary_group_full_qualified as previous
from pg3204_expiry_group_full_six import SOURCE, validate


def server():
    raw = previous.server().replace('PG3054', 'PG3204').replace('3691', '3694').replace("'batch':(1291,173,568)", "'batch':(1294,173,568)")
    if "'batch':(1294,173,568)" not in raw:
        raise ValueError('exact batch1294 required')
    compile(raw, '<independent new3694 XML and static qualification>', 'exec')
    return raw


def main():
    raw = inspect.getsource(previous.main).replace('pg3056-boundary-group-full-qualified-v1', 'pg3206-expiry-group-full-qualified-v1').replace('pg3054-server-six-v1', 'pg3204-server-six-v1').replace('PG3054', 'PG3204')
    ns = {**previous.__dict__, 'SOURCE': SOURCE, 'validate': validate, 'server': server}
    exec(compile(raw, '<whole3694 source and all-scope independent qualification>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
