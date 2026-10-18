"""Archive factories, constructor-before-getter, prebuilt terminal ports and named Main growth."""
import json
import xml.etree.ElementTree as ET
import pg5138_factory_bytecode as bytecode
import pg5142_storage_callers_bytecode as caller
import pg5150_native_fd_bytecode as native
import pg5265_owned_factory_proof as publish
import pg5390_archive_pipeline_selected as entry

SOURCE='2d9711a9785911e0cbd42af53ea44bed34d632bf'
RUN='pg5390-archive-pipeline-green-v1'
OUT='PG5392-archive-pipeline-bytecode-v1'
CLASS='dev.codex.schubert.nk.batch.platform.BackupArchiveProcess'


def main():
    work=entry.selected.ROOT.parent/'pgpt-runs/PG379';run=work/RUN;prior_run=work/'pg5380-nss-root-query-green-v1'
    result=json.loads((run/'manifest.safe.json').read_bytes());prior=json.loads((prior_run/'manifest.safe.json').read_bytes())
    if type(result['actualExit']) is not int or result['actualExit']!=0 or result['phaseExits']!=[0,0] or (
        result['sourceSnapshot'],result['tests'],result['suites'])!=(SOURCE,1138,134):
        raise ValueError('current original terminal/source/complete inventory first')
    if prior['actualExit']!=0 or prior['sourceSnapshot']!='d3f618962cc3a0297c818cd4890698c2269a0f5f':
        raise ValueError('exact previous qualification, never imported counters')
    before=prior['mainDelta']['physicalSha256'];after=result['mainDelta']['physicalSha256']
    changed={k for k in before.keys()&after.keys() if before[k]!=after[k]}
    required={entry.PREFIX+'BackupArchiveProcess.class'};optional={entry.PREFIX+n+'.class' for n in entry.DEBUG}
    entry.selected.validate_physical_delta(changed,set(after)-set(before),set(before)-set(after),
        required,optional,entry.ADDED,entry.REMOVED)
    if len(before)!=764 or len(after)!=765:raise ValueError('explicit net one Main growth, none excluded')
    methods,outer_hash=bytecode.decode(run/'source','batch',CLASS)
    sites=caller.callers(methods)
    if len(sites)!=4:raise ValueError('four owned process/stdout/stdin/stderr acquisition scopes')
    factory=bytecode.one([m for m in methods if any('$Start.execute:' in o[2] for o in m['ops'])],'one pipeline factory')
    tail=caller.tail(factory,'$Start.execute:')
    execute=bytecode.one([m for m in methods if bytecode.named(m,'execute')],'one archive execution')
    construction=bytecode.index_of(execute,'$TerminalPlan."<init>":')
    if construction>=bytecode.index_of(execute,'ResourceScope.acquire:'):
        raise ValueError('all terminal plan construction precedes pipeline factory entry')
    io,io_hash=bytecode.decode(run/'source','batch',CLASS+'$StdIoOwner')
    constructor=bytecode.one([m for m in io if '$StdIoOwner(' in m['header']],'one preallocated stream wrapper')
    opened=bytecode.index_of(constructor,'ResourceScope$Acquire.open:')
    remainder=constructor['ops'][opened+1:]
    if [o[1] for o in remainder]!=['checkcast','putfield','return'] or 'java/io/Closeable' not in remainder[0][2] or 'Field stream:' not in remainder[1][2]:
        raise ValueError('getter success only declared reference cast/store/constructor return')
    if not any('Object."<init>":' in o[2] for o in constructor['ops'][:opened]):
        raise ValueError('wrapper initialization precedes actual getter')
    plan,plan_hash=bytecode.decode(run/'source','batch',CLASS+'$TerminalPlan')
    close=bytecode.one([m for m in plan if bytecode.named(m,'close')],'one terminal connection')
    index=bytecode.index_of(close,'ResourceScope.acquire:')
    fields=[o[2] for o in close['ops'][:index] if o[1]=='getfield'][-3:]
    if len(fields)!=3 or any(('Field '+name+':') not in field for name,field in zip(('acquire','hold','stop'),fields)):
        raise ValueError('cleanup borrows only the three constructor-prebuilt ports')
    if any(o[1]=='invokedynamic' for o in close['ops']):raise ValueError('no callback construction during terminal cleanup')
    constructors=[m for m in plan if '$TerminalPlan(' in m['header']]
    if sum(o[1]=='invokedynamic' for m in constructors for o in m['ops'])!=3:
        raise ValueError('three complete ports constructed before native ownership')
    drains={}
    for name in ('stopAll','stopAfterKnown','stopRest','holdAll'):
        method=bytecode.one([m for m in plan if bytecode.named(m,name)],'one iterative '+name)
        if any(o[1] in ('invokedynamic','anewarray','newarray','multianewarray','new') for o in method['ops']):
            raise ValueError('no callback/heap construction while native terminal iteration is active')
        if any('Method '+name+':' in o[2] for o in method['ops']):raise ValueError('no recursive native cleanup')
        if not any(o[1]=='goto' and int(o[2])<o[0] for o in method['ops']):raise ValueError('actual iteration required')
        drains[name]={'method':method['header'],'nonRecursiveNoHeap':True}
    old,_=bytecode.decode(prior_run/'source','batch',CLASS)
    for name in ('holdTerminal','holdAfterUnknown','backoff'):
        native.same_methods([bytecode.one([m for m in old if bytecode.named(m,name)],'old quarantine')],
            [bytecode.one([m for m in methods if bytecode.named(m,name)],'current quarantine')])
    debug=[]
    for key in sorted(changed-required):
        name=key.split(':',1)[1][:-6].replace('/','.')
        old_methods,old_hash=bytecode.decode(prior_run/'source','batch',name)
        new_methods,new_hash=bytecode.decode(run/'source','batch',name)
        native.require_reference(before,key,old_hash['classSha256']);native.same_methods(old_methods,new_methods)
        debug.append({'class':name,'old':old_hash,'current':new_hash,'allOpcodeHandlerSemanticsEqual':True})
    report=ET.parse(run/'source/src/schubert-nk-batch/target/site/jacoco/jacoco.xml').getroot()
    targets={c.get('name'):{v.get('type'):{'missed':int(v.get('missed')),'covered':int(v.get('covered'))}
        for v in c.findall('counter') if v.get('type') in ('LINE','METHOD','CLASS','BRANCH')}
        for c in report.findall('package/class') if c.get('name') in {CLASS.replace('.','/')+s for s in ('','$TerminalPlan','$StdIoOwner')}}
    if len(targets)!=3:raise ValueError('every current target, no removed-class coverage import')
    value={'source':SOURCE,'actualExit':0,'physicalMain':765,'semanticClasses':3,'proofs':{
        CLASS:{'scopes':sites,'rawFactoryTail':tail,**outer_hash},
        CLASS+'$StdIoOwner':{'scopes':[],**io_hash},CLASS+'$TerminalPlan':{'scopes':[{'prebuiltFields':fields}],**plan_hash}},
        'nestedDebugEquivalent':debug,'otherPhysicalClassesUnchanged':len(after)-len(changed)-len(entry.ADDED),
        'addedMain':sorted(entry.ADDED),'removedMain':sorted(entry.REMOVED),'netMainGrowth':1,
        'targetClassCounters':targets,'selectedManifestSha256':entry.selected.sha(run/'manifest.safe.json'),
        'terminalDrains':drains,'oldQuarantineOpcodesHandlersUnchanged':True,
        'originalScopeSites':7,'currentOwnedScopes':4,'currentPrebuiltBorrowedCleanupScope':1,
        'implementationDecision':'PG-D431','bugs':['BUG1414'],'ykt':['YKT1178'],'ssc':['SSC091','SSC308'],
        'wholeHorizontalComplete':False,'formalAccepted':False,'nativeImported':False,'vmActions':0,'testReplays':0}
    publish.publish(entry,value,OUT)


if __name__=='__main__':main()
