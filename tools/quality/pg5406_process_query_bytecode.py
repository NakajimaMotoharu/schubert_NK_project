"""Actual query-only ports, factory-before-protection and null-admission constructor proof."""
import json
import xml.etree.ElementTree as ET
import pg5138_factory_bytecode as bytecode
import pg5150_native_fd_bytecode as native
import pg5265_owned_factory_proof as publish
import pg5404_process_query_selected as entry

SOURCE='93616b8fba14489ba83f8ee548d5bead808b05f0'
RUN='pg5404-process-query-green-v2'
OUT='PG5406-process-query-bytecode-v1'
PACKAGE='dev.codex.schubert.nk.batch.platform.'


def query_sites(methods):
    sites=[]
    for method in methods:
        for index,row in enumerate(method['ops']):
            if 'ProcessResourceScope.acquire:' not in row[2]:continue
            ports=[op for op in method['ops'][:index] if op[1]=='invokedynamic'][-3:]
            if len(ports)!=3 or any(kind not in op[2] for op,kind in zip(ports,(
                'ResourceScope$Acquire;','java/util/function/Consumer;','ProcessResourceScope$OwnedQuery;'))):
                raise ValueError('three query-specific ports before factory; never common IO-normalizing ports')
            sites.append({'method':method['header'],'acquirePc':row[0],'portPcs':[op[0] for op in ports]})
    if any('ProcessResourceScope.use:' in op[2] for method in methods for op in method['ops']):
        raise ValueError('no reviewed acquisition remains outside its query protection')
    return sites


