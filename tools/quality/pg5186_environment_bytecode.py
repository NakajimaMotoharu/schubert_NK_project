"""Thirteen environment scopes; existing UNAVAILABLE IO3 and exact semantic/debug class boundary."""
import json
import os
import pg5138_factory_bytecode as bytecode
import pg5142_storage_callers_bytecode as caller
import pg5150_native_fd_bytecode as native
import pg5178_backup_bytecode as checked
import pg5184_environment_selected as entry

selected=entry.selected
RUN=selected.ROOT.parent/'pgpt-runs/PG379/pg5184-environment-scopes-green-v1'
PACKAGE='dev.codex.schubert.nk.batch.file.'
KINDS={
 'InspectorEnvironmentFiles':{'OwnedTransferDirectory.open:':(4,False),'OwnedTransferDirectory.openExistingChild:':(6,False)},
 'InspectorEnvironmentReader':{'$Io.open:':(1,True)},
 'InspectorEnvironmentPublisher':{'$Io.openWriter:':(2,True)},
}


def main():
    result=json.loads((RUN/'manifest.safe.json').read_bytes())
    if result['actualExit']!=0 or result['tests']!=642 or result['suites']!=81:
        raise ValueError('original642/81 complete first')
    prior_run=selected.ROOT.parent/'pgpt-runs/PG379/pg5176-backup-scopes-green-v1'
    prior=json.loads((prior_run/'manifest.safe.json').read_bytes())
    before=prior['mainDelta']['physicalSha256'];after=result['mainDelta']['physicalSha256']
    required={entry.PREFIX+n+'.class' for n in entry.OUTERS}
    optional={entry.PREFIX+n+'.class' for n in entry.DEBUG}
    changed={key for key in before if key in after and before[key]!=after[key]}
    if set(before)!=set(after) or not required<=changed or not changed<=required|optional:
        raise ValueError('exact3 environment outer and bounded debug changes only')
    proofs={}
    for name,kinds in KINDS.items():
        methods,hashed=bytecode.decode(RUN/'source','batch',PACKAGE+name)
        scopes=caller.callers(methods)
        if len(scopes)!=sum(count for count,_ in kinds.values()):raise ValueError('exact environment scope count')
        factories=[]
        for needle,(count,is_checked) in kinds.items():
            found=[m for m in methods if any(needle in op[2] for op in m['ops'])]
            if len(found)!=count:raise ValueError('exact environment factory '+needle)
            for method in found:
                pcs=checked.checked_factory(method,needle) if is_checked else caller.tail(method,needle)
                factories.append({'method':method['header'],'acquisition':needle,'checkedNullIo':is_checked,
                                  'nonnullReturnPcs':pcs})
        proofs[name]={'scopes':scopes,'factories':factories,**hashed}
    debug=[]
    for key in sorted(changed-required):
        name=key.split(':',1)[1][:-6].replace('/','.')
        old,old_hash=bytecode.decode(prior_run/'source','batch',name)
        current,current_hash=bytecode.decode(RUN/'source','batch',name)
        native.require_reference(before,key,old_hash['classSha256']);native.same_methods(old,current)
        debug.append({'class':name,'old':old_hash,'current':current_hash,'allOpcodeHandlerSemanticsEqual':True})
    value={'source':result['sourceSnapshot'],'actualExit':0,'physicalMain':764,'proofs':proofs,
       'selectedManifestSha256':selected.sha(RUN/'manifest.safe.json'),'newOuterChanges':3,
       'checkedNullIoFactories':3,'nestedDebugEquivalent':debug,'otherPhysicalClassesUnchanged':761-len(debug),
       'bugs':['BUG1414'],'ykt':['YKT1178'],'ssc':['SSC308'],'wholeHorizontalComplete':False,
       'formalAccepted':False,'nativeImported':False,'actualHeapOomReproduced':False,'vmActions':0,'testReplays':0}
    out=selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5186-environment-bytecode-v1'
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'scopes':13,'checkedNullIo':3,'debugCount':len(debug),
                      'sha256':selected.sha(out/'manifest.json')}))


if __name__=='__main__':main()
