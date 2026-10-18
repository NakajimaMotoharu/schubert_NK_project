import pg5348_manager_session_selected as entry
import pg5336_service_resources_public as previous
import pg5281_factory_finish as finish
from pg5350_manager_session_bytecode import RUN,OUT

NAMES=('managerown001FactoryFailuresKeepIdentityAndAllowAFreshNextAcquisition',
    'managerown002UnconfirmedPostCloseObservationRetainsPendingAndNeverCreatesAgain')


def revalidated_case_ids(owner_new=False):
    values=previous.revalidated_case_ids()
    for number,name in enumerate(NAMES,1):
        values[('dev.codex.schubert.nk.bootstrap.SystemManagerObservationTest',name)]={
            'testId':f'PT-OPS-MANAGEROWN{number:03d}','newIndependentCase':True,'newInThisChange':owner_new}
    return values


if __name__=='__main__':
    raise SystemExit(finish.publish_current(entry=entry,run_name=RUN,proof_name=OUT,counts=(1092,132),
        spec='1094_ManagerSession取得・pending保持_PT仕様.md',proof_key='managerSessionBytecodeProofSha256',
        independent_cases=80,case_overrides=revalidated_case_ids(owner_new=True),case_repetitions=entry.repetitions(),
        extra={'originalScopeSites':1,'newIndependentCases':2,'priorIndependentCasesRevalidated':78,
            'newJavaCasesInThisGroup':2,'logicalTestMethods':1083,'repeatedLogicalMethods':1,'repeatedInvocations':10,
            'implementationDecision':'PG-D428'}))
