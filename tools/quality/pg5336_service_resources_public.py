import json
import pg5332_service_resources_selected as entry
import pg5326_cgroup_owner_public as previous
import pg5281_factory_finish as finish

NAMES=('serviceown001PortsExistBeforeResourceAndNormalReleaseIsOnce',
    'serviceown002NullPortsAndFailedOrNullFactoriesNeverRelease',
    'serviceown003NonRetainedReleaseKeepsAllOriginalFailureIdentities',
    'serviceown004UnknownIoRuntimeAndFatalRetainOuterOwnerAfterInterrupt')


def revalidated_case_ids(owner_new=False):
    values=previous.revalidated_case_ids()
    for number,name in enumerate(NAMES,1):
        values[('dev.codex.schubert.nk.api.file.ServiceOwnedReleaseTest',name)]={
            'testId':f'PT-OPS-SERVICEOWN{number:03d}','newIndependentCase':True,'newInThisChange':owner_new}
    return values


if __name__=='__main__':
    result=json.loads((finish.public.W/'pg5332-service-resources-green-v1/manifest.safe.json').read_bytes())
    raise SystemExit(finish.publish_current(entry=entry,run_name='pg5332-service-resources-green-v1',
        proof_name='PG5334-service-resources-bytecode-v1',counts=(1090,132),
        spec='1092_ServiceResource取得・UNKNOWN保持_PT仕様.md',proof_key='serviceResourcesBytecodeProofSha256',
        independent_cases=78,case_overrides=revalidated_case_ids(owner_new=True),case_repetitions=entry.repetitions(),
        extra={'originalScopeSites':4,'newIndependentCases':4,'priorIndependentCasesRevalidated':74,
            'newJavaCasesInThisGroup':4,'logicalTestMethods':1081,'repeatedLogicalMethods':1,'repeatedInvocations':10,
            'fixtureDatabase':result['fixtureDatabase'],'implementationDecision':'PG-D427'}))
