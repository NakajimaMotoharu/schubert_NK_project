"""Actual current4856 owned graph, admitted only from same-source terminal/whole/parent18."""
import inspect
import pg2708_operation_owned_sources as old
import pg3472_outbox_acceptance as current

SOURCE = current.SOURCE
BOM = current.BOM
TOOLS = 'pg3490-outbox-owned-stop-tools-v1'


def candidate_bom():
    return BOM


def bind(raw):
    raw = current.bind(old.bind(raw))
    for a, b in [(old.TOOLS, TOOLS), ('pg2706-operation-current-parent-projection-v1', 'pg3478-outbox-parent-projection-v1'),
                 ('pg2712-operation-owned-stage-v1', 'pg3494-outbox-owned-stage-v1'),
                 ('pg2716-operation-owned-post-v1', 'pg3496-outbox-owned-post-v1'),
                 ('PG2716-operation-owned-post-v1', 'PG3496-outbox-owned-post-v1'),
                 ('pg2708', 'pg3490'), ('Pg2708', 'Pg3490'), ('PG2708', 'PG3490'),
                 ('pg2710', 'pg3492'), ('pg2712', 'pg3494'), ('pg2713', 'pg3495'), ('pg2714', 'pg3497')]:
        raw = raw.replace(a, b)
    return raw


def namespace():
    raw = inspect.getsource(old.namespace)
    ns = {**old.__dict__, 'SOURCE': SOURCE, 'TOOLS': TOOLS, 'bind': bind,
          'terminal_payload': lambda binding, bom=None: current.terminal_payload(binding),
          'candidate_bom': candidate_bom}
    exec(compile(raw, '<new source same sealed owned graph namespace>', 'exec'), ns)
    return ns['namespace']()


def context():
    return namespace()['context']()


def sources():
    return namespace()['sources']()


if __name__ == '__main__':
    raise SystemExit('factory only; no operation')
