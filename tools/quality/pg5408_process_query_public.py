import json
import pg5404_process_query_selected as entry
import pg5394_archive_pipeline_public as previous
import pg5281_factory_finish as finish
from pg5404_process_query_tools_test import NAMES
from pg5406_process_query_bytecode import RUN,OUT


def revalidated_case_ids(owner_new=False):
    values=previous.revalidated_case_ids()
    for number,name in enumerate(NAMES,1):
        values[('dev.codex.schubert.nk.batch.platform.ProcessResourceScopeTest',name)]={
            'testId':f'PT-OPS-QUERYOWN{number:03d}','newIndependentCase':True,'newInThisChange':owner_new}
    return values


if __name__=='__main__':
    result=json.loads((finish.public.W/RUN/'manifest.safe.json').read_bytes())
    raise SystemExit(finish.publish_current(entry=entry,run_name=RUN,proof_name=OUT,counts=(1164,137),
        spec='1103_Process照会所有・例外優先順位_PT仕様.md',proof_key='processQueryBytecodeProofSha256',
        independent_cases=105,case_overrides=revalidated_case_ids(owner_new=True),case_repetitions=entry.repetitions(),
        extra={'originalScopeSites':12,'newIndependentCases':7,'priorIndependentCasesRevalidated':98,
            'newJavaCasesInThisGroup':7,'logicalTestMethods':1155,'repeatedLogicalMethods':1,'repeatedInvocations':10,
            'priorRelatedNewlySelectedCases':19,'fixtureDatabase':result['fixtureDatabase'],'physicalMain':767,
            'addedMain':sorted(entry.ADDED),'removedMain':[],'netMainGrowth':2,'implementationDecision':'PG-D432'}))
