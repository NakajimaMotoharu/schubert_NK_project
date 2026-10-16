"""Explicit new-only stage/place only, never publishes or starts a business actor."""
import inspect
import sys
import types
import pg3760_hygiene_unused_dispatch as previous
import pg3982_literal_invariant_unused_sources as role
import pg3984_literal_invariant_unused_compile as compiler

TARGET = compiler.TARGET
GUEST = '/var/lib/pgpt-s1-preservation/' + role.TOOLS


def stage_source(): return role.normalized_text(previous.STAGE)


def source():
    raw = role.normalized_text(previous.source())
    compile(raw, '<new unused stage or placement only>', 'exec')
    return raw


def before_record():
    namespace = {**previous.__dict__, 'role': role}
    raw = role.normalized_text(inspect.getsource(previous.before_record)).replace('pg3752-current-preservation-readonly-v1', 'pg3978-current-preservation-readonly-v1')
    exec(compile(raw, '<fresh current data-only receipt>', 'exec'), namespace)
    return namespace['before_record']()


def runtime_namespace(candidate, before):
    return types.FunctionType(previous.runtime_namespace.__code__, {**previous.__dict__, 'role': role, 'TARGET': TARGET, 'GUEST': GUEST, 'STAGE': stage_source(), '__file__': __file__})(candidate, before)


def main():
    values = {**previous.__dict__, 'role': role, 'compiler': compiler, 'TARGET': TARGET, 'GUEST': GUEST,
              'before_record': before_record, 'runtime_namespace': runtime_namespace, 'source': source, '__file__': __file__}
    raw = role.normalized_text(inspect.getsource(previous.main))
    exec(compile(raw, '<new unused placement explicit action>', 'exec'), values)
    return values['main']()


if __name__ == '__main__':
    if sys.argv[1:] not in [['stage'], ['place']]: raise SystemExit('one explicit new stage/place action; no replay/resume alias')
    raise SystemExit(main())
