"""Current200 Batch quality/domain validation plus six direct generated Evaluation contracts."""
from collections import Counter
import copy
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
import pg7549_protected_alert_host as execution
import pg7553_protected_alert_six_compile as compilation
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7558-protected-alert-review-v1'

def require(value,message):
    if not value:raise ValueError(message)

def domains(trace,current,physical,previous):
    counts=anchors(trace['sourceRows'],previous,dict(changed=5,unchanged=89,introduced=0));by_path={r['path']:r for r in trace['sourceRows']}
    require(len(trace['physicalRows'])==81 and len({r['className'] for r in trace['physicalRows']})==81,'all80 unique physical')
    for row in trace['sourceRows']:
        path=row['path'];require(row['currentSourceCoverageTransferred'] is False,'no coverage transfer')
        if path in current['sourceFiles']:
            require(row['sha256']==current['sourceFiles'][path] and row['executionWitness']['source']==current['source']
              and row['executionWitness']['tests']==204 and row['componentCounterScope']=='ALL_CURRENT_BATCH_EXECUTABLES_ONLY','only actual Batch source/current200 witness')
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
    require(sum(r['currentSourceExecutionAccepted'] for r in trace['physicalRows'])==49,'all current48 and historical31 distinct')
    return counts


def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only protected auto-close source review, BUG1667')
    proofs={};pins={}
    for key,path,digest in (
      ('current','PG7550-protected-alert-post-v1/manifest.json',None),
      ('physical','PG7554-protected-alert-six-post-v1/manifest.json',None),
      ('trace','PG7556-protected-alert-trace-v1/manifest.json',None),
      ('previousTrace','PG7540-async-byte-unit-trace-v1/manifest.json','662fa8a43b797e2ceafa2c2d6f3fe8ab9c449e6013cee1c6c601fc8eaf28bd81'),
      ('previousBatch','PG7534-async-byte-unit-post-v1/manifest.json','11cf6da4a00b9bb8316cec7274ef6263110437336ff1dc7aeeb2b219e976ba64'),
      ('asyncGeneration','PG7543-async-byte-unit-review-v2/manifest.json','03d1e311e2c32f5270138b0851afe03edfcee913b30df21e685534c51c84baac'),
      ('previousReview','PG7430-batch-generated-review-v1/manifest.json','5bb62f608a4d31fc31e8a54bc89dd79e0723d0e72eaa45e29416d9aa01acefec'),
      ('webGeneration','PG7500-web-log-backlog-review-v1/manifest.json','618204a0ab00df122f3bb45e08330a5c938fbc12aed43698df9fa30dad00725e'),
      ('expiryGeneration','PG7528-expiry-backlog-review-v1/manifest.json','4f30c5296575b54c684b0608f7b906f0f59cad83ea79d8cf9a7d3322fc585755'),
      ('platform','PG7413-api-generated-value-review-v2/manifest.json','7d108ca7499763b5ed5526e60144276ace055c66aa88e380a0ccde0a3be2a82e')):
        file=host.BASE/path;sha=host.sha(file);require(digest is None or sha==digest,'exact original witness')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=path,sha256=sha)
    current=proofs['current'];physical=proofs['physical'];trace=proofs['trace'];old=proofs['previousBatch'];prior=proofs['previousReview']
    require(current['source']==physical['source']==trace['source']==compilation.SOURCE and current['tests']==204 and current['suites']==27
      and current['actualSessions']==1 and current['actualCrcMismatch']==0 and len(current['executableClasses'])==49
      and all(v['missed']==0 and v['covered']>0 for v in current['counters'].values()),'current204/49/four100')
    canonical=lambda row:json.dumps(row,sort_keys=True);raw=current['staticRaw']['pmd'];before=old['staticRaw']['pmd']
    require(len(raw['findings'])==28 and raw['actualExit']==4 and raw['processingErrors']==0
      and proofs['expiryGeneration']['unclassified']==0,'raw preserved and exact prior rationale witness')
    old_rows=Counter(map(canonical,before['findings']));new_rows=Counter(map(canonical,raw['findings']))
    removed=[json.loads(x) for x in (old_rows-new_rows).elements()];added=[json.loads(x) for x in (new_rows-old_rows).elements()]
    require(len(removed)==len(added)==2 and sum((old_rows&new_rows).values())==26,'two explicit moved synchronization rows only')
    old_core='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/AlertLifecycle.java'
    was_source=subprocess.check_output(['git','show',old['source']+':'+old_core],cwd=host.ROOT).decode()
    now_source=subprocess.check_output(['git','show',compilation.SOURCE+':'+old_core],cwd=host.ROOT).decode()
    inserted='    // SS351 §12: routine normal samples/cause flags cannot retire investigation-required alerts.\n    if (conditionKey == Condition.DLQ || conditionKey == Condition.INTEGRITY_CONFIG) return active;\n'
    require(now_source.count(inserted)==1 and now_source.replace(inserted,'')==was_source,
      'only declared two-line guard changes core; all synchronize methods/locks/body text unchanged')
    rebase=[]
    for method,line_before,line_after in (('interruptContinuity','177','179'),('snapshot','186','188')):
        old_match=[x for x in removed if x['method']==method];new_match=[x for x in added if x['method']==method]
        require(len(old_match)==len(new_match)==1,'one row per explicit method')
        was=old_match[0];now=new_match[0]
        require(was['class']==now['class']=='AlertLifecycle' and was['rule']==now['rule']=='AvoidSynchronizedStatement'
          and was['beginline']==was['endline']==line_before and now['beginline']==now['endline']==line_after
          and {k:v for k,v in was.items() if k not in ('beginline','endline')}==
              {k:v for k,v in now.items() if k not in ('beginline','endline')},'exact row attrs, only explicit source insertion line shift')
        rebase.append(dict(previous=was,current=now,rationale='unchanged private lock/no blocking I/O, existing bounded ordinary concurrency and continuity tests execute current source'))
    issue_sources=set()
    for finding in raw['findings']:
        path='src/schubert-nk-batch/src/main/java/'+finding['package'].replace('.','/')+'/'+finding['class'].split('.')[0]+'.java'
        require(path in current['sourceFiles'] and (path==old_core or current['sourceFiles'][path]==old['sourceFiles'].get(path)),
          'all other individual rationale owners unchanged, changed core exact two-line delta reviewed')
        issue_sources.add(path)
    context_rebase=dict(sourcePath=old_core,rows=rebase,declaredCoreInsertionSha256=hashlib.sha256(inserted.encode()).hexdigest(),
      originalCoreSha256=old['sourceFiles'][old_core],currentCoreSha256=current['sourceFiles'][old_core],
      unchangedObservedSynchronizationRow=True,noRawSuppression=True)
    require(current['spotbugs']['actualExit']==0 and current['spotbugs']['findings']==0
      and current['staticRaw']['checkstyle']['actualExit']==0 and not current['staticRaw']['checkstyle']['findings'],'actual SB/CS zero')
    original=json.loads((execution.SLOT/'manifest.safe.json').read_bytes())
    for simple,count in (('GeneratedBatchValueContractTest',7),('WebLogBacklogMonitorTest',8),
      ('AsyncQueueMonitorTest',9),('ExpiryBacklogMonitorTest',8),('MonitoringPolicyEngineTest',8),('AlertThresholdsTest',14),('AlertLifecycleTest',12),('AlertRegistryTest',4),('MonitoringMissingObservationTest',3)):
        group=[r for r in original['cases'] if r['classname'].endswith('.'+simple)]
        require(len(group)==count and all(r['result']=='PASS' for r in group),'all affected and generated cases actually run')
    for row in prior['generatedTypes']:
        require(current['physicalClasses'].get(row['className']+'.class')==row['sha256'],'prior19 types same byte/current GENB7 not old PT')
    for key in ('webGeneration','expiryGeneration'):
        row=proofs[key]['newGeneratedContract']
        require(current['physicalClasses'].get(row['className']+'.class')==row['sha256'],'unchanged record/current ordinary contract')
    platform=proofs['platform']
    require(host.sha(host.TC/'jdk-25.0.4/lib/modules')==platform['jdkModulesSha256']
      and host.sha(host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar')==platform['jacocoCoreSha256'],
      'same official generated filter/JDK byte proof, no PT transfer')
    generated=proofs['asyncGeneration']['correctedGeneratedContracts']
    require(len(generated)==2 and sum(len(x['methods']) for x in generated)==11,'exact corrected Async11 methods')
    for row in generated:
        require(current['physicalClasses'].get(row['className']+'.class')==row['sha256'],
          'unchanged Async generated Main bytes/current ordinary9 including independent byte oracle, not historic PT transfer')
    src='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/'
    code=lambda name:''.join(subprocess.check_output(['git','show',compilation.SOURCE+':'+src+name+'.java'],cwd=host.ROOT).decode().split())
    threshold=code('AlertThresholds');monitor=code('AsyncQueueMonitor');engine=code('MonitoringPolicyEngine')
    require('asyncQueue(longqueued,longusedBytes,longcapacityBytes)' in threshold
      and 'BigInteger.valueOf(usedBytes).multiply(BigInteger.valueOf(100))' in threshold
      and 'BigInteger.valueOf(capacityBytes)' in threshold and 'nonnegative(usedBytes)' in threshold
      and 'thresholds.asyncQueue(queued,usedBytes,capacityBytes)' in engine
      and 'thresholds.asyncQueue(queued.orElse(0),bytes.usedBytes(),bytes.capacityBytes())' in monitor
      and 'booleancomplete=queued.isPresent()&&byteUsage.isPresent()' in monitor
      and '!complete&&level==Severity.NORMAL?lifecycle.snapshot()' in monitor,
      'independent byte/count dimensions and incomplete evidence never establishes recovery')
    lifecycle=code('AlertLifecycle')
    require('if(conditionKey==Condition.DLQ||conditionKey==Condition.INTEGRITY_CONFIG)returnactive;' in lifecycle,
      'explicit protected-key auto-close prohibition remains in actual source')
    previous={r['path']:r for r in proofs['previousTrace']['sourceRows']};counts=domains(trace,current,physical,previous);negative=[]
    history=next(i for i,r in enumerate(trace['physicalRows']) if r['className'].startswith('api:') and r['executable'])
    active=next(i for i,r in enumerate(trace['sourceRows']) if r['path'] in current['sourceFiles'])
    changed=next(i for i,r in enumerate(trace['sourceRows']) if r['sourceChangedSincePreviousTrace'])
    for kind in ('historical-current-flag','role-alias','historical-source','current-witness','previous-anchor','changed-flag'):
        mutant=copy.deepcopy(trace)
        if kind=='historical-current-flag':mutant['physicalRows'][history]['currentSourceExecutionAccepted']=True
        elif kind=='role-alias':mutant['physicalRows'][history]['qualificationDomain']='CURRENT_BATCH_QUALIFIED'
        elif kind=='historical-source':mutant['physicalRows'][history]['executionSource']=current['source']
        elif kind=='current-witness':mutant['sourceRows'][active]['executionWitness']['source']=physical['historicalApi']['source']
        elif kind=='previous-anchor':mutant['sourceRows'][changed]['previousSourceByteSha256']='0'*64
        else:mutant['sourceRows'][changed]['sourceChangedSincePreviousTrace']=False
        try:domains(mutant,current,physical,previous)
        except ValueError:negative.append(dict(kind=kind,rejected=True))
        else:raise ValueError('provenance mutation accepted')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),witnesses=pins,
      rawPmdFindings=28,rawPmdExit=4,unchangedIndividualRationaleCount=26,rebasedIndividualRationaleCount=2,contextRebase=context_rebase,issueSources=sorted(issue_sources),
      changedMainRawFindings=3,unclassified=0,actualViolationsOutstanding=0,suppressionsAdded=0,
      correctedGeneratedContracts=generated,currentBatchGeneratedTypes=23,currentBatchGeneratedMethodsSeparatelyVerifiedNotAddedToCounters=82,
      customExclusionsAdded=False,byteCountDimensionsIndependent=True,protectedAutoCloseProhibited=True,partialEvidenceNeverNormal=True,
      negativeGuards=negative,editAnchorCounts=counts,ptExecutedByReview=0,counters=current['counters'],
      whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,targetClassInitializedByReview=False)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rawFindings=28,rebased=2,unclassified=0,generatedMethods=82,negativeGuards=len(negative),anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
