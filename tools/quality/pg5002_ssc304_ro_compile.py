"""Compile only the new RO role against qualified current ABI; no whole replay."""
import inspect
import types
import pg4874_ssc301_302_ro_compile as previous
import pg5000_ssc304_ro_sources as role

W = role.W
TARGET = W / role.TOOLS
PRIOR = W / role.unused.TOOLS
sha = previous.sha
TEMPLATE = previous.previous.previous


def generated():
    ns = {**vars(previous.previous), 'role': role, 'PRIOR': PRIOR}
    raw = inspect.getsource(previous.previous.generated).replace('pg3994', 'pg5000')
    exec(compile(raw, '<all18 RO/current04bb exact bundle>', 'exec'), ns)
    return ns['generated']()


def compiler():
    raw = previous.compiler()
    for a, b in [('pg4874', 'pg5002'), ('pg4866', 'pg4988'), ('Pg4864', 'Pg4986'),
                 ('pg4702-release-v1', 'pg4860-release-v1')]:
        raw = raw.replace(a, b)
    return raw


def main():
    ns = {**vars(TEMPLATE), '__file__': __file__, 'role': role, 'TARGET': TARGET,
          'PRIOR': PRIOR, 'generated': generated}
    ns['write'] = types.FunctionType(TEMPLATE.write.__code__, ns)
    exec(compile(compiler(), '<RO only against actual04bb ABI>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
