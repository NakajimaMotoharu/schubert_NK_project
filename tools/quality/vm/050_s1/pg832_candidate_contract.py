"""SSC239 closed literal class-byte delta; no deployment authority or generated expected set."""
from pg749_candidate_contract import MODULES as MODULES, verify_delta as algorithm
CHANGED={'batch':frozenset({
 'dev/codex/schubert/nk/batch/platform/RootStartupContext.class',
 'dev/codex/schubert/nk/batch/platform/RootStartupContext$NativeIo.class'})}
ADDED={'batch':frozenset({
 'dev/codex/schubert/nk/batch/platform/LinuxSystemdQuery.class',
 'dev/codex/schubert/nk/batch/platform/LinuxSystemdQuery$Budget.class',
 'dev/codex/schubert/nk/batch/platform/LinuxSystemdQuery$Factory.class',
 'dev/codex/schubert/nk/batch/platform/LinuxSystemdQuery$Owner.class',
 'dev/codex/schubert/nk/batch/platform/LinuxSystemdQuery$Property.class',
 'dev/codex/schubert/nk/batch/platform/LinuxSystemdQuery$Session.class',
 'dev/codex/schubert/nk/batch/platform/LinuxSystemdSession.class',
 'dev/codex/schubert/nk/batch/platform/LinuxSystemdSession$Calls.class',
 'dev/codex/schubert/nk/batch/platform/LinuxSystemdSession$Factory.class',
 'dev/codex/schubert/nk/batch/platform/LinuxSystemdSession$Native.class',
 'dev/codex/schubert/nk/batch/platform/LinuxSystemdSession$Octets.class',
 'dev/codex/schubert/nk/batch/platform/RootStartupContext$NativeIo$UnitQuery.class'})}
def verify_delta(old,candidate):
    import types
    return types.FunctionType(algorithm.__code__,{**algorithm.__globals__,'CHANGED':CHANGED,'ADDED':ADDED},algorithm.__name__)(old,candidate)
