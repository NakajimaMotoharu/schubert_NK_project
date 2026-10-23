"""API162/34 same-source quality, existing17 individual reasons and generated52+2; no synthetic counters."""
from collections import Counter
import copy
import json
import os
from pathlib import Path
import pg6966_chr_adapter_host as host
import pg7912_mq_event_host as execution
import pg7916_mq_event_six_compile as compilation
import pg7032_monitoring_six_artifact_post as steps
from monitoring_api_domains import validate_domains
from host_tool_invocation import capture,verify
OUT=host.BASE/'PG7922-mq-event-review-v1'
PREFIX='dev/codex/schubert/nk/api/monitoring/'
def require(value,message):
    if not value:raise ValueError(message)
def domains(trace,current,physical,previous):
    return validate_domains(trace,current,physical,previous,previous_count=127,physical_count=114,test_count=162,current_executable=34)
def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only exact quality review')
    proofs={};pins={}
    for key,path,digest in (
      ('current','PG7914-mq-event-post-v1/manifest.json',None),
      ('physical','PG7918-mq-event-six-post-v1/manifest.json',None),
      ('trace','PG7920-mq-event-trace-v1/manifest.json',None),
      ('previousTrace','PG7900-mq-duration-trace-v1/manifest.json','a9b64acc272d4af3b0270c70ac92ebc5cdb7bd2e00f494ae7460c9464fc88b06'),
      ('previousApi','PG7894-mq-duration-post-v1/manifest.json','136eeab5dba12fb70fddcd8b19e66196d53d24aeb11b9077d4b2a9b854f98072'),
      ('previousReview','PG7902-mq-duration-review-v1/manifest.json','8b7bc1e6c063413185839d69274b66374b8301248020c9e7fdb6e37fc7201d73'),
      ('platform','PG7413-api-generated-value-review-v2/manifest.json','7d108ca7499763b5ed5526e60144276ace055c66aa88e380a0ccde0a3be2a82e')):
        f=host.BASE/path;sha=host.sha(f);require(digest is None or sha==digest,'exact original witness')
        proofs[key]=json.loads(f.read_bytes());pins[key]=dict(path=path,sha256=sha)
    c=proofs['current'];p=proofs['physical'];t=proofs['trace'];old=proofs['previousApi'];prior=proofs['previousReview']
    require(c['actualExit']==p['actualExit']==t['actualExit']==0 and c['source']==p['source']==t['source']==compilation.SOURCE
      and c['tests']==162 and c['suites']==20 and len(c['sourceFiles'])==40 and len(c['executableClasses'])==34
      and len(c['physicalClasses'])==35 and c['actualCrcMismatch']==0 and c['actualSessions']==1
      and all(v['missed']==0 and v['covered']>0 for v in c['counters'].values()),'actual162/34 same-source/singleexec/four100')
    require(all(c['sourceFiles'].get(k)==v for k,v in old['sourceFiles'].items())
      and all(c['physicalClasses'].get(k)==v for k,v in old['physicalClasses'].items()),'all old38 Java/33 physical unchanged including debug')
    canonical=lambda r:json.dumps(r,sort_keys=True);raw=c['staticRaw']['pmd']
    require(raw['actualExit']==4 and raw['processingErrors']==0 and len(raw['findings'])==17
      and Counter(map(canonical,raw['findings']))==Counter(map(canonical,old['staticRaw']['pmd']['findings']))
      and prior['actualExit']==0 and prior['unclassified']==prior['actualViolationsOutstanding']==0
      and len(prior['staticDispositions'])==17,'all17 exact individual reason rows and no new issue')
    dispositions=copy.deepcopy(prior['staticDispositions'])
    for row in dispositions:
        source=row['sourcePath'];require(source in c['sourceFiles'] and c['sourceFiles'][source]==old['sourceFiles'][source],'every issue-bearing source unchanged')
        row.update(source=compilation.SOURCE,ordinaryTestWitness='PG7912-mq-event-host-v1',currentRationaleWitness=pins['previousReview'])
    require(c['spotbugs']['actualExit']==0 and c['spotbugs']['findings']==0
      and c['staticRaw']['checkstyle']['actualExit']==0 and not c['staticRaw']['checkstyle']['findings'],'actual SB/CS0')
    run=json.loads((execution.SLOT/'manifest.safe.json').read_bytes())
    require(run['actualExit']==0 and len(run['cases'])==162 and all(r['result']=='PASS' for r in run['cases']),'all current ordinary cases PASS')
    require(len([r for r in run['cases'] if r['classname'].endswith('.MqMessageMetricRecorderTest')])==8
      and any(r['name']=='mqEvent003SevenTypedStageMappingsAndGeneratedFactoriesRejectUnknownOrNull' for r in run['cases']),
      'eight new cases include independent enum generated factories')
    require(prior['currentApiGeneratedTypes']==13 and prior['currentApiGeneratedMethodsSeparatelyVerifiedNotAddedToCounters']==52,'old52 separate generated contracts')
    platform=proofs['platform'];require(host.sha(host.TC/'jdk-25.0.4/lib/modules')==platform['jdkModulesSha256']
      and host.sha(host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar')==platform['jacocoCoreSha256'],'same official filters/platform')
    work=host.W/'pg7922-mq-event-review-v1';require(not work.exists(),'new-only metadata work');work.mkdir();steps.SLOT=work
    classes=execution.SLOT/'snapshot/tools/quality/harnesses/target/classes';generated=[]
    for suffix in ('Stage',):
        name=PREFIX+'MqMessageMetricRecorder$'+suffix;f=classes/(name+'.class')
        require(host.sha(f)==c['physicalClasses'][name+'.class'],'exact current executed enum byte')
        receipt,stdout=steps.step('javap-'+suffix,[str(host.TC/'jdk-25.0.4/bin/javap'),'-p','-c','-s',str(f)])
        require(receipt['actualExit']==0 and 'values();' in stdout and 'valueOf(java.lang.String);' in stdout
          and 'clone:' in stdout and 'java/lang/Enum.valueOf:' in stdout,'two generated enum methods direct typed current ordinary plus noninitializing bytecode')
        generated.append(dict(className=name,sha256=host.sha(f),methods=['values','valueOf'],ordinaryTest='MQEVENT003',receipt=receipt))
    main_path='src/schubert-nk-api/src/main/java/'+PREFIX+'MqMessageMetricRecorder.java'
    code=''.join((host.ROOT/main_path).read_text().split())
    require('LayoutRegistry.standard().require(Objects.requireNonNull(layout,"MQmetriclayout"),1)' in code
      and 'Objects.requireNonNull(destination,"MQmetricdestination")' in code
      and 'Counter.builder("nk_mq_messages_total")' in code
      and 'stage.direction()' in code and 'stage.outcome()' in code and 'destination.address()' in code
      and '.close(' not in code and 'catch(' not in code and 'nanoTime(' not in code
      and '.send(' not in code and '.acknowledge(' not in code,'closed supplied stage labels and single increment, never broker authority')
    previous={r['path']:r for r in proofs['previousTrace']['sourceRows']};counts=domains(t,c,p,previous);negative=[]
    history=next(i for i,r in enumerate(t['physicalRows']) if r['className'].startswith('batch:') and r['executable'])
    active=next(i for i,r in enumerate(t['sourceRows']) if r['path'] in c['sourceFiles'])
    anchor=next(i for i,r in enumerate(t['sourceRows']) if r['path'] in previous)
    for kind in ('historical-current-flag','role-alias','historical-source','current-witness','previous-anchor'):
        mutant=copy.deepcopy(t)
        if kind=='historical-current-flag':mutant['physicalRows'][history]['currentSourceExecutionAccepted']=True
        elif kind=='role-alias':mutant['physicalRows'][history]['qualificationDomain']='CURRENT_API_QUALIFIED'
        elif kind=='historical-source':mutant['physicalRows'][history]['executionSource']=c['source']
        elif kind=='current-witness':mutant['sourceRows'][active]['executionWitness']['source']=p['historicalBatch']['source']
        else:mutant['sourceRows'][anchor]['previousSourceByteSha256']='0'*64
        try:domains(mutant,c,p,previous)
        except ValueError:negative.append(dict(kind=kind,rejected=True))
        else:raise ValueError('invalid provenance accepted')
    require(c['productionDependencyJarHashes']==p['unmeasuredProductionDependencyJarHashes']
      and p['protocolDependencyPhysicalBytesMatched']==176 and p['protocolDependencyCoverageTransferred'] is False,'no dependency counter transfer')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,witnesses=pins,staticDispositions=dispositions,
      rawPmdFindings=17,rawPmdExit=4,newMainRawFindings=0,unclassified=0,actualViolationsOutstanding=0,suppressionsAdded=0,
      currentApiGeneratedTypes=14,currentApiGeneratedMethodsSeparatelyVerifiedNotAddedToCounters=54,newGeneratedContracts=generated,
      existingGenerated52CurrentSourceAndOrdinaryQualified=True,generatedContractByteIdentityOnlyNotOldExecution=True,
      negativeGuards=negative,editAnchorCounts=counts,counters=c['counters'],customExclusionsAdded=False,
      ptExecutedByReview=0,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,
      actualVmActions=0,actualDatabaseActions=0,targetClassInitializedByReview=False)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rawFindings=17,unclassified=0,generatedMethods=54,negativeGuards=5,manifestSha256=host.sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
