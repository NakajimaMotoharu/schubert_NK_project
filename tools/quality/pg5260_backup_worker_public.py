"""Original864/101 and Backup owner-tail evidence; previous54 independent cases revalidated."""
import json
import pg5122_root_elf_public as public
import pg5252_startup_view_public as ids
import pg5256_backup_worker_selected as entry

selected=entry.selected


def main():
    run=public.W/'pg5256-backup-worker-green-v1';result=json.loads((run/'manifest.safe.json').read_bytes())
    path=selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5258-backup-worker-bytecode-v1/manifest.json'
    proof=json.loads(path.read_bytes())
    if proof['actualExit']!=0 or proof['source']!=result['sourceSnapshot'] or proof['physicalMain']!=764:
        raise ValueError('same-source actual ten Backup factory proof first')
    entry.configure()
    return public.main(factory_run_name=run.name,measurement_module=selected,required_counts=(864,101,54),
        case_overrides=ids.revalidated_case_ids(),extra_suites=entry.extra_suites(),case_name_aliases=entry.aliases.invocation_aliases(),
        extra_fields={'newIndependentCases':0,'priorIndependentCasesRevalidated':54,'newJavaCasesInThisGroup':0,
        'spec':'1075_BackupWorker・Copy・Bundle10_factory所有_PT仕様.md','ssc':['SSC308'],'bugs':['BUG1414'],'ykt':['YKT1178'],
        'backupWorkerBytecodeProofSha256':selected.sha(path),'storageFourCounters':result['storageFourCounters'],
        'semanticClasses':3,'nestedDebugEquivalent':proof['nestedDebugEquivalent'],
        'otherPhysicalClassesUnchanged':proof['otherPhysicalClassesUnchanged'],'targetClassCounters':proof['targetClassCounters'],
        'checkedNullIoFactories':3,'directPortFactories':4,'rawDirectoryFactories':2,'rawChannelFactories':1,
        'wholeHorizontalComplete':False})


if __name__=='__main__':raise SystemExit(main())
