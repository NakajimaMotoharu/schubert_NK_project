"""SSC261 two changed classes/three nested additions; no deployment authority."""
import types
from pg749_candidate_contract import MODULES,verify_delta as algorithm

CHANGED={'bootstrap':frozenset('dev/codex/schubert/nk/bootstrap/'+n+'.class'for n in [
    'NativeCoveragePrivateFile','NativeCoveragePrivateFile$NativeIo'])}
ADDED={'bootstrap':frozenset('dev/codex/schubert/nk/bootstrap/'+n+'.class'for n in [
    'NativeCoveragePrivateFile$FileCalls','NativeCoveragePrivateFile$NativeFileCalls',
    'NativeCoveragePrivateFile$ReadOnlyObservation'])}


def verify_delta(old,candidate):
    return types.FunctionType(algorithm.__code__,{**algorithm.__globals__,
        'CHANGED':CHANGED,'ADDED':ADDED},algorithm.__name__)(old,candidate)
