"""Original642/81 and13 environment scopes with unchanged checked-null IO, allowlist only."""
import json
import pg5122_root_elf_public as public
import pg5180_backup_public as common
import pg5184_environment_selected as entry

selected=entry.selected


def main():
    run=public.W/'pg5184-environment-scopes-green-v1'
    result=json.loads((run/'manifest.safe.json').read_bytes())
    path=selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5186-environment-bytecode-v1/manifest.json'
    proof=json.loads(path.read_bytes())
    if proof['actualExit']!=0 or proof['source']!=result['sourceSnapshot'] or proof['physicalMain']!=764:
        raise ValueError('same-source actual13 environment proof first')
    entry.configure()
    return public.main(factory_run_name=run.name,measurement_module=selected,
       required_counts=(642,81,42),case_overrides=common.revalidated_case_ids(),extra_suites=entry.extra_suites(),
       extra_fields={'newIndependentCases':0,'priorIndependentCasesRevalidated':42,'newJavaCasesInThisChange':0,
       'spec':'1059_Inspector環境file保持scope_factory所有_PT仕様.md',
       'ssc':['SSC308'],'bugs':['BUG1414'],'ykt':['YKT1178'],'environmentScopeBytecodeProofSha256':selected.sha(path),
       'storageFourCounters':result['storageFourCounters'],'newChangedOuterClasses':3,
       'nestedDebugEquivalent':proof['nestedDebugEquivalent'],'otherPhysicalClassesUnchanged':proof['otherPhysicalClassesUnchanged'],
       'checkedNullIoFactories':3,'wholeHorizontalComplete':False})


if __name__=='__main__':raise SystemExit(main())
