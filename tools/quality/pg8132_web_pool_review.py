"""Same-source Web90/20, all13 raw reasons,8/27 generated contracts and metadata/provenance guards."""
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile
import pg7362_api_pool_observation_host as pool_libraries
import pg6966_chr_adapter_host as host
import pg8122_web_pool_six_compile as compilation
import pg8124_web_pool_host as execution
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG8132-web-pool-review-v1'
PREFIX='dev/codex/schubert/nk/web/monitoring/'
FAMILIES={'WebDbPoolMetricRecorder':'WEBPOOLMET001..008','WebDbPoolMetricObservation':'WEBPOOLREAD001..008','WebDbPoolMetricCollector':'WEBPOOLCONN001..008'}
MARKERS={'dev/codex/schubert/nk/api/monitoring/ExactDurationSupport.class',PREFIX+'OverflowSafeDurationSupport.class'}
def require(value,message):
    if not value:raise ValueError(message)

def domains(trace,current,physical,previous):
    require(trace['source']==current['source']==physical['source']==compilation.SOURCE,'same source')
    counts=anchors(trace['sourceRows'],previous,dict(changed=0,unchanged=141,introduced=6))
    paths={r['path']:r for r in trace['sourceRows']}
    require(len(paths)==147 and len(trace['physicalRows'])==130 and len({r['className'] for r in trace['physicalRows']})==130,'all unique141/125')
    for row in trace['sourceRows']:
        path=row['path'];require(row['currentSourceCoverageTransferred'] is False,'no transferred counters')
        if path in current['sourceFiles']:
            require(row['sha256']==current['sourceFiles'][path] and row['executionWitness']['source']==current['source']
              and row['executionWitness']['tests']==114 and row['executionWitness']['suites']==14
              and row['componentCounterScope']=='ALL_CURRENT_WEB_MONITORING_EXECUTABLES_ONLY','every current Web input exact')
        elif path.endswith('/pom.xml'):
            require(row['componentCounterScope']=='NOT_EXECUTABLE_CONFIGURATION' and row['compileWitness']['source']==current['source'],'POM not PT')
        else:require('executionWitness' not in row and row['componentCounterScope']=='HISTORICAL_ONLY_NO_CURRENT_COUNTERS','history not current execution')
        if path not in previous:require(Path(path).name in {name+suffix+'.java' for name in ('WebDbPoolMetricRecorder','WebDbPoolMetricObservation','WebDbPoolMetricCollector') for suffix in ('','Test')}
          and row['testIdFamily']==FAMILIES[Path(path).stem.removesuffix('Test')],'only declared new factory/capability/test')
    for row in trace['physicalRows']:
        role,entry=row['className'].split(':',1);proof=physical[{'web':'currentWeb','api':'historicalApi','batch':'historicalBatch'}[role]]
        executable=not entry.endswith('package-info.class') and entry not in MARKERS
        source='src/schubert-nk-'+role+'/src/main/java/'+entry.removesuffix('.class').split('$',1)[0]+'.java'
        require(row['sourcePath']==source and row['owner']==paths[source]['owner'] and row['sha256']==proof['physicalClasses'][row['className']]
          and row['executionSource']==proof['source'] and row['executable'] is executable
          and row['currentSourceExecutionAccepted'] is (role=='web' and executable)
          and row['qualificationDomain']==('CURRENT_WEB_QUALIFIED' if role=='web' else 'HISTORICAL_'+role.upper()+'_BYTE_ONLY'),'true physical/role/owner/source/metadata')
    require(sum(r['currentSourceExecutionAccepted'] for r in trace['physicalRows'])==25==len(current['executableClasses']),'only actual25')
    return counts

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only quality review')
    definitions=(
      ('current','PG8126-web-pool-post-v1/manifest.json','655e3f064bc57fc9266414fd290ac2f034ce3dbe20a0acae09d408c70bc25201'),
      ('physical','PG8128-web-pool-six-post-v1/manifest.json','ca562f955fc9140bd4ae0c52f4bec2ef5e70cbd032061ad02e861807ac6c932c'),
      ('trace','PG8130-web-pool-trace-v1/manifest.json','afde0e390c42a29d6379bd8baa4cc44d74fbc2c6f7b407361c2d3b1dd367342e'),
      ('previousTrace','PG8106-http-duration-nullable-trace-v1/manifest.json','088bce78df5206ac2903b3a84e4ab2edb6b128564bd927cd86a37a5a50930722'),
      ('old','PG8102-http-duration-nullable-post-v1/manifest.json','000581a1be960459c1e8d4ad6eccbcf9422b979fd8779a600678a76ec3dddac6'),
      ('prior','PG8108-http-duration-nullable-review-v1/manifest.json','23243334d0bf06e1421a1c671ff27bf73baee4a4a7b8f4ddd3148a6ae240a8fd'),
      ('platform','PG7413-api-generated-value-review-v2/manifest.json','7d108ca7499763b5ed5526e60144276ace055c66aa88e380a0ccde0a3be2a82e'),
      ('recoveryGuards','PG8076-http-duration-recovery-guards-v1/manifest.json','7c0139c80c80ab97661c8d830098d6ce93f2b3e948cc2d9f7cfe0f721bd729ae'))
    proofs={};pins={}
    for key,name,digest in definitions:
        file=host.BASE/name;actual=host.sha(file);require(digest is None or actual==digest,'exact public original witness')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=name,sha256=actual)
    c=proofs['current'];p=proofs['physical'];t=proofs['trace'];old=proofs['old'];prior=proofs['prior']
    require(c['actualExit']==p['actualExit']==t['actualExit']==0 and c['source']==p['source']==t['source']==compilation.SOURCE
      and c['tests']==114 and c['suites']==14 and len(c['sourceFiles'])==29 and len(c['physicalClasses'])==27
      and len(c['executableClasses'])==25 and c['actualCrcMismatch']==0 and c['actualSessions']==1
      and all(v['missed']==0 and v['covered']>0 for v in c['counters'].values()),'actual90/20/singleexec/four100')
    for key in ('spotbugs','checkstyle'):
        raw=c['staticRaw'][key];require(raw['actualExit']==0 and raw['processingErrors']==0 and not raw['findings'],'all static findings/missing0, no ignored optional dependency')
    raw=c['staticRaw']['pmd'];canonical=lambda r:json.dumps(r,sort_keys=True)
    dispositions=copy.deepcopy(prior['individualRationaleRows'])
    new=[r for r in raw['findings'] if r['class'].startswith('WebDbPool')]
    unchanged=[r for r in raw['findings'] if r not in new]
    require(raw['actualExit']==4 and raw['processingErrors']==0 and len(raw['findings'])==16 and len(new)==3
      and Counter(map(canonical,unchanged))==Counter(map(canonical,old['staticRaw']['pmd']['findings']))
      ==Counter(canonical(r.get('rawFinding',r.get('raw'))) for r in dispositions)
      and prior['actualExit']==0 and prior['unclassified']==prior['actualViolationsOutstanding']==0,'all old13 exact reasons plus3 new context rows')
    for row in dispositions:
        finding=row.get('rawFinding',row.get('raw'));path='src/schubert-nk-web/src/main/java/'+PREFIX+finding['class'].split('.')[0]+'.java'
        require(c['sourceFiles'][path]==old['sourceFiles'][path],'every old issue-bearing Main unchanged')
        row.update(source=compilation.SOURCE,sourcePath=path,sourceSha256=c['sourceFiles'][path],ordinaryTestWitness='PG8124-web-pool-host-v1',currentRationaleWitness=pins['prior'])
    seen=set()
    for row in new:
        key=(row['rule'],row['beginline'],row['begincolumn'])
        require(key in {('AvoidSynchronizedStatement','27','5'),('AvoidCatchingGenericException','34','16'),('AvoidCatchingGenericException','34','35')}
          and key not in seen and row['class']=='WebDbPoolMetricCollector' and row['method']=='collect'
          and row['package']=='dev.codex.schubert.nk.web.monitoring','every exact new context position')
        seen.add(key);path='src/schubert-nk-web/src/main/java/'+PREFIX+'WebDbPoolMetricCollector.java'
        dispositions.append(dict(raw=row,classification='CONTEXT_NOT_APPLICABLE',sourcePath=path,sourceSha256=c['sourceFiles'][path],source=compilation.SOURCE,
          reason='411 private owner lock across four borrowed getter calls and complete publication; Runtime/Error only clears unknown then rethrows same object, no normal return/retry/format/graph walk. WEBPOOLCONN003/006/007 prove provider identity, actual second contender BLOCKED and64 independent inputs. No cross-gauge atomic scrape is claimed.',
          ordinaryTestWitness='PG8124-web-pool-host-v1',suppressionAdded=False,sourceOrRulesChanged=False))
    run=json.loads((execution.SLOT/'manifest.safe.json').read_bytes())
    require(run['actualExit']==0 and len(run['cases'])==114 and len(run['suites'])==14 and all(r['result']=='PASS' for r in run['cases']),'all actual90 PASS, not wrapper begin')
    helper=execution.HELPER.read_text();selected=re.findall(r'"dev\.codex\.schubert\.nk\.web\.monitoring\.([A-Za-z0-9]+Test)"',helper)
    require(len(selected)==14 and set(selected)==set(execution.COUNTS) and host.sha(execution.HELPER)==run['begin']['helperSha256']
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
        if 'currentMetadata' in row:row['historicalCurrentMetadata']=row['currentMetadata']
        row['currentMetadata']=dict(actualExit=0,command=done.args,sha256=hashlib.sha256(done.stdout.encode()).hexdigest(),source=compilation.SOURCE,
          actualOrdinaryWitness='PG8124-web-pool-host-v1',targetInitialized=False)
        if 'javapReceipt' in row:row['historicalJavapReceipt']=row.pop('javapReceipt')
    pool_code={}
    for name in FAMILIES:
        path='src/schubert-nk-web/src/main/java/'+PREFIX+name+'.java'
        pool_code[name]=''.join((host.ROOT/path).read_text().split())
    require('.tag("service","WEB")' in pool_code['WebDbPoolMetricRecorder']
      and all(x in pool_code['WebDbPoolMetricObservation'] for x in ('pool.getActiveConnections()','pool.getIdleConnections()','pool.getThreadsAwaitingConnection()','config.getMaximumPoolSize()'))
      and 'metrics.missing();throwunavailableObservation;' in pool_code['WebDbPoolMetricCollector'],'fixed WEB labels/four getters/unknown then original propagation')
    require(not any(x in code for code in pool_code.values() for x in ('HikariDataSource','newHikariConfig(','.getConnection(','ManagementFactory','.suspendPool(','.resumePool(','.softEvictConnections(','getUsername(','getPassword(','setPassword(')),'no actual pool/DB/management/credential path in new kernels')
    pool_jar=next(Path(p) for p in pool_libraries.EXTRA if Path(p).name.startswith('HikariCP-'))
    require(c['additionalTypedPoolLibraryJarHashes']==p['currentTypedPoolLibraryJarHashes']==pool_libraries.EXTRA
      and all(host.sha(Path(path))==sha for path,sha in pool_libraries.EXTRA.items()),'all typed pool/normal library bindings, no dependency counters')
    with zipfile.ZipFile(pool_jar) as archive:
        interface_hashes={name:hashlib.sha256(archive.read(name)).hexdigest() for name in ('com/zaxxer/hikari/HikariPoolMXBean.class','com/zaxxer/hikari/HikariConfigMXBean.class')}
    require(any(r['name']=='webPoolMetric001DebugHasExactlyFourCanonicalUnknownSeries' for r in run['cases'])
      and any(r['name']=='webPoolMetric002LiteralCountsAndIndependentGaugeValuesRemainExact' for r in run['cases']),'current typed independent enum/record contracts')
    owner='src/schubert-nk-web/src/main/java/'+PREFIX+'WebDbPoolMetricRecorder.java'
    for suffix,methods,test in (('State',['values','valueOf'],'WEBPOOLMET001'),
      ('Counts',['active','idle','pending','maximum','equals','hashCode','toString'],'WEBPOOLMET002')):
        name=PREFIX+'WebDbPoolMetricRecorder$'+suffix;file=classes/(name+'.class')
        require(host.sha(file)==c['physicalClasses'][name+'.class'],'exact new executed class byte')
        done=subprocess.run([str(host.TC/'jdk-25.0.4/bin/javap'),'-p','-c','-s','-v',str(file)],capture_output=True,text=True,check=False)
        require(done.returncode==0 and all(method+'(' in done.stdout for method in methods),'all declared generated signatures')
        require(('java/lang/Enum.valueOf' in done.stdout and 'clone:' in done.stdout) if suffix=='State' else 'java/lang/runtime/ObjectMethods.bootstrap' in done.stdout,'official enum/record compiler body shape')
        generated.append(dict(className=name,sha256=host.sha(file),sourcePath=owner,sourceSha256=c['sourceFiles'][owner],
          methods=[dict(name=m) for m in methods],testIds=test,customExclusionAdded=False,directOrdinaryContractsVerified=True,
          currentMetadata=dict(actualExit=0,command=done.args,sha256=hashlib.sha256(done.stdout.encode()).hexdigest(),source=compilation.SOURCE,targetInitialized=False)))
    require(len(generated)==10 and sum(len(r['methods']) for r in generated)==36,'old8/27 plus new2/9, never counter synthesis')
    marker=PREFIX+'OverflowSafeDurationSupport.class'
    require(c['metadataClasses']==[PREFIX+'package-info.class',marker] and len(c['additionalMarkerMetadataProofs'])==1
      and c['additionalMarkerMetadataProofs'][0]['methods']==c['additionalMarkerMetadataProofs'][0]['fields']==0
      and c['additionalMarkerMetadataProofs'][0]['sha256']==c['physicalClasses'][marker],'proved empty marker retained, not executable exclusion')
    previous={r['path']:r for r in proofs['previousTrace']['sourceRows']};counts=domains(t,c,p,previous);negative=[]
    history=next(i for i,r in enumerate(t['physicalRows']) if r['className'].startswith('api:') and r['executable'])
    active=next(i for i,r in enumerate(t['sourceRows']) if r['path'] in c['sourceFiles'])
    changed=next(i for i,r in enumerate(t['sourceRows']) if r['path'] in previous)
    introduced=next(i for i,r in enumerate(t['sourceRows']) if r['sourceIntroducedSincePreviousTrace'])
    metadata=next(i for i,r in enumerate(t['physicalRows']) if r['className']=='web:'+marker)
    for kind in ('history-current','role-alias','history-source','current-witness','previous-anchor','changed-flag','metadata-executable','program-family'):
        mutant=copy.deepcopy(t)
        if kind=='history-current':mutant['physicalRows'][history]['currentSourceExecutionAccepted']=True
        elif kind=='role-alias':mutant['physicalRows'][history]['qualificationDomain']='CURRENT_WEB_QUALIFIED'
        elif kind=='history-source':mutant['physicalRows'][history]['executionSource']=c['source']
        elif kind=='current-witness':mutant['sourceRows'][active]['executionWitness']['source']=p['historicalApi']['source']
        elif kind=='previous-anchor':mutant['sourceRows'][changed]['previousSourceByteSha256']='0'*64
        elif kind=='changed-flag':mutant['sourceRows'][changed]['sourceChangedSincePreviousTrace']=True
        elif kind=='program-family':mutant['sourceRows'][introduced]['testIdFamily']='WRONG001'
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
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,witnesses=pins,tests=114,suites=14,counters=c['counters'],
      individualRationaleRows=dispositions,rawPmdFindings=16,rawPmdExit=4,newMainRawFindings=3,staticMissingClasses=0,unclassified=0,
      actualViolationsOutstanding=0,suppressionsAdded=0,generatedTypes=generated,generatedMethodCount=36,
      generatedExistingContractsCurrentOrdinaryQualified=True,metadataNegativeGuards=audit_negative,domainNegativeGuards=negative,
      typedPoolInterfaceClassSha256=interface_hashes,additionalTypedPoolLibraryJarHashes=pool_libraries.EXTRA,
      recoveryNegativeGuardsWitness=pins['recoveryGuards'],editAnchorCounts=counts,helperSha256=host.sha(execution.HELPER),
      independentOracleAnchor=dict(path=testpath,method=method,originalSource=original_source,normalizedMethodSha256=hashlib.sha256(extract(after).encode()).hexdigest()),
      actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,ptExecutedByReview=0,whole451Accepted=False,formalUpdated=False,
      newAccepted=0,effortPercent=None,coverageUnion=False,customExclusionsAdded=False)
    verify(invocation);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rawFindings=16,unclassified=0,missingClasses=0,generatedMethods=36,domainNegative=8,metadataNegative=7,manifestSha256=host.sha(OUT/'manifest.json'))))
if __name__=='__main__':main()

