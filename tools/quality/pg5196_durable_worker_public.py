"""Original684/85, allowlisted cases only; Morning native wrapper remains unaccepted."""
import json
import pg5122_root_elf_public as public
import pg5180_backup_public as common
import pg5192_durable_worker_selected as entry

selected=entry.selected


def main():
    run=public.W/'pg5192-durable-worker-scopes-green-v1'
    result=json.loads((run/'qualification.safe.json').read_bytes())
    path=selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5194-durable-worker-bytecode-v1/manifest.json'
    proof=json.loads(path.read_bytes())
    if proof['actualExit']!=0 or proof['source']!=result['sourceSnapshot'] or proof['physicalMain']!=764:
        raise ValueError('same-source actual8 caller proof first')
    entry.configure()
    return public.main(factory_run_name=run.name,measurement_module=selected,
        required_counts=(684,85,42),case_overrides=common.revalidated_case_ids(),extra_suites=entry.extra_suites(),
        qualification_path=run/'qualification.safe.json',
        extra_fields={'newIndependentCases':0,'priorIndependentCasesRevalidated':42,'newJavaCasesInThisChange':0,
        'spec':'1061_永続記録・worker要求_factory所有_PT仕様.md','ssc':['SSC308'],'bugs':['BUG1414'],'ykt':['YKT1178'],
        'durableWorkerBytecodeProofSha256':selected.sha(path),'storageFourCounters':result['storageFourCounters'],
        'newChangedOuterClasses':4,'nestedDebugEquivalent':proof['nestedDebugEquivalent'],
        'otherPhysicalClassesUnchanged':proof['otherPhysicalClassesUnchanged'],'checkedNullIoFactories':7,
        'limitedClosedOriginalSites':7,'morningPublishPartialOnly':True,'wholeHorizontalComplete':False,
        'originalRunnerActualExit':1,'separateQualificationActualExit':0,
        'separateQualificationSha256':selected.sha(run/'qualification.safe.json')})


if __name__=='__main__':raise SystemExit(main())
