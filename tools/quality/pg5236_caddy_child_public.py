"""Original812/96 and four Caddy/Child read factories, no live config/Unit/VM changes."""
import json
import pg5122_root_elf_public as public
import pg5180_backup_public as common
import pg5204_morning_owner_public as morning
import pg5232_caddy_child_selected as entry

selected=entry.selected


def main():
    run=public.W/'pg5232-caddy-child-green-v1'
    result=json.loads((run/'manifest.safe.json').read_bytes())
    path=selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5234-caddy-child-bytecode-v1/manifest.json'
    proof=json.loads(path.read_bytes())
    if proof['actualExit']!=0 or proof['source']!=result['sourceSnapshot'] or proof['physicalMain']!=764:
        raise ValueError('same-source actual4 direct-return proof first')
    entry.configure();overrides=common.revalidated_case_ids()
    overrides.update({('dev.codex.schubert.nk.batch.file.MorningBackupRequestPublicationTest',name):
        {'testId':'PT-OPS-MBPUB'+str(i).zfill(3),'newIndependentCase':True,'newInThisChange':False}
        for i,name in enumerate(morning.NAMES,7)})
    return public.main(factory_run_name=run.name,measurement_module=selected,required_counts=(812,96,46),
        case_overrides=overrides,extra_suites=entry.extra_suites(),case_name_aliases=entry.previous.aliases.invocation_aliases(),
        extra_fields={'newIndependentCases':0,'priorIndependentCasesRevalidated':46,'newJavaCasesInThisChange':0,
        'spec':'1071_Caddy公開設定・Childnative読取4_factory所有_PT仕様.md','ssc':['SSC308'],'bugs':['BUG1414'],'ykt':['YKT1178'],
        'caddyChildBytecodeProofSha256':selected.sha(path),'storageFourCounters':result['storageFourCounters'],
        'semanticClasses':2,'otherPhysicalClassesUnchanged':762,'targetClassCounters':proof['targetClassCounters'],
        'rawStreamFactories':2,'directoryFactories':2,'wholeHorizontalComplete':False})


if __name__=='__main__':raise SystemExit(main())
