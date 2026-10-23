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
import pg7578_restart_health_host as execution
import pg7582_restart_health_six_compile as compilation
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7588-restart-health-review-v1'

def require(value,message):
    if not value:raise ValueError(message)

def domains(trace,current,physical,previous):
    counts=anchors(trace['sourceRows'],previous,dict(changed=4,unchanged=92,introduced=2));by_path={r['path']:r for r in trace['sourceRows']}
    require(len(trace['physicalRows'])==86 and len({r['className'] for r in trace['physicalRows']})==86,'all80 unique physical')
    for row in trace['sourceRows']:
        path=row['path'];require(row['currentSourceCoverageTransferred'] is False,'no coverage transfer')
        if path in current['sourceFiles']:
            require(row['sha256']==current['sourceFiles'][path] and row['executionWitness']['source']==current['source']
              and row['executionWitness']['tests']==221 and row['componentCounterScope']=='ALL_CURRENT_BATCH_EXECUTABLES_ONLY','only actual Batch source/current200 witness')
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
    require(sum(r['currentSourceExecutionAccepted'] for r in trace['physicalRows'])==54,'all current48 and historical31 distinct')
    return counts



def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only Restart/rate-limit source review')
    proofs={};pins={}
    for key,path,digest in (
      ('current','PG7580-restart-health-post-v1/manifest.json',None),
      ('physical','PG7584-restart-health-six-post-v1/manifest.json',None),
      ('trace','PG7586-restart-health-trace-v1/manifest.json',None),
      ('previousTrace','PG7570-backup-health-trace-v1/manifest.json','3146aaf1d84f57795bebfec0795303f770c42f824fcbb2e30fbfbede63fff2d0'),
      ('previousBatch','PG7564-backup-health-post-v1/manifest.json','91774ed46664a490dd9286d521ca77b78444f0bb228717d9b3135dbbee6add20'),
      ('previousReview','PG7572-backup-health-review-v1/manifest.json','4da20ac3a0afe88cae37349ecfaa9f8b5e1f9e43886caeb9518d0e8a73fe1daf'),
      ('platform','PG7413-api-generated-value-review-v2/manifest.json','7d108ca7499763b5ed5526e60144276ace055c66aa88e380a0ccde0a3be2a82e')):
        file=host.BASE/path;sha=host.sha(file);require(digest is None or sha==digest,'exact original witness')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=path,sha256=sha)
    current=proofs['current'];physical=proofs['physical'];trace=proofs['trace'];old=proofs['previousBatch'];prior=proofs['previousReview']
    require(current['source']==physical['source']==trace['source']==compilation.SOURCE and current['tests']==221 and current['suites']==29
      and current['actualSessions']==1 and current['actualCrcMismatch']==0 and len(current['executableClasses'])==54
      and all(v['missed']==0 and v['covered']>0 for v in current['counters'].values()),'current212/54 positive four-counter qualification')
    canonical=lambda row:json.dumps(row,sort_keys=True);raw=current['staticRaw']['pmd'];before=old['staticRaw']['pmd']
    require(len(raw['findings'])==28 and raw['actualExit']==4 and raw['processingErrors']==0
      and Counter(map(canonical,raw['findings']))==Counter(map(canonical,before['findings']))
      and prior['actualExit']==0 and prior['unclassified']==0 and prior['rawPmdFindings']==28,'all28 current individual raw/context reasons unchanged')
    base='src/schubert-nk-batch/src/';pkg='dev/codex/schubert/nk/batch/monitoring/'
    expected_edits={base+kind+'/java/'+pkg+name+'.java' for kind,name in (
      ('main','AlertThresholds'),('main','MonitoringPolicyEngine'),('test','AlertThresholdsTest'),('test','MonitoringPolicyEngineTest'))}
    changed={p for p,h in old['sourceFiles'].items() if current['sourceFiles'].get(p)!=h}
    require(changed==expected_edits,'exact four existing source edits, no historical alias')
    changed_classes={pkg+name+'.class' for name in ('AlertThresholds','MonitoringPolicyEngine')}
    require(all(current['physicalClasses'].get(p)==h for p,h in old['physicalClasses'].items() if p not in changed_classes)
      and all(current['physicalClasses'][p]!=old['physicalClasses'][p] for p in changed_classes),
      'only two declared old Main class bytes change; all prior generated93 classes unchanged')
    def source_text(source,name):
        return subprocess.check_output(['git','show',source+':'+base+'main/java/'+pkg+name+'.java'],cwd=host.ROOT).decode()
    threshold_before=source_text(old['source'],'AlertThresholds');threshold_now=source_text(compilation.SOURCE,'AlertThresholds')
    expected=threshold_before.replace('public Severity restarts(long lastTenMinutes) {','public Severity restarts(long lastTenMinutes, boolean rateLimited) {').replace(
      'return level(lastTenMinutes >= 5, lastTenMinutes >= 1);','return level(lastTenMinutes >= 5 || rateLimited, lastTenMinutes >= 1);')
    require(expected!=threshold_before and threshold_now==expected,'threshold only exact signature/independent OR insertion; percentage full method remains byte text identical')
    engine_before=source_text(old['source'],'MonitoringPolicyEngine');engine_now=source_text(compilation.SOURCE,'MonitoringPolicyEngine')
    expected=engine_before.replace('Service service, long lastTenMinutes, ObservationContext context) {',
      'Service service, long lastTenMinutes, boolean rateLimited, ObservationContext context) {').replace(
      '    return record(Condition.RESTART, service, thresholds.restarts(lastTenMinutes), context);',
      '    return record(\n        Condition.RESTART, service, thresholds.restarts(lastTenMinutes, rateLimited), context);')
    require(expected!=engine_before and engine_now==expected,'engine only exact independent flag passthrough change')
    for finding in raw['findings']:
        path=base+'main/java/'+finding['package'].replace('.','/')+'/'+finding['class'].split('.')[0]+'.java'
        if path==base+'main/java/'+pkg+'AlertThresholds.java':
            require(finding['method']=='percentage' and finding['rule']=='AvoidLiteralsInIfCondition'
              and finding['beginline']==finding['endline']=='117','exact unchanged100 percentage boundary context, no broad source exemption')
        else:require(current['sourceFiles'][path]==old['sourceFiles'][path],'all other rationale owners byte unchanged')
    require(current['spotbugs']['actualExit']==0 and current['spotbugs']['findings']==0
      and current['staticRaw']['checkstyle']['actualExit']==0 and not current['staticRaw']['checkstyle']['findings'],'actual SB/CS zero')
    original=json.loads((execution.SLOT/'manifest.safe.json').read_bytes())
    for simple,count in (('GeneratedBatchValueContractTest',7),('WebLogBacklogMonitorTest',8),('AsyncQueueMonitorTest',9),
      ('ExpiryBacklogMonitorTest',8),('AlertLifecycleTest',12),('RestartHealthMonitorTest',8),('RestartHealthMonitorTest',8),('MonitoringPolicyEngineTest',9),('AlertThresholdsTest',14)):
        cases=[r for r in original['cases'] if r['classname'].endswith('.'+simple)]
        require(len(cases)==count and all(r['result']=='PASS' for r in cases),'all prior generated93 and new6 contracts run by current ordinary PT')
    require(prior['currentBatchGeneratedMethodsSeparatelyVerifiedNotAddedToCounters']==93,'exact previous generated contract baseline, not current coverage')
    platform=proofs['platform']
    require(host.sha(host.TC/'jdk-25.0.4/lib/modules')==platform['jdkModulesSha256']
      and host.sha(host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar')==platform['jacocoCoreSha256'],
      'same JDK31fold/official filter byte proof, not runtime transfer')
    generated=[];classes=execution.SLOT/'snapshot/tools/quality/harnesses/target/classes'
    for simple,fields,testid in (
      ('Evaluation',[('restartCountPresent','Z'),('rateLimitPresent','Z'),('event','Ljava/util/Optional;')],'RESTARTMON008'),):
        name='dev/codex/schubert/nk/batch/monitoring/RestartHealthMonitor$'+simple;file=classes/(name+'.class')
        require(host.sha(file)==current['physicalClasses'][name+'.class'],'new generated record actual executed class byte')
        command=[str(host.TC/'jdk-25.0.4/bin/javap'),'-p','-c','-v','-classpath',str(classes),name.replace('/','.')]
        done=subprocess.run(command,capture_output=True,text=True);text=done.stdout
        methods=['equals(java.lang.Object)','hashCode()','toString()',*[field+'()' for field,_ in fields]]
        require(done.returncode==0 and 'java/lang/runtime/ObjectMethods.bootstrap' in text and all(m+';' in text for m in methods)
          and all(re.search(r'REF_getField\s+[^\s]+\.'+f+':'+d,text) for f,d in fields),'all6 generated methods/every actual bootstrap field')
        generated.append(dict(className=name,sha256=host.sha(file),methods=methods,testId=testid,command=command,actualExit=done.returncode,
          stdoutSha256=hashlib.sha256(text.encode()).hexdigest(),stderrSha256=hashlib.sha256(done.stderr.encode()).hexdigest()))
    source='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/RestartHealthMonitor.java'
    code=''.join(subprocess.check_output(['git','show',compilation.SOURCE+':'+source],cwd=host.ROOT).decode().split())
    require('thresholds.restarts(lastTenMinutes.orElse(0),rateLimited.orElse(false))' in code
      and 'booleancomplete=lastTenMinutes.isPresent()&&rateLimited.isPresent();' in code
      and 'if(!continuous||!complete)lifecycle.interruptContinuity(at.elapsed());' in code
      and '!complete&&level==Severity.NORMAL?lifecycle.snapshot()' in code,'independent flag/missing evidence never establishes recovery')
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
      rawPmdFindings=28,rawPmdExit=4,unchangedIndividualRationaleCount=27,unchangedMethodWithinChangedSourceRationale=1,newMainRawFindings=0,unclassified=0,actualViolationsOutstanding=0,suppressionsAdded=0,
      newGeneratedContracts=generated,currentBatchGeneratedTypes=26,currentBatchGeneratedMethodsSeparatelyVerifiedNotAddedToCounters=99,
      customExclusionsAdded=False,partialEvidenceNeverNormal=True,negativeGuards=negative,editAnchorCounts=counts,ptExecutedByReview=0,
      counters=current['counters'],whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,targetClassInitializedByReview=False)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rawFindings=28,unclassified=0,newGeneratedMethods=6,negativeGuards=len(negative),anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
