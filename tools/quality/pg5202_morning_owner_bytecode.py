"""Independent Morning native factory/assembly/transfer bytecode proof, no old run imported."""
import json
import os
import subprocess
import xml.etree.ElementTree as ET
import pg5138_factory_bytecode as bytecode
import pg5142_storage_callers_bytecode as caller
import pg5150_native_fd_bytecode as native
import pg5200_morning_owner_selected as entry

selected=entry.selected
RUN=selected.ROOT.parent/'pgpt-runs/PG379/pg5200-morning-owner-green-v1'
PACKAGE='dev.codex.schubert.nk.batch.file.'
CLASS=PACKAGE+'MorningBackupRequestPublication'
KEY='batch:'+CLASS.replace('.','/')+'.class'
OWNER=KEY[:-6]+'$1.class'


def main(*,result=None):
    if result is None:result=json.loads((RUN/'qualification.safe.json').read_bytes())
    if result['actualExit']!=0 or result['phaseExits']!=[0,0] or result['tests']!=688 or result['suites']!=85:
        raise ValueError('original688/85 complete first')
    prior_run=selected.ROOT.parent/'pgpt-runs/PG379/pg5192-durable-worker-scopes-green-v1'
    prior=json.loads((prior_run/'qualification.safe.json').read_bytes())
    before=prior['mainDelta']['physicalSha256'];after=result['mainDelta']['physicalSha256']
    changed={key for key in before if key in after and before[key]!=after[key]}
    if set(before)!=set(after) or KEY not in changed or not changed<={KEY,OWNER}:
        raise ValueError('only Morning outer and private anonymous-owner dependency')
    methods,hashes=bytecode.decode(RUN/'source','batch',CLASS)
    publish=bytecode.one([m for m in methods if ' void publish(' in m['header']],'one publication entry')
    if len(caller.callers([publish]))!=1:raise ValueError('publish3 ports before acquisition')
    helper=bytecode.one([m for m in methods if ' openOwned(' in m['header']],'one ownership-transfer helper')
    position=bytecode.index_of(helper,'ResourceScope.acquire:')
    ports=[op for op in helper['ops'][:position] if op[1]=='invokedynamic']
    if len(ports)!=2 or any('ResourceScope$'+kind+';' not in op[2]
                           for op,kind in zip(ports,('Release','OwnedAction'))):
        raise ValueError('caller-owned Acquire plus two prebuilt helper ports')
    if sum('Objects.requireNonNull:' in op[2] for op in helper['ops'][:position])!=2:
        raise ValueError('both ports validated before acquire')
    state=bytecode.one([i for i,op in enumerate(helper['ops']) if op[1]=='newarray'],'one preallocated transfer state')
    if state>=position:raise ValueError('transfer state must predate resource acquisition')
    factory=bytecode.one([m for m in methods if any('OwnedTransferDirectory.open:' in op[2] for op in m['ops'])],
                        'one direct raw Directory factory')
    tail=caller.tail(factory,'OwnedTransferDirectory.open:')
    assembly=bytecode.one([m for m in methods if any(op[1]=='new' and 'BackupWorkerRequestFiles' in op[2] for op in m['ops'])],
                         'one protected production assembly')
    if 'lambda$openNative$' not in assembly['header']:
        raise ValueError('native owner may only be constructed by protected assembly action')
    transfer=bytecode.one([m for m in methods if any(op[1]=='bastore' for op in m['ops'])],
                         'one final ownership transfer')
    store=bytecode.one([i for i,op in enumerate(transfer['ops']) if op[1]=='bastore'],'one transfer store')
    if not any('ResourceScope$OwnedAction.run:' in op[2] for op in transfer['ops'][:store]) or not any(
            'Objects.requireNonNull:' in op[2] for op in transfer['ops'][:store]):
        raise ValueError('complete nonnull owner before transfer')
    if [op[1] for op in transfer['ops'][store+1:]]!=['aload_3','areturn']:
        raise ValueError('no calls/allocations after final transfer, immediate owner return')
    release=bytecode.one([m for m in methods if any(op[1]=='baload' for op in m['ops'])],
                        'one conditional pre-transfer release')
    if sum('OwnedTransferDirectory.close:' in op[2] for op in release['ops'])!=1 or any(
            op[1] in ('new','invokedynamic','anewarray','newarray') for op in release['ops']):
        raise ValueError('one allocation-free conditional cleanup')
    verbose=subprocess.check_output([str(bytecode.JAVAP),'-p','-c','-v','-classpath',
        str(RUN/'source/src/schubert-nk-batch/target/classes'),CLASS],text=True)
    if 'REF_invokeInterface dev/codex/schubert/nk/batch/file/MorningBackupRequestPublication$Open.open:' not in verbose:
        raise ValueError('publish direct factory reference retained')
    nested=[]
    if OWNER in changed:
        old,old_hash=bytecode.decode(prior_run/'source','batch',CLASS+'$1')
        current,current_hash=bytecode.decode(RUN/'source','batch',CLASS+'$1')
        native.require_reference(before,OWNER,old_hash['classSha256']);native.same_methods(old,current)
        nested.append({'class':CLASS+'$1','old':old_hash,'current':current_hash,
            'allMethodOpcodeHandlerSemanticsEqual':True,'enclosingAssemblyMovedUnderProtection':True,
            'notClaimedPureDebugOnly':True})
    report=ET.parse(RUN/'source/src/schubert-nk-batch/target/site/jacoco/jacoco.xml').getroot()
    target=bytecode.one([c for c in report.findall('package/class') if c.get('name')==CLASS.replace('.','/')],
                        'one actual target class')
    measured={m.get('name')+m.get('desc'):{c.get('type'):{'covered':int(c.get('covered')),'missed':int(c.get('missed'))}
        for c in m.findall('counter')} for m in target.findall('method') if 'openOwned' in m.get('name','')}
    if not measured or any(v['missed'] for counts in measured.values() for kind,v in counts.items()
                           if kind in ('LINE','METHOD','BRANCH')):
        raise ValueError('all helper/transfer/release line/method/branch required')
    value={'source':result['sourceSnapshot'],'actualExit':0,'physicalMain':764,'class':hashes,
        'callerHelper':helper['header'],'directDirectoryFactory':factory['header'],'factoryReturnPcs':tail,
        'protectedAssembly':assembly['header'],'transfer':transfer['header'],'release':release['header'],
        'helperMethodCounters':measured,'nestedMethodEquivalent':nested,'otherPhysicalClassesUnchanged':764-len(changed),
        'selectedManifestSha256':selected.sha(RUN/'manifest.safe.json'),'originalSitesLimitedDelta':1,
        'extraInternalNativeGapClosedLimited':True,'bugs':['BUG1414'],'ykt':['YKT1178'],'ssc':['SSC308'],
        'wholeHorizontalComplete':False,'formalAccepted':False,'nativeImported':False,'vmActions':0,'testReplays':0}
    out=selected.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5202-morning-owner-bytecode-v1'
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'physicalMain':764,'nestedEquivalent':len(nested),
                      'sha256':selected.sha(out/'manifest.json')}))


if __name__=='__main__':main()
