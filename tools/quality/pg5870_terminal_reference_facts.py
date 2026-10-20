"""Current851 Main-only compiler facts; no production method, PT, VM or runtime invocation."""
import inspect
import types
import pg5818_current_reference_facts as previous
import pg5766_reference_identity_facts as engine
from pg5860_terminal_whole import SOURCE


def inputs():
    raw=inspect.getsource(previous.inputs)
    changes={'PG5810-rollback-static-reauth-v1':'PG5858-terminal-static-v1','pg5810-rollback-static-reauth-v1':'pg5858-terminal-static-v1','68b697ad9162315810ccc0c4adb0cceb200dc60ca44c8686750998742cea5c23':'4e5b6cb920bbc01334c6d1ef81f0042db10ca9fe5bbce8a920e2d7bd770cccdf','pg5800-rollback-selected54-v5':'pg5856-terminal-selected81-v3','len(current)!=850':'len(current)!=851','len(physical)!=1665':'len(physical)!=1666'}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('one fixed current compiler input binding')
        raw=raw.replace(old,new,1)
    scope={**vars(previous),'SOURCE':SOURCE};exec(compile(raw,'<current851 compiler inputs>','exec'),scope)
    return scope['inputs']()


def main():
    scope={**vars(engine),'SOURCE':SOURCE,'SLOT':'pg5870-terminal-reference-facts-v1','inputs':inputs}
    return types.FunctionType(engine.main.__code__,scope,'current_terminal_reference_facts')()


if __name__=='__main__':raise SystemExit(main())
