"""Independent two-module nine factory/port proof and complete physical Main delta."""
import json
import subprocess
import xml.etree.ElementTree as ET
import pg5138_factory_bytecode as bytecode
import pg5142_storage_callers_bytecode as caller
import pg5150_native_fd_bytecode as native
import pg5265_owned_factory_proof as output
import pg5380_nss_root_query_selected as entry

SOURCE='d3f618962cc3a0297c818cd4890698c2269a0f5f'
RUN='pg5380-nss-root-query-green-v1'
OUT='PG5382-nss-root-query-bytecode-v1'
TARGETS={
    'bootstrap:dev/codex/schubert/nk/bootstrap/FixedServiceIdentity$NativeQuery.class':
        (4,{'FixedServiceIdentity$Start.execute:':1}),
    'batch:dev/codex/schubert/nk/batch/platform/RootStartupContext$NativeIo.class':
        (5,{'SystemctlStateSource$Start.execute:':1,'java/nio/file/Files.newInputStream:':1})}


def main():
    work=entry.selected.ROOT.parent/'pgpt-runs/PG379';run=work/RUN
    result=json.loads((run/'manifest.safe.json').read_bytes())
    if type(result['actualExit']) is not int or result['actualExit']!=0 or result['phaseExits']!=[0,0] or (
        result['sourceSnapshot'],result['tests'],result['suites'])!=(SOURCE,1122,133):
        raise ValueError('exact current source and complete original job first')
    prior_run=work/'pg5372-ffm-progress-green-v1';prior=json.loads((prior_run/'manifest.safe.json').read_bytes())
    if prior['actualExit']!=0 or prior['sourceSnapshot']!='fceffefd6639ae0b217565dc0acdf0d2e0a2a6fe':
        raise ValueError('exact prior qualified reference')
    before=prior['mainDelta']['physicalSha256'];after=result['mainDelta']['physicalSha256']
    changed={k for k in before if k in after and before[k]!=after[k]}
    if len(after)!=764 or set(before)!=set(after) or not entry.REQUIRED<=changed or not changed<=entry.REQUIRED|entry.OPTIONAL:
        raise ValueError('only declared two-module semantic and bounded nested classes')
    proofs={};counters={}
    for key,(count,kinds) in TARGETS.items():
        module,name=key.split(':',1);name=name[:-6].replace('/','.')
        methods,hashed=bytecode.decode(run/'source',module,name)
        if hashed['classSha256']!=after[key]:raise ValueError('actual class matches frozen physical map')
        sites=caller.callers(methods)
        if len(sites)!=count:raise ValueError('all nine ports precede acquisition')
        tails={}
        for needle,expected in kinds.items():
            found=[m for m in methods if any(needle in o[2] for o in m['ops'])]
            if len(found)!=expected:raise ValueError('one direct native process/file factory')
            tails[needle]=[caller.tail(m,needle) for m in found]
        verbose=subprocess.check_output([str(bytecode.JAVAP),'-p','-v','-classpath',
            str(run/('source/src/schubert-nk-'+module+'/target/classes')),name],text=True)
        for getter in ('getInputStream','getOutputStream','getErrorStream'):
            if 'REF_invokeVirtual java/lang/Process.'+getter+':' not in verbose:
                raise ValueError('actual process getter method reference required')
        proofs[name]={'scopes':sites,'rawFactoryTails':tails,**hashed}
        report=ET.parse(run/('source/src/schubert-nk-'+module+'/target/site/jacoco/jacoco.xml')).getroot()
        target=bytecode.one([c for c in report.findall('package/class') if c.get('name')==name.replace('.','/')],'current target')
        counters[name.replace('.','/')]={v.get('type'):{'missed':int(v.get('missed')),'covered':int(v.get('covered'))}
            for v in target.findall('counter') if v.get('type') in ('LINE','METHOD','CLASS','BRANCH')}
    debug=[]
    for key in sorted(changed-entry.REQUIRED):
        module,name=key.split(':',1);name=name[:-6].replace('/','.')
        old,old_hash=bytecode.decode(prior_run/'source',module,name)
        current,current_hash=bytecode.decode(run/'source',module,name)
        native.require_reference(before,key,old_hash['classSha256']);native.same_methods(old,current)
        debug.append({'class':name,'old':old_hash,'current':current_hash,'allOpcodeHandlerSemanticsEqual':True})
    value={'source':SOURCE,'actualExit':0,'physicalMain':764,'semanticClasses':2,
        'nestedDebugEquivalent':debug,'otherPhysicalClassesUnchanged':764-len(changed),'proofs':proofs,
        'targetClassCounters':counters,'selectedManifestSha256':entry.selected.sha(run/'manifest.safe.json'),
        'storageFourCounters':result['storageFourCounters'],'originalScopeSites':9,'newJavaCasesInGroup':4,
        'implementationDecision':'PG-D430','bugs':['BUG1414'],'ykt':['YKT1178'],'ssc':['SSC308'],
        'wholeHorizontalComplete':False,'formalAccepted':False,'nativeImported':False,
        'actualHeapOomReproduced':False,'vmActions':0,'testReplays':0}
    output.publish(entry,value,OUT)


if __name__=='__main__':main()
