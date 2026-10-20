"""Current851 Main-only catch facts; no annotation processing or Production invocation."""
import inspect
import types
import pg5818_current_reference_facts as inputs_engine
import pg5770_current_catch_facts as engine
from pg5944_private_lock_whole import SOURCE


def inputs():
    raw = inspect.getsource(inputs_engine.inputs)
    for old, new in (('PG5810-rollback-static-reauth-v1', 'PG5942-private-lock-static-v1'),
                     ('pg5810-rollback-static-reauth-v1', 'pg5942-private-lock-static-v1'),
                     ('68b697ad9162315810ccc0c4adb0cceb200dc60ca44c8686750998742cea5c23', 'fba315bab4168d6150638c7a21b5209dfce88b0f97951e456ed3d52d33edbda5'),
                     ('pg5800-rollback-selected54-v5', 'pg5940-private-lock-compile-v1'), ('len(current)!=850', 'len(current)!=851'), ('len(physical)!=1665', 'len(physical)!=1666')):
        if raw.count(old) != 1:
            raise ValueError('one current851/1666 strict Main-only binding')
        raw = raw.replace(old, new, 1)
    scope = {**vars(inputs_engine), 'SOURCE': SOURCE}
    exec(compile(raw, '<current851 Main-only input>', 'exec'), scope)
    return scope['inputs']()


def main():
    scope = {**vars(engine), 'SOURCE': SOURCE, 'SLOT': 'pg5952-current-catch-facts-v1', 'inputs': inputs}
    return types.FunctionType(engine.main.__code__, scope, 'current851_catch_facts')()


if __name__ == '__main__':
    raise SystemExit(main())
