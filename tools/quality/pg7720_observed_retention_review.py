"""Same-source Batch245: exact Mode-only addition, raw25 unchanged/3 declaration moves, generated120 and provenance guards."""
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
import pg7710_observed_retention_host as execution
import pg7714_observed_retention_six_compile as compilation
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7720-observed-retention-review-v1'
POLICY='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/MonitoringModePolicy.java'

def require(value,message):
    if not value:raise ValueError(message)

def compact(text):
    return ''.join(re.sub(r'/\*.*?\*/|//[^\n]*','',text,flags=re.S).split())

def previous_semantics(before,after):
    result=compact(after)
    additions=(
      'importjava.util.Optional;',
      'publicrecordRetentionConfiguration(intdays,longbytes){publicRetentionConfiguration{if(days<0||bytes<0)thrownewIllegalArgumentException("CONFIG_INVALID");}}',
      'privatestaticfinalStringDRIFT_CODE="CONFIG_DRIFT";',
      'publicvoidverifyObservedRetention(Optional<RetentionConfiguration>observed){Objects.requireNonNull(observed,"retentionconfigurationobservation");if(observed.isEmpty())thrownewIllegalStateException(DRIFT_CODE);varconfiguration=observed.orElseThrow();if(configuration.days()!=retentionDays||configuration.bytes()!=retentionBytes)thrownewIllegalStateException(DRIFT_CODE);}')
    for addition in additions:
        require(result.count(addition)==1,'only each exact declared import/value type/constant/guard added')
        result=result.replace(addition,'',1)
    require(result.count('thrownewIllegalStateException(DRIFT_CODE);')==2,'only two preexisting literal factoring sites')
    result=result.replace('thrownewIllegalStateException(DRIFT_CODE);','thrownewIllegalStateException("CONFIG_DRIFT");')
    require(result==compact(before),'all original enum constants/fields/constructors/method logic unchanged after exact reverse projection')
    return dict(additions=4,oldLiteralFactoringSites=2,allOriginalExecutableSourceSemanticsPreserved=True,commentsAndWhitespaceOnlyNormalized=True)

