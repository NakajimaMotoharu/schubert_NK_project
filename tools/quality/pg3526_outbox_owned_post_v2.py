"""Independent full post of new v2 normal owned stop."""
import inspect
import pg3496_outbox_owned_post as previous
import pg3520_outbox_owned_sources_v2 as role

SLOT = 'pg3526-outbox-owned-post-v2'


def namespace():
    ns = {**previous.__dict__, 'role': role, 'SLOT': SLOT}
    exec(compile(inspect.getsource(previous.namespace), '<v2 exact independent post composer>', 'exec'), ns)
    return ns['namespace']()


def entry():return namespace()['entry']()


if __name__ == '__main__':raise SystemExit(entry()())
