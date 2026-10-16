"""Complete new RO ABI, all actual shared hashes and exactly one bundle definition."""
import inspect
import types
import pg3782_hygiene_ro_compile as previous
import pg3994_literal_invariant_ro_sources as role
import pg3982_literal_invariant_unused_sources as unused

W = role.W; TARGET = W / role.TOOLS; PRIOR = W / unused.TOOLS; sha = previous.sha


def generated():
    namespace = {**previous.__dict__, 'role': role, 'PRIOR': PRIOR}
    raw = inspect.getsource(previous.generated).replace('pg3780', 'pg3994')
    exec(compile(raw, '<actual new RO single bundle>', 'exec'), namespace)
    return namespace['generated']()


def compiler():
    raw = inspect.getsource(previous.main)
    for old, new in [('pg3782', 'pg3996'), ('pg3768', 'pg3984'), ('Pg3766', 'Pg3982'), ('pg3420-release-v1', 'pg3748-release-v1')]: raw = raw.replace(old, new)
    return raw


def main():
    namespace = {**previous.__dict__, 'role': role, 'TARGET': TARGET, 'PRIOR': PRIOR, 'generated': generated}
    namespace['write'] = types.FunctionType(previous.write.__code__, namespace)
    exec(compile(compiler(), '<whole new RO host ABI>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__': raise SystemExit(main())
