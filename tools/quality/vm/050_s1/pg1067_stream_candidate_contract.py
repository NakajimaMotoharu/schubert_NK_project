"""PG-D411 one NativeReader main-class delta from deployed40ef/PG932; no authority."""
from pg749_candidate_contract import MODULES,verify_delta as algorithm

CHANGED={'batch':frozenset({'dev/codex/schubert/nk/batch/platform/InspectorUnitProbe$NativeReader.class'})}
ADDED={}


def verify_delta(old,candidate):
    import types
    return types.FunctionType(algorithm.__code__,{**algorithm.__globals__,'CHANGED':CHANGED,'ADDED':ADDED},algorithm.__name__)(old,candidate)
