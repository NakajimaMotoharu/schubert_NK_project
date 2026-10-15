"""Host-only full warm unused graph ABI against currenta9; never stages/places/starts."""
import inspect
import types

import pg2659_operation_candidate_compile as old
import pg3434_current_outbox_candidate_sources as role

TARGET = role.W / role.TOOLS
ARCHIVE = old.previous.graph.engine.P / role.ARCHIVE


def bind(raw):
    for before, after in [('pg2654', 'pg3420'), ('PG2654', 'PG3420'),
                          ('pg2656-current-a79-before-v1', 'pg3432-current-a9-before-view-v2'),
                          ('pg2658', 'pg3434'), ('Pg2658', 'Pg3434'), ('PG2658', 'PG3434'),
                          ('pg2659', 'pg3436'), ('PG2659', 'PG3436'),
                          ('pg2555-frozen-v1', 'pg3152-frozen-v1'),
                          ('pg2554-strict-current-owned-stop-tools-v1', 'pg3150-browser-business-owned-stop-tools-v1'),
                          ('Pg2554', 'Pg3150'), ('pg2554', 'pg3150'), ('pg2512-release-v1', 'pg2802-release-v1')]:
        raw = raw.replace(before, after)
    return raw


def compiler():
    raw = bind(old.compiler())
    compile(raw, '<new candidate full host ABI only>', 'exec')
    return raw


def validate_actual_graph(target, hashes):
    original = old.previous.graph
    raw = inspect.getsource(original.validate_actual_graph).replace('pg2132', 'pg3434').replace('pg2126-manifest-v1.sig', 'pg3420-manifest-v1.sig')
    namespace = {**original.__dict__, 'ARCHIVE': ARCHIVE}
    exec(compile(raw, '<actual warm candidate graph fixed bundle>', 'exec'), namespace)
    return namespace['validate_actual_graph'](target, hashes)


def main():
    role.qualify()
    graph = old.previous.graph
    namespace = {**graph.engine.__dict__, '__file__': __file__, 'TARGET': TARGET, 'ARCHIVE': ARCHIVE,
                 'TOOLS': role.TOOLS, 'CURRENT': role.CURRENT, 'PRODUCTION': role.SOURCE, 'BEFORE': role.BEFORE,
                 'sources': role.sources, 'validate_actual_graph': validate_actual_graph, 'inventory': graph.inventory}
    namespace['write'] = types.FunctionType(graph.write.__code__, {**graph.__dict__, 'TARGET': TARGET})
    exec(compile(compiler(), '<currenta9/new4856 host ABI entry>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
