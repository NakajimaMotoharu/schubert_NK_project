"""Nineteen Backup scopes; checked-null IO retains allocation-free nonnull return paths."""
import json
import os
import pg5138_factory_bytecode as bytecode
import pg5142_storage_callers_bytecode as caller
import pg5150_native_fd_bytecode as native
import pg5176_backup_selected as entry

selected=entry.selected
RUN=selected.ROOT.parent/'pgpt-runs/PG379/pg5176-backup-scopes-green-v1'
PACKAGE='dev.codex.schubert.nk.batch.file.'
COUNTS={'BackupArtifactVerifier':(7,2,1,0),'BackupManifestPublisher':(2,0,1,1),
        'BackupManifestReader':(3,1,1,0)}


def checked_factory(method,needle):
    opened=bytecode.index_of(method,needle)
    pcs=bytecode.positive_path(method,opened+1,None,'nonnull')
    selected_ops=[op for op in method['ops'] if op[0] in pcs]
    if any(op[1]=='putfield' for op in selected_ops) or not any(op[1]=='areturn' for op in method['ops']):
        raise ValueError('nonnull factory must return only, never mutate an owner or return void')
    if any(op[1] in ('return','ireturn','lreturn','freturn','dreturn') for op in method['ops']):
        raise ValueError('reference factory required')
    if not any('unavailable:' in op[2] for op in method['ops']):
        raise ValueError('legacy null-only UNAVAILABLE IO rejection required')
    return pcs


def main():
    actual=json.loads((RUN/'manifest.safe.json').read_bytes())
    if actual['actualExit']!=0 or actual['tests']!=611 or actual['suites']!=78:
        raise ValueError('original611/78 complete first')
    prior_run=selected.ROOT.parent/'pgpt-runs/PG379/pg5168-release-scopes-green-v1'
    prior=json.loads((prior_run/'manifest.safe.json').read_bytes())
    before=prior['mainDelta']['physicalSha256'];after=actual['mainDelta']['physicalSha256']
    required={entry.PREFIX+n+'.class' for n in entry.OUTERS}
    optional={entry.PREFIX+n+'.class' for n in entry.DEBUG}
    changed={key for key in before if key in after and before[key]!=after[key]}
    if set(before)!=set(after) or not required<=changed or not changed<=required|optional:
        raise ValueError('three exact outer changes and bounded nested debug only')
    proofs={}
    for name,counts in COUNTS.items():
        methods,hashed=bytecode.decode(RUN/'source','batch',PACKAGE+name)
        scopes=caller.callers(methods)
        if len(scopes)!=sum(counts):raise ValueError('exact candidate scope count')
        factories=[]
        for needle,count,checked in zip(
          ('OwnedTransferDirectory.openExistingChild:','$Io.openNames:','$Io.open:','$Io.openWriter:'),
          counts,(False,True,True,True)):
            found=[m for m in methods if any(needle in op[2] for op in m['ops'])]
            if len(found)!=count:raise ValueError('exact factory kind '+name+needle)
            for method in found:
                pcs=checked_factory(method,needle) if checked else caller.tail(method,needle)
                factories.append({'method':method['header'],'acquisition':needle,'checkedNullIo':checked,
                                  'nonnullReturnPcs':pcs})
        proofs[name]={'scopes':scopes,'factories':factories,**hashed}
    debug=[]
    for key in sorted(changed-required):
        name=key.split(':',1)[1][:-6].replace('/','.')
        old,old_hash=bytecode.decode(prior_run/'source','batch',name)
        current,current_hash=bytecode.decode(RUN/'source','batch',name)
        native.require_reference(before,key,old_hash['classSha256']);native.same_methods(old,current)
        debug.append({'class':name,'old':old_hash,'current':current_hash,'allOpcodeHandlerSemanticsEqual':True})
    provider,provider_hash=bytecode.decode(RUN/'source','batch',PACKAGE+'InspectorEnvironmentPublisher$NioIo')
    writer,writer_hash=bytecode.decode(RUN/'source','batch',PACKAGE+'InspectorEnvironmentPublisher$NioWriter')
    opened=bytecode.one([m for m in provider if ' openWriter(' in m['header']],'one production writer factory')
    position=bytecode.index_of(opened,'FileChannel.open:')
    new=bytecode.one([i for i,op in enumerate(opened['ops']) if op[1]=='new' and '$NioWriter' in op[2]],'one writer allocation')
    if new>=position:raise ValueError('writer object must predate FileChannel acquisition')
    ctor=bytecode.one([m for m in writer if '$NioWriter(' in m['header']],'one writer constructor')
    if any(op[1] in ('new','anewarray','newarray','invokedynamic','ldc','ldc_w') for op in ctor['ops']):
        raise ValueError('writer constructor must only retain channel without allocation')
    value={'source':actual['sourceSnapshot'],'actualExit':0,'physicalMain':764,'proofs':proofs,
       'selectedManifestSha256':selected.sha(RUN/'manifest.safe.json'),'checkedNullIoFactories':7,
       'newOuterChanges':3,'nestedDebugEquivalent':debug,'otherPhysicalClassesUnchanged':761-len(debug),
       'writerWrapperBeforeNativeOpen':True,'writerConstructorAllocationFree':True,
       'writerProviderClass':provider_hash,'writerClass':writer_hash,
       'bugs':['BUG1414'],'ykt':['YKT1178'],'ssc':['SSC308'],'wholeHorizontalComplete':False,
       'formalAccepted':False,'nativeImported':False,'actualHeapOomReproduced':False,'vmActions':0,'testReplays':0}
    out=selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5178-backup-bytecode-v1'
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'scopes':19,'checkedNullIo':7,'debugCount':len(debug),
                      'sha256':selected.sha(out/'manifest.json')}))


if __name__=='__main__':main()
