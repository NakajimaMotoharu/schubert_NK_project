"""Typed native catch primary with bounded first/known/drain phases; no heap before remaining drain."""
import json
import os
import subprocess
import xml.etree.ElementTree as ET
import pg5138_factory_bytecode as bytecode
import pg5142_storage_callers_bytecode as caller
import pg5150_native_fd_bytecode as native
from pg5242_startup_view_bytecode import registration
import pg5248_startup_view_selected as entry

selected=entry.selected
RUN=selected.ROOT.parent/'pgpt-runs/PG379/pg5248-startup-view-owner-green-v1'
CLASS='dev.codex.schubert.nk.batch.file.StartupAdmissionFile'
ENTRY=entry.previous
HEAP={'new','newarray','anewarray','multianewarray','invokedynamic','ldc','ldc_w'}


def native_loop(method,delegates):
    ops=method['ops'];at=bytecode.index_of(method,'DirectoryCalls.close:');pc=ops[at][0]
    back=bytecode.one([i for i,op in enumerate(ops) if op[1]=='goto' and i>at and int(op[2].split()[0])<=pc],
                      'one finite reverse native-close loop per phase')
    if any(op[1] in HEAP for op in ops[:back+1]):raise ValueError('phase may not allocate during native drain')
    for op in ops[:back+1]:
        if op[1].startswith('invoke') and 'DirectoryCalls.close:' not in op[2] and not any(
                name+':' in op[2] for name in delegates):
            raise ValueError('only native close or explicitly verified remaining-drain delegates')
    handlers={kind for start,end,_,kind in method['handlers'] if start<=pc<end}
    if not {'Class dev/codex/schubert/nk/storage/StorageIoException','Class java/lang/RuntimeException',
            'Class java/lang/Error'}<=handlers:raise ValueError('all close failure categories must drain')
    if 'appendSecondary' in delegates:
        drained=bytecode.index_of(method,'drain:(I)V');appended=bytecode.index_of(method,'appendSecondary:')
        if drained>=appended:raise ValueError('secondary aggregation only after delegated full remaining drain')
        if [op[1] for op in ops[drained-3:drained]]!=['iload_1','iconst_1','isub'] and not (
                ops[drained-3][1].startswith('iload') and [op[1] for op in ops[drained-2:drained]]==['iconst_1','isub']):
            raise ValueError('remaining drain starts strictly below already-consumed current FD')
    return {'method':method['header'],'nativeClosePc':pc,'loopBackPc':ops[back][0],
        'handlerTypes':sorted(handlers),'heapFreeBeforeLoopExit':True,'delegates':sorted(delegates)}


