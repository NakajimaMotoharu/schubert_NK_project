"""Original688/85 and four independent owner-transfer tests, explicit source/invocation join."""
import json
import pg5122_root_elf_public as public
import pg5180_backup_public as common
import pg5200_morning_owner_selected as entry

selected=entry.selected
NAMES=('mbpub007FactoryAndNullPortsRefuseBeforeAssembly',
       'mbpub008CompleteOwnerTakesOverDirectoryExactlyOnce',
       'mbpub009IncompleteAssemblyAlwaysReleasesDirectory',
       'mbpub010AssemblyCloseMatrixPreservesIndependentFailurePriority')


def main():
    run=public.W/'pg5200-morning-owner-green-v1'
    result=json.loads((run/'qualification.safe.json').read_bytes())
    path=selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5202-morning-owner-bytecode-v1/manifest.json'
    proof=json.loads(path.read_bytes())
    if proof['actualExit']!=0 or proof['source']!=result['sourceSnapshot'] or proof['physicalMain']!=764:
        raise ValueError('same-source actual owner-transfer proof first')
    entry.configure();overrides=common.revalidated_case_ids()
    overrides.update({('dev.codex.schubert.nk.batch.file.MorningBackupRequestPublicationTest',name):
        {'testId':'PT-OPS-MBPUB'+str(i).zfill(3),'newIndependentCase':True,'newInThisChange':True}
        for i,name in enumerate(NAMES,7)})
    return public.main(factory_run_name=run.name,measurement_module=selected,
        required_counts=(688,85,46),case_overrides=overrides,extra_suites=entry.extra_suites(),
        qualification_path=run/'qualification.safe.json',case_name_aliases=entry.invocation_aliases(),
        extra_fields={'newIndependentCases':4,'priorIndependentCasesRevalidated':42,'newJavaCasesInThisChange':4,
        'spec':'1063_Morning実factory_所有移管_PT仕様.md','ssc':['SSC308'],'bugs':['BUG1414','BUG1431'],'ykt':['YKT1178','YKT1195'],
        'morningOwnerBytecodeProofSha256':selected.sha(path),'storageFourCounters':result['storageFourCounters'],
        'newChangedOuterClasses':1,'nestedMethodEquivalent':proof['nestedMethodEquivalent'],
        'otherPhysicalClassesUnchanged':proof['otherPhysicalClassesUnchanged'],
        'helperMethodCounters':proof['helperMethodCounters'],'extraInternalNativeGapClosedLimited':True,
        'wholeHorizontalComplete':False,'originalRunnerActualExit':1,'separateQualificationActualExit':0,
        'qualifiedInvocationAliases':entry.invocation_aliases(),
        'separateQualificationSha256':selected.sha(run/'qualification.safe.json')})


if __name__=='__main__':raise SystemExit(main())
