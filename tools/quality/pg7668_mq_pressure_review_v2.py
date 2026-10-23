"""Current API114; fixed-label quality, new9+old32 generated methods and five provenance guards."""
from collections import Counter
import copy
import datetime
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
import pg7658_mq_pressure_host_v2 as execution
import pg7662_mq_pressure_six_compile_v2 as compilation
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify
from inbox_protocol_harness_contract import verify_harness

OUT=host.BASE/'PG7668-mq-pressure-review-v2'

def require(value,message):
    if not value:raise ValueError(message)

def domains(trace,current,physical,previous):
    counts=anchors(trace['sourceRows'],previous,dict(changed=0,unchanged=104,introduced=2))
    by_path={r['path']:r for r in trace['sourceRows']}
    require(len(trace['physicalRows'])==94 and len({r['className'] for r in trace['physicalRows']})==94,'all94 unique physical')
    for row in trace['sourceRows']:
        path=row['path'];require(row['currentSourceCoverageTransferred'] is False,'no coverage transfer')
        if path in current['sourceFiles']:
            require(row['sha256']==current['sourceFiles'][path] and row['executionWitness']['source']==current['source']
              and row['executionWitness']['tests']==114 and row['componentCounterScope']=='ALL_CURRENT_API_EXECUTABLES_ONLY','only current actual API input')
        elif path.endswith('/pom.xml'):
            require(row['componentCounterScope']=='NOT_EXECUTABLE_CONFIGURATION' and row['compileWitness']['source']==current['source'],'normal POM not PT')
        else:require('executionWitness' not in row and row['componentCounterScope']=='HISTORICAL_ONLY_NO_CURRENT_COUNTERS','history not current PT')
    expected={'api':('CURRENT_API_QUALIFIED',physical['currentApi']),
      'batch':('HISTORICAL_BATCH_BYTE_ONLY',physical['historicalBatch']),
      'web':('HISTORICAL_WEB_BYTE_ONLY',physical['historicalWeb'])}
    for row in trace['physicalRows']:
        role,entry=row['className'].split(':',1);label,proof=expected[role];executable=not entry.endswith('package-info.class')
        path='src/schubert-nk-'+role+'/src/main/java/'+entry.removesuffix('.class').split('$',1)[0]+'.java'
        require(row['qualificationDomain']==label and row['executionSource']==proof['source'] and row['executable'] is executable
          and row['currentSourceExecutionAccepted'] is (role=='api' and executable)
          and row['sha256']==proof['physicalClasses'][row['className']] and row['sourcePath']==path and row['owner']==by_path[path]['owner'],
          'exact true role/source/byte/owner, no aliases')
    require(sum(r['currentSourceExecutionAccepted'] for r in trace['physicalRows'])==23,'currentAPI23 only')
    return counts

