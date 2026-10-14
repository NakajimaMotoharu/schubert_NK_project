"""Host-only complete actual current/candidate ABI freeze, requires signed candidate."""
import inspect
import types
import pg2433_current_boot_question_compile as previous
import pg2133_current_normal_unused_compile as graph
from pg2516_current_strict_candidate_sources import sources, bind, TOOLS, ARCHIVE as ARCHIVE_NAME, CURRENT, BEFORE, production

TARGET = graph.engine.W / TOOLS
ARCHIVE = graph.engine.P / ARCHIVE_NAME


def compiler():
    raw = bind(previous.compiler()).replace('pg2433-', 'pg2517-')
    for before, after in [('pg2375-frozen-v1', 'pg2459-frozen-v1'),
                          ('pg2374-current-resume-owned-stop-tools-v1', 'pg2458-question-current-owned-stop-tools-v1'),
                          ('Pg2374', 'Pg2458'), ('pg2374', 'pg2458')]:
        raw = raw.replace(before, after)
    compile(raw, '<new current/candidate ABI compiler>', 'exec')
    return raw


def validate_actual_graph(target, hashes):
    raw = inspect.getsource(graph.validate_actual_graph).replace('pg2132', 'pg2516').replace('pg2126-manifest-v1.sig', 'pg2512-manifest-v1.sig')
    ns = {**graph.__dict__, 'ARCHIVE': ARCHIVE}
    exec(compile(raw, '<new actual whole graph inventory>', 'exec'), ns)
    return ns['validate_actual_graph'](target, hashes)


def main():
    ns = {**graph.engine.__dict__, '__file__': __file__, 'TARGET': TARGET, 'ARCHIVE': ARCHIVE,
          'TOOLS': TOOLS, 'CURRENT': CURRENT, 'PRODUCTION': production(), 'BEFORE': BEFORE,
          'sources': sources, 'validate_actual_graph': validate_actual_graph, 'inventory': graph.inventory}
    ns['write'] = types.FunctionType(graph.write.__code__, {**graph.__dict__, 'TARGET': TARGET})
    exec(compile(compiler(), '<new host actual ABI entry>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