def domains(trace,current,physical,previous):
    counts=anchors(trace['sourceRows'],previous,dict(changed=1,unchanged=109,introduced=1))
    paths={r['path']:r for r in trace['sourceRows']}
    require(len(trace['sourceRows'])==111 and len(trace['physicalRows'])==97 and len({r['className'] for r in trace['physicalRows']})==97,'all unique111/97 source owners')
    for row in trace['sourceRows']:
        path=row['path'];require(row['currentSourceCoverageTransferred'] is False,'no transferred counters')
        if path in current['sourceFiles']:
            require(row['sha256']==current['sourceFiles'][path] and row['executionWitness']['source']==current['source']
              and row['executionWitness']['tests']==245 and row['componentCounterScope']=='ALL_CURRENT_BATCH_EXECUTABLES_ONLY','current actual Batch source only')
        elif path.endswith('/pom.xml'):
            require(row['componentCounterScope']=='NOT_EXECUTABLE_CONFIGURATION' and row['compileWitness']['source']==current['source'],'POM is normal compile not PT')
        else:require('executionWitness' not in row and row['componentCounterScope']=='HISTORICAL_ONLY_NO_CURRENT_COUNTERS','history not current PT')
    roles={'batch':('CURRENT_BATCH_QUALIFIED',physical['currentBatch']),
      'api':('HISTORICAL_API_BYTE_ONLY',physical['historicalApi']),'web':('HISTORICAL_WEB_BYTE_ONLY',physical['historicalWeb'])}
    for row in trace['physicalRows']:
        role,entry=row['className'].split(':',1);label,proof=roles[role];executable=not entry.endswith('package-info.class')
        path='src/schubert-nk-'+role+'/src/main/java/'+entry.removesuffix('.class').split('$',1)[0]+'.java'
        require(row['qualificationDomain']==label and row['executionSource']==proof['source'] and row['executable'] is executable
          and row['currentSourceExecutionAccepted'] is (role=='batch' and executable)
          and row['sha256']==proof['physicalClasses'][row['className']] and row['sourcePath']==path and row['owner']==paths[path]['owner'],
          'every true role/source/byte/owner/current flag')
    require(sum(r['currentSourceExecutionAccepted'] for r in trace['physicalRows'])==60,'current Batch60 only')
    return counts

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only same-source retention review')
    proofs={};pins={}
    for key,path,digest in (
      ('current','PG7712-observed-retention-post-v1/manifest.json','4da07632be45c13495dc4929e0b197fc9ed2e6b6b917226e41362a6204774931'),
      ('physical','PG7716-observed-retention-six-post-v1/manifest.json',None),
      ('trace','PG7718-observed-retention-trace-v1/manifest.json',None),
      ('previousTrace','PG7698-mq-pressure-connection-trace-v1/manifest.json','997c8aaa641e6f48f0fde90cd78e3ed8cffd4349547f77e5e80fe9659ea9af83'),
      ('previousBatch','PG7612-dlq-health-post-v1/manifest.json','c49dac694a6b9d1afb593d3ee328bbca38c28796183c024654ce30d44a62a780'),
      ('previousReview','PG7620-dlq-health-review-v1/manifest.json','dad87706057c2238ccf38a6a23d87936ae475927be3ac2781b55e509fce179f3'),
      ('platform','PG7413-api-generated-value-review-v2/manifest.json','7d108ca7499763b5ed5526e60144276ace055c66aa88e380a0ccde0a3be2a82e')):
        file=host.BASE/path;sha=host.sha(file);require(digest is None or sha==digest,'exact original public witness')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=path,sha256=sha)
    current=proofs['current'];physical=proofs['physical'];trace=proofs['trace'];old=proofs['previousBatch'];prior=proofs['previousReview']
    require(current['source']==physical['source']==trace['source']==compilation.SOURCE and current['tests']==245 and current['suites']==32
      and current['actualCrcMismatch']==0 and current['actualSessions']==1 and len(current['executableClasses'])==60
      and all(v['missed']==0 and v['covered']>0 for v in current['counters'].values()),'genuine current245/60/CRC0/single session/four100')
    require(len(old['sourceFiles'])==63 and all(current['sourceFiles'].get(p)==h for p,h in old['sourceFiles'].items() if p!=POLICY),
      'all62 other prior source inputs unchanged')
    changed_types={'dev/codex/schubert/nk/batch/monitoring/MonitoringModePolicy.class',
      'dev/codex/schubert/nk/batch/monitoring/MonitoringModePolicy$DetailService.class'}
    require(all(current['physicalClasses'].get(p)==h for p,h in old['physicalClasses'].items() if p not in changed_types),
      'all prior physical bytes unchanged except two declared Mode source owners')
    before=subprocess.check_output(['git','show',old['source']+':'+POLICY],cwd=host.ROOT).decode()
    after=subprocess.check_output(['git','show',compilation.SOURCE+':'+POLICY],cwd=host.ROOT).decode()
    require(hashlib.sha256(before.encode()).hexdigest()==old['sourceFiles'][POLICY]
      and hashlib.sha256(after.encode()).hexdigest()==current['sourceFiles'][POLICY],'both exact executable source versions')
    semantics=previous_semantics(before,after)
    raw=current['staticRaw']['pmd'];old_raw=old['staticRaw']['pmd'];canonical=lambda r:json.dumps(r,sort_keys=True)
    require(raw['actualExit']==4 and raw['processingErrors']==0 and len(raw['findings'])==28
      and prior['actualExit']==0 and prior['unclassified']==prior['actualViolationsOutstanding']==0 and prior['rawPmdFindings']==28,
      'all28 actual raw rows and prior individually-qualified rationale chain')
    new_other=[r for r in raw['findings'] if r['class']!='MonitoringModePolicy'];old_other=[r for r in old_raw['findings'] if r['class']!='MonitoringModePolicy']
    require(len(new_other)==25 and Counter(map(canonical,new_other))==Counter(map(canonical,old_other)),'all25 exact rows unchanged including positions')
    moved=[];fields={'detailedMetricsEnabled':'private final boolean detailedMetricsEnabled;',
      'retentionDays':'private final int retentionDays;','retentionBytes':'private final long retentionBytes;'}
    old_fields={r['variable']:r for r in old_raw['findings'] if r['class']=='MonitoringModePolicy'}
    for row in raw['findings']:
        if row['class']!='MonitoringModePolicy':continue
        variable=row['variable'];require(variable in fields and row['rule']=='AvoidFieldNameMatchingMethodName','only each declared existing property naming context')
        original=old_fields[variable];new_line=int(row['beginline']);old_line=int(original['beginline'])
        require(row['endline']==row['beginline'] and original['endline']==original['beginline']
          and after.splitlines()[new_line-1].strip()==before.splitlines()[old_line-1].strip()==fields[variable],
          'actual unchanged exact field declaration before/after, no generic line ignoring')
        without_lines=lambda r:{k:v for k,v in r.items() if k not in ('beginline','endline')}
        require(without_lines(row)==without_lines(original),'every non-line raw attribute exactly unchanged')
        moved.append(dict(raw=row,previousRaw=original,sourcePath=POLICY,sourceSha256=current['sourceFiles'][POLICY],
          reason='Existing private enum property/getter naming contract unchanged; exact whole original source restored by reverse projection, current MONMODE and RETCONF literal values prove no API/behavior change.',classification='CONTEXT_NOT_APPLICABLE'))
    require(len(moved)==3 and {r['raw']['variable'] for r in moved}==set(fields),'all three moved declarations, none unclassified')
    require(current['spotbugs']['actualExit']==0 and current['spotbugs']['findings']==0
      and current['staticRaw']['checkstyle']['actualExit']==0 and not current['staticRaw']['checkstyle']['findings'],'actual SB/CS zero')
    original_run=json.loads((execution.SLOT/'manifest.safe.json').read_bytes())
    for name,count in (('MonitoringModePolicyTest',7),('MonitoringRetentionConfigurationTest',8),('GeneratedBatchValueContractTest',7),
      ('DlqHealthMonitorTest',8),('IntegrityHealthMonitorTest',8),('RestartHealthMonitorTest',8),('BackupHealthMonitorTest',8),('AsyncQueueMonitorTest',9)):
        cases=[r for r in original_run['cases'] if r['classname'].endswith('.'+name)]
        require(len(cases)==count and all(r['result']=='PASS' for r in cases),'existing115/new5 value contracts actually run now')
    require(prior['currentBatchGeneratedTypes']==29 and prior['currentBatchGeneratedMethodsSeparatelyVerifiedNotAddedToCounters']==115,'exact previous115 provenance, not a counter')
    platform=proofs['platform'];require(host.sha(host.TC/'jdk-25.0.4/lib/modules')==platform['jdkModulesSha256']
      and host.sha(host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar')==platform['jacocoCoreSha256'],
      'same inspected JDK31fold/official record-enum filter bytes')
    classes=execution.SLOT/'snapshot/tools/quality/harnesses/target/classes';generated=[]
    for simple in ('MonitoringModePolicy','MonitoringModePolicy$DetailService','MonitoringModePolicy$RetentionConfiguration'):
        name='dev/codex/schubert/nk/batch/monitoring/'+simple;file=classes/(name+'.class')
        require(host.sha(file)==current['physicalClasses'][name+'.class'],'each changed/new actual executed class byte')
        command=[str(host.TC/'jdk-25.0.4/bin/javap'),'-p','-c','-v','-classpath',str(classes),name.replace('/','.')]
        done=subprocess.run(command,capture_output=True,text=True);text=done.stdout
        if simple.endswith('RetentionConfiguration'):
            methods=['equals(java.lang.Object)','hashCode()','toString()','days()','bytes()']
            require('java/lang/runtime/ObjectMethods.bootstrap' in text and all(m+';' in text for m in methods)
              and all(re.search(r'REF_getField\s+[^\s]+\.'+f+':'+d,text) for f,d in (('days','I'),('bytes','J'))),'all new5 methods and both exact bootstrap fields')
            testid='RETCONF008';new_type=True
        else:
            methods=['values()','valueOf(java.lang.String)'];testid='GENB004';new_type=False
            require(all(m+';' in text for m in methods) and 'java/lang/Enum.valueOf' in text
              and re.search(r'clone:\(\)Ljava/lang/Object;',text),'both changed enum factory byte contracts independently exercised by current GENB004')
        require(done.returncode==0,'javap metadata zero, no target initializer')
        generated.append(dict(className=name,sha256=host.sha(file),methods=methods,testId=testid,newType=new_type,command=command,
          actualExit=done.returncode,stdoutSha256=hashlib.sha256(text.encode()).hexdigest(),stderrSha256=hashlib.sha256(done.stderr.encode()).hexdigest()))
    previous={r['path']:r for r in proofs['previousTrace']['sourceRows']};counts=domains(trace,current,physical,previous);negative=[]
    history=next(i for i,r in enumerate(trace['physicalRows']) if r['className'].startswith('api:') and r['executable'])
    active=next(i for i,r in enumerate(trace['sourceRows']) if r['path'] in current['sourceFiles']);anchor=next(i for i,r in enumerate(trace['sourceRows']) if r['path'] in previous)
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
      rawPmdFindings=28,rawPmdExit=4,unchangedIndividualRationaleCount=25,movedModePropertyRationales=moved,newMainRawFindings=0,
      originalModeSemantics=semantics,unclassified=0,actualViolationsOutstanding=0,suppressionsAdded=0,
      newAndChangedGeneratedContracts=generated,currentBatchGeneratedTypes=30,currentBatchGeneratedMethodsSeparatelyVerifiedNotAddedToCounters=120,
      customExclusionsAdded=False,negativeGuards=negative,editAnchorCounts=counts,counters=current['counters'],ptExecutedByReview=0,
      whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,targetClassInitializedByReview=False)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rawFindings=28,unclassified=0,generatedMethods=120,negativeGuards=len(negative),anchors=counts,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
