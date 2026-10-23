"""Current API130, old13 plus three exact private-owner context rows, current41 generated contracts and five domain guards."""
from collections import Counter
import copy
import datetime
import json
import os
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
import pg7690_mq_pressure_connection_host as execution
import pg7694_mq_pressure_connection_six_compile as compilation
from monitoring_api_domains import validate_domains
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7700-mq-pressure-connection-review-v1'

def require(value,message):
    if not value:raise ValueError(message)

def domains(trace,current,physical,previous):
    return validate_domains(trace,current,physical,previous,previous_count=108,physical_count=96,test_count=130,current_executable=25)

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only same-source quality review')
    proofs={};pins={}
    for key,path,digest in (
      ('current','PG7692-mq-pressure-connection-post-v1/manifest.json',None),
      ('physical','PG7696-mq-pressure-connection-six-post-v1/manifest.json',None),
      ('trace','PG7698-mq-pressure-connection-trace-v1/manifest.json',None),
      ('previousTrace','PG7682-mq-redelivery-trace-v1/manifest.json','0391c383d310aa9477c8113a6364f623deb6ffbc8149a8adfc7d389a2c73b9bb'),
      ('previousApi','PG7676-mq-redelivery-post-v1/manifest.json','ddf5f0c2709a56bd7d51c348e23cf2e38d2fbf846a75adb088ee0a5c5054ba0d'),
      ('previousReview','PG7684-mq-redelivery-review-v1/manifest.json','3faa0db478fa9cc94584c884bb64715fea3a633b23ac96a7b421fc5e3e5b5df8'),
      ('platform','PG7413-api-generated-value-review-v2/manifest.json','7d108ca7499763b5ed5526e60144276ace055c66aa88e380a0ccde0a3be2a82e')):
        file=host.BASE/path;sha=host.sha(file);require(digest is None or sha==digest,'exact original witness')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=path,sha256=sha)
    current=proofs['current'];physical=proofs['physical'];trace=proofs['trace'];old=proofs['previousApi'];prior=proofs['previousReview']
    require(current['actualExit']==physical['actualExit']==trace['actualExit']==0
      and current['source']==physical['source']==trace['source']==compilation.SOURCE and current['tests']==130 and current['suites']==16
      and current['actualCrcMismatch']==0 and current['actualSessions']==1 and len(current['executableClasses'])==25
      and all(v['missed']==0 and v['covered']>0 for v in current['counters'].values()),'actual same-source130/25/CRC0/one session/four100')
    require(all(current['sourceFiles'].get(p)==h for p,h in old['sourceFiles'].items())
      and all(current['physicalClasses'].get(p)==h for p,h in old['physicalClasses'].items()),'all prior30 source/25 physical unchanged before reason reuse')
    canonical=lambda r:json.dumps(r,sort_keys=True);raw=current['staticRaw']['pmd']
    previous_raw=[row for row in raw['findings'] if row['class']!='MqPressureMetricCollector']
    require(len(raw['findings'])==16 and raw['actualExit']==4 and raw['processingErrors']==0
      and Counter(map(canonical,previous_raw))==Counter(map(canonical,old['staticRaw']['pmd']['findings']))
      and prior['actualExit']==0 and prior['unclassified']==prior['actualViolationsOutstanding']==0
      and len(prior['staticDispositions'])==13,'all prior13 exact rows/rationales plus only three declared owner/failure context rows')
    new_dispositions=[];seen=set()
    expected={('AvoidSynchronizedStatement','30','5'),('AvoidCatchingGenericException','38','16'),('AvoidCatchingGenericException','38','35')}
    source_path='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/MqPressureMetricCollector.java'
    for row in raw['findings']:
        if row['class']!='MqPressureMetricCollector':continue
        key=(row['rule'],row['beginline'],row['begincolumn'])
        require(key in expected and key not in seen and row['method']=='collect'
          and row['package']=='dev.codex.schubert.nk.api.monitoring','each exact current-source new context row')
        seen.add(key);new_dispositions.append(dict(raw=row,classification='CONTEXT_NOT_APPLICABLE',sourcePath=source_path,
          sourceSha256=current['sourceFiles'][source_path],ordinaryTestWitness='PG7690-mq-pressure-connection-host-v1',
          reason='411 private one-owner read/complete publication lock; Runtime/Error clears only selected destination and rethrows same object without format/retry/normalization/close. MQCONN001/003/005/006 independently verify timing, exact failure/null identity and actual owned contender BLOCKED.',sourceOrRulesChanged=False,suppressionAdded=False))
    require(seen==expected,'all three new rows individually classified, no generic rule or source suppression')
    require(current['spotbugs']['actualExit']==0 and current['spotbugs']['findings']==0
      and current['staticRaw']['checkstyle']['actualExit']==0 and not current['staticRaw']['checkstyle']['findings'],'actual SB/CS zero')
    original=json.loads((execution.SLOT/'manifest.safe.json').read_bytes())
    for name,count in (('GeneratedMetricValueContractTest',8),('OutboxAgeMetricRecorderTest',8),
      ('OutboxObservationRepositoryTest',10),('OutboxMetricCollectorTest',8),('MqPressureMetricRecorderTest',8),('MqRedeliveryMetricRecorderTest',8),('MqPressureMetricCollectorTest',8)):
        cases=[r for r in original['cases'] if r['classname'].endswith('.'+name)]
        require(len(cases)==count and all(r['result']=='PASS' for r in cases),'all prior generated41 and new8 contracts run now')
    require(prior['currentApiGeneratedTypes']==9 and prior['currentApiGeneratedMethodsSeparatelyVerifiedNotAddedToCounters']==41
      and current['physicalClasses'][prior['newGeneratedContract']['className']+'.class']==prior['newGeneratedContract']['sha256'],
      'all previous generated contracts exact current bytes, not fabricated counter')
    platform=proofs['platform'];require(host.sha(host.TC/'jdk-25.0.4/lib/modules')==platform['jdkModulesSha256']
      and host.sha(host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar')==platform['jacocoCoreSha256'],'same inspected platform/filter')
    for path,row in prior['contractInputClassifications'].items():require(host.sha(host.ROOT/path)==row['sha256'],'every declared dependency/quality input unchanged')
    execution.dependency.verify_inputs()
    require(current['productionDependencyJarHashes']==physical['unmeasuredProductionDependencyJarHashes']
      and physical['protocolDependencyPhysicalBytesMatched']==176 and physical['protocolDependencyCoverageTransferred'] is False,'same actual unmeasured protocol dependency')
    main_path='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/MqPressureMetricCollector.java'
    code=''.join(subprocess.check_output(['git','show',compilation.SOURCE+':'+main_path],cwd=host.ROOT).decode().split())
    require('privatefinalObjectlock=newObject();' in code and 'synchronized(lock){' in code
      and 'if(!metrics.detailedMetricsRequested())returnOptional.empty();' in code
      and 'catch(RuntimeException|ErrorunavailableObservation){metrics.missing(destination);throwunavailableObservation;}' in code
      and 'Objects.requireNonNull(observation.apply(destination),"MQpressureobservation")' in code
      and '.close(' not in code,'source read then publication under private owner; unavailable is unknown and original failure, never normal return')
    order=['observation.apply(destination)','if(supplied.isPresent())metrics.record(destination,supplied.orElseThrow());','return supplied;']
    offsets=[code.index(''.join(p.split())) for p in order]
    require(offsets==sorted(offsets),'source complete before observation publication and return')
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
    dispositions=copy.deepcopy(prior['staticDispositions'])+new_dispositions
    for row in dispositions:row.update(source=compilation.SOURCE,ordinaryTestWitness='PG7690-mq-pressure-connection-host-v1')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),witnesses=pins,
      staticDispositions=dispositions,rawPmdFindings=16,rawPmdExit=4,newMainRawFindings=3,unclassified=0,actualViolationsOutstanding=0,suppressionsAdded=0,
      currentApiGeneratedTypes=9,currentApiGeneratedMethodsSeparatelyVerifiedNotAddedToCounters=41,customExclusionsAdded=False,
      contractInputClassifications=prior['contractInputClassifications'],newGeneratedContract=prior['newGeneratedContract'],
      generatedContractByteIdentityOnlyNotOldExecution=True,negativeGuards=negative,editAnchorCounts=counts,counters=current['counters'],
      ptExecutedByReview=0,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,targetClassInitializedByReview=False)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rawFindings=16,unclassified=0,generatedMethods=41,negativeGuards=len(negative),anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