def main():
    work=entry.selected.ROOT.parent/'pgpt-runs/PG379';run=work/RUN;prior_run=work/'pg5390-archive-pipeline-green-v2'
    result=json.loads((run/'manifest.safe.json').read_bytes());prior=json.loads((prior_run/'manifest.safe.json').read_bytes())
    if type(result['actualExit']) is not int or result['actualExit']!=0 or result['phaseExits']!=[0,0] or (
        result['sourceSnapshot'],result['tests'],result['suites'])!=(SOURCE,1164,137):
        raise ValueError('current original terminal/source/complete inventory first')
    if prior['actualExit']!=0 or prior['sourceSnapshot']!='60bc8f54b154e82c16ad3a32a71143d7ca80affe':
        raise ValueError('exact prior byte reference only, never counter import')
    before=prior['mainDelta']['physicalSha256'];after=result['mainDelta']['physicalSha256']
    changed={key for key in before.keys()&after.keys() if before[key]!=after[key]}
    entry.selected.validate_physical_delta(changed,set(after)-set(before),set(before)-set(after),
        entry.REQUIRED,entry.DEBUG,entry.ADDED,set())
    if len(before)!=765 or len(after)!=767:raise ValueError('all physical Main including both new classes')
    proofs={};decoded={}
    for name,count in [('SystemctlStateSource',4),('InspectorUnitProbe$NativeReader',8)]:
        methods,hashed=bytecode.decode(run/'source','batch',PACKAGE+name);decoded[name]=methods
        sites=query_sites(methods)
        if len(sites)!=count:raise ValueError('exact query caller count '+name)
        proofs[name]={'scopes':sites,**hashed}
    methods,hashed=bytecode.decode(run/'source','batch',PACKAGE+'ProcessResourceScope')
    old,_=bytecode.decode(prior_run/'source','batch',PACKAGE+'ProcessResourceScope')
    native.same_methods([bytecode.one([m for m in old if bytecode.named(m,'use')],'old query use')],
        [bytecode.one([m for m in methods if bytecode.named(m,'use')],'current query use')])
    acquire=bytecode.one([m for m in methods if bytecode.named(m,'acquire')],'new typed query acquire')
    prefix=bytecode.scope_prefix(acquire)
    if 'Class java/lang/InterruptedException' not in prefix['handlerTypes']:
        raise ValueError('declared interruption protected with original query semantics')
    proofs['ProcessResourceScope']={'scopes':[], 'factoryPrefix':prefix,**hashed}
    for name in ('SystemctlStateSource$StdIo','InspectorUnitProbe$SafeStream','InspectorUnitProbe$QueryProcess'):
        methods,hashed=bytecode.decode(run/'source','batch',PACKAGE+name)
        constructor=bytecode.one([m for m in methods if name+'(' in m['header']],'one complete wrapper constructor')
        opened=bytecode.index_of(constructor,'ResourceScope$Acquire.open:')
        if not any('Object."<init>":' in op[2] for op in constructor['ops'][:opened]):
            raise ValueError('wrapper construction begins before getter/start')
        positive=bytecode.positive_path(constructor,opened+1,None,'nonnull')
        if any(op[1].startswith('if') for op in constructor['ops'][opened+1:]):
            raise ValueError('wrapper only stores nullable return; admission is protected by owned action')
        proofs[name]={'scopes':[],'admissionInOwnedAction':True,'postAcquisitionSuccessPcs':positive,**hashed}
    admissions=[]
    for method in decoded['InspectorUnitProbe$NativeReader']:
        points=[i for i,op in enumerate(method['ops']) if '$SafeStream.required:' in op[2] or '$QueryProcess.required:' in op[2]]
        if not points:continue
        if len(points)!=1 or any(not op[1].startswith('aload') for op in method['ops'][:points[0]]):
            raise ValueError('each Inspector owner admits immediately, before any next getter or body action')
        admissions.append(method['header'])
    if len(admissions)!=8:raise ValueError('both queries preserve four immediate admissions each')
    # The wrapper factory allocates the wrapper BEFORE the constructor may invoke any getter/start.
    constructed={}
    for outer,wrapper,expected in [('SystemctlStateSource','SystemctlStateSource$StdIo',3),
        ('InspectorUnitProbe$NativeReader','InspectorUnitProbe$SafeStream',6),
        ('InspectorUnitProbe$NativeReader','InspectorUnitProbe$QueryProcess',2)]:
        factories=[m for m in decoded[outer] if any(wrapper+'."<init>":' in op[2] for op in m['ops'])]
        if len(factories)!=expected:raise ValueError('all wrapper factory callsites '+wrapper)
        for factory in factories:
            allocated=bytecode.one([i for i,op in enumerate(factory['ops']) if op[1]=='new' and wrapper in op[2]],'one wrapper NEW')
            constructor=bytecode.index_of(factory,wrapper+'."<init>":')
            if allocated>=constructor or [op[1] for op in factory['ops'][constructor+1:]]!=['areturn']:
                raise ValueError('complete wrapper returned directly; no post-acquisition allocation')
        constructed[wrapper]=expected
    debug=[]
    for key in sorted(changed-entry.REQUIRED):
        name=key.split(':',1)[1][:-6].replace('/','.')
        previous,previous_hash=bytecode.decode(prior_run/'source','batch',name)
        current,current_hash=bytecode.decode(run/'source','batch',name)
        native.require_reference(before,key,previous_hash['classSha256']);native.same_methods(previous,current)
        debug.append({'class':name,'old':previous_hash,'current':current_hash,'allOpcodeHandlerSemanticsEqual':True})
    report=ET.parse(run/'source/src/schubert-nk-batch/target/site/jacoco/jacoco.xml').getroot()
    names={PACKAGE.replace('.','/')+name for name in ('ProcessResourceScope','SystemctlStateSource',
        'SystemctlStateSource$StdIo','InspectorUnitProbe$NativeReader','InspectorUnitProbe$SafeStream','InspectorUnitProbe$QueryProcess')}
    targets={c.get('name'):{v.get('type'):{'missed':int(v.get('missed')),'covered':int(v.get('covered'))}
        for v in c.findall('counter') if v.get('type') in ('LINE','METHOD','CLASS','BRANCH')}
        for c in report.findall('package/class') if c.get('name') in names}
    if len(targets)!=6:raise ValueError('every query target including previous unexecuted NativeReader')
    if any(v['missed'] for counters in targets.values() for v in counters.values()):
        raise ValueError('all query classes four100, no ignored deadline/exception branch')
    value={'source':SOURCE,'actualExit':0,'physicalMain':767,'semanticClasses':7,'proofs':proofs,
        'nestedDebugEquivalent':debug,'otherPhysicalClassesUnchanged':len(after)-len(changed)-len(entry.ADDED),
        'addedMain':sorted(entry.ADDED),'removedMain':[],'netMainGrowth':2,'targetClassCounters':targets,
        'queryWrapperFactories':constructed,'immediateOwnedAdmissions':admissions,'oldQueryUseOpcodeAndHandlerSemanticsEqual':True,
        'originalScopeSites':12,'currentOwnedScopes':12,'selectedManifestSha256':entry.selected.sha(run/'manifest.safe.json'),
        'implementationDecision':'PG-D432','bugs':['BUG1414'],'ykt':['YKT1178'],'ssc':['SSC308'],
        'wholeHorizontalComplete':False,'formalAccepted':False,'nativeImported':False,'vmActions':0,'testReplays':0}
    publish.publish(entry,value,OUT)


if __name__=='__main__':main()
