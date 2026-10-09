"""PG-D407..409 exact four-class delta from installed e016; no added classes or authority."""
from pg749_candidate_contract import MODULES as MODULES,verify_delta as algorithm
CHANGED={'bootstrap':frozenset({'dev/codex/schubert/nk/bootstrap/ChildStartupContext.class','dev/codex/schubert/nk/bootstrap/ChildStartupContext$NativeIo.class'}),'api':frozenset({'dev/codex/schubert/nk/api/file/InspectorApplication.class'}),'batch':frozenset({'dev/codex/schubert/nk/batch/platform/InspectorUnitSnapshot.class'})}
ADDED={}
def verify_delta(old,candidate):
    import types
    return types.FunctionType(algorithm.__code__,{**algorithm.__globals__,'CHANGED':CHANGED,'ADDED':ADDED},algorithm.__name__)(old,candidate)
