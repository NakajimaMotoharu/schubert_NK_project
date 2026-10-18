"""Same strict independent post, only new stop receipt/output slot after BUG1455."""
import types
import pg5502_current_owned_post as previous

SLOT='pg5534-current-owned-post-v1'


def code_with_receipt(code):
    return code.replace(co_consts=tuple(code_with_receipt(value)if isinstance(value,types.CodeType)else
        'pg5532-stop-v1.safe.json'if value=='pg5500-stop-v1.safe.json'else value for value in code.co_consts))


def namespace():
    # Bind the complete emitter namespace as well as the host directory before
    # building either factory. Its read-only result retains the canonical PG5502
    # reader label; execution identity is this new slot, source and payload hash.
    result=types.FunctionType(previous.namespace.__code__,{**vars(previous),'SLOT':SLOT})();original=result['entry']()
    if original.__code__.co_consts.count('pg5500-stop-v1.safe.json')!=1:
        raise ValueError('one exact original genuine-stop selector')
    fixed=types.FunctionType(code_with_receipt(original.__code__),{**original.__globals__,'SLOT':SLOT},
        original.__name__,original.__defaults__,original.__closure__)
    return{**result,'entry':lambda:fixed}


if __name__=='__main__':previous.authenticate_host();raise SystemExit(namespace()['entry']()())