def main():
    result=json.loads((RUN/'manifest.safe.json').read_bytes())
    if result['actualExit']!=0 or result['phaseExits']!=[0,0] or result['tests']!=829 or result['suites']!=98:
        raise ValueError('new original829/98 static0 complete first, never failed673')
    prior_run=selected.ROOT.parent/'pgpt-runs/PG379/pg5232-caddy-child-green-v1'
    prior=json.loads((prior_run/'manifest.safe.json').read_bytes())
    before=prior['mainDelta']['physicalSha256'];after=result['mainDelta']['physicalSha256']
    required={ENTRY.PREFIX+n+'.class' for n in ENTRY.OUTERS};optional={ENTRY.PREFIX+n+'.class' for n in ENTRY.DEBUG}
    changed={key for key in before if key in after and before[key]!=after[key]}
    if set(before)!=set(after) or not required<=changed or not changed<=required|optional:
        raise ValueError('only outer/ViewOwner semantics and explicitly bounded nested references')
    outer,outer_hash=bytecode.decode(RUN/'source','batch',CLASS)
    if len(caller.callers(outer))!=1:raise ValueError('one prebuilt factory owner scope')
    factory=bytecode.one([m for m in outer if any(op[1]=='new' and '$ViewOwner' in op[2] for op in m['ops'])],
                        'one owner factory before native IO')
    add=bytecode.index_of(factory,'Math.addExact:')
    if not any(op[1]=='iconst_3' for op in factory['ops'][:add]):raise ValueError('N+root/app/entry3')
    owner,owner_hash=bytecode.decode(RUN/'source','batch',CLASS+'$ViewOwner')
    ctor=bytecode.one([m for m in owner if '$ViewOwner(' in m['header']],'one primitive owner constructor')
    if sum(op[1]=='newarray' for op in ctor['ops'])!=2 or any(op[1]=='anewarray' for op in ctor['ops']):
        raise ValueError('primitive int FD and boolean secondary bitmap both preallocated')
    if any('DirectoryCalls.open' in op[2] for op in ctor['ops']):raise ValueError('constructor has no native IO')
    if any('Integer.valueOf:' in op[2] or 'ArrayList' in op[2] or op[1]=='checkcast' and 'java/lang/RuntimeException' in op[2]
            for m in owner for op in m['ops']):raise ValueError('no FD boxing/grow or erased Runtime cast')
    acquisition={}
    for name in ('openRoot','openDirectory','openEntry'):
        method=bytecode.one([m for m in owner if bytecode.named(m,name)],'one primitive '+name)
        acquisition[name]=registration(method,'DirectoryCalls.'+name+':')
    phases={name:bytecode.one([m for m in owner if bytecode.named(m,name)],'one '+name)
            for name in ('close','closeAfterKnown','drain','appendSecondary')}
    proofs={'close':native_loop(phases['close'],{'closeAfterKnown','drain','appendSecondary'}),
            'known':native_loop(phases['closeAfterKnown'],{'drain','appendSecondary'}),
            'drain':native_loop(phases['drain'],set())}
    closing=phases['closeAfterKnown'];back=proofs['known']['loopBackPc']
    if any(op[0]<=back for op in closing['ops'] if op[1]=='new' or 'getSuppressed:' in op[2]):
        raise ValueError('known IO normalization only after final remaining native attempt')
    if any('DirectoryCalls.' in op[2] for op in phases['appendSecondary']['ops']):
        raise ValueError('suppression phase cannot touch native resources')
    if any('Method '+name+':' in op[2] for name,m in phases.items() for op in m['ops']):
        raise ValueError('no recursive drain/aggregation')
    verbose=subprocess.check_output([str(bytecode.JAVAP),'-p','-v','-classpath',
        str(RUN/'source/src/schubert-nk-batch/target/classes'),CLASS+'$ViewOwner'],text=True)
    if 'ACC_SYNTHETIC' in verbose:raise ValueError('do not move unknown throws into synthetic methods')
    nested=[]
    for key in sorted(changed-required):
        name=key.split(':',1)[1][:-6].replace('/','.')
        old,old_hash=bytecode.decode(prior_run/'source','batch',name)
        current,current_hash=bytecode.decode(RUN/'source','batch',name)
        native.require_reference(before,key,old_hash['classSha256']);native.same_methods(old,current)
        nested.append({'class':name,'old':old_hash,'current':current_hash,'allOpcodeHandlerSemanticsEqual':True,
            'ownerPackageAccessReference':name.endswith('$ViewOperation'),'notClaimedPureDebugOnly':name.endswith('$ViewOperation')})
    report=ET.parse(RUN/'source/src/schubert-nk-batch/target/site/jacoco/jacoco.xml').getroot()
    target=bytecode.one([c for c in report.findall('package/class') if c.get('name')==(CLASS+'$ViewOwner').replace('.','/')],
                        'one current Owner counters')
    four={v.get('type'):{'missed':int(v.get('missed')),'covered':int(v.get('covered'))}
          for v in target.findall('counter') if v.get('type') in ('LINE','METHOD','CLASS','BRANCH')}
    if set(four)!={'LINE','METHOD','CLASS','BRANCH'} or any(v['missed'] or v['covered']<=0 for v in four.values()):
        raise ValueError('current Owner four counters100 without exclusions')
    value={'source':result['sourceSnapshot'],'actualExit':0,'physicalMain':764,'outer':outer_hash,'owner':owner_hash,
        'acquisitionProof':acquisition,'drainPhases':proofs,'ownerFourCounters':four,'capacityExtraRootAppEntry':3,
        'typedNativeCatchPrimaryPreserved':True,'secondaryPrimitiveBitmap':True,'noSyntheticThrowEscape':True,
        'selectedManifestSha256':selected.sha(RUN/'manifest.safe.json'),'semanticClasses':2,'nestedMethodEquivalent':nested,
        'otherPhysicalClassesUnchanged':762-len(nested),'failedSource673Imported':False,
        'bugs':['BUG1414','BUG1432'],'ykt':['YKT1178','YKT1196'],'ssc':['SSC308'],'wholeHorizontalComplete':False,
        'formalAccepted':False,'nativeImported':False,'actualHeapOomReproduced':False,'vmActions':0,'testReplays':0}
    out=selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5250-startup-view-bytecode-v1'
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'ownerFourCounters':four,'nestedEquivalent':len(nested),
                      'sha256':selected.sha(out/'manifest.json')}))


if __name__=='__main__':main()
