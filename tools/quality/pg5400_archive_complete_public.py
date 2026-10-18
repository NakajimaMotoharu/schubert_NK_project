import json
import pg5390_archive_pipeline_selected as entry
import pg5394_archive_pipeline_public as ids
import pg5281_factory_finish as finish
from pg5398_archive_complete_bytecode import RUN,OUT


if __name__=='__main__':
    result=json.loads((finish.public.W/RUN/'manifest.safe.json').read_bytes())
    raise SystemExit(finish.publish_current(entry=entry,run_name=RUN,proof_name=OUT,counts=(1138,134),
        spec='1101_Archive取得・全terminal保全_PT仕様.md',proof_key='archivePipelineBytecodeProofSha256',
        independent_cases=98,case_overrides=ids.revalidated_case_ids(owner_new=True),case_repetitions=entry.repetitions(),
        extra={'originalScopeSites':7,'newIndependentCases':6,'priorIndependentCasesRevalidated':92,
            'newJavaCasesInThisGroup':6,'newJavaCasesInThisSource':0,'logicalTestMethods':1129,
            'repeatedLogicalMethods':1,'repeatedInvocations':10,'priorRelatedNewlySelectedCases':10,
            'fixtureDatabase':result['fixtureDatabase'],'physicalMain':765,'addedMain':sorted(entry.ADDED),
            'removedMain':sorted(entry.REMOVED),'netMainGrowth':1,'implementationDecision':'PG-D431'}))
