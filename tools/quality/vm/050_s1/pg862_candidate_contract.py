"""SSC240 finite three-source-family delta, explicit compiled classes incl line metadata."""
from pg749_candidate_contract import MODULES as MODULES, verify_delta as algorithm
CHANGED={'batch':frozenset({
 'dev/codex/schubert/nk/batch/file/MaintenanceRunFiles.class',
 'dev/codex/schubert/nk/batch/file/MaintenanceRunFiles$Session.class',
 'dev/codex/schubert/nk/batch/file/MaintenanceRunFiles$Graph.class',
 'dev/codex/schubert/nk/batch/file/MaintenanceRunFiles$CapturedFile.class',
 'dev/codex/schubert/nk/batch/file/MaintenanceRunFiles$NioIo.class',
 'dev/codex/schubert/nk/batch/file/MaintenanceRunFiles$Inventory.class',
 'dev/codex/schubert/nk/batch/file/MorningNewRunAdmission.class',
 'dev/codex/schubert/nk/batch/file/MorningNewRunAdmission$OriginalFiles.class',
 'dev/codex/schubert/nk/batch/file/MorningNewRunAdmission$OriginalProof.class',
 'dev/codex/schubert/nk/batch/file/MorningNewRunAdmission$1.class',
 'dev/codex/schubert/nk/batch/file/MorningNewRunAdmission$2.class',
 'dev/codex/schubert/nk/batch/file/MorningNewRunAdmission$2$1.class',
 'dev/codex/schubert/nk/batch/file/MorningNewRunAdmission$3.class',
 'dev/codex/schubert/nk/batch/file/MorningResumeAdmission.class',
 'dev/codex/schubert/nk/batch/file/MorningResumeAdmission$2$1.class'})}
ADDED={}
def verify_delta(old,candidate):
    import types
    return types.FunctionType(algorithm.__code__,{**algorithm.__globals__,'CHANGED':CHANGED,'ADDED':ADDED},algorithm.__name__)(old,candidate)
