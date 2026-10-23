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
import pg7562_backup_health_host as execution
import pg7566_backup_health_six_compile as compilation
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7572-backup-health-review-v1'

def require(value,message):
    if not value:raise ValueError(message)

def domains(trace,current,physical,previous):
    counts=anchors(trace['sourceRows'],previous,dict(changed=0,unchanged=94,introduced=2));by_path={r['path']:r for r in trace['sourceRows']}
    require(len(trace['physicalRows'])==84 and len({r['className'] for r in trace['physicalRows']})==84,'all80 unique physical')
    for row in trace['sourceRows']:
        path=row['path'];require(row['currentSourceCoverageTransferred'] is False,'no coverage transfer')
        if path in current['sourceFiles']:
            require(row['sha256']==current['sourceFiles'][path] and row['executionWitness']['source']==current['source']
              and row['executionWitness']['tests']==212 and row['componentCounterScope']=='ALL_CURRENT_BATCH_EXECUTABLES_ONLY','only actual Batch source/current200 witness')
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
    require(sum(r['currentSourceExecutionAccepted'] for r in trace['physicalRows'])==52,'all current48 and historical31 distinct')
    return counts



def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only current Backup source review')
    proofs={};pins={}
    for key,path,digest in (
      ('current','PG7564-backup-health-post-v1/manifest.json',None),
      ('physical','PG7568-backup-health-six-post-v1/manifest.json',None),
      ('trace','PG7570-backup-health-trace-v1/manifest.json',None),
      ('previousTrace','PG7556-protected-alert-trace-v1/manifest.json','1c6883b725742d327cf00c0ff6cc5d4dccc1119dfd324a73ab1656878ef91c55'),
      ('previousBatch','PG7550-protected-alert-post-v1/manifest.json','a66a2a1f437ac38b95c1619e1b4d9daae480e0800f8d5df18a0e31334e616e52'),
      ('previousReview','PG7558-protected-alert-review-v1/manifest.json','6b7bdebb0764238cce1d51bc176a3d8940ac55b4614b36efdf9f8260cf2e1a82'),
      ('platform','PG7413-api-generated-value-review-v2/manifest.json','7d108ca7499763b5ed5526e60144276ace055c66aa88e380a0ccde0a3be2a82e')):
        file=host.BASE/path;sha=host.sha(file);require(digest is None or sha==digest,'exact original witness')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=path,sha256=sha)
    current=proofs['current'];physical=proofs['physical'];trace=proofs['trace'];old=proofs['previousBatch'];prior=proofs['previousReview']
    require(current['source']==physical['source']==trace['source']==compilation.SOURCE and current['tests']==212 and current['suites']==28
      and current['actualSessions']==1 and current['actualCrcMismatch']==0 and len(current['executableClasses'])==52
      and all(v['missed']==0 and v['covered']>0 for v in current['counters'].values()),'current212/52 positive four-counter qualification')
    canonical=lambda row:json.dumps(row,sort_keys=True);raw=current['staticRaw']['pmd'];before=old['staticRaw']['pmd']
    require(len(raw['findings'])==28 and raw['actualExit']==4 and raw['processingErrors']==0
      and Counter(map(canonical,raw['findings']))==Counter(map(canonical,before['findings']))
      and prior['actualExit']==0 and prior['unclassified']==0 and prior['rawPmdFindings']==28,'all28 current individual raw/context reasons unchanged')
    require(all(current['sourceFiles'].get(p)==h for p,h in old['sourceFiles'].items())
      and all(current['physicalClasses'].get(p)==h for p,h in old['physicalClasses'].items()),'all prior55 source/50 physical bytes exact before rationale/generated proof reuse')
    require(current['spotbugs']['actualExit']==0 and current['spotbugs']['findings']==0
      and current['staticRaw']['checkstyle']['actualExit']==0 and not current['staticRaw']['checkstyle']['findings'],'actual SB/CS zero')
    original=json.loads((execution.SLOT/'manifest.safe.json').read_bytes())
    for simple,count in (('GeneratedBatchValueContractTest',7),('WebLogBacklogMonitorTest',8),('AsyncQueueMonitorTest',9),
      ('ExpiryBacklogMonitorTest',8),('AlertLifecycleTest',12),('BackupHealthMonitorTest',8)):
        cases=[r for r in original['cases'] if r['classname'].endswith('.'+simple)]
        require(len(cases)==count and all(r['result']=='PASS' for r in cases),'all prior generated82 and new11 contracts run by current ordinary PT')
    require(prior['currentBatchGeneratedMethodsSeparatelyVerifiedNotAddedToCounters']==82,'exact previous generated contract baseline, not current coverage')
    platform=proofs['platform']
    require(host.sha(host.TC/'jdk-25.0.4/lib/modules')==platform['jdkModulesSha256']
      and host.sha(host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar')==platform['jacocoCoreSha256'],
      'same JDK31fold/official filter byte proof, not runtime transfer')
    generated=[];classes=execution.SLOT/'snapshot/tools/quality/harnesses/target/classes'
    for simple,fields,testid in (
      ('Completion',[('scheduledRunPassed','Z'),('todaySuccess','Z')],'BACKUPMON007'),
      ('Evaluation',[('completionPresent','Z'),('failureCountPresent','Z'),('event','Ljava/util/Optional;')],'BACKUPMON008')):
        name='dev/codex/schubert/nk/batch/monitoring/BackupHealthMonitor$'+simple;file=classes/(name+'.class')
        require(host.sha(file)==current['physicalClasses'][name+'.class'],'new generated record actual executed class byte')
        command=[str(host.TC/'jdk-25.0.4/bin/javap'),'-p','-c','-v','-classpath',str(classes),name.replace('/','.')]
        done=subprocess.run(command,capture_output=True,text=True);text=done.stdout
        methods=['equals(java.lang.Object)','hashCode()','toString()',*[field+'()' for field,_ in fields]]
        require(done.returncode==0 and 'java/lang/runtime/ObjectMethods.bootstrap' in text and all(m+';' in text for m in methods)
          and all(re.search(r'REF_getField\s+[^\s]+\.'+f+':'+d,text) for f,d in fields),'all11 generated methods/every actual bootstrap field')
        generated.append(dict(className=name,sha256=host.sha(file),methods=methods,testId=testid,command=command,actualExit=done.returncode,
          stdoutSha256=hashlib.sha256(text.encode()).hexdigest(),stderrSha256=hashlib.sha256(done.stderr.encode()).hexdigest()))
    source='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/BackupHealthMonitor.java'
    code=''.join(subprocess.check_output(['git','show',compilation.SOURCE+':'+source],cwd=host.ROOT).decode().split())
    require('thresholds.backup(status.scheduledRunPassed(),status.todaySuccess(),consecutiveFailures.orElse(0))' in code
      and 'booleancomplete=completion.isPresent()&&consecutiveFailures.isPresent();' in code
      and 'if(!continuous||!complete)lifecycle.interruptContinuity(at.elapsed());' in code
      and '!complete&&level==Severity.NORMAL?lifecycle.snapshot()' in code,'unknown partial evidence cannot establish normal recovery')
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
      newGeneratedContracts=generated,currentBatchGeneratedTypes=25,currentBatchGeneratedMethodsSeparatelyVerifiedNotAddedToCounters=93,
      customExclusionsAdded=False,partialEvidenceNeverNormal=True,negativeGuards=negative,editAnchorCounts=counts,ptExecutedByReview=0,
      counters=current['counters'],whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,targetClassInitializedByReview=False)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rawFindings=28,unclassified=0,newGeneratedMethods=11,negativeGuards=len(negative),anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
