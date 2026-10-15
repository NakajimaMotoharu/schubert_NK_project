"""Independent new3699/542/1643/static6 proof; selected63 is not global acceptance."""
import inspect
import pg3250_cycle_group_full_qualified as previous
from pg3258_statement_group_full_six import SOURCE, validate


def server():
    raw = previous.server().replace('PG3248', 'PG3258').replace('3697', '3699').replace("'batch':(1297,173,568)", "'batch':(1299,173,568)")
    if "'batch':(1299,173,568)" not in raw: raise ValueError('exact batch1299 expected')
    compile(raw, '<independent3699 all-source qualification>', 'exec'); return raw


def main():
    raw = inspect.getsource(previous.main).replace('pg3250-cycle-group-full-qualified-v1', 'pg3260-statement-group-full-qualified-v1').replace('pg3248-server-six-v1', 'pg3258-server-six-v1').replace('PG3248', 'PG3258')
    ns = {**previous.__dict__, 'SOURCE': SOURCE, 'validate': validate, 'server': server}
    exec(compile(raw, '<independent3699 transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
