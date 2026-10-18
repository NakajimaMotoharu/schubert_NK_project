import json
import pg5322_cgroup_owner_selected as entry
import pg5281_factory_finish as finish
import pg5318_readiness_stream_public as ids
from pg5322_cgroup_owner_selected_test import NAMES


def revalidated_case_ids(owner_new=False):
    values=ids.revalidated_case_ids()
    for number,name in enumerate(NAMES,1):
        values[('dev.codex.schubert.nk.batch.platform.CgroupPrimitiveOwnerTest',name)]={
            'testId':f'PT-OPS-CGROUPFD{number:03d}','newIndependentCase':True,'newInThisChange':owner_new}
    return values


if __name__=='__main__':
    path=entry.selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5324-cgroup-owner-bytecode-v1/manifest.json'
    proof=json.loads(path.read_bytes())
    raise SystemExit(finish.publish_current(entry=entry,run_name='pg5322-cgroup-owner-green-v1',
        proof_name='PG5324-cgroup-owner-bytecode-v1',counts=(1086,131),
        spec='1089_CgroupOwner_primitive取得・取得順全drain_PT仕様.md',proof_key='cgroupOwnerBytecodeProofSha256',
        independent_cases=74,case_overrides=revalidated_case_ids(owner_new=True),case_repetitions=entry.repetitions(),
        extra={'originalScopeSites':2,'newIndependentCases':8,'priorIndependentCasesRevalidated':66,
            'newJavaCasesInThisGroup':8,'logicalTestMethods':1077,'repeatedLogicalMethods':1,'repeatedInvocations':10,
            'ownerFourCounters':proof['ownerFourCounters'],'nativeCloseOrder':proof['nativeCloseOrder'],
            'logicalConsumedNotKernelCloseAck':True,'implementationDecision':'PG-D426'}))
