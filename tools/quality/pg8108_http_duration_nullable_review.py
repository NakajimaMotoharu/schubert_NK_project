"""Same-source Web90/20, all13 raw reasons,8/27 generated contracts and metadata/provenance guards."""
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import pg6966_chr_adapter_host as host
import pg8098_http_duration_nullable_six_compile as compilation
import pg8100_http_duration_nullable_host as execution
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG8108-http-duration-nullable-review-v1'
PREFIX='dev/codex/schubert/nk/web/monitoring/'
MARKERS={'dev/codex/schubert/nk/api/monitoring/ExactDurationSupport.class',PREFIX+'OverflowSafeDurationSupport.class'}
def require(value,message):
    if not value:raise ValueError(message)

def domains(trace,current,physical,previous):
    require(trace['source']==current['source']==physical['source']==compilation.SOURCE,'same source')
    counts=anchors(trace['sourceRows'],previous,dict(changed=3,unchanged=135,introduced=3))
    paths={r['path']:r for r in trace['sourceRows']}
    require(len(paths)==141 and len(trace['physicalRows'])==125 and len({r['className'] for r in trace['physicalRows']})==125,'all unique141/125')
    for row in trace['sourceRows']:
        path=row['path'];require(row['currentSourceCoverageTransferred'] is False,'no transferred counters')
        if path in current['sourceFiles']:
            require(row['sha256']==current['sourceFiles'][path] and row['executionWitness']['source']==current['source']
              and row['executionWitness']['tests']==90 and row['executionWitness']['suites']==11
              and row['componentCounterScope']=='ALL_CURRENT_WEB_MONITORING_EXECUTABLES_ONLY','every current Web input exact')
        elif path.endswith('/pom.xml'):
            require(row['componentCounterScope']=='NOT_EXECUTABLE_CONFIGURATION' and row['compileWitness']['source']==current['source'],'POM not PT')
        else:require('executionWitness' not in row and row['componentCounterScope']=='HISTORICAL_ONLY_NO_CURRENT_COUNTERS','history not current execution')
        if path not in previous:require(Path(path).name in {'OverflowSafeHttpMeterRegistry.java','OverflowSafeDurationSupport.java','OverflowSafeHttpMeterRegistryTest.java'}
          and row['testIdFamily']=='HTTPDUR001..012','only declared new factory/capability/test')
    for row in trace['physicalRows']:
        role,entry=row['className'].split(':',1);proof=physical[{'web':'currentWeb','api':'historicalApi','batch':'historicalBatch'}[role]]
        executable=not entry.endswith('package-info.class') and entry not in MARKERS
        source='src/schubert-nk-'+role+'/src/main/java/'+entry.removesuffix('.class').split('$',1)[0]+'.java'
        require(row['sourcePath']==source and row['owner']==paths[source]['owner'] and row['sha256']==proof['physicalClasses'][row['className']]
          and row['executionSource']==proof['source'] and row['executable'] is executable
          and row['currentSourceExecutionAccepted'] is (role=='web' and executable)
          and row['qualificationDomain']==('CURRENT_WEB_QUALIFIED' if role=='web' else 'HISTORICAL_'+role.upper()+'_BYTE_ONLY'),'true physical/role/owner/source/metadata')
    require(sum(r['currentSourceExecutionAccepted'] for r in trace['physicalRows'])==20==len(current['executableClasses']),'only actual20')
    return counts

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only quality review')
    definitions=(
      ('current','PG8102-http-duration-nullable-post-v1/manifest.json','000581a1be960459c1e8d4ad6eccbcf9422b979fd8779a600678a76ec3dddac6'),
      ('physical','PG8104-http-duration-nullable-six-post-v1/manifest.json',None),
      ('trace','PG8106-http-duration-nullable-trace-v1/manifest.json',None),
      ('previousTrace','PG8042-exact-duration-trace-v5/manifest.json','232778568815d10f7fa3a952ab8e3210ab857a188858896f562fd51799a33a2e'),
      ('old','PG7946-web-outbox-post-v1/manifest.json','7bfe1a10cdbaf81a9b39bb3c8a70774bf37d712c11f6e7f02b017a55bd97a5f0'),
      ('prior','PG7952-web-outbox-review-v1/manifest.json','39b04f011a1d850c7cf9640cfad5270d26d3d4ffd20f1f3a06293a181d38d56f'),
      ('platform','PG7413-api-generated-value-review-v2/manifest.json','7d108ca7499763b5ed5526e60144276ace055c66aa88e380a0ccde0a3be2a82e'),
      ('recoveryGuards','PG8076-http-duration-recovery-guards-v1/manifest.json','7c0139c80c80ab97661c8d830098d6ce93f2b3e948cc2d9f7cfe0f721bd729ae'))
    proofs={};pins={}
    for key,name,digest in definitions:
        file=host.BASE/name;actual=host.sha(file);require(digest is None or actual==digest,'exact public original witness')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=name,sha256=actual)
    c=proofs['current'];p=proofs['physical'];t=proofs['trace'];old=proofs['old'];prior=proofs['prior']
    require(c['actualExit']==p['actualExit']==t['actualExit']==0 and c['source']==p['source']==t['source']==compilation.SOURCE
      and c['tests']==90 and c['suites']==11 and len(c['sourceFiles'])==23 and len(c['physicalClasses'])==22
      and len(c['executableClasses'])==20 and c['actualCrcMismatch']==0 and c['actualSessions']==1
      and all(v['missed']==0 and v['covered']>0 for v in c['counters'].values()),'actual90/20/singleexec/four100')
    for key in ('spotbugs','checkstyle'):
        raw=c['staticRaw'][key];require(raw['actualExit']==0 and raw['processingErrors']==0 and not raw['findings'],'all static findings/missing0, no ignored optional dependency')
    raw=c['staticRaw']['pmd'];canonical=lambda r:json.dumps(r,sort_keys=True)
    dispositions=copy.deepcopy(prior['individualRationaleRows'])
    require(raw['actualExit']==4 and raw['processingErrors']==0 and len(raw['findings'])==13
      and Counter(map(canonical,raw['findings']))==Counter(map(canonical,old['staticRaw']['pmd']['findings']))
      ==Counter(canonical(r.get('rawFinding',r.get('raw'))) for r in dispositions)
      and prior['actualExit']==0 and prior['unclassified']==prior['actualViolationsOutstanding']==0,'all13 exact raw/individual reasons, no new issue')
    for row in dispositions:
        finding=row.get('rawFinding',row.get('raw'));path='src/schubert-nk-web/src/main/java/'+PREFIX+finding['class'].split('.')[0]+'.java'
        require(c['sourceFiles'][path]==old['sourceFiles'][path],'every old issue-bearing Main unchanged')
        row.update(source=compilation.SOURCE,sourcePath=path,sourceSha256=c['sourceFiles'][path],ordinaryTestWitness='PG8100-http-duration-nullable-host-v1',currentRationaleWitness=pins['prior'])
    run=json.loads((execution.SLOT/'manifest.safe.json').read_bytes())
    require(run['actualExit']==0 and len(run['cases'])==90 and len(run['suites'])==11 and all(r['result']=='PASS' for r in run['cases']),'all actual90 PASS, not wrapper begin')
    helper=execution.HELPER.read_text();selected=re.findall(r'"dev\.codex\.schubert\.nk\.web\.monitoring\.([A-Za-z0-9]+Test)"',helper)
    require(len(selected)==11 and set(selected)==set(execution.COUNTS) and host.sha(execution.HELPER)==run['begin']['helperSha256']
      and not any(x in helper for x in ('getMessage(','getCause(','getSuppressed(','Class.forName(')),'exact safe helper only, bounded frames/no provider formatting')
    testpath='src/schubert-nk-web/src/test/java/'+PREFIX+'HttpMetricRecorderTest.java'
    method='httpRec010ExtremeRangeOrdersNeverWrapCumulativeTimerOrLoseSmallBuckets'
    original_source='7e57c7ace25f19a20012019768daca1844861b85'
    before=subprocess.check_output(['git','show',original_source+':'+testpath],cwd=host.ROOT,text=True)
    after=(host.ROOT/testpath).read_text()
    extract=lambda s:''.join(s[s.index('  void '+method+'('):].split())
    require(extract(before)==extract(after) and any(r['name']==method for r in run['cases']),'original failed010 oracle body unchanged and actual current PASS')
    mainpath='src/schubert-nk-web/src/main/java/'+PREFIX+'OverflowSafeHttpMeterRegistry.java'
    code=''.join((host.ROOT/mainpath).read_text().split())
    require('implementsTimer' in code and 'extendsAbstractTimer' not in code and 'NoPauseDetector' in code
      and 'Textends@NullableObject' in code and 'newHistogramSnapshot(snapshot.count(),totalTime(TimeUnit.NANOSECONDS)' in code
      and 'DoubleAdder' in code and 'catch(' not in code,'public composition/null result contract, safe public total/snapshot and no catch')
    platform=proofs['platform'];require(host.sha(host.TC/'jdk-25.0.4/lib/modules')==platform['jdkModulesSha256']
      and host.sha(host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar')==platform['jacocoCoreSha256'],'same official compiler/filter bytes')
    generated=copy.deepcopy(prior['generatedTypes']);require(len(generated)==8 and sum(len(r['methods']) for r in generated)==prior['generatedMethodCount']==27,'complete8/27 generated contract inventory')
    classes=execution.COMPILE/'snapshot/src/schubert-nk-web/target/classes'
    for row in generated:
        name=row['className']+'.class';file=classes/name
        require(c['physicalClasses'][name]==row['sha256']==host.sha(file)
          and c['sourceFiles'][row['sourcePath']]==row['sourceSha256'],'all generated owner/physical bytes unchanged, not old execution transfer')
        done=subprocess.run([str(host.TC/'jdk-25.0.4/bin/javap'),'-p','-c','-s',str(file)],capture_output=True,text=True,check=False)
        require(done.returncode==0,'noninitializing current generated metadata')
        row['currentMetadata']=dict(actualExit=0,command=done.args,sha256=hashlib.sha256(done.stdout.encode()).hexdigest(),source=compilation.SOURCE,
          actualOrdinaryWitness='PG8100-http-duration-nullable-host-v1',targetInitialized=False)
        if 'javapReceipt' in row:row['historicalJavapReceipt']=row.pop('javapReceipt')
    marker=PREFIX+'OverflowSafeDurationSupport.class'
    require(c['metadataClasses']==[PREFIX+'package-info.class',marker] and len(c['additionalMarkerMetadataProofs'])==1
      and c['additionalMarkerMetadataProofs'][0]['methods']==c['additionalMarkerMetadataProofs'][0]['fields']==0
      and c['additionalMarkerMetadataProofs'][0]['sha256']==c['physicalClasses'][marker],'proved empty marker retained, not executable exclusion')
    previous={r['path']:r for r in proofs['previousTrace']['sourceRows']};counts=domains(t,c,p,previous);negative=[]
    history=next(i for i,r in enumerate(t['physicalRows']) if r['className'].startswith('api:') and r['executable'])
    active=next(i for i,r in enumerate(t['sourceRows']) if r['path'] in c['sourceFiles'])
    changed=next(i for i,r in enumerate(t['sourceRows']) if r['sourceChangedSincePreviousTrace'])
    metadata=next(i for i,r in enumerate(t['physicalRows']) if r['className']=='web:'+marker)
    for kind in ('history-current','role-alias','history-source','current-witness','previous-anchor','changed-flag','metadata-executable'):
        mutant=copy.deepcopy(t)
        if kind=='history-current':mutant['physicalRows'][history]['currentSourceExecutionAccepted']=True
        elif kind=='role-alias':mutant['physicalRows'][history]['qualificationDomain']='CURRENT_WEB_QUALIFIED'
        elif kind=='history-source':mutant['physicalRows'][history]['executionSource']=c['source']
        elif kind=='current-witness':mutant['sourceRows'][active]['executionWitness']['source']=p['historicalApi']['source']
        elif kind=='previous-anchor':mutant['sourceRows'][changed]['previousSourceByteSha256']='0'*64
        elif kind=='changed-flag':mutant['sourceRows'][changed]['sourceChangedSincePreviousTrace']=False
        else:mutant['physicalRows'][metadata]['executable']=True
        try:domains(mutant,c,p,previous)
        except ValueError:negative.append(dict(kind=kind,rejected=True))
        else:raise ValueError('invalid provenance accepted')
    command=c['auditStages'][1]['command'];metadata_arg='--metadata='+marker.removesuffix('.class');main=PREFIX+'OverflowSafeHttpMeterRegistry';audit_negative=[]
    for kind in ('omit-marker','duplicate-marker','executable-alias','executable-metadata','unknown-marker','missing-marker','missing-executable'):
        altered=list(command)
        if kind=='omit-marker':altered.remove(metadata_arg)
        elif kind=='duplicate-marker':altered.append(metadata_arg)
        elif kind=='executable-alias':altered.append('--metadata='+main)
        elif kind=='executable-metadata':altered.remove(main);altered.append('--metadata='+main)
        elif kind=='unknown-marker':altered[altered.index(metadata_arg)]='--metadata='+PREFIX+'UnknownMarker'
        elif kind=='missing-marker':altered.append('--metadata='+PREFIX+'MissingMarker')
        else:altered.remove(main)
        done=subprocess.run(altered,capture_output=True,text=True,check=False);require(done.returncode!=0,'all metadata/executable false claims rejected')
        audit_negative.append(dict(kind=kind,actualExit=done.returncode,rejected=True,command=altered,stdoutSha256=hashlib.sha256(done.stdout.encode()).hexdigest(),
          stderrSha256=hashlib.sha256(done.stderr.encode()).hexdigest(),targetInitialized=False,productPtExecuted=0))
    require(proofs['recoveryGuards']['actualExit']==0 and len(proofs['recoveryGuards']['negativeGuards'])==7,'original wrapper recovery guards preserved, not reexecuted as product PT')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,witnesses=pins,tests=90,suites=11,counters=c['counters'],
      individualRationaleRows=dispositions,rawPmdFindings=13,rawPmdExit=4,newMainRawFindings=0,staticMissingClasses=0,unclassified=0,
      actualViolationsOutstanding=0,suppressionsAdded=0,generatedTypes=generated,generatedMethodCount=27,
      generatedExistingContractsCurrentOrdinaryQualified=True,metadataNegativeGuards=audit_negative,domainNegativeGuards=negative,
      recoveryNegativeGuardsWitness=pins['recoveryGuards'],editAnchorCounts=counts,helperSha256=host.sha(execution.HELPER),
      independentOracleAnchor=dict(path=testpath,method=method,originalSource=original_source,normalizedMethodSha256=hashlib.sha256(extract(after).encode()).hexdigest()),
      actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,ptExecutedByReview=0,whole451Accepted=False,formalUpdated=False,
      newAccepted=0,effortPercent=None,coverageUnion=False,customExclusionsAdded=False)
    verify(invocation);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rawFindings=13,unclassified=0,missingClasses=0,generatedMethods=27,domainNegative=7,metadataNegative=7,manifestSha256=host.sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
