"""Actual primitive holder success paths, prebuilt dual-owner cleanup and physical nested debug proof."""
import json
import os
import re
import pg5138_factory_bytecode as bytecode
import pg5148_native_fd_selected as selected

RUN=selected.ROOT.parent/'pgpt-runs/PG379/pg5148-native-fd-green-v2'
PACKAGE='dev.codex.schubert.nk.storage.'
NATIVE=('LinuxFileLock','LinuxSealedProof','LinuxStartupAdmission')


def constructor_factories(methods,kind,expected):
    proofs=[]
    for method in methods:
        calls=[i for i,op in enumerate(method['ops']) if kind+'.\"<init>\":' in op[2]]
        for call in calls:
            news=[i for i,op in enumerate(method['ops'][:call]) if op[1]=='new' and kind in op[2]]
            if len(news)!=1:raise ValueError('one holder allocated before constructor can acquire primitive')
            proofs.append({'method':method['header'],'allocationPc':method['ops'][news[0]][0],
                           'constructorPc':method['ops'][call][0]})
    if len(proofs)!=expected:raise ValueError('exact primitive factory sites')
    return proofs


def same_methods(old,new):
    before={m['header']:bytecode.canonical(m) for m in old}
    after={m['header']:bytecode.canonical(m) for m in new}
    if len(before)!=len(old) or len(after)!=len(new) or before!=after:
        raise ValueError('nested debug-only class method/opcode/handler semantics changed')


def dual_close(methods):
    return bytecode.one([m for m in methods if re.search(r'(?:^| )void close\(\)',m['header'])],
                        'one dual release')


def require_reference(expected,key,actual):
    if key not in expected or expected[key] != actual:
        raise ValueError('actual old class must match original qualified whole SHA')


def reference_hashes(reference):
    result=reference.get('result',{})
    if (type(reference.get('actualExit')) is not int or reference['actualExit']!=0
        or result.get('productionSource')!=selected.FACTORY_REFERENCE or result.get('tests')!=3814
        or result.get('mainClasses')!=1654 or result.get('staticSixModules')!=0
        or result.get('FESFlakyNotRun')!=0 or result.get('allSixFormatBeforeAnyPt') is not True
        or len(result.get('allPhysicalMainSha256',{}))!=1654):
        raise ValueError('qualified original result envelope/source/physical schema required')
    return result['allPhysicalMainSha256']


def main():
    result=json.loads((RUN/'manifest.safe.json').read_bytes())
    if result['actualExit']!=0 or result['tests']!=224 or result['suites']!=32:
        raise ValueError('complete same-source224/32 first')
    snapshot=RUN/'source';holders={};outer={}
    for name,holder,count in (('LinuxFileLock','OwnedDescriptor',3),('LinuxSealedProof','Descriptor',2)):
        methods,hashed=bytecode.decode(snapshot,'storage',PACKAGE+name)
        constructor_proofs=constructor_factories(methods,name+'$'+holder,count)
        owned,owned_hash=bytecode.decode(snapshot,'storage',PACKAGE+name+'$'+holder)
        ctor=bytecode.one([m for m in owned if '$'+holder+'(' in m['header']],'one primitive holder constructor')
        opened=bytecode.index_of(ctor,'IntSupplier.getAsInt:')
        success=bytecode.positive_path(ctor,opened+1,None,'nonnegative')
        holders[name]={'factories':constructor_proofs,'successfulPostAcquisitionPcs':success,**owned_hash}
        outer[name]=hashed
    owners,owners_hash=bytecode.decode(snapshot,'storage',PACKAGE+'LinuxStartupAdmission$FdOwners')
    ctor=bytecode.one([m for m in owners if '$FdOwners(' in m['header']],'one dual constructor')
    if sum(op[1]=='new' and 'LinuxStartupAdmission$FdOwner' in op[2] for op in ctor['ops'])!=2:
        raise ValueError('both owners must exist before adoption')
    if sum(op[1]=='invokedynamic' for op in ctor['ops'])!=2 or any('Io.' in op[2] for op in ctor['ops']):
        raise ValueError('both close ports constructed with no native operation before adoption')
    close=dual_close(owners)
    if any(op[1] in ('new','invokedynamic','ldc','ldc_w','anewarray','newarray') for op in close['ops']):
        raise ValueError('dual release must use prebuilt ports')
    bytecode.index_of(close,'ResourceScope.use:')
    old_snapshot=selected.ROOT.parent/'pgpt-runs/PG379/pg5140-storage-callers-green-v3/source'
    original=reference_hashes(json.loads(selected.FACTORY_FULL.read_bytes()))
    prefix='storage:dev/codex/schubert/nk/storage/'
    semantic={prefix+n+'.class' for n in NATIVE}|{prefix+'LinuxFileLock$OwnedDescriptor.class'}
    debug=[]
    for key in result['mainDelta']['changed']:
        if not any(key.startswith(prefix+n+'$') for n in NATIVE) or key in semantic:continue
        name=key.split(':',1)[1][:-6].replace('/','.')
        prior,prior_hash=bytecode.decode(old_snapshot,'storage',name)
        require_reference(original,key,prior_hash['classSha256'])
        current,current_hash=bytecode.decode(snapshot,'storage',name)
        same_methods(prior,current)
        debug.append({'class':name,'old':prior_hash,'current':current_hash,'allMethodOpcodeAndHandlerSemanticsEqual':True})
    value={'source':result['sourceSnapshot'],'actualExit':0,'selectedManifestSha256':selected.sha(RUN/'manifest.safe.json'),
       'primitiveHolders':holders,'nativeOuterClasses':outer,'dualOwnerClass':owners_hash,
       'bothOwnerAndReleasePortsBeforeAdoption':True,'dualReleaseUsesOnlyPrebuiltPorts':True,
       'nestedDebugEquivalent':debug,'physicalMain':result['mainDelta']['selectedPhysicalMain'],
       'actualHeapOomReproduced':False,'formalAccepted':False,'wholeHorizontalComplete':False,
       'bugs':['BUG1414'],'ykt':['YKT1178'],'ssc':['SSC308'],'vmActions':0,'testReplays':0}
    out=selected.ROOT/'evidence/01_PT/003_NK-PRO-003/evidence/provisional/PG5150-native-fd-bytecode-v1'
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'debugEquivalent':[r['class'] for r in debug],
                     'sha256':selected.sha(out/'manifest.json')}))


if __name__=='__main__':main()
