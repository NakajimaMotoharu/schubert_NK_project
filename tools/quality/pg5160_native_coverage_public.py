"""Original536/73 exact input/XML/class projection; no prior source native/coverage imported."""
import json
import pg5122_root_elf_public as public
import pg5156_native_coverage_selected as entry

selected=entry.selected


def main():
    run=public.W/'pg5156-native-coverage-green-v2'
    result=json.loads((run/'manifest.safe.json').read_bytes())
    path=selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5158-native-coverage-directory-bytecode-v1/manifest.json'
    proof=json.loads(path.read_bytes())
    if proof['actualExit']!=0 or proof['source']!=result['sourceSnapshot'] or proof['physicalMain']!=764:
        raise ValueError('complete same-source7-scope proof and exact physical delta first')
    selected.EXTRA_CHANGED={'bootstrap:dev/codex/schubert/nk/bootstrap/NativeCoveragePrivateFile.class'}
    names=('childfd009OwnerSetAdoptsBothAndConsumesProofBeforeAdmissionOnce',
           'childfd010OwnerSetCompoundFailuresKeepIndependentPriorityAndBothConsumption')
    overrides={('dev.codex.schubert.nk.storage.LinuxStartupAdmissionTest',name):
       {'testId':'PT-OPS-CHILDFD-'+str(i).zfill(3),'newIndependentCase':True,'newInThisChange':False}
       for i,name in enumerate(names,9)}
    return public.main(factory_run_name=run.name,measurement_module=selected,
       required_counts=(536,73,41),case_overrides=overrides,extra_suites=entry.bootstrap_suites(),extra_fields={
       'newIndependentCases':0,'priorIndependentCasesRevalidated':41,'newJavaCasesInThisChange':0,
       'spec':'1053_nativeCoverage保持directory_factory所有_PT仕様.md',
       'ssc':['SSC308'],'bugs':['BUG1414','BUG1427','BUG1428'],'ykt':['YKT1178','YKT1191','YKT1192'],
       'coverageDirectoryBytecodeProofSha256':selected.sha(path),'storageFourCounters':result['storageFourCounters'],
       'targetCoverageClassCounters':proof['targetClassCounters'],'targetClassFour100':proof['targetWholeCoverage100'],
       'newChangedPhysicalClasses':1,'otherPreviousPhysicalClassesByteIdentical':763,'wholeHorizontalComplete':False})


if __name__=='__main__':raise SystemExit(main())
