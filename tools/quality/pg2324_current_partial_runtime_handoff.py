"""Same-peer once recovery; partial fragment stays unchanged, no reload."""
import inspect
import types
import pg2311_current_resume_pair_handoff as prior
from pg2322_current_partial_runtime_pair_proof import body,SLOT as PROOF_SLOT,bound,SOURCE

SLOT='pg2324-current-partial-runtime-handoff-v1'
PROOF_SHA='4385ba0ed4594081e3549d4ae03eb5b3678042d4ab72bd7e319a81501b928f3b'


def payload():
    namespace={**prior.__dict__,'body':body,'PROOF_SLOT':PROOF_SLOT,'SLOT':SLOT,'PROOF_SHA':PROOF_SHA}
    exec(compile(inspect.getsource(prior.payload),'<current partial pair generator>','exec'),namespace)
    raw=bound(namespace['payload']())
    raw=raw.replace("expected['candidateNotPlaced']is True","expected['partialRuntimeFileVerified']is True and expected['reloadNotReserved']is True")
    from pyflakes.api import check
    if check(raw,'<whole current partial handoff>'):raise ValueError('all current partial handoff globals required')
    compile(raw,'<same-peer current partial handoff>','exec');return raw


def main():
    fn=types.FunctionType(prior.main.__code__,{**prior.__dict__,'SLOT':SLOT,'PROOF_SLOT':PROOF_SLOT,'PROOF_SHA':PROOF_SHA,'SOURCE':SOURCE,'payload':payload},'current_partial_handoff')
    return fn()


if __name__=='__main__':raise SystemExit(main())
