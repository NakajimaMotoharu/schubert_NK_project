"""Read-only same-source owner-port/raw-return proof; no acceptance or old counter import."""
import json
import os
import re
import xml.etree.ElementTree as ET
import pg5138_factory_bytecode as bytecode
import pg5142_storage_callers_bytecode as caller
import pg5150_native_fd_bytecode as native
import pg5122_root_elf_public as public


def validate_module(entry,module):
    if module not in ('storage','bootstrap','batch') or not entry.PREFIX.startswith(module+':'):
        raise ValueError('explicit compiled module and matching physical class namespace required')
    return module


def prove(*,entry,run_name,prior_name,source,tests,suites,package,scopes,kinds,out_name,qualification_path=None,module='batch'):
    validate_module(entry,module)
    if re.fullmatch(r'[0-9a-f]{40}',source) is None:
        raise ValueError('source pin must be a full40hex commit')
    selected=entry.selected;work=selected.ROOT.parent/'pgpt-runs/PG379'
    run=work/run_name;prior_run=work/prior_name
    original_path=run/'manifest.safe.json'
    result=json.loads((qualification_path or original_path).read_bytes())
    if qualification_path is not None:
        if qualification_path!=run/'qualification.safe.json':raise ValueError('fixed original job qualification only')
        public.validate_separate_qualification(result,json.loads(original_path.read_bytes()),selected.sha(original_path))
    if result['actualExit']!=0 or result['phaseExits']!=[0,0] or result['tests']!=tests or result['suites']!=suites or result['sourceSnapshot']!=source:
        raise ValueError('exact original selected source, terminal and all current counts required')
    prior=json.loads((prior_run/'manifest.safe.json').read_bytes())
    if prior.get('actualExit')!=0:
        prior_qualification=prior_run/'qualification.safe.json'
        qualified=json.loads(prior_qualification.read_bytes())
        public.validate_separate_qualification(qualified,prior,selected.sha(prior_run/'manifest.safe.json'))
        if type(qualified['actualExit']) is not int or qualified['actualExit']!=0 or qualified['phaseExits']!=[0,0]:
            raise ValueError('prior reference must have genuine independent qualification')
        prior=qualified
    before=prior['mainDelta']['physicalSha256'];after=result['mainDelta']['physicalSha256']
    required={entry.PREFIX+n+'.class' for n in entry.OUTERS};optional={entry.PREFIX+n+'.class' for n in entry.DEBUG}
    changed={key for key in before if key in after and before[key]!=after[key]}
    if set(before)!=set(after) or not required<=changed or not changed<=required|optional:
        raise ValueError('declared semantic outers and bounded nested candidates only')
    proofs={}
    for name,expected in scopes.items():
        methods,hashed=bytecode.decode(run/'source',module,package+name)
        actual=caller.callers(methods)
        if len(actual)!=expected:raise ValueError('exact caller count '+name)
        factories=[]
        for needle,count in kinds[name].items():
            found=[m for m in methods if any(needle in op[2] for op in m['ops'])]
            if len(found)!=count:raise ValueError('exact factory '+name+needle)
            for method in found:
                factories.append({'method':method['header'],'acquisition':needle,'rawReturnPcs':caller.tail(method,needle)})
        proofs[name]={'scopes':actual,'factories':factories,**hashed}
    debug=[]
    for key in sorted(changed-required):
        name=key.split(':',1)[1][:-6].replace('/','.')
        old,old_hash=bytecode.decode(prior_run/'source',module,name)
        current,current_hash=bytecode.decode(run/'source',module,name)
        native.require_reference(before,key,old_hash['classSha256']);native.same_methods(old,current)
        debug.append({'class':name,'old':old_hash,'current':current_hash,'allOpcodeHandlerSemanticsEqual':True})
    report=ET.parse(run/('source/src/schubert-nk-'+module+'/target/site/jacoco/jacoco.xml')).getroot()
    targets={c.get('name'):{v.get('type'):{'missed':int(v.get('missed')),'covered':int(v.get('covered'))}
        for v in c.findall('counter') if v.get('type') in ('LINE','METHOD','CLASS','BRANCH')}
        for c in report.findall('package/class') if c.get('name') in {package.replace('.','/')+n for n in scopes}}
    if len(targets)!=len(scopes):raise ValueError('all current target counters including zero-executed classes')
    value={'source':source,'actualExit':0,'physicalMain':len(after),'proofs':proofs,
        'selectedManifestSha256':selected.sha(run/'manifest.safe.json'),'semanticClasses':len(required),
        'nestedDebugEquivalent':debug,'otherPhysicalClassesUnchanged':len(after)-len(changed),'targetClassCounters':targets,
        'bugs':['BUG1414'],'ykt':['YKT1178'],'ssc':['SSC308'],'wholeHorizontalComplete':False,
        'formalAccepted':False,'nativeImported':False,'actualHeapOomReproduced':False,'vmActions':0,'testReplays':0}
    if qualification_path is not None:
        value.update(originalRunnerActualExit=1,selectedQualificationSha256=selected.sha(qualification_path),
            qualificationKind=result['qualificationKind'])
    return run,value


def publish(entry,value,out_name):
    out=entry.selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/out_name
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'scopes':sum(len(v['scopes']) for v in value['proofs'].values()),
        'debugCount':len(value['nestedDebugEquivalent']),'sha256':entry.selected.sha(out/'manifest.json')}))
