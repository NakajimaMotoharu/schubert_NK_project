"""Read-only same-generation a2ecc Root identity, no old owner inheritance."""
import inspect
import pg4894_new_normal_live_binding as previous
import pg5022_new_normal_root_once as entry
from pg4996_resume_connection import authenticate_host

SLOT = 'pg5024-new-normal-live-binding-v1'
SOURCE, BOM, ONCE = entry.SOURCE, entry.BOM, entry.SLOT


def body():
    return entry.observer.bind(previous.body()).replace(previous.ONCE, ONCE)


def main():
    authenticate_host()
    template = previous.previous.previous
    ns = {**vars(template), 'SLOT': SLOT, 'SOURCE': SOURCE, 'BOM': BOM, 'ONCE': ONCE, 'body': body}
    exec(compile(inspect.getsource(template.main), '<fresh a2ecc same-current binding>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
