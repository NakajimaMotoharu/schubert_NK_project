"""Current192 Batch quality/domain validation plus six direct generated Evaluation contracts."""
from collections import Counter
import copy
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import pg6966_chr_adapter_host as host
import pg7504_async_queue_host as execution
import pg7508_async_queue_six_compile as compilation
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7514-async-queue-review-v1'

def require(value,message):
    if not value:raise ValueError(message)

def domains(trace,current,physical,previous):
    counts=anchors(trace['sourceRows'],previous,dict(changed=0,unchanged=90,introduced=2));by_path={r['path']:r for r in trace['sourceRows']}
    require(len(trace['physicalRows'])==78 and len({r['className'] for r in trace['physicalRows']})==78,'all78 unique physical')
    for row in trace['sourceRows']:
        path=row['path'];require(row['currentSourceCoverageTransferred'] is False,'no coverage transfer')
        if path in current['sourceFiles']:
            require(row['sha256']==current['sourceFiles'][path] and row['executionWitness']['source']==current['source']
              and row['executionWitness']['tests']==192 and row['componentCounterScope']=='ALL_CURRENT_BATCH_EXECUTABLES_ONLY','only actual Batch source/current192 witness')
        elif path.endswith('/pom.xml'):
            require(row['componentCounterScope']=='NOT_EXECUTABLE_CONFIGURATION' and row['compileWitness']['source']==current['source'],'POM actual normal compile, not PT')
        else:require('executionWitness' not in row and row['componentCounterScope']=='HISTORICAL_ONLY_NO_CURRENT_COUNTERS','historical source lacks current execution witness')
    expected={'batch':('CURRENT_BATCH_QUALIFIED',physical['currentBatch']),
      'api':('HISTORICAL_API_BYTE_ONLY',physical['historicalApi']),'web':('HISTORICAL_WEB_BYTE_ONLY',physical['historicalWeb'])}
    for row in trace['physicalRows']:
        role,entry=row['className'].split(':',1);label,proof=expected[role];executable=not entry.endswith('package-info.class')
        path='src/schubert-nk-'+role+'/src/main/java/'+entry.removesuffix('.class').split('$',1)[0]+'.java'
        require(row['qualificationDomain']==label and row['executionSource']==proof['source'] and row['executable'] is executable
          and row['currentSourceExecutionAccepted'] is (role=='batch' and executable)
          and row['sha256']==proof['physicalClasses'][row['className']] and row['sourcePath']==path and row['owner']==by_path[path]['owner'],
          'true role/source/class byte/owner, no aliases')
    require(sum(r['currentSourceExecutionAccepted'] for r in trace['physicalRows'])==46,'all current46 and historical31 distinct')
    return counts

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only current-source quality review')
    proofs={};pins={}
    for key,path,digest in (
      ('current','PG7506-async-queue-post-v1/manifest.json',None),
      ('physical','PG7510-async-queue-six-post-v1/manifest.json',None),
      ('trace','PG7512-async-queue-trace-v1/manifest.json',None),
      ('previousTrace','PG7498-web-log-backlog-trace-v1/manifest.json','00cd30701bf388273093753457df0dd333aa2f32a0f4c5041862fa0feb45b008'),
      ('previousBatch','PG7492-web-log-backlog-post-v1/manifest.json','cd8cdea5901615449f5f626722c7d9266d766f4f15539fcf3b6d8ef0d377a198'),
      ('previousReview','PG7430-batch-generated-review-v1/manifest.json','5bb62f608a4d31fc31e8a54bc89dd79e0723d0e72eaa45e29416d9aa01acefec'),
      ('webGeneration','PG7500-web-log-backlog-review-v1/manifest.json','618204a0ab00df122f3bb45e08330a5c938fbc12aed43698df9fa30dad00725e'),
      ('platform','PG7413-api-generated-value-review-v2/manifest.json','7d108ca7499763b5ed5526e60144276ace055c66aa88e380a0ccde0a3be2a82e')):
        file=host.BASE/path;sha=host.sha(file);require(digest is None or sha==digest,'exact original public witness')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=path,sha256=sha)
    current=proofs['current'];physical=proofs['physical'];trace=proofs['trace'];old=proofs['previousBatch'];prior=proofs['previousReview']
    require(current['source']==physical['source']==trace['source']==compilation.SOURCE and current['tests']==192 and current['suites']==26
      and current['actualSessions']==1 and current['actualCrcMismatch']==0 and len(current['executableClasses'])==46
      and all(v['missed']==0 and v['covered']>0 for v in current['counters'].values()),'all192 current46 positive four-counter qualification')
    canonical=lambda row:json.dumps(row,sort_keys=True);raw=current['staticRaw']['pmd'];before=old['staticRaw']['pmd']
    require(len(raw['findings'])==28 and raw['actualExit']==4 and raw['processingErrors']==0
      and Counter(map(canonical,raw['findings']))==Counter(map(canonical,before['findings']))
      and prior['actualExit']==0 and prior['unclassified']==0 and prior['rawPmdFindings']==28,'all28 same individual reasons and actual raw preserved')
    require(all(current['sourceFiles'].get(p)==h for p,h in old['sourceFiles'].items())
      and all(current['physicalClasses'].get(p)==h for p,h in old['physicalClasses'].items()),'all original Batch source/class bytes before rationale reuse')
    require(current['spotbugs']['actualExit']==0 and current['spotbugs']['findings']==0
      and current['staticRaw']['checkstyle']['actualExit']==0 and not current['staticRaw']['checkstyle']['findings'],'actual current SB/CS zero')
    original=json.loads((execution.SLOT/'manifest.safe.json').read_bytes())
    for simple,count in (('GeneratedBatchValueContractTest',7),('WebLogBacklogMonitorTest',8),('AsyncQueueMonitorTest',8)):
        group=[r for r in original['cases'] if r['classname'].endswith('.'+simple)]
        require(len(group)==count and all(r['result']=='PASS' for r in group),'current source actually executed all generated and new cases')
    for row in prior['generatedTypes']:require(current['physicalClasses'].get(row['className']+'.class')==row['sha256'],'all prior60 contract Main bytes exact, no old PT transfer')
    require(proofs['webGeneration']['actualExit']==0 and proofs['webGeneration']['unclassified']==0
      and proofs['webGeneration']['rawPmdFindings']==28
      and proofs['webGeneration']['witnesses']['current']['sha256']==pins['previousBatch']['sha256'],
      'exact immediate previous source static reasons, not an older-source-only rationale')
    web_record=proofs['webGeneration']['newGeneratedContract']
    require(current['physicalClasses'].get(web_record['className']+'.class')==web_record['sha256'],'prior WebLog generated6 actual Main bytes with current ordinary8, not historical PT transfer')
    name='dev/codex/schubert/nk/batch/monitoring/AsyncQueueMonitor$Evaluation'
    classes=execution.SLOT/'snapshot/tools/quality/harnesses/target/classes';file=classes/(name+'.class')
    require(host.sha(file)==current['physicalClasses'][name+'.class'],'new record actually executed byte')
    command=[str(host.TC/'jdk-25.0.4/bin/javap'),'-p','-c','-v','-classpath',str(classes),name.replace('/','.')]
    done=subprocess.run(command,capture_output=True,text=True);text=done.stdout
    methods=['equals(java.lang.Object)','hashCode()','toString()','queuedPresent()','capacityPresent()','event()']
    require(done.returncode==0 and 'java/lang/runtime/ObjectMethods.bootstrap' in text and all(m+';' in text for m in methods)
      and all(re.search(r'REF_getField\s+[^\s]+\.'+field+':'+descriptor,text) for field,descriptor in (
        ('queuedPresent','Z'),('capacityPresent','Z'),('event','Ljava/util/Optional;'))),'all six generated contracts and every field in actual bootstrap')
    platform=proofs['platform'];require(host.sha(host.TC/'jdk-25.0.4/lib/modules')==platform['jdkModulesSha256']
      and host.sha(host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar')==platform['jacocoCoreSha256'],'same original platform31fold/official filter byte proof, not runtime transfer')
    source='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/AsyncQueueMonitor.java'
    code=''.join(subprocess.check_output(['git','show',compilation.SOURCE+':'+source],cwd=host.ROOT).decode().split())
    require('capacity.orElse(Long.MAX_VALUE)' in code and 'thresholds.asyncQueue(' in code
      and 'booleancomplete=queued.isPresent()&&capacity.isPresent();' in code
      and 'if(!continuous||!complete)lifecycle.interruptContinuity(at.elapsed());' in code
      and '!complete&&level==Severity.NORMAL?lifecycle.snapshot():lifecycle.observe(' in code,
      'partial evidence never asserts normal recovery, known abnormal and explicit gap retained')
    previous={r['path']:r for r in proofs['previousTrace']['sourceRows']};counts=domains(trace,current,physical,previous);negative=[]
    history=next(i for i,r in enumerate(trace['physicalRows']) if r['className'].startswith('api:') and r['executable'])
    active=next(i for i,r in enumerate(trace['sourceRows']) if r['path'] in current['sourceFiles'])
    anchor=next(i for i,r in enumerate(trace['sourceRows']) if r['path'] in previous)
    for kind in ('historical-current-flag','role-alias','historical-source','current-witness','previous-anchor'):
        changed=copy.deepcopy(trace)
        if kind=='historical-current-flag':changed['physicalRows'][history]['currentSourceExecutionAccepted']=True
        elif kind=='role-alias':changed['physicalRows'][history]['qualificationDomain']='CURRENT_BATCH_QUALIFIED'
        elif kind=='historical-source':changed['physicalRows'][history]['executionSource']=current['source']
        elif kind=='current-witness':changed['sourceRows'][active]['executionWitness']['source']=physical['historicalApi']['source']
        else:changed['sourceRows'][anchor]['previousSourceByteSha256']='0'*64
        try:domains(changed,current,physical,previous)
        except ValueError:negative.append(dict(kind=kind,rejected=True))
        else:raise ValueError('independent role/source/counter provenance mutation accepted')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),witnesses=pins,
      rawPmdFindings=28,rawPmdExit=4,unchangedIndividualRationaleCount=28,newMainRawFindings=0,unclassified=0,actualViolationsOutstanding=0,suppressionsAdded=0,
      newGeneratedContract=dict(className=name,sha256=host.sha(file),methods=methods,testIds=['ASYNCQUEUE008'],command=command,actualExit=0,
        stdoutSha256=hashlib.sha256(done.stdout.encode()).hexdigest(),stderrSha256=hashlib.sha256(done.stderr.encode()).hexdigest(),
        independentEmptyHash=1221152,nonemptyHash='1221152 + platform Object identity of immutable Event'),
      currentBatchGeneratedTypes=21,currentBatchGeneratedMethodsSeparatelyVerifiedNotAddedToCounters=72,customExclusionsAdded=False,
      partialEvidenceNeverNormal=True,negativeGuards=negative,editAnchorCounts=counts,ptExecutedByReview=0,counters=current['counters'],
      whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,targetClassInitializedByReview=False)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rawFindings=28,unclassified=0,newGeneratedMethods=6,negativeGuards=len(negative),anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
