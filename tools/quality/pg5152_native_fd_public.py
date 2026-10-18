"""Only original 224/32, native FD bytecode and all764 physical classes; never test replay."""
import json
import pg5122_root_elf_public as public
import pg5148_native_fd_selected as selected


def main():
    run=public.W/'pg5148-native-fd-green-v2'
    measured=json.loads((run/'manifest.safe.json').read_bytes())
    path=selected.ROOT/'evidence/01_PT/003_NK-PRO-003/evidence/provisional/PG5150-native-fd-bytecode-v1/manifest.json'
    proof=json.loads(path.read_bytes())
    if proof['actualExit']!=0 or proof['source']!=measured['sourceSnapshot'] or proof['physicalMain']!=764:
        raise ValueError('complete original-source native FD bytecode/physical proof first')
    names=('childfd009OwnerSetAdoptsBothAndConsumesProofBeforeAdmissionOnce',
           'childfd010OwnerSetCompoundFailuresKeepIndependentPriorityAndBothConsumption')
    overrides={('dev.codex.schubert.nk.storage.LinuxStartupAdmissionTest',name):
               {'testId':'PT-OPS-CHILDFD-'+str(i).zfill(3),'newIndependentCase':True,'newInThisChange':True}
               for i,name in enumerate(names,9)}
    return public.main(factory_run_name=run.name,measurement_module=selected,
       required_counts=(224,32,41),case_overrides=overrides,extra_fields={
       'newIndependentCases':2,'priorIndependentCasesRevalidated':39,'newJavaCasesInThisChange':2,
       'spec':'003_NK-PRO-003/020_native_FD取得と二継承FD所有_単体テスト仕様.md',
       'ssc':['SSC308'],'bugs':['BUG1414','BUG1422','BUG1424','BUG1425'],
       'ykt':['YKT1178','YKT1186','YKT1188','YKT1189'],
       'nativeDescriptorBytecodeProofSha256':selected.sha(path),
       'storageFourCounters':measured['storageFourCounters'],
       'nestedDebugEquivalent':proof['nestedDebugEquivalent'],'wholeHorizontalComplete':False})


if __name__=='__main__':raise SystemExit(main())
