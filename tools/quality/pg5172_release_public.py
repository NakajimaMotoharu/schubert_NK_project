"""Original537/73 and sixteen immutable-release scopes, no test/VM replay."""
import json
import pg5122_root_elf_public as public
import pg5168_release_selected as entry

selected=entry.selected


def main():
    run=public.W/'pg5168-release-scopes-green-v1'
    result=json.loads((run/'manifest.safe.json').read_bytes())
    path=selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5170-release-bytecode-v1/manifest.json'
    proof=json.loads(path.read_bytes())
    if proof['actualExit']!=0 or proof['source']!=result['sourceSnapshot'] or proof['physicalMain']!=764:
        raise ValueError('same-source exact16 proof and physical delta first')
    entry.configure()
    child=('childfd009OwnerSetAdoptsBothAndConsumesProofBeforeAdmissionOnce',
           'childfd010OwnerSetCompoundFailuresKeepIndependentPriorityAndBothConsumption')
    overrides={('dev.codex.schubert.nk.storage.LinuxStartupAdmissionTest',name):
       {'testId':'PT-OPS-CHILDFD-'+str(i).zfill(3),'newIndependentCase':True,'newInThisChange':False}
       for i,name in enumerate(child,9)}
    overrides[('dev.codex.schubert.nk.bootstrap.NativeCoverageExportTest',
       'nchannel193001ReadOnlyAgentMetadataRequiresExactlyOneLink')]={
       'testId':'PT-NEXPORT193-META001','newIndependentCase':True,'newInThisChange':False}
    return public.main(factory_run_name=run.name,measurement_module=selected,
       required_counts=(537,73,42),case_overrides=overrides,extra_suites=entry.bootstrap.bootstrap_suites(),
       extra_fields={'newIndependentCases':0,'priorIndependentCasesRevalidated':42,'newJavaCasesInThisChange':0,
       'spec':'1055_immutableRelease保持scope_factory所有_PT仕様.md',
       'ssc':['SSC308'],'bugs':['BUG1414'],'ykt':['YKT1178'],'releaseScopeBytecodeProofSha256':selected.sha(path),
       'storageFourCounters':result['storageFourCounters'],'newChangedOuterClasses':2,
       'nestedDebugEquivalent':proof['debugEquivalent'],'otherPhysicalClassesUnchanged':proof['otherPhysicalClassesUnchanged'],
       'metadataCheckedCounters':proof['metadataCheckedCounters'],
       'coverageDirectoryClassCounters':proof['coverageDirectoryClassCounters'],
       'metadataBranch100':True,'coverageDirectoryClassBranch100':True,'wholeHorizontalComplete':False})


if __name__=='__main__':raise SystemExit(main())
