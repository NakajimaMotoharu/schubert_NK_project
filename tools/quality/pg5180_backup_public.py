"""Original611/78 allowlist publication after checked-null/FD-wrapper/physical proof, no replay."""
import json
import pg5122_root_elf_public as public
import pg5176_backup_selected as entry

selected=entry.selected


def revalidated_case_ids():
    child=('childfd009OwnerSetAdoptsBothAndConsumesProofBeforeAdmissionOnce',
           'childfd010OwnerSetCompoundFailuresKeepIndependentPriorityAndBothConsumption')
    overrides={('dev.codex.schubert.nk.storage.LinuxStartupAdmissionTest',name):
       {'testId':'PT-OPS-CHILDFD-'+str(i).zfill(3),'newIndependentCase':True,'newInThisChange':False}
       for i,name in enumerate(child,9)}
    overrides[('dev.codex.schubert.nk.bootstrap.NativeCoverageExportTest',
       'nchannel193001ReadOnlyAgentMetadataRequiresExactlyOneLink')]={
       'testId':'PT-NEXPORT193-META001','newIndependentCase':True,'newInThisChange':False}
    return overrides


def main():
    run=public.W/'pg5176-backup-scopes-green-v1'
    result=json.loads((run/'manifest.safe.json').read_bytes())
    path=selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5178-backup-bytecode-v1/manifest.json'
    proof=json.loads(path.read_bytes())
    if proof['actualExit']!=0 or proof['source']!=result['sourceSnapshot'] or proof['physicalMain']!=764:
        raise ValueError('same-source actual19 checked-null/bytecode proof first')
    entry.configure()
    overrides=revalidated_case_ids()
    return public.main(factory_run_name=run.name,measurement_module=selected,
       required_counts=(611,78,42),case_overrides=overrides,extra_suites=entry.extra_suites(),
       extra_fields={'newIndependentCases':0,'priorIndependentCasesRevalidated':42,'newJavaCasesInThisChange':0,
       'spec':'1057_BackupManifest保持scope_factory所有_PT仕様.md',
       'ssc':['SSC308'],'bugs':['BUG1414'],'ykt':['YKT1178'],'backupScopeBytecodeProofSha256':selected.sha(path),
       'storageFourCounters':result['storageFourCounters'],'newChangedOuterClasses':3,
       'nestedDebugEquivalent':proof['nestedDebugEquivalent'],'otherPhysicalClassesUnchanged':proof['otherPhysicalClassesUnchanged'],
       'checkedNullIoFactories':7,'writerProviderPreallocatesWrapper':True,'wholeHorizontalComplete':False})


if __name__=='__main__':raise SystemExit(main())
