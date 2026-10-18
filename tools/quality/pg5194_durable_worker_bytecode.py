"""Eight caller scopes, seven legacy checked-null IO factories; Morning native still open."""
import json
import os
import subprocess
import pg5138_factory_bytecode as bytecode
import pg5142_storage_callers_bytecode as caller
import pg5150_native_fd_bytecode as native
import pg5178_backup_bytecode as checked
import pg5192_durable_worker_selected as entry

selected=entry.selected
RUN=selected.ROOT.parent/'pgpt-runs/PG379/pg5192-durable-worker-scopes-green-v1'
PACKAGE='dev.codex.schubert.nk.batch.file.'
COUNTS={'DurableRecordFiles':(1,2),'BackupWorkerRequestFiles':(1,1),'CleanupWorkerRequestFiles':(1,1)}


def main(*,result=None):
    if result is None:result=json.loads((RUN/'qualification.safe.json').read_bytes())
    if result['actualExit']!=0 or result['phaseExits']!=[0,0] or result['tests']!=684 or result['suites']!=85:
        raise ValueError('original684/85 complete first')
    prior_run=selected.ROOT.parent/'pgpt-runs/PG379/pg5184-environment-scopes-green-v1'
    prior=json.loads((prior_run/'manifest.safe.json').read_bytes())
    before=prior['mainDelta']['physicalSha256'];after=result['mainDelta']['physicalSha256']
    required={entry.PREFIX+n+'.class' for n in entry.OUTERS}
    optional={entry.PREFIX+n+'.class' for n in entry.DEBUG}
    changed={key for key in before if key in after and before[key]!=after[key]}
    if set(before)!=set(after) or not required<=changed or not changed<=required|optional:
        raise ValueError('exact4 outer and bounded nested debug changes only')
    proofs={}
    for name,counts in COUNTS.items():
        methods,hashed=bytecode.decode(RUN/'source','batch',PACKAGE+name)
        scopes=caller.callers(methods)
        if len(scopes)!=sum(counts):raise ValueError('exact durable/worker scope count')
        factories=[]
        for needle,count in zip(('$Io.open:','$Io.openWriter:'),counts):
            found=[m for m in methods if any(needle in op[2] for op in m['ops'])]
            if len(found)!=count:raise ValueError('exact factory '+name+needle)
            for method in found:
                factories.append({'method':method['header'],'acquisition':needle,'checkedNullIo':True,
                                  'nonnullReturnPcs':checked.checked_factory(method,needle)})
        proofs[name]={'scopes':scopes,'factories':factories,**hashed}
    name='MorningBackupRequestPublication'
    methods,hashed=bytecode.decode(RUN/'source','batch',PACKAGE+name)
    scopes=caller.callers(methods)
    if len(scopes)!=1:raise ValueError('one Morning publish scope')
    verbose=subprocess.check_output([str(bytecode.JAVAP),'-p','-c','-v','-classpath',
        str(RUN/'source/src/schubert-nk-batch/target/classes'),PACKAGE+name],text=True)
    if 'REF_invokeInterface dev/codex/schubert/nk/batch/file/MorningBackupRequestPublication$Open.open:()Ldev/codex/schubert/nk/batch/file/MorningBackupRequestPublication$Owner;' not in verbose:
        raise ValueError('Morning actual direct Open::open factory')
    proofs[name]={'scopes':scopes,'openDirectMethodReference':True,'nativeFactoryStillUnprotected':True,**hashed}
    debug=[]
    for key in sorted(changed-required):
        name=key.split(':',1)[1][:-6].replace('/','.')
        old,old_hash=bytecode.decode(prior_run/'source','batch',name)
        current,current_hash=bytecode.decode(RUN/'source','batch',name)
        native.require_reference(before,key,old_hash['classSha256']);native.same_methods(old,current)
        debug.append({'class':name,'old':old_hash,'current':current_hash,'allOpcodeHandlerSemanticsEqual':True})
    value={'source':result['sourceSnapshot'],'actualExit':0,'physicalMain':764,'proofs':proofs,
        'selectedManifestSha256':selected.sha(RUN/'manifest.safe.json'),
        'originalJobActualExit':1,'newOuterChanges':4,
        'checkedNullIoFactories':7,'nestedDebugEquivalent':debug,'otherPhysicalClassesUnchanged':760-len(debug),
        'limitedClosedOriginalSites':7,'morningPublishPartialOnly':True,'bugs':['BUG1414'],'ykt':['YKT1178'],
        'ssc':['SSC308'],'wholeHorizontalComplete':False,'formalAccepted':False,'nativeImported':False,
        'actualHeapOomReproduced':False,'vmActions':0,'testReplays':0}
    out=selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5194-durable-worker-bytecode-v1'
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'scopes':8,'checkedNullIo':7,'debugCount':len(debug),
                      'sha256':selected.sha(out/'manifest.json')}))


if __name__=='__main__':main()
