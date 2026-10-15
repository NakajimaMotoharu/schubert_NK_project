"""Host-only candidate RO ABI; completed current a9 and unused4856 remain separate."""
import inspect

import pg2667_operation_ro_compile as old
import pg3442_current_outbox_ro_sources as role

TARGET = role.W / role.TOOLS


def compiler():
    raw = role.bind(old.compiler())
    for before, after in [('pg2667-', 'pg3444-'), ('pg2659-frozen', 'pg3436-frozen'),
                          ('pg2658-operation-unused-tools-v1', 'pg3434-current-outbox-unused-tools-v1'),
                          ('Pg2658', 'Pg3434'), ('pg2658', 'pg3434'),
                          ('pg2664-operation-unused-post-v1', 'pg3440-current-outbox-unused-independent-post-v1')]:
        raw = raw.replace(before, after)
    compile(raw, '<same candidate RO full host ABI>', 'exec')
    return raw


def main():
    role.qualify()
    engine = old.previous.previous.prior.prior.prior
    namespace = {**engine.__dict__, 'TARGET': TARGET, 'TOOLS': role.TOOLS, 'sources': role.sources,
                 'CANDIDATE': role.role.SOURCE, 'OLD': role.role.CURRENT, 'BEFORE': role.role.BEFORE}
    exec(compile(inspect.getsource(engine.write), '<canonical RO writer>', 'exec'), namespace)
    exec(compile(compiler(), '<new RO host ABI entry>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
