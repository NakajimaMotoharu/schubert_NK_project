import pg5356_ffm_outputs_selected as entry
import pg5352_manager_session_public as previous
import pg5281_factory_finish as finish
from pg5366_ffm_outputs_bytecode import RUN,OUT

NAMES=('ffmown001WriteThenUnknownKeepsOutputAndArenaWithoutRetry',
    'ffmown002ThreeOutputSlotsReuseAndLegacyReplyRequestFreeBusOrder',
    'ffmown003NegativeAndWrongStatusesReleaseKnownOutputsInOriginalOrder',
    'ffmown004UnknownReplyReleaseDrainsKnownRequestButRetainsBusAndArena',
    'ffmown005BeforeCallFailureAndArrayDecodeFailureKeepExactOwnership',
    'ffmown006OutputDecodeFailureRefusesCleanupClaimsAndAnyFurtherNativeCall',
    'ffmown007ArenaCloseUnknownAfterBusConsumptionNeverAllowsANextQueryOrRetry')


def revalidated_case_ids(owner_new=False):
    values=previous.revalidated_case_ids()
    for number,name in enumerate(NAMES,1):
        values[('dev.codex.schubert.nk.bootstrap.LinuxSystemdSessionTest',name)]={
            'testId':f'PT-OPS-FFMOWN{number:03d}','newIndependentCase':True,'newInThisChange':owner_new}
    return values


if __name__=='__main__':
    raise SystemExit(finish.publish_current(entry=entry,run_name=RUN,proof_name=OUT,counts=(1099,132),
        spec='1096_FFM返却先行所有・UNKNOWN保持_PT仕様.md',proof_key='ffmOutputsBytecodeProofSha256',
        independent_cases=87,case_overrides=revalidated_case_ids(owner_new=True),case_repetitions=entry.repetitions(),
        extra={'originalScopeSites':4,'newIndependentCases':7,'priorIndependentCasesRevalidated':80,
            'newJavaCasesInThisGroup':7,'logicalTestMethods':1090,'repeatedLogicalMethods':1,'repeatedInvocations':10,
            'additionalBoundariesOutsideOriginal':2,'implementationDecision':'PG-D429'}))
