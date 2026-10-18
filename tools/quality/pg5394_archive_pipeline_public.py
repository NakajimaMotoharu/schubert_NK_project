import pg5390_archive_pipeline_selected as entry
import pg5384_nss_root_query_public as previous
import pg5281_factory_finish as finish
from pg5390_archive_pipeline_tools_test import NAMES
from pg5392_archive_pipeline_bytecode import RUN,OUT


def revalidated_case_ids(owner_new=False):
    values=previous.revalidated_case_ids()
    for number,name in enumerate(NAMES,1):
        values[('dev.codex.schubert.nk.batch.platform.BackupArchiveProcessTest',name)]={
            'testId':f'PT-OPS-ARCHOWN{number:03d}','newIndependentCase':True,'newInThisChange':owner_new}
    return values


if __name__=='__main__':
    raise SystemExit(finish.publish_current(entry=entry,run_name=RUN,proof_name=OUT,counts=(1138,134),
        spec='1101_Archive取得・全terminal保全_PT仕様.md',proof_key='archivePipelineBytecodeProofSha256',
        independent_cases=98,case_overrides=revalidated_case_ids(owner_new=True),case_repetitions=entry.repetitions(),
        extra={'originalScopeSites':7,'newIndependentCases':6,'priorIndependentCasesRevalidated':92,
            'newJavaCasesInThisGroup':6,'logicalTestMethods':1129,'repeatedLogicalMethods':1,'repeatedInvocations':10,
            'priorRelatedNewlySelectedCases':10,'physicalMain':765,'addedMain':sorted(entry.ADDED),
            'removedMain':sorted(entry.REMOVED),'netMainGrowth':1,'implementationDecision':'PG-D431'}))
