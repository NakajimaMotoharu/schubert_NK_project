"""BUG1305 new-only graph: bind actual emitted bytes, not only composers."""
import inspect
import pg3490_outbox_owned_sources as previous

SOURCE = previous.SOURCE
BOM = previous.BOM
TOOLS = 'pg3520-outbox-owned-stop-tools-v2'
current = previous.current


def final_bind(raw):
    for old, new in [
        (previous.TOOLS, TOOLS),
        ('pg3494-outbox-owned-stage-v1', 'pg3524-outbox-owned-stage-v2'),
        ('pg3496-outbox-owned-post-v1', 'pg3526-outbox-owned-post-v2'),
        ('PG3496-outbox-owned-post-v1', 'PG3526-outbox-owned-post-v2'),
        ('pg3490', 'pg3520'), ('Pg3490', 'Pg3520'), ('PG3490', 'PG3520'),
        ('pg3492', 'pg3522'), ('pg3494', 'pg3524'), ('pg3495', 'pg3525'),
        ('pg3497', 'pg3527'), ('PG2654', 'PG3420'), ('pg2654', 'pg3420'),
        ('b2d6f605-61cf-425f-8fbd-12d606f6ee66', '79a3260a-e16d-42bf-942a-b914ed144c28'),
        ('b2d6f60561cf425f8fbd12d606f6ee66', '79a3260ae16d42bf942ab914ed144c28'),
    ]:
        raw = raw.replace(old, new)
    return raw


def bind(raw):
    # Composer input is Python. Final output may also be Java: never compile
    # Java as Python or omit final binding because a composer compiled cleanly.
    return final_bind(previous.bind(raw))


def candidate_bom():
    return BOM


def namespace():
    ns = {**previous.__dict__, 'TOOLS': TOOLS, 'bind': bind}
    exec(compile(inspect.getsource(previous.namespace), '<new v2 owned composer>', 'exec'), ns)
    return ns['namespace']()


def context():
    return namespace()['context']()


def sources():
    result = {final_bind(name): final_bind(raw) for name, raw in namespace()['sources']().items()}
    for raw in result.values():
        if any(old in raw for old in ['b2d6f605', 'pg2654', 'PG2654', 'pg3490', 'Pg3490']):
            raise ValueError('legacy role in actual v2 emitted output')
    return result
