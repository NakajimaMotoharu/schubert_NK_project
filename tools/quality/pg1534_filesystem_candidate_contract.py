"""SSC269 exact Production delta; artifact qualification, never deployment authority."""
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'vm/050_s1'))
from pg749_candidate_contract import MODULES, verify_delta as algorithm
__all__ = ['MODULES', 'CHANGED', 'ADDED', 'verify_delta']

CHANGED = {'batch': frozenset('dev/codex/schubert/nk/batch/file/' + n + '.class'
                            for n in ['EnvironmentInodePolicy', 'EnvironmentInodePolicy$Metadata', 'EnvironmentInodePolicy$Snapshot', 'InspectorEnvironmentReader$NioIo'])}
ADDED = {'storage': frozenset('dev/codex/schubert/nk/storage/LinuxFilesystemClassifier' + n + '.class'
                            for n in ['', '$StatfsCall'])}

def verify_delta(old, candidate):
    return types.FunctionType(algorithm.__code__, {**algorithm.__globals__, 'CHANGED': CHANGED, 'ADDED': ADDED}, algorithm.__name__)(old, candidate)
