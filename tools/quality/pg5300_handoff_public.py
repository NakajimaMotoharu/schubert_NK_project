"""Six new handoff cases and original same-source1011, no old scope success substitution."""
import json
import pg5122_root_elf_public as public
import pg5252_startup_view_public as old_ids
import pg5296_handoff_selected as entry
from pg5296_handoff_selected_test import METHODS


def revalidated_case_ids(handoff_new=False):
    values=old_ids.revalidated_case_ids()
    for number,name in enumerate(METHODS,13):
        values[('dev.codex.schubert.nk.storage.FactoryResourceScopeTest',name)]={
            'testId':'PT-IOFACT-'+str(number).zfill(3),'newIndependentCase':True,'newInThisChange':handoff_new}
    return values


def main():
    run=public.W/'pg5296-handoff-green-v1';result=json.loads((run/'manifest.safe.json').read_bytes())
    path=entry.selected.ROOT/'evidence/01_PT/003_NK-PRO-003/evidence/provisional/PG5298-handoff-bytecode-v1/manifest.json'
    proof=json.loads(path.read_bytes())
    if proof['actualExit']!=0 or proof['source']!=result['sourceSnapshot'] or proof['physicalMain']!=764:
        raise ValueError('current complete handoff/four100 proof required')
    entry.configure()
    return public.main(factory_run_name=run.name,measurement_module=entry.selected,required_counts=(1011,124,60),
        case_overrides=revalidated_case_ids(handoff_new=True),extra_suites=entry.extra_suites(),
        case_name_aliases=entry.aliases.invocation_aliases(),
        extra_fields={'newIndependentCases':6,'priorIndependentCasesRevalidated':54,'newJavaCasesInThisGroup':6,
            'spec':'003_NK-PRO-003/022_完成owner_handoff_独立単体テスト仕様.md',
            'ssc':['SSC308'],'bugs':['BUG1414'],'ykt':['YKT1178'],'handoffBytecodeProofSha256':entry.selected.sha(path),
            'semanticClasses':1,'otherPhysicalClassesUnchanged':763,'scopeFourCounters':proof['scopeFourCounters'],
            'storageFourCounters':result['storageFourCounters'],'original237ClosedDelta':0,'wholeHorizontalComplete':False})


if __name__=='__main__':raise SystemExit(main())
