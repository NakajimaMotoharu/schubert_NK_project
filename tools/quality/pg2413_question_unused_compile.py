"""Freeze new-only full current/new-resource graph; host ABI only, no guest write."""
import inspect
import json
import types
import pg2133_current_normal_unused_compile as prior
from pg2412_question_unused_sources import sources, bind, TOOLS, BEFORE, CURRENT, production
from pg2412_question_unused_sources import ARCHIVE as ARCHIVE_NAME

TARGET = prior.engine.W / TOOLS
ARCHIVE = prior.engine.P / ARCHIVE_NAME


def compiler():
    raw = bind(prior.compiler()).replace('pg2133-','pg2413-')
    for a,b in [('pg2091-frozen-v1','pg2375-frozen-v1'),
                ('pg2090-current-newrun-owned-stop-tools-v1','pg2374-current-resume-owned-stop-tools-v1'),
                ('Pg2090','Pg2374'),('pg2090','pg2374')]:
        raw = raw.replace(a,b)
    compile(raw,'<new question full ABI graph>','exec')
    return raw


def validate_actual_graph(target, hashes):
    raw = bind(inspect.getsource(prior.validate_actual_graph))
    namespace = {**prior.__dict__, 'TARGET':TARGET,'ARCHIVE':ARCHIVE}
    exec(compile(raw,'<new question exact graph inventory>','exec'),namespace)
    return namespace['validate_actual_graph'](target,hashes)


def main():
    before = json.loads((prior.engine.W/'pg2410-retired-current-before-v1/manifest.safe.json').read_bytes())
    if before['actualExit'] != 0 or before['productionSource'] != CURRENT or before['privateBeforeSha256'] != BEFORE or not before['runtimeAlreadyRetired']:
        raise ValueError('actual current all-resource retired proof required')
    namespace = {**prior.engine.__dict__, '__file__':__file__,'TARGET':TARGET,'ARCHIVE':ARCHIVE,
                 'TOOLS':TOOLS,'CURRENT':CURRENT,'PRODUCTION':production(),'BEFORE':BEFORE,
                 'sources':sources,'validate_actual_graph':validate_actual_graph,'inventory':prior.inventory}
    namespace['write'] = types.FunctionType(prior.write.__code__,{**prior.__dict__,'TARGET':TARGET,'ARCHIVE':ARCHIVE})
    exec(compile(compiler(),'<host new question full ABI>','exec'),namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