def guards_hash(guards,path):
    require(guards['actualExit']==0,'genuine original guard terminal')
    return guards['inputHashes'][path]

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only current API review')
    proofs={};pins={}
    for key,path,digest in (
      ('current','PG7660-mq-pressure-post-v2/manifest.json',None),
      ('physical','PG7664-mq-pressure-six-post-v2/manifest.json',None),
      ('trace','PG7666-mq-pressure-trace-v2/manifest.json',None),
      ('previousTrace','PG7636-api-inbox-replay-trace-v1/manifest.json','15f83e6c5d9738c46b8edd9c4241a0c9c8ba2dd9757066891684d597d084efc1'),
      ('previousApi','PG7478-api-outbox-connection-post-v1/manifest.json','8efcb8cfe0cbdc620f98652d3773b936d385c86f6b9d114dfa67f243be18327c'),
      ('previousReview','PG7486-api-outbox-connection-review-v1/manifest.json','403d51196faf507ef6c867e30995a4b957c76d50f6234532f198ab638506b67a'),
      ('guards','PG7626-api-inbox-dependency-guards-v1/manifest.json','c2c89e4b37a70dbb520e5edbccc3c78829c54a4f0a430d979821e615df00ed47'),
      ('platform','PG7413-api-generated-value-review-v2/manifest.json','7d108ca7499763b5ed5526e60144276ace055c66aa88e380a0ccde0a3be2a82e')):
        file=host.BASE/path;sha=host.sha(file);require(digest is None or sha==digest,'exact original public witness')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=path,sha256=sha)
    current=proofs['current'];physical=proofs['physical'];trace=proofs['trace'];old=proofs['previousApi'];prior=proofs['previousReview']
    require(current['source']==physical['source']==trace['source']==compilation.SOURCE and current['tests']==114 and current['suites']==14
      and current['actualSessions']==1 and current['actualCrcMismatch']==0 and len(current['executableClasses'])==23
      and all(v['missed']==0 and v['covered']>0 for v in current['counters'].values()),'same-source actual106/22 four100/CRC/session')
    canonical=lambda row:json.dumps(row,sort_keys=True)
    raw=current['staticRaw']['pmd'];before=old['staticRaw']['pmd']
    require(len(raw['findings'])==13 and raw['actualExit']==4 and raw['processingErrors']==0
      and Counter(map(canonical,raw['findings']))==Counter(map(canonical,before['findings']))
      and prior['actualExit']==0 and prior['currentApiUnclassified']==prior['currentApiApplicableViolations']==0
      and len(prior['staticDispositions'])==13,'all13 individual raw rationale contexts byte-for-byte unchanged')
    require(all(current['sourceFiles'].get(p)==h for p,h in old['sourceFiles'].items())
      and all(current['physicalClasses'].get(p)==h for p,h in old['physicalClasses'].items()),'all old24 source/21physical exact before rationale reuse')
    require(current['spotbugs']['actualExit']==0 and current['spotbugs']['findings']==0
      and current['staticRaw']['checkstyle']['actualExit']==0 and not current['staticRaw']['checkstyle']['findings'],'actual SB/CS zero')
    original=json.loads((execution.SLOT/'manifest.safe.json').read_bytes())
    for simple,count in (('GeneratedMetricValueContractTest',8),('OutboxAgeMetricRecorderTest',8),
      ('OutboxObservationRepositoryTest',10),('OutboxMetricCollectorTest',8),('InboxReplayMetricRecorderTest',8),('MqPressureMetricRecorderTest',8)):
        cases=[r for r in original['cases'] if r['classname'].endswith('.'+simple)]
        require(len(cases)==count and all(r['result']=='PASS' for r in cases),'all prior generated32 and new8 contracts actually run now')
    generated=prior['additionalReview']
    require(generated['currentApiGeneratedTypes']==8 and generated['currentApiGeneratedMethodsSeparatelyVerifiedNotAddedToCounters']==32,
      'exact generated32 baseline, not a counter')
    input_contracts={}
    for path,digest in generated['contractInputHashes'].items():
        blob=subprocess.check_output(['git','show',compilation.SOURCE+':'+path],cwd=host.ROOT)
        if path==execution.POM:
            before_blob=subprocess.check_output(['git','show','a605c7287:'+path],cwd=host.ROOT)
            require(hashlib.sha256(before_blob).hexdigest()==digest,'exact historical baseline harness bytes')
            semantics=verify_harness(before_blob,blob,execution.previous.previous.PROTOCOL_PATH)
            require(original['begin']['inputHashes'][path]==hashlib.sha256(blob).hexdigest()
              ==guards_hash(proofs['guards'],path),'actual executed source and tested guard harness bytes agree')
            input_contracts[path]=dict(kind='EXACT_DECLARED_TEST_DEPENDENCY_ADDITION',beforeSha256=digest,sha256=hashlib.sha256(blob).hexdigest(),semanticGuard=semantics)
        else:
            require(hashlib.sha256(blob).hexdigest()==digest,'every other declared contract input unchanged')
            input_contracts[path]=dict(kind='EXACT_UNCHANGED',sha256=digest)
    require(len(input_contracts)==4 and sum(v['kind']=='EXACT_DECLARED_TEST_DEPENDENCY_ADDITION' for v in input_contracts.values())==1,
      'only one explicitly declared change; no generic hash exception')
    platform=proofs['platform']
    require(host.sha(host.TC/'jdk-25.0.4/lib/modules')==platform['jdkModulesSha256']
      and host.sha(host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar')==platform['jacocoCoreSha256'],
      'same independently inspected JDK/official filter bytes')
    guards=proofs['guards'];require(guards['actualExit']==0 and guards['methods']==6 and guards['harnessNegativeMutations']==8,
      'actual saved new metadata guard terminal')
    for path,digest in guards['inputHashes'].items():require(host.sha(host.ROOT/path)==digest,'all guard source/harness bytes fixed')
    guardlog=host.BASE/'PG7626-api-inbox-dependency-guards-v1/result.log'
    require(host.sha(guardlog)==guards['logSha256'] and 'Ran 6 tests' in guardlog.read_text() and '\nOK\n' in guardlog.read_text(),'actual original metadata result not inferred')
    execution.previous.previous.verify_inputs()
    require(physical['protocolDependencyPhysicalBytesMatched']==176 and physical['unmeasuredProductionDependencyJarHashes']==current['productionDependencyJarHashes']
      =={execution.previous.previous.PROTOCOL_PATH:execution.previous.previous.PROTOCOL_SHA} and physical['protocolDependencyCoverageTransferred'] is False,'same actual dependency bytes, no protocol PT transfer')
    main_path='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/MqPressureMetricRecorder.java'
    code=''.join(subprocess.check_output(['git','show',compilation.SOURCE+':'+main_path],cwd=host.ROOT).decode().split())
    require('for(vardestination:BrokerTopology.values())' in code
      and 'if(messages<0||queueBytes<0||addressMemoryBytes<0||addressPagedBytes<0||pageFiles<0)' in code
      and 'observations=Map.copyOf(rows);' in code
      and 'current.get().map(measure::applyAsDouble).orElse(Double.NaN)' in code
      and 'privatestaticfinalStringADDRESS_LABEL="address";' in code
      and 'privatestaticfinalStringQUEUE_LABEL="queue";' in code
      and 'catch(' not in code and '.close(' not in code,
      'closed destination labels/nonnegative independent fields/unknown NaN/no failure catch-close-retry')
    classes=execution.SLOT/'snapshot/tools/quality/harnesses/target/classes'
    name='dev/codex/schubert/nk/api/monitoring/MqPressureMetricRecorder$Snapshot'
    file=classes/(name+'.class');require(host.sha(file)==current['physicalClasses'][name+'.class'],'new record actual executed bytes')
    command=[str(host.TC/'jdk-25.0.4/bin/javap'),'-p','-c','-v','-classpath',str(classes),name.replace('/','.')]
    done=subprocess.run(command,capture_output=True,text=True);javap=done.stdout
    fields=[('messages','J'),('queueBytes','J'),('addressMemoryBytes','J'),('addressPagedBytes','J'),('pagingActive','Z'),('pageFiles','J')]
    methods=['equals(java.lang.Object)','hashCode()','toString()',*[field+'()' for field,_ in fields]]
    require(done.returncode==0 and 'java/lang/runtime/ObjectMethods.bootstrap' in javap
      and all(m+';' in javap for m in methods)
      and all(re.search(r'REF_getField\s+[^\s]+\.'+f+':'+d,javap) for f,d in fields),
      'all9 generated methods and each primitive bootstrap field')
    new_generated=dict(className=name,sha256=host.sha(file),methods=methods,testId='MQPRESS008',command=command,
      actualExit=done.returncode,stdoutSha256=hashlib.sha256(javap.encode()).hexdigest(),
      stderrSha256=hashlib.sha256(done.stderr.encode()).hexdigest())
    previous={r['path']:r for r in proofs['previousTrace']['sourceRows']};counts=domains(trace,current,physical,previous);negative=[]
    history=next(i for i,r in enumerate(trace['physicalRows']) if r['className'].startswith('batch:') and r['executable'])
    active=next(i for i,r in enumerate(trace['sourceRows']) if r['path'] in current['sourceFiles'])
    anchor=next(i for i,r in enumerate(trace['sourceRows']) if r['path'] in previous)
    for kind in ('historical-current-flag','role-alias','historical-source','current-witness','previous-anchor'):
        mutant=copy.deepcopy(trace)
        if kind=='historical-current-flag':mutant['physicalRows'][history]['currentSourceExecutionAccepted']=True
        elif kind=='role-alias':mutant['physicalRows'][history]['qualificationDomain']='CURRENT_API_QUALIFIED'
        elif kind=='historical-source':mutant['physicalRows'][history]['executionSource']=current['source']
        elif kind=='current-witness':mutant['sourceRows'][active]['executionWitness']['source']=physical['historicalBatch']['source']
        else:mutant['sourceRows'][anchor]['previousSourceByteSha256']='0'*64
        try:domains(mutant,current,physical,previous)
        except ValueError:negative.append(dict(kind=kind,rejected=True))
        else:raise ValueError('provenance mutation accepted')
    dispositions=copy.deepcopy(prior['staticDispositions'])
    for row in dispositions:row.update(ordinaryTestWitness='PG7658-mq-pressure-host-v2',source=compilation.SOURCE)
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),witnesses=pins,
      rawPmdFindings=13,rawPmdExit=4,unchangedIndividualRationaleCount=13,staticDispositions=dispositions,newMainRawFindings=0,
      unclassified=0,actualViolationsOutstanding=0,suppressionsAdded=0,currentApiGeneratedTypes=9,
      contractInputClassifications=input_contracts,priorToolCorrectionBug='BUG-1669',relatedBug='BUG-1670',relatedYkt='YKT-1421',newGeneratedContract=new_generated,
      currentApiGeneratedMethodsSeparatelyVerifiedNotAddedToCounters=41,customExclusionsAdded=False,
      unmeasuredProductionDependencyJarHashes=current['productionDependencyJarHashes'],protocolCoverageTransferred=False,
      negativeGuards=negative,editAnchorCounts=counts,ptExecutedByReview=0,counters=current['counters'],
      whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,targetClassInitializedByReview=False)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rawFindings=13,unclassified=0,generatedMethods=41,negativeGuards=len(negative),anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
