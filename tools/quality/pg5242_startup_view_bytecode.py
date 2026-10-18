"""Primitive FD registration/all-close-drain proof and exact same-source Owner four100."""
import json
import os
import xml.etree.ElementTree as ET
import pg5138_factory_bytecode as bytecode
import pg5142_storage_callers_bytecode as caller
import pg5150_native_fd_bytecode as native
import pg5240_startup_view_selected as entry

selected=entry.selected
RUN=selected.ROOT.parent/'pgpt-runs/PG379/pg5240-startup-view-owner-green-v1'
CLASS='dev.codex.schubert.nk.batch.file.StartupAdmissionFile'


def registration(method,needle):
    opened=bytecode.index_of(method,needle)
    guard=bytecode.index_of(method,'guard:()V')
    if guard>=opened:raise ValueError('capacity/closed guard must predate native acquisition')
    post=method['ops'][opened+1:]
    for index,op in enumerate(post):
        if op[1] in ('new','newarray','anewarray','multianewarray','invokedynamic','ldc','ldc_w'):
            raise ValueError('FD registration may not allocate or resolve constants')
        if op[1].startswith('invoke') and not (op[1]=='invokestatic' and 'StartupAdmissionFile.unavailable:' in op[2]
                                               and index+1<len(post) and post[index+1][1]=='athrow'):
            raise ValueError('post-FD calls only on immediately throwing invalid-value branches')
    store=bytecode.one([i for i,op in enumerate(post) if op[1]=='iastore'],'one primitive owned-slot store')
    if len(post[store+1:])!=2 or not post[store+1][1].startswith('iload') or post[store+2][1]!='ireturn':
        raise ValueError('only same primitive FD return after registration')
    if post[store-1][1:]!=post[store+1][1:]:raise ValueError('returned FD must equal stored FD')
    return {'method':method['header'],'guardPc':method['ops'][guard][0],
        'openPc':method['ops'][opened][0],'primitiveStorePc':post[store][0],
        'successfulPostOpenNoAllocations':True,'invalidOnlyCallsTerminateByThrow':True}


def drain(method):
    ops=method['ops'];closed=bytecode.index_of(method,'DirectoryCalls.close:');pc=ops[closed][0]
    back=bytecode.one([i for i,op in enumerate(ops) if op[1]=='goto' and i>closed and int(op[2].split()[0])<=pc],
                      'one reverse native-close loop')
    prefix=ops[:back+1]
    if any(op[1] in ('new','newarray','anewarray','multianewarray','invokedynamic','ldc','ldc_w') for op in prefix):
        raise ValueError('no allocation/constants/callbacks before drain ends')
    if any(op[1].startswith('invoke') and 'DirectoryCalls.close:' not in op[2] for op in prefix):
        raise ValueError('all exception normalization/suppression calls must follow full drain')
    if not any(op[1]=='aastore' for op in prefix):raise ValueError('preallocated failure scratch required')
    if not any(op[1]=='putfield' and 'closed:Z' in op[2] for op in ops[:closed]):
        raise ValueError('consume-once flag must predate close attempts')
    handlers={kind for start,end,_,kind in method['handlers'] if start<=pc<end}
    if not {'Class dev/codex/schubert/nk/storage/StorageIoException','Class java/lang/RuntimeException',
            'Class java/lang/Error'}<=handlers:
        raise ValueError('all native close IO/Runtime/Error must be recorded and drain continued')
    first=bytecode.index_of(method,'firstFailure:')
    if first<=back:raise ValueError('normalization may start only after all native attempts')
    return {'nativeClosePc':pc,'loopBackPc':ops[back][0],'firstNormalizationPc':ops[first][0],
        'noHeapWorkDuringDrain':True,'handlerTypes':sorted(handlers)}


