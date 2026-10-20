"""Fresh source870 typed catch facts; parse/analyze only, no Production code invocation."""
import inspect
import types
import pg5818_current_reference_facts as input_engine
import pg5770_current_catch_facts as engine
from pg6082_web_factory_qualification import SOURCE

STATIC_SHA = '134e8181764a40b725fd0fa9365f5d18fa714b66221e4f46b992d3f84cd7e735'


def input_source():
    raw = inspect.getsource(input_engine.inputs)
    changes = {
        'PG5810-rollback-static-reauth-v1': 'PG6082-web-factory-qualification-v1',
        'pg5810-rollback-static-reauth-v1': 'pg6082-web-factory-qualification-v1',
        '68b697ad9162315810ccc0c4adb0cceb200dc60ca44c8686750998742cea5c23': STATIC_SHA,
        'pg5800-rollback-selected54-v5': 'pg6086-web-factory-selected-v2',
        'len(current)!=850': 'len(current)!=851',
        'len(physical)!=1665': 'len(physical)!=1667',
        "proof['auxClassHashes']": "proof['allPhysicalMainSha256']"}
    for old, new in changes.items():
        if raw.count(old) != 1:
            raise ValueError('one explicit qualified851/1667/actual Jar input binding')
        raw = raw.replace(old, new, 1)
    compile(raw, '<current870 type inputs>', 'exec')
    return raw


def inputs():
    scope = {**vars(input_engine), 'SOURCE': SOURCE}
    exec(compile(input_source(), '<current870 Main-only type inputs>', 'exec'), scope)
    return scope['inputs']()


def main():
    scope = {**vars(engine), 'SOURCE': SOURCE, 'SLOT': 'pg6094-jms-catch-facts-v1', 'inputs': inputs}
    return types.FunctionType(engine.main.__code__, scope, 'current870_catch_facts')()


if __name__ == '__main__':
    raise SystemExit(main())
