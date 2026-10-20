"""Current851 Main-only compiler facts; no production invocation or historical PT import."""
import inspect
import types
import pg5818_current_reference_facts as previous
from pg5832_isolation_whole import SOURCE


def inputs():
    raw=inspect.getsource(previous.inputs)
    changes={
      'PG5810-rollback-static-reauth-v1':'PG5830-isolation-static-v1',
      'pg5810-rollback-static-reauth-v1':'pg5830-isolation-static-v1',
      '68b697ad9162315810ccc0c4adb0cceb200dc60ca44c8686750998742cea5c23':'a8db12fed46184684ec8d911266dedac6206f42ca65be2fcd8f8c424ab6bbf8f',
      'pg5800-rollback-selected54-v5':'pg5828-isolation-selected66-v1',
      'len(current)!=850':'len(current)!=851',
      'len(physical)!=1665':'len(physical)!=1666'}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('exact current851 parser input binding')
        raw=raw.replace(old,new,1)
    scope={**vars(previous),'SOURCE':SOURCE};exec(compile(raw,'<current851 type inputs>','exec'),scope)
    return scope['inputs']()


def main():
    scope={**vars(previous.previous),'SOURCE':SOURCE,'SLOT':'pg5840-current-reference-facts-v1','inputs':inputs}
    return types.FunctionType(previous.previous.main.__code__,scope,'current851_reference_facts')()


if __name__=='__main__':raise SystemExit(main())
