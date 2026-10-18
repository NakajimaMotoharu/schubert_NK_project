"""Shared limited publication/classification, strict current proof and basename contracts."""
import json
import os
import re
import pg5122_root_elf_public as public
import pg5252_startup_view_public as ids
import pg5261_scope_inventory_continue as carry


def validate_proof(proof,result,main):
    if type(proof['actualExit']) is not int or proof['actualExit']!=0:
        raise ValueError('genuine actual integer zero proof required')
    if not re.fullmatch(r'[0-9a-f]{40}',proof['source']) or proof['source']!=result['sourceSnapshot']:
        raise ValueError('exact immutable current source proof required')
    if proof['physicalMain']!=main:raise ValueError('exact physical current Main count')


def new_files(entry):
    names=getattr(entry,'FILES',entry.OUTERS)
    if not names or any(re.fullmatch(r'[A-Z][A-Za-z0-9]*',n) is None for n in names):
        raise ValueError('explicit original outer class basenames, no nested or filename ambiguity')
    return {n+'.java' for n in names}


def publish_current(*,entry,run_name,proof_name,counts,spec,proof_key,extra):
    run=public.W/run_name;result=json.loads((run/'manifest.safe.json').read_bytes())
    path=entry.selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/proof_name/'manifest.json'
    proof=json.loads(path.read_bytes());validate_proof(proof,result,764)
    fields={'newIndependentCases':0,'priorIndependentCasesRevalidated':54,'newJavaCasesInThisGroup':0,
        'spec':spec,'ssc':['SSC308'],'bugs':['BUG1414'],'ykt':['YKT1178'],
        proof_key:entry.selected.sha(path),'storageFourCounters':result['storageFourCounters'],
        'semanticClasses':proof['semanticClasses'],'nestedDebugEquivalent':proof['nestedDebugEquivalent'],
        'otherPhysicalClassesUnchanged':proof['otherPhysicalClassesUnchanged'],'targetClassCounters':proof['targetClassCounters'],
        'nativeOwnerExecutionQualified':False,'wholeHorizontalComplete':False}
    fields.update(extra);entry.configure()
    return public.main(factory_run_name=run_name,measurement_module=entry.selected,required_counts=(*counts,54),
        case_overrides=ids.revalidated_case_ids(),extra_suites=entry.extra_suites(),case_name_aliases=entry.aliases.invocation_aliases(),
        extra_fields=fields)


def classify_current(*,entry,source,previous_ref,previous_sha,previous_source,qualified_ref,tests,suites,counts,out_name):
    value,proof=carry.continue_current(root=entry.selected.ROOT,sha=entry.selected.sha,
        previous_ref=previous_ref,previous_sha=previous_sha,previous_source=previous_source,
        source=source,qualified_ref=qualified_ref,tests=tests,suites=suites,new_files=new_files(entry),expected_counts=counts)
    value.update(semanticClasses=proof['semanticClasses'],nestedDebugEquivalent=proof['nestedDebugEquivalent'],
        otherPhysicalClassesUnchanged=proof['otherPhysicalClassesUnchanged'],nativeOwnerExecutionQualified=False)
    out=entry.selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/out_name
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'counts':value['classificationCounts'],'sha256':entry.selected.sha(out/'manifest.json')}))
