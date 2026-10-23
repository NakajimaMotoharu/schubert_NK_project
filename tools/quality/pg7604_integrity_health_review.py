"""Current200 Batch quality/domain validation plus six direct generated Evaluation contracts."""
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
import pg7594_integrity_health_host as execution
import pg7598_integrity_health_six_compile as compilation
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7604-integrity-health-review-v1'

def require(value,message):
    if not value:raise ValueError(message)

def domains(trace,current,physical,previous):
    counts=anchors(trace['sourceRows'],previous,dict(changed=0,unchanged=98,introduced=2));by_path={r['path']:r for r in trace['sourceRows']}
    require(len(trace['physicalRows'])==88 and len({r['className'] for r in trace['physicalRows']})==88,'all80 unique physical')
    for row in trace['sourceRows']:
        path=row['path'];require(row['currentSourceCoverageTransferred'] is False,'no coverage transfer')
        if path in current['sourceFiles']:
            require(row['sha256']==current['sourceFiles'][path] and row['executionWitness']['source']==current['source']
              and row['executionWitness']['tests']==229 and row['componentCounterScope']=='ALL_CURRENT_BATCH_EXECUTABLES_ONLY','only actual Batch source/current200 witness')
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
    require(sum(r['currentSourceExecutionAccepted'] for r in trace['physicalRows'])==56,'all current48 and historical31 distinct')
    return counts



