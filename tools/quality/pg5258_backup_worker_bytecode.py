"""Ten Backup factories and native port return tails; exact current source864 only."""
import json
import os
import subprocess
import xml.etree.ElementTree as ET
import pg5138_factory_bytecode as bytecode
import pg5142_storage_callers_bytecode as caller
import pg5150_native_fd_bytecode as native
import pg5178_backup_bytecode as checked
import pg5256_backup_worker_selected as entry

selected=entry.selected
RUN=selected.ROOT.parent/'pgpt-runs/PG379/pg5256-backup-worker-green-v1'
PACKAGE='dev.codex.schubert.nk.batch.file.'
KINDS={'BackupDatabaseWorker':{'OwnedTransferDirectory.createPrivateChild:':(1,False),
        'OwnedTransferDirectory.openExistingChild:':(1,False),'$Io.open:':(1,False)},
       'BackupDatabaseCopy':{'$Io.openWriter:':(1,True),'$Io.open:':(1,True)},
       'BackupBundlePublisher':{'$Io.openWriter:':(1,True)}}
SCOPES={'BackupDatabaseWorker':7,'BackupDatabaseCopy':2,'BackupBundlePublisher':1}


def main():
    result=json.loads((RUN/'manifest.safe.json').read_bytes())
    if result['actualExit']!=0 or result['phaseExits']!=[0,0] or result['tests']!=864 or result['suites']!=101:
        raise ValueError('original864/101 static0 first')
    prior_run=selected.ROOT.parent/'pgpt-runs/PG379/pg5248-startup-view-owner-green-v1'
    prior=json.loads((prior_run/'manifest.safe.json').read_bytes())
    before=prior['mainDelta']['physicalSha256'];after=result['mainDelta']['physicalSha256']
    required={entry.PREFIX+n+'.class' for n in entry.OUTERS};optional={entry.PREFIX+n+'.class' for n in entry.DEBUG}
    changed={key for key in before if key in after and before[key]!=after[key]}
    if set(before)!=set(after) or not required<=changed or not changed<=required|optional:
        raise ValueError('three Backup outer semantics and declared nested candidates only')
    proofs={}
    for name,kinds in KINDS.items():
        methods,hashed=bytecode.decode(RUN/'source','batch',PACKAGE+name)
        scopes=caller.callers(methods)
        if len(scopes)!=SCOPES[name]:raise ValueError('exact Backup caller count')
        factories=[]
        for needle,(count,is_checked) in kinds.items():
            found=[m for m in methods if any(needle in op[2] for op in m['ops'])]
            if len(found)!=count:raise ValueError('exact factory '+name+needle)
            for method in found:
                factories.append({'method':method['header'],'acquisition':needle,'checkedNullIo':is_checked,
                    'nonnullReturnPcs':checked.checked_factory(method,needle) if is_checked else caller.tail(method,needle)})
        proofs[name]={'scopes':scopes,'factories':factories,**hashed}
    verbose=subprocess.check_output([str(bytecode.JAVAP),'-p','-c','-v','-classpath',
        str(RUN/'source/src/schubert-nk-batch/target/classes'),PACKAGE+'BackupDatabaseWorker'],text=True)
    ports={}
    methods,hashed=bytecode.decode(RUN/'source','batch',PACKAGE+'BackupDatabaseWorker$NativePorts')
    for name in ('credentials','runtime','backup'):
        if ('REF_invokeInterface dev/codex/schubert/nk/batch/file/BackupDatabaseWorker$Ports.'+name+
                ':()Ldev/codex/schubert/nk/storage/OwnedTransferDirectory;') not in verbose:
            raise ValueError('direct native port factory reference '+name)
        method=bytecode.one([m for m in methods if bytecode.named(m,name)],'one native '+name)
        ports[name]={'method':method['header'],'rawDirectoryReturnPcs':caller.tail(method,'OwnedTransferDirectory.open:')}
    debug=[]
    for key in sorted(changed-required):
        name=key.split(':',1)[1][:-6].replace('/','.')
        old,old_hash=bytecode.decode(prior_run/'source','batch',name)
        current,current_hash=bytecode.decode(RUN/'source','batch',name)
        native.require_reference(before,key,old_hash['classSha256']);native.same_methods(old,current)
        debug.append({'class':name,'old':old_hash,'current':current_hash,'allOpcodeHandlerSemanticsEqual':True})
    report=ET.parse(RUN/'source/src/schubert-nk-batch/target/site/jacoco/jacoco.xml').getroot()
    targets={c.get('name'):{v.get('type'):{'missed':int(v.get('missed')),'covered':int(v.get('covered'))}
        for v in c.findall('counter') if v.get('type') in ('LINE','METHOD','CLASS','BRANCH')}
        for c in report.findall('package/class') if c.get('name') in {PACKAGE.replace('.','/')+n for n in KINDS}}
    if len(targets)!=3:raise ValueError('actual three targets')
    value={'source':result['sourceSnapshot'],'actualExit':0,'physicalMain':764,'proofs':proofs,
        'directPortFactories':4,'nativePortReturnTails':ports,'nativePortClass':hashed,
        'selectedManifestSha256':selected.sha(RUN/'manifest.safe.json'),'semanticClasses':3,
        'checkedNullIoFactories':3,'rawDirectoryFactories':2,'rawChannelFactories':1,
        'nestedDebugEquivalent':debug,'otherPhysicalClassesUnchanged':761-len(debug),'targetClassCounters':targets,
        'bugs':['BUG1414'],'ykt':['YKT1178'],'ssc':['SSC308'],'wholeHorizontalComplete':False,
        'formalAccepted':False,'nativeImported':False,'actualHeapOomReproduced':False,'vmActions':0,'testReplays':0}
    out=selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5258-backup-worker-bytecode-v1'
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'scopes':10,'debugCount':len(debug),'sha256':selected.sha(out/'manifest.json')}))


if __name__=='__main__':main()
