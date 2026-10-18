"""Actual prebuilt handoff state/ports, nonnull-last transfer, old scope bytecode and four100."""
import json
import os
import re
import xml.etree.ElementTree as ET
import pg5138_factory_bytecode as bytecode
import pg5150_native_fd_bytecode as native
import pg5296_handoff_selected as entry

SOURCE='5eb1d4c44650b79aa8983f044531b3e3e22e214e'
CLASS='dev.codex.schubert.nk.storage.ResourceScope'


def main():
    root=entry.selected.ROOT;work=root.parent/'pgpt-runs/PG379'
    run=work/'pg5296-handoff-green-v1';prior_run=work/'pg5288-morning-launch-green-v1'
    result=json.loads((run/'manifest.safe.json').read_bytes())
    if result['sourceSnapshot']!=SOURCE or result['actualExit']!=0 or result['phaseExits']!=[0,0] or result['tests']!=1011 or result['suites']!=124:
        raise ValueError('exact original complete1011/124 selected first')
    old_manifest=json.loads((prior_run/'manifest.safe.json').read_bytes())
    before=old_manifest['mainDelta']['physicalSha256'];after=result['mainDelta']['physicalSha256']
    changed={k for k in before if k in after and before[k]!=after[k]}
    key='storage:'+CLASS.replace('.','/')+'.class'
    if set(before)!=set(after) or len(after)!=764 or changed!={key}:
        raise ValueError('one ResourceScope semantic class only/all other763 byte-identical')
    old,old_hash=bytecode.decode(prior_run/'source','storage',CLASS)
    current,hashed=bytecode.decode(run/'source','storage',CLASS)
    native.require_reference(before,key,old_hash['classSha256'])
    old_names={m['header'] for m in old};new_names={m['header'] for m in current}
    if not old_names<new_names:raise ValueError('all old scope methods retained')
    added=[m for m in current if m['header'] not in old_names]
    if len(added)!=3 or sum(bytecode.named(m,'handoff') for m in added)!=1 or sum('lambda$handoff$' in m['header'] for m in added)!=2:
        raise ValueError('only handoff and two prebuilt implementation callbacks added')
    native.same_methods(old,[m for m in current if m['header'] in old_names])
    handoff=bytecode.one([m for m in added if bytecode.named(m,'handoff')],'one handoff')
    invoke=bytecode.index_of(handoff,'Method acquire:')
    prefix=handoff['ops'][:invoke]
    arrays=[o for o in prefix if o[1]=='newarray' and 'boolean' in o[2]]
    ports=[o for o in prefix if o[1]=='invokedynamic']
    guards=[o for o in prefix if 'Objects.requireNonNull:' in o[2]]
    if len(arrays)!=1 or len(ports)!=2 or len(guards)!=3 or max(o[0] for o in guards)>=arrays[0][0] or arrays[0][0]>=ports[0][0]:
        raise ValueError('nonnull guards, primitive state and both ports must precede acquisition')
    if not all('ResourceScope$'+kind+';' in op[2] for op,kind in zip(ports,('Release','OwnedAction'))):
        raise ValueError('ordered prebuilt release/assembly ports')
    if [o[1] for o in handoff['ops'][invoke+1:]]!=['areturn']:
        raise ValueError('no work after returned complete owner')
    assembly=bytecode.one([m for m in added if any('ResourceScope$OwnedAction.run:' in o[2] for o in m['ops'])],'one assembly')
    owned=bytecode.index_of(assembly,'ResourceScope$OwnedAction.run:')
    required=bytecode.index_of(assembly,'Objects.requireNonNull:')
    stores=[i for i,o in enumerate(assembly['ops']) if o[1]=='bastore']
    if len(stores)!=1 or not owned<required<stores[0]:raise ValueError('only complete nonnull owner transfers')
    if any(re.fullmatch(r'aload(?:_\d+)?|areturn',o[1]) is None for o in assembly['ops'][stores[0]+1:]):
        raise ValueError('primitive transfer must immediately return without heap/callback work')
    release=bytecode.one([m for m in added if any('ResourceScope$Release.close:' in o[2] for o in m['ops'])],'one conditional release')
    if sum(o[1]=='baload' for o in release['ops'])!=1 or sum(o[1].startswith('if') for o in release['ops'])!=1 or sum('ResourceScope$Release.close:' in o[2] for o in release['ops'])!=1:
        raise ValueError('exact one conditional release of the preexisting resource')
    report=ET.parse(run/'source/src/schubert-nk-storage/target/site/jacoco/jacoco.xml').getroot()
    target=bytecode.one([c for c in report.findall('package/class') if c.get('name')==CLASS.replace('.','/')],'current scope counters')
    counters={c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))}
        for c in target.findall('counter') if c.get('type') in ('LINE','METHOD','CLASS','BRANCH')}
    if len(counters)!=4 or any(c['missed'] for c in counters.values()):raise ValueError('all scope four counters must be100')
    value={'source':SOURCE,'actualExit':0,'physicalMain':764,'semanticClasses':1,'otherPhysicalClassesUnchanged':763,
        'class':hashed,'priorClass':old_hash,'allPriorScopeMethodOpcodesAndHandlersUnchanged':True,
        'handoff':handoff,'assembly':assembly,'conditionalRelease':release,'scopeFourCounters':counters,
        'storageFourCounters':result['storageFourCounters'],'selectedManifestSha256':entry.selected.sha(run/'manifest.safe.json'),
        'newCases':6,'oldTwelveTestOraclesChanged':False,'original237ClosedDelta':0,'formalAccepted':False,
        'nativeImported':False,'wholeHorizontalComplete':False,'actualHeapOomReproduced':False,'vmActions':0,'testReplays':0,
        'bugs':['BUG1414'],'ykt':['YKT1178'],'ssc':['SSC308']}
    out=root/'evidence/01_PT/003_NK-PRO-003/evidence/provisional/PG5298-handoff-bytecode-v1'
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'scopeFourCounters':counters,'sha256':entry.selected.sha(out/'manifest.json')}))


if __name__=='__main__':main()