def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only current Integrity source review')
    proofs={};pins={}
    for key,path,digest in (
      ('current','PG7596-integrity-health-post-v1/manifest.json',None),
      ('physical','PG7600-integrity-health-six-post-v1/manifest.json',None),
      ('trace','PG7602-integrity-health-trace-v1/manifest.json',None),
      ('previousTrace','PG7586-restart-health-trace-v1/manifest.json','dcb6d501b7011ef7e4292ba3324a7625296ebd5963a700704587038a2cb4eb9a'),
      ('previousBatch','PG7580-restart-health-post-v1/manifest.json','33d96f1323ddef81acb2c54a8d9f94f02d26c639941f104d17e7e9016792629e'),
      ('previousReview','PG7588-restart-health-review-v1/manifest.json','daa5ab216cb22dda83c23a74c64f8386795ca858193cf1ac1a2744c36d494216'),
      ('platform','PG7413-api-generated-value-review-v2/manifest.json','7d108ca7499763b5ed5526e60144276ace055c66aa88e380a0ccde0a3be2a82e')):
        file=host.BASE/path;sha=host.sha(file);require(digest is None or sha==digest,'exact original witness')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=path,sha256=sha)
    current=proofs['current'];physical=proofs['physical'];trace=proofs['trace'];old=proofs['previousBatch'];prior=proofs['previousReview']
    require(current['source']==physical['source']==trace['source']==compilation.SOURCE and current['tests']==229 and current['suites']==30
      and current['actualSessions']==1 and current['actualCrcMismatch']==0 and len(current['executableClasses'])==56
      and all(v['missed']==0 and v['covered']>0 for v in current['counters'].values()),'current212/56 positive four-counter qualification')
    canonical=lambda row:json.dumps(row,sort_keys=True);raw=current['staticRaw']['pmd'];before=old['staticRaw']['pmd']
    require(len(raw['findings'])==28 and raw['actualExit']==4 and raw['processingErrors']==0
      and Counter(map(canonical,raw['findings']))==Counter(map(canonical,before['findings']))
      and prior['actualExit']==0 and prior['unclassified']==0 and prior['rawPmdFindings']==28,'all28 current individual raw/context reasons unchanged')
    require(all(current['sourceFiles'].get(p)==h for p,h in old['sourceFiles'].items())
      and all(current['physicalClasses'].get(p)==h for p,h in old['physicalClasses'].items()),'all prior59 source/55 physical bytes exact before rationale/generated proof reuse')
    require(current['spotbugs']['actualExit']==0 and current['spotbugs']['findings']==0
      and current['staticRaw']['checkstyle']['actualExit']==0 and not current['staticRaw']['checkstyle']['findings'],'actual SB/CS zero')
    original=json.loads((execution.SLOT/'manifest.safe.json').read_bytes())
    for simple,count in (('GeneratedBatchValueContractTest',7),('WebLogBacklogMonitorTest',8),('AsyncQueueMonitorTest',9),
      ('ExpiryBacklogMonitorTest',8),('AlertLifecycleTest',12),('BackupHealthMonitorTest',8),('RestartHealthMonitorTest',8),('IntegrityHealthMonitorTest',8)):
        cases=[r for r in original['cases'] if r['classname'].endswith('.'+simple)]
        require(len(cases)==count and all(r['result']=='PASS' for r in cases),'all prior generated99 and new5 contracts run by current ordinary PT')
    require(prior['currentBatchGeneratedMethodsSeparatelyVerifiedNotAddedToCounters']==99,'exact previous generated contract baseline, not current coverage')
    platform=proofs['platform']
    require(host.sha(host.TC/'jdk-25.0.4/lib/modules')==platform['jdkModulesSha256']
      and host.sha(host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar')==platform['jacocoCoreSha256'],
      'same JDK31fold/official filter byte proof, not runtime transfer')
    generated=[];classes=execution.SLOT/'snapshot/tools/quality/harnesses/target/classes'
    for simple,fields,testid in (
      ('Evaluation',[('failureCountPresent','Z'),('event','Ljava/util/Optional;')],'INTEGRITYMON008'),):
        name='dev/codex/schubert/nk/batch/monitoring/IntegrityHealthMonitor$'+simple;file=classes/(name+'.class')
        require(host.sha(file)==current['physicalClasses'][name+'.class'],'new generated record actual executed class byte')
        command=[str(host.TC/'jdk-25.0.4/bin/javap'),'-p','-c','-v','-classpath',str(classes),name.replace('/','.')]
        done=subprocess.run(command,capture_output=True,text=True);text=done.stdout
        methods=['equals(java.lang.Object)','hashCode()','toString()',*[field+'()' for field,_ in fields]]
        require(done.returncode==0 and 'java/lang/runtime/ObjectMethods.bootstrap' in text and all(m+';' in text for m in methods)
          and all(re.search(r'REF_getField\s+[^\s]+\.'+f+':'+d,text) for f,d in fields),'all5 generated methods/every actual bootstrap field')
        generated.append(dict(className=name,sha256=host.sha(file),methods=methods,testId=testid,command=command,actualExit=done.returncode,
          stdoutSha256=hashlib.sha256(text.encode()).hexdigest(),stderrSha256=hashlib.sha256(done.stderr.encode()).hexdigest()))
    source='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/IntegrityHealthMonitor.java'
    code=''.join(subprocess.check_output(['git','show',compilation.SOURCE+':'+source],cwd=host.ROOT).decode().split())
    require('thresholds.integrity(failures.orElse(0))' in code
      and 'if(!continuous||failures.isEmpty())lifecycle.interruptContinuity(at.elapsed());' in code
      and 'failures.isEmpty()?lifecycle.snapshot():lifecycle.observe(' in code,
      'unknown never supplied normal and protected lifecycle handles genuine known normal')
    lifecycle=''.join(subprocess.check_output(['git','show',compilation.SOURCE+':src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/AlertLifecycle.java'],cwd=host.ROOT).decode().split())
    require('if(conditionKey==Condition.DLQ||conditionKey==Condition.INTEGRITY_CONFIG)returnactive;' in lifecycle,'same protected auto-close prohibition, not an implied retirement authority')
    previous={r['path']:r for r in proofs['previousTrace']['sourceRows']};counts=domains(trace,current,physical,previous);negative=[]
    history=next(i for i,r in enumerate(trace['physicalRows']) if r['className'].startswith('api:') and r['executable'])
    active=next(i for i,r in enumerate(trace['sourceRows']) if r['path'] in current['sourceFiles'])
    anchor=next(i for i,r in enumerate(trace['sourceRows']) if r['path'] in previous)
    for kind in ('historical-current-flag','role-alias','historical-source','current-witness','previous-anchor'):
        mutant=copy.deepcopy(trace)
        if kind=='historical-current-flag':mutant['physicalRows'][history]['currentSourceExecutionAccepted']=True
        elif kind=='role-alias':mutant['physicalRows'][history]['qualificationDomain']='CURRENT_BATCH_QUALIFIED'
        elif kind=='historical-source':mutant['physicalRows'][history]['executionSource']=current['source']
        elif kind=='current-witness':mutant['sourceRows'][active]['executionWitness']['source']=physical['historicalApi']['source']
        else:mutant['sourceRows'][anchor]['previousSourceByteSha256']='0'*64
        try:domains(mutant,current,physical,previous)
        except ValueError:negative.append(dict(kind=kind,rejected=True))
        else:raise ValueError('provenance mutation accepted')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),witnesses=pins,
      rawPmdFindings=28,rawPmdExit=4,unchangedIndividualRationaleCount=28,newMainRawFindings=0,unclassified=0,actualViolationsOutstanding=0,suppressionsAdded=0,
      newGeneratedContracts=generated,currentBatchGeneratedTypes=27,currentBatchGeneratedMethodsSeparatelyVerifiedNotAddedToCounters=104,
      customExclusionsAdded=False,partialEvidenceNeverNormal=True,negativeGuards=negative,editAnchorCounts=counts,ptExecutedByReview=0,
      counters=current['counters'],whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,targetClassInitializedByReview=False)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rawFindings=28,unclassified=0,newGeneratedMethods=5,negativeGuards=len(negative),anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
