"""Current200 Batch quality/domain validation plus six direct generated Evaluation contracts."""
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
import pg7532_async_byte_unit_host as execution
import pg7536_async_byte_unit_six_compile as compilation
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7543-async-byte-unit-review-v2'

def require(value,message):
    if not value:raise ValueError(message)

def domains(trace,current,physical,previous):
    counts=anchors(trace['sourceRows'],previous,dict(changed=6,unchanged=88,introduced=0));by_path={r['path']:r for r in trace['sourceRows']}
    require(len(trace['physicalRows'])==81 and len({r['className'] for r in trace['physicalRows']})==81,'all80 unique physical')
    for row in trace['sourceRows']:
        path=row['path'];require(row['currentSourceCoverageTransferred'] is False,'no coverage transfer')
        if path in current['sourceFiles']:
            require(row['sha256']==current['sourceFiles'][path] and row['executionWitness']['source']==current['source']
              and row['executionWitness']['tests']==202 and row['componentCounterScope']=='ALL_CURRENT_BATCH_EXECUTABLES_ONLY','only actual Batch source/current200 witness')
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
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only corrected source context review, BUG1666')
    proofs={};pins={}
    for key,path,digest in (
      ('current','PG7534-async-byte-unit-post-v1/manifest.json','11cf6da4a00b9bb8316cec7274ef6263110437336ff1dc7aeeb2b219e976ba64'),
      ('physical','PG7538-async-byte-unit-six-post-v1/manifest.json','8e59fbd578d0c5b3b89e2734d11d0ad41d92ee94a6fc1bef3b35be7ec91bb29d'),
      ('trace','PG7540-async-byte-unit-trace-v1/manifest.json',None),
      ('previousTrace','PG7526-expiry-backlog-trace-v1/manifest.json','58266f8880f2f2efe2fefe757584b0a19b2fe0981faf2e8362639a2549220c65'),
      ('previousBatch','PG7520-expiry-backlog-post-v1/manifest.json','a5b44aae1f25eee8c119e33b4a953779fb0a25aaf36d3fe54dc7e3797e02f7f6'),
      ('previousReview','PG7430-batch-generated-review-v1/manifest.json','5bb62f608a4d31fc31e8a54bc89dd79e0723d0e72eaa45e29416d9aa01acefec'),
      ('webGeneration','PG7500-web-log-backlog-review-v1/manifest.json','618204a0ab00df122f3bb45e08330a5c938fbc12aed43698df9fa30dad00725e'),
      ('expiryGeneration','PG7528-expiry-backlog-review-v1/manifest.json','4f30c5296575b54c684b0608f7b906f0f59cad83ea79d8cf9a7d3322fc585755'),
      ('platform','PG7413-api-generated-value-review-v2/manifest.json','7d108ca7499763b5ed5526e60144276ace055c66aa88e380a0ccde0a3be2a82e')):
        file=host.BASE/path;sha=host.sha(file);require(digest is None or sha==digest,'exact original witness')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=path,sha256=sha)
    current=proofs['current'];physical=proofs['physical'];trace=proofs['trace'];old=proofs['previousBatch'];prior=proofs['previousReview']
    require(current['source']==physical['source']==trace['source']==compilation.SOURCE and current['tests']==202 and current['suites']==27
      and current['actualSessions']==1 and current['actualCrcMismatch']==0 and len(current['executableClasses'])==49
      and all(v['missed']==0 and v['covered']>0 for v in current['counters'].values()),'current202/49/four100')
    canonical=lambda row:json.dumps(row,sort_keys=True);raw=current['staticRaw']['pmd'];before=old['staticRaw']['pmd']
    require(len(raw['findings'])==28 and raw['actualExit']==4 and raw['processingErrors']==0
      and proofs['expiryGeneration']['unclassified']==0,'raw preserved and exact prior rationale witness')
    old_rows=Counter(map(canonical,before['findings']));new_rows=Counter(map(canonical,raw['findings']))
    removed=list((old_rows-new_rows).elements());added=list((new_rows-old_rows).elements())
    require(len(removed)==len(added)==1 and sum((old_rows&new_rows).values())==27,'only one explicit moved context')
    was=json.loads(removed[0]);now=json.loads(added[0])
    require(was['class']==now['class']=='AlertThresholds' and was['method']==now['method']=='percentage'
      and was['rule']==now['rule']=='AvoidLiteralsInIfCondition'
      and was['beginline']==was['endline']=='115' and now['beginline']==now['endline']=='117'
      and {k:v for k,v in was.items() if k not in ('beginline','endline')}==
          {k:v for k,v in now.items() if k not in ('beginline','endline')},'same single rule/context attributes, exact line rebase only')
    threshold_path='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/AlertThresholds.java'
    old_code=subprocess.check_output(['git','show',old['source']+':'+threshold_path],cwd=host.ROOT).decode()
    new_code=subprocess.check_output(['git','show',compilation.SOURCE+':'+threshold_path],cwd=host.ROOT).decode()
    body=r'  private static void percentage\(double value\) \{\n    nonnegativeFinite\(value\);\n    if \(value > 100\) throw new IllegalArgumentException\(INVALID\);\n  \}'
    first=re.findall(body,old_code);last=re.findall(body,new_code)
    require(len(first)==len(last)==1 and first==last
      and old_code.splitlines()[114].strip()==new_code.splitlines()[116].strip()=='if (value > 100) throw new IllegalArgumentException(INVALID);',
      'entire percentage method exact byte text,100 independent semantic boundary not a suppression')
    issue_sources=set()
    for finding in raw['findings']:
        path='src/schubert-nk-batch/src/main/java/'+finding['package'].replace('.','/')+'/'+finding['class'].split('.')[0]+'.java'
        require(path in current['sourceFiles'] and (path==threshold_path or current['sourceFiles'][path]==old['sourceFiles'].get(path)),
          'all other rationale owners byte unchanged; changed percentage explicitly classified')
        issue_sources.add(path)
    context_rebase=dict(previous=was,current=now,sourcePath=threshold_path,
      wholeMethodSha256=hashlib.sha256(first[0].encode()).hexdigest(),
      rationale='100 is dimensionless percent maximum, strict greater-than invalid; exact independent THRESH001/013 include0/100/100.00001 plus NaN and negative',
      actualCurrentThresholdOrdinaryCases=14,changedOtherMainRawFindings=0)
    require(current['spotbugs']['actualExit']==0 and current['spotbugs']['findings']==0
      and current['staticRaw']['checkstyle']['actualExit']==0 and not current['staticRaw']['checkstyle']['findings'],'actual SB/CS zero')
    original=json.loads((execution.SLOT/'manifest.safe.json').read_bytes())
    for simple,count in (('GeneratedBatchValueContractTest',7),('WebLogBacklogMonitorTest',8),
      ('AsyncQueueMonitorTest',9),('ExpiryBacklogMonitorTest',8),('MonitoringPolicyEngineTest',8),('AlertThresholdsTest',14)):
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
    generated=[];classes=execution.SLOT/'snapshot/tools/quality/harnesses/target/classes'
    for simple,fields,testid in (
      ('Evaluation',[('queuedPresent','Z'),('byteUsagePresent','Z'),('event','Ljava/util/Optional;')],'ASYNCQUEUE008'),
      ('ByteUsage',[('usedBytes','J'),('capacityBytes','J')],'ASYNCBYTE002')):
        name='dev/codex/schubert/nk/batch/monitoring/AsyncQueueMonitor$'+simple;file=classes/(name+'.class')
        require(host.sha(file)==current['physicalClasses'][name+'.class'],'actually executed generated class byte')
        command=[str(host.TC/'jdk-25.0.4/bin/javap'),'-p','-c','-v','-classpath',str(classes),name.replace('/','.')]
        done=subprocess.run(command,capture_output=True,text=True);text=done.stdout
        methods=['equals(java.lang.Object)','hashCode()','toString()',*[field+'()' for field,_ in fields]]
        require(done.returncode==0 and 'java/lang/runtime/ObjectMethods.bootstrap' in text
          and all(m+';' in text for m in methods)
          and all(re.search(r'REF_getField\s+[^\s]+\.'+f+':'+d,text) for f,d in fields),'all current generated fields/methods')
        generated.append(dict(className=name,sha256=host.sha(file),methods=methods,testId=testid,command=command,
          actualExit=done.returncode,stdoutSha256=hashlib.sha256(text.encode()).hexdigest(),
          stderrSha256=hashlib.sha256(done.stderr.encode()).hexdigest()))
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
      rawPmdFindings=28,rawPmdExit=4,unchangedIndividualRationaleCount=27,rebasedIndividualRationaleCount=1,contextRebase=context_rebase,issueSources=sorted(issue_sources),
      changedMainRawFindings=1,unclassified=0,actualViolationsOutstanding=0,suppressionsAdded=0,
      correctedGeneratedContracts=generated,currentBatchGeneratedTypes=23,currentBatchGeneratedMethodsSeparatelyVerifiedNotAddedToCounters=82,
      customExclusionsAdded=False,byteCountDimensionsIndependent=True,partialEvidenceNeverNormal=True,
      negativeGuards=negative,editAnchorCounts=counts,ptExecutedByReview=0,counters=current['counters'],
      whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,targetClassInitializedByReview=False)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rawFindings=28,rebased=1,unclassified=0,generatedMethods=82,negativeGuards=len(negative),anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
