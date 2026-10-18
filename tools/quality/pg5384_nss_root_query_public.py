import pg5380_nss_root_query_selected as entry
import pg5376_ffm_progress_public as previous
import pg5281_factory_finish as finish
from pg5382_nss_root_query_bytecode import RUN,OUT

CASES={
    'dev.codex.schubert.nk.bootstrap.FixedServiceIdentityTest':('PT-OPS-NSSOWN',
        ('nssown001GetterNullRuntimeAndFatalKeepExactPartialCleanupOrder','nssown002FactoryIoRuntimeFatalAndNullNeverBecomeAProcessOwner')),
    'dev.codex.schubert.nk.batch.platform.RootStartupContextTest':('PT-OPS-ROOTQUERYOWN',
        ('rootqueryown001GetterNullRuntimeAndFatalKeepExactPartialCleanupOrder','rootqueryown002FactoryIoRuntimeFatalAndNullNeverBecomeAProcessOwner'))}


def revalidated_case_ids(owner_new=False):
    values=previous.revalidated_case_ids()
    for cls,(prefix,names) in CASES.items():
        for number,name in enumerate(names,1):
            values[(cls,name)]={'testId':prefix+f'{number:03d}','newIndependentCase':True,'newInThisChange':owner_new}
    return values


if __name__=='__main__':
    raise SystemExit(finish.publish_current(entry=entry,run_name=RUN,proof_name=OUT,counts=(1122,133),
        spec='1098_NSS・Root取得9境界_PT仕様.md',proof_key='nssRootQueryBytecodeProofSha256',
        independent_cases=92,case_overrides=revalidated_case_ids(owner_new=True),case_repetitions=entry.repetitions(),
        extra={'originalScopeSites':9,'newIndependentCases':4,'priorIndependentCasesRevalidated':88,
            'newJavaCasesInThisGroup':4,'logicalTestMethods':1113,'repeatedLogicalMethods':1,'repeatedInvocations':10,
            'priorRelatedNewlySelectedCases':18,'implementationDecision':'PG-D430'}))
