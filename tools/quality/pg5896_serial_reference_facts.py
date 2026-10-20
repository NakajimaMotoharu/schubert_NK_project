"""Current851 Main-only compiler facts for serial receiver changes; no Production invocation."""
import inspect
import types
import pg5818_current_reference_facts as previous
import pg5766_reference_identity_facts as engine
from pg5886_terminal_serial_whole import SOURCE


def inputs():
    raw=inspect.getsource(previous.inputs)
    changes={'PG5810-rollback-static-reauth-v1':'PG5882-terminal-serial-static-v1','pg5810-rollback-static-reauth-v1':'pg5882-terminal-serial-static-v1','68b697ad9162315810ccc0c4adb0cceb200dc60ca44c8686750998742cea5c23':'2b5a42b051c804000affd8b92ea51c51c4e6dcf8e21addbed975a966335b7ec8','pg5800-rollback-selected54-v5':'pg5880-terminal-serial83-v1','len(current)!=850':'len(current)!=851','len(physical)!=1665':'len(physical)!=1666'}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('one immutable serial type-input binding')
        raw=raw.replace(old,new,1)
    scope={**vars(previous),'SOURCE':SOURCE};exec(compile(raw,'<current851 serial facts inputs>','exec'),scope)
    return scope['inputs']()


def main():
    scope={**vars(engine),'SOURCE':SOURCE,'SLOT':'pg5896-serial-reference-facts-v1','inputs':inputs}
    return types.FunctionType(engine.main.__code__,scope,'current_serial_facts')()


if __name__=='__main__':raise SystemExit(main())
