import json
import pg5332_service_resources_selected as entry
import pg5336_service_resources_public as ids
import pg5281_factory_finish as finish
from pg5342_service_resources_bytecode import RUN,OUT


if __name__=='__main__':
    result=json.loads((finish.public.W/RUN/'manifest.safe.json').read_bytes())
    path=entry.selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/OUT/'manifest.json'
    proof=json.loads(path.read_bytes())
    raise SystemExit(finish.publish_current(entry=entry,run_name=RUN,proof_name=OUT,counts=(1090,132),
        spec='1092_ServiceResource取得・UNKNOWN保持_PT仕様.md',proof_key='serviceResourcesBytecodeProofSha256',
        independent_cases=78,case_overrides=ids.revalidated_case_ids(owner_new=True),case_repetitions=entry.repetitions(),
        extra={'originalScopeSites':4,'newIndependentCases':4,'priorIndependentCasesRevalidated':74,
            'newJavaCasesInThisGroup':4,'newJavaCasesInThisSource':0,'logicalTestMethods':1081,
            'repeatedLogicalMethods':1,'repeatedInvocations':10,'serviceFourCounters':proof['serviceFourCounters'],
            'fixtureDatabase':result['fixtureDatabase'],'implementationDecision':'PG-D427'}))
