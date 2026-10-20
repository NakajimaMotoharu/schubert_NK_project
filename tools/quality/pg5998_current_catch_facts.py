"""Fresh b471 Main-only type facts, all851 inputs/1666classes; no Production invocation/PT."""
import inspect
import types
import pg5818_current_reference_facts as inputs_engine
import pg5770_current_catch_facts as engine
from pg5994_web24_public import SOURCE, STATIC_SHA


def input_source():
    raw=inspect.getsource(inputs_engine.inputs)
    changes={'PG5810-rollback-static-reauth-v1':'PG5992-web-contract-static-v1',
             'pg5810-rollback-static-reauth-v1':'pg5992-web-contract-static-v1',
             "'68b697ad9162315810ccc0c4adb0cceb200dc60ca44c8686750998742cea5c23'":'STATIC_SHA',
             'pg5800-rollback-selected54-v5':'pg5990-web-contract-selected921-v1',
             'len(current)!=850':'len(current)!=851','len(physical)!=1665':'len(physical)!=1666'}
    for old,new in changes.items():
        if raw.count(old)!=1:
            raise ValueError('one current851/1666 actual typed-input binding')
        raw=raw.replace(old,new,1)
    compile(raw,'<current b471 Main-only inputs>','exec')
    return raw


def inputs():
    scope={**vars(inputs_engine),'SOURCE':SOURCE,'STATIC_SHA':STATIC_SHA}
    exec(compile(input_source(),'<current851 actual static inputs>','exec'),scope)
    return scope['inputs']()


def main():
    scope={**vars(engine),'SOURCE':SOURCE,'SLOT':'pg5998-current-catch-facts-v1','inputs':inputs}
    return types.FunctionType(engine.main.__code__,scope,'current851_catch_facts')()


if __name__=='__main__':
    raise SystemExit(main())