def main():
    result=json.loads((RUN/'manifest.safe.json').read_bytes())
    if result['actualExit']!=0 or result['phaseExits']!=[0,0] or result['tests']!=829 or result['suites']!=98:
        raise ValueError('original829/98 complete first')
    prior_run=selected.ROOT.parent/'pgpt-runs/PG379/pg5232-caddy-child-green-v1'
    prior=json.loads((prior_run/'manifest.safe.json').read_bytes())
    before=prior['mainDelta']['physicalSha256'];after=result['mainDelta']['physicalSha256']
    required={entry.PREFIX+n+'.class' for n in entry.OUTERS};optional={entry.PREFIX+n+'.class' for n in entry.DEBUG}
    changed={key for key in before if key in after and before[key]!=after[key]}
    if set(before)!=set(after) or not required<=changed or not changed<=required|optional:
        raise ValueError('only outer/ViewOwner semantics and explicitly bounded nested dependencies')
    outer,outer_hash=bytecode.decode(RUN/'source','batch',CLASS)
    if len(caller.callers(outer))!=1:raise ValueError('one prebuilt factory owner scope')
    factory=bytecode.one([m for m in outer if any(op[1]=='new' and '$ViewOwner' in op[2] for op in m['ops'])],
                        'one owner factory before native IO')
    add=bytecode.index_of(factory,'Math.addExact:')
    if not any(op[1]=='iconst_3' for op in factory['ops'][:add]):raise ValueError('runtime segments plus root/app/entry3')
    owner,owner_hash=bytecode.decode(RUN/'source','batch',CLASS+'$ViewOwner')
    ctor=bytecode.one([m for m in owner if '$ViewOwner(' in m['header']],'one primitive owner constructor')
    if sum(op[1]=='newarray' for op in ctor['ops'])!=1 or sum(op[1]=='anewarray' for op in ctor['ops'])!=1:
        raise ValueError('primitive FD and failure scratch both preallocated')
    if any('DirectoryCalls.open' in op[2] for op in ctor['ops']):raise ValueError('no native IO during owner construction')
    if any('Integer.valueOf:' in op[2] or 'ArrayList' in op[2] for m in owner for op in m['ops']):
        raise ValueError('primitive owner must not box descriptors or grow a list')
    acquisition={}
    for name in ('openRoot','openDirectory','openEntry'):
        method=bytecode.one([m for m in owner if ' int '+name+'(' in m['header']],'one primitive '+name)
        acquisition[name]=registration(method,'DirectoryCalls.'+name+':')
    closing=bytecode.one([m for m in owner if ' void close(' in m['header']],'one all-drain close')
    drain_proof=drain(closing);nested=[]
    for key in sorted(changed-required):
        name=key.split(':',1)[1][:-6].replace('/','.')
        old,old_hash=bytecode.decode(prior_run/'source','batch',name)
        current,current_hash=bytecode.decode(RUN/'source','batch',name)
        native.require_reference(before,key,old_hash['classSha256']);native.same_methods(old,current)
        nested.append({'class':name,'old':old_hash,'current':current_hash,'allOpcodeHandlerSemanticsEqual':True,
            'ownerPackageAccessReference':name.endswith('$ViewOperation'),
            'notClaimedPureDebugOnly':name.endswith('$ViewOperation')})
    report=ET.parse(RUN/'source/src/schubert-nk-batch/target/site/jacoco/jacoco.xml').getroot()
    target=bytecode.one([c for c in report.findall('package/class') if c.get('name')==(CLASS+'$ViewOwner').replace('.','/')],
                        'one physical Owner counters')
    four={v.get('type'):{'missed':int(v.get('missed')),'covered':int(v.get('covered'))}
          for v in target.findall('counter') if v.get('type') in ('LINE','METHOD','CLASS','BRANCH')}
    if set(four)!={'LINE','METHOD','CLASS','BRANCH'} or any(v['missed'] or v['covered']<=0 for v in four.values()):
        raise ValueError('new Owner all four counters must100, no exclusions')
    value={'source':result['sourceSnapshot'],'actualExit':0,'physicalMain':764,'outer':outer_hash,'owner':owner_hash,
        'acquisitionProof':acquisition,'drainProof':drain_proof,'ownerFourCounters':four,
        'capacityExtraRootAppEntry':3,'selectedManifestSha256':selected.sha(RUN/'manifest.safe.json'),
        'semanticClasses':2,'nestedMethodEquivalent':nested,'otherPhysicalClassesUnchanged':762-len(nested),
        'bugs':['BUG1414'],'ykt':['YKT1178'],'ssc':['SSC308'],'wholeHorizontalComplete':False,
        'formalAccepted':False,'nativeImported':False,'actualHeapOomReproduced':False,'vmActions':0,'testReplays':0}
    out=selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5242-startup-view-bytecode-v1'
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'ownerFourCounters':four,'nestedEquivalent':len(nested),
                      'sha256':selected.sha(out/'manifest.json')}))


if __name__=='__main__':main()
