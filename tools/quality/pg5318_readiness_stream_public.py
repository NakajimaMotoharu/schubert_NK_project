import json
import pg5314_readiness_stream_selected as entry
import pg5281_factory_finish as finish
import pg5308_permit_intent_public as ids
from pg5314_readiness_stream_selected_test import NAMES


def revalidated_case_ids(stream_new=False):
    values=ids.revalidated_case_ids()
    for number,name in enumerate(NAMES,1):
        values[('dev.codex.schubert.nk.batch.platform.MorningCaddyReadinessTest',name)]={
            'testId':f'PT-CADDYSTREAM{number:03d}','newIndependentCase':True,'newInThisChange':stream_new}
    return values


if __name__=='__main__':
    path=entry.selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5316-readiness-stream-bytecode-v1/manifest.json'
    proof=json.loads(path.read_bytes())
    raise SystemExit(finish.publish_current(entry=entry,run_name='pg5314-readiness-stream-green-v1',
        proof_name='PG5316-readiness-stream-bytecode-v1',counts=(1068,129),
        spec='1087_Readiness_stream3_取得前保護_PT仕様.md',proof_key='readinessStreamBytecodeProofSha256',
        independent_cases=66,case_overrides=revalidated_case_ids(stream_new=True),case_repetitions=entry.repetitions(),
        extra={'originalScopeSites':3,'newIndependentCases':6,'priorIndependentCasesRevalidated':60,
            'newJavaCasesInThisGroup':6,'logicalTestMethods':1059,'repeatedLogicalMethods':1,'repeatedInvocations':10,
            'focusedCaddyHelperCounters':proof['focusedCaddyHelperCounters'],'implementationDecision':'PG-D425',
            'realNullBodyAcquisitionsCounted':False}))
