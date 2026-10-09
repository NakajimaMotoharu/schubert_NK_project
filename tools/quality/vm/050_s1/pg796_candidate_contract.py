"""SSC237 literal one changed class/four nested additions, byte-delta only, no authority."""
from pg749_candidate_contract import MODULES as MODULES
from pg749_candidate_contract import verify_delta as previous

__all__=('MODULES','CHANGED','ADDED','verify_delta')

CHANGED={'batch':frozenset({'dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner.class'})}
ADDED={'batch':frozenset('dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner$'+n+'.class'for n in ('ApiRetained','CompletionPhase','CompletionProgress','CompletionRetirement'))}


def verify_delta(old,candidate):
    # The audited algorithm takes closed literal sets, not generated expected class digests.
    import types
    globals_={**previous.__globals__,'CHANGED':CHANGED,'ADDED':ADDED}
    return types.FunctionType(previous.__code__,globals_,previous.__name__)(old,candidate)
