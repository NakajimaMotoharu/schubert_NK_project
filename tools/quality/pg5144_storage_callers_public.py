"""Re-use independent allowlist projection against original d916 snapshot, no test/VM replay."""
import json
import pg5122_root_elf_public as public
import pg5140_storage_callers_selected as selected


def main():
    root=selected.ROOT
    proof=root/'evidence/01_PT/003_NK-PRO-003/evidence/provisional/PG5142-storage-callers-bytecode-v3/manifest.json'
    evidence=json.loads(proof.read_bytes())
    run=public.W/'pg5140-storage-callers-green-v3'
    measured=json.loads((run/'manifest.safe.json').read_bytes())
    if evidence['actualExit'] != 0 or evidence['source'] != measured['sourceSnapshot']:
        raise ValueError('same-source actual caller/factory proof first')
    # Re-read all 762 class identities; old root/common proof uses only unchanged exact classes.
    old=json.loads((public.W/'pg5136-factory-io-green-v6/manifest.safe.json').read_bytes())
    before=old['mainDelta']['physicalSha256'];after=measured['mainDelta']['physicalSha256']
    names=('StorageRootInspection','ExistingFileAccess','ServiceConfigFiles','LinuxFilesystemClassifier')
    expected={'storage:dev/codex/schubert/nk/storage/'+name+'.class' for name in names}
    if set(before)!=set(after) or {key for key in before if before[key]!=after[key]} != expected:
        raise ValueError('exact four new caller classes; unchanged root/common actual proof only')
    return public.main(factory_run_name=run.name,measurement_module=selected,extra_fields={
       'newIndependentCases':0,'priorIndependentCasesRevalidated':39,'newJavaCasesInThisChange':0,
       'spec':'003_NK-PRO-003/018_storage共通caller所有_単体テスト仕様.md',
       'ssc':['SSC308'],'bugs':['BUG1414','BUG1422','BUG1423'],'ykt':['YKT1178','YKT1186','YKT1187'],
       'callerBytecodeProofSha256':selected.sha(proof),'storageFourCounters':measured['storageFourCounters'],
       'newChangedCallerClasses':sorted(expected),'allOtherSelectedClassesByteIdenticalToPG5136':758,
       'wholeHorizontalComplete':False,'wholeCoverage100':False})


if __name__=='__main__':raise SystemExit(main())
