"""Current API122, unchanged raw13/41 generated contracts, finite redelivery and five provenance guards."""
from collections import Counter
import copy
import datetime
import json
import os
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
import pg7674_mq_redelivery_host as execution
import pg7678_mq_redelivery_six_compile as compilation
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7684-mq-redelivery-review-v1'

def require(value,message):
    if not value:raise ValueError(message)

def domains(trace,current,physical,previous):
    counts=anchors(trace['sourceRows'],previous,dict(changed=0,unchanged=106,introduced=2))
    paths={r['path']:r for r in trace['sourceRows']}
    require(len(trace['physicalRows'])==95 and len({r['className'] for r in trace['physicalRows']})==95,'all95 unique owners')
    for row in trace['sourceRows']:
        path=row['path'];require(row['currentSourceCoverageTransferred'] is False,'no transferred counters')
        if path in current['sourceFiles']:
            require(row['sha256']==current['sourceFiles'][path] and row['executionWitness']['source']==current['source']
              and row['executionWitness']['tests']==122 and row['componentCounterScope']=='ALL_CURRENT_API_EXECUTABLES_ONLY','current API exact actual witness')
        elif path.endswith('/pom.xml'):
            require(row['componentCounterScope']=='NOT_EXECUTABLE_CONFIGURATION' and row['compileWitness']['source']==current['source'],'normal POM not executed PT')
        else:require('executionWitness' not in row and row['componentCounterScope']=='HISTORICAL_ONLY_NO_CURRENT_COUNTERS','historical source no current PT')
    roles={'api':('CURRENT_API_QUALIFIED',physical['currentApi']),
      'batch':('HISTORICAL_BATCH_BYTE_ONLY',physical['historicalBatch']),
      'web':('HISTORICAL_WEB_BYTE_ONLY',physical['historicalWeb'])}
    for row in trace['physicalRows']:
        role,entry=row['className'].split(':',1);label,proof=roles[role];executable=not entry.endswith('package-info.class')
        path='src/schubert-nk-'+role+'/src/main/java/'+entry.removesuffix('.class').split('$',1)[0]+'.java'
        require(row['qualificationDomain']==label and row['executionSource']==proof['source'] and row['executable'] is executable
          and row['currentSourceExecutionAccepted'] is (role=='api' and executable)
          and row['sha256']==proof['physicalClasses'][row['className']] and row['sourcePath']==path and row['owner']==paths[path]['owner'],
          'all true role/source/bytes/owner/current flags')
    require(sum(r['currentSourceExecutionAccepted'] for r in trace['physicalRows'])==24,'only24 current API executables')
    return counts

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only same-source quality review')
    proofs={};pins={}
    for key,path,digest in (
      ('current','PG7676-mq-redelivery-post-v1/manifest.json',None),
      ('physical','PG7680-mq-redelivery-six-post-v1/manifest.json',None),
      ('trace','PG7682-mq-redelivery-trace-v1/manifest.json',None),
      ('previousTrace','PG7666-mq-pressure-trace-v2/manifest.json','24dc29624cad45fd24f63bc9c6d9eeddb414baf913726182cda487a81c4c93fa'),
      ('previousApi','PG7660-mq-pressure-post-v2/manifest.json','020a8f6e8bf6b5e479229bdc025fd8cbc2a9e07e6900e2262df9cb9298621587'),
      ('previousReview','PG7668-mq-pressure-review-v2/manifest.json','d4c08cb34a35e94ea76efbe5c0bc6748ed5da190ecf5f66d7a832bfa1b06abf0'),
      ('platform','PG7413-api-generated-value-review-v2/manifest.json','7d108ca7499763b5ed5526e60144276ace055c66aa88e380a0ccde0a3be2a82e')):
        file=host.BASE/path;sha=host.sha(file);require(digest is None or sha==digest,'exact original witness')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=path,sha256=sha)
    current=proofs['current'];physical=proofs['physical'];trace=proofs['trace'];old=proofs['previousApi'];prior=proofs['previousReview']
    require(current['actualExit']==physical['actualExit']==trace['actualExit']==0
      and current['source']==physical['source']==trace['source']==compilation.SOURCE and current['tests']==122 and current['suites']==15
      and current['actualCrcMismatch']==0 and current['actualSessions']==1 and len(current['executableClasses'])==24
      and all(v['missed']==0 and v['covered']>0 for v in current['counters'].values()),'actual same-source122/24/CRC0/one session/four100')
    require(all(current['sourceFiles'].get(p)==h for p,h in old['sourceFiles'].items())
      and all(current['physicalClasses'].get(p)==h for p,h in old['physicalClasses'].items()),'all prior28 source/24 physical unchanged before reason reuse')
    canonical=lambda r:json.dumps(r,sort_keys=True);raw=current['staticRaw']['pmd']
    require(len(raw['findings'])==13 and raw['actualExit']==4 and raw['processingErrors']==0
      and Counter(map(canonical,raw['findings']))==Counter(map(canonical,old['staticRaw']['pmd']['findings']))
      and prior['actualExit']==0 and prior['unclassified']==prior['actualViolationsOutstanding']==0
      and len(prior['staticDispositions'])==13,'all13 unchanged individual source/position reasons, not blanket suppression')
    require(current['spotbugs']['actualExit']==0 and current['spotbugs']['findings']==0
      and current['staticRaw']['checkstyle']['actualExit']==0 and not current['staticRaw']['checkstyle']['findings'],'actual SB/CS zero')
    original=json.loads((execution.SLOT/'manifest.safe.json').read_bytes())
    for name,count in (('GeneratedMetricValueContractTest',8),('OutboxAgeMetricRecorderTest',8),
      ('OutboxObservationRepositoryTest',10),('OutboxMetricCollectorTest',8),('MqPressureMetricRecorderTest',8),('MqRedeliveryMetricRecorderTest',8)):
        cases=[r for r in original['cases'] if r['classname'].endswith('.'+name)]
        require(len(cases)==count and all(r['result']=='PASS' for r in cases),'all prior generated41 and new8 contracts run now')
    require(prior['currentApiGeneratedTypes']==9 and prior['currentApiGeneratedMethodsSeparatelyVerifiedNotAddedToCounters']==41
      and current['physicalClasses'][prior['newGeneratedContract']['className']+'.class']==prior['newGeneratedContract']['sha256'],
      'all previous generated contracts exact current bytes, not fabricated counter')
    platform=proofs['platform'];require(host.sha(host.TC/'jdk-25.0.4/lib/modules')==platform['jdkModulesSha256']
      and host.sha(host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar')==platform['jacocoCoreSha256'],'same inspected platform/filter')
    for path,row in prior['contractInputClassifications'].items():require(host.sha(host.ROOT/path)==row['sha256'],'every declared dependency/quality input unchanged')
    execution.previous.previous.previous.verify_inputs()
    require(current['productionDependencyJarHashes']==physical['unmeasuredProductionDependencyJarHashes']
      and physical['protocolDependencyPhysicalBytesMatched']==176 and physical['protocolDependencyCoverageTransferred'] is False,'same actual unmeasured protocol dependency')
    main_path='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/MqRedeliveryMetricRecorder.java'
    code=''.join(subprocess.check_output(['git','show',compilation.SOURCE+':'+main_path],cwd=host.ROOT).decode().split())
    require('for(vardestination:BrokerTopology.values())' in code and 'for(intdelivery=2;delivery<=4;delivery++)' in code
      and 'if(deliveryCount<1||deliveryCount>4)' in code and 'if(detailed&&deliveryCount>1)' in code
      and '.tag("queue",destination.queue()).tag("delivery_count",Integer.toString(delivery))' in code
      and 'catch(' not in code and '.close(' not in code and '.increment();' in code,'finite initial1 excluded/redelivery2..4/no retry or failure normalization')
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
    for row in dispositions:row.update(source=compilation.SOURCE,ordinaryTestWitness='PG7674-mq-redelivery-host-v1')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),witnesses=pins,
      staticDispositions=dispositions,rawPmdFindings=13,rawPmdExit=4,newMainRawFindings=0,unclassified=0,actualViolationsOutstanding=0,suppressionsAdded=0,
      currentApiGeneratedTypes=9,currentApiGeneratedMethodsSeparatelyVerifiedNotAddedToCounters=41,customExclusionsAdded=False,
      contractInputClassifications=prior['contractInputClassifications'],newGeneratedContract=prior['newGeneratedContract'],
      generatedContractByteIdentityOnlyNotOldExecution=True,negativeGuards=negative,editAnchorCounts=counts,counters=current['counters'],
      ptExecutedByReview=0,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,targetClassInitializedByReview=False)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rawFindings=13,unclassified=0,generatedMethods=41,negativeGuards=len(negative),anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
