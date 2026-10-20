"""Current851 Main-only resolved catch facts; annotation processing and production calls disabled."""
import inspect
import types
import pg5818_current_reference_facts as inputs_engine
import pg5770_current_catch_facts as engine
from pg5918_api_static_rebind import SOURCE


def input_source():
    raw = inspect.getsource(inputs_engine.inputs)
    changes = {'PG5810-rollback-static-reauth-v1': 'PG5914-api-expression-static-v1',
               'pg5810-rollback-static-reauth-v1': 'pg5914-api-expression-static-v1',
               '68b697ad9162315810ccc0c4adb0cceb200dc60ca44c8686750998742cea5c23': '318d3783a5bfa4fe9a3920b252d3449eca01b9131c925758eadf13f8289548b4',
               'pg5800-rollback-selected54-v5': 'pg5912-api-expression-selected35-v1',
               'len(current)!=850': 'len(current)!=851', 'len(physical)!=1665': 'len(physical)!=1666'}
    for old, new in changes.items():
        if raw.count(old) != 1:
            raise ValueError('one immutable current851 catch-input binding')
        raw = raw.replace(old, new, 1)
    compile(raw, '<Main-only current851 catch input definitions>', 'exec')
    return raw


def inputs():
    scope = {**vars(inputs_engine), 'SOURCE': SOURCE}
    exec(compile(input_source(), '<current851 catch inputs>', 'exec'), scope)
    return scope['inputs']()


def main():
    scope = {**vars(engine), 'SOURCE': SOURCE, 'SLOT': 'pg5922-current-catch-facts-v1', 'inputs': inputs}
    return types.FunctionType(engine.main.__code__, scope, 'current851_catch_facts')()


if __name__ == '__main__':
    raise SystemExit(main())
