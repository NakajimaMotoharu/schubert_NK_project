"""All current36,19 individually classified raw rows,54 generated contracts and provenance/metadata guards."""
from collections import Counter
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import pg6966_chr_adapter_host as host
import pg8026_exact_duration_six_compile_v4 as compilation
import pg8022_exact_duration_host_v4 as execution
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG8044-exact-duration-review-v5'
PREFIX='dev/codex/schubert/nk/api/monitoring/'
def require(value,message):
    if not value:raise ValueError(message)

def domains(trace,current,physical,previous):
    require(trace['source']==current['source']==physical['source']==compilation.SOURCE,'same source')
    counts=anchors(trace['sourceRows'],previous,dict(changed=5,unchanged=130,introduced=3))
    paths={r['path']:r for r in trace['sourceRows']}
    require(len(paths)==138 and len(trace['physicalRows'])==122 and len({r['className'] for r in trace['physicalRows']})==122,'all unique138/122')
    for row in trace['sourceRows']:
        path=row['path'];require(row['currentSourceCoverageTransferred'] is False,'no transferred counters')
        if path in current['sourceFiles']:
            require(row['sha256']==current['sourceFiles'][path] and row['executionWitness']['source']==current['source']
              and row['executionWitness']['tests']==174 and row['executionWitness']['suites']==21
              and row['componentCounterScope']=='ALL_CURRENT_API_EXECUTABLES_ONLY','all exact current inputs')
        elif path.endswith('/pom.xml'):
            require(row['componentCounterScope']=='NOT_EXECUTABLE_CONFIGURATION' and row['compileWitness']['source']==current['source'],'POM is not PT')
        else:require('executionWitness' not in row and row['componentCounterScope']=='HISTORICAL_ONLY_NO_CURRENT_COUNTERS','history not execution')
        if path not in previous:require(Path(path).name in {'ExactDurationMeterRegistry.java','ExactDurationMeterRegistryTest.java','ExactDurationSupport.java'}
          and row['testIdFamily']=='EXDUR001..010','only exact factory capability new family')
    for row in trace['physicalRows']:
        role,entry=row['className'].split(':',1)
        proof=physical[{'api':'currentApi','web':'historicalWeb','batch':'historicalBatch'}[role]]
        executable=not entry.endswith('package-info.class') and entry!=PREFIX+'ExactDurationSupport.class'
        source='src/schubert-nk-'+role+'/src/main/java/'+entry.removesuffix('.class').split('$',1)[0]+'.java'
        require(row['sourcePath']==source and row['owner']==paths[source]['owner'] and row['sha256']==proof['physicalClasses'][row['className']]
          and row['executionSource']==proof['source'] and row['executable'] is executable
          and row['currentSourceExecutionAccepted'] is (role=='api' and executable)
          and row['qualificationDomain']==('CURRENT_API_QUALIFIED' if role=='api' else 'HISTORICAL_'+role.upper()+'_BYTE_ONLY'),'all role/byte/metadata provenance')
    require(sum(r['currentSourceExecutionAccepted'] for r in trace['physicalRows'])==36==len(current['executableClasses']),'only actual36')
    return counts

def method_text(source,name):
    begin=source.index('  void '+name+'(')
    end=source.find('\n  @Test',begin)
    return ''.join(source[begin:end if end>=0 else len(source)].split())

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only bounded quality review')
    definitions=(
      ('current','PG8038-exact-duration-post-v5/manifest.json','f4c41071587cdc360f06beb97bcbc71b9dad254109c59c431201fd0e214812ea'),
      ('physical','PG8040-exact-duration-six-post-v5/manifest.json','42148108d6ea638087ca0ab150099e6b120956e63dc424bb6a85995397f25167'),
      ('trace','PG8042-exact-duration-trace-v5/manifest.json','232778568815d10f7fa3a952ab8e3210ab857a188858896f562fd51799a33a2e'),
      ('previousTrace','PG7950-web-outbox-trace-v1/manifest.json','f27a24b8e1c2d9f72519f64f85f97a8baf80ffae4c0824fffd71d964a3043800'),
      ('old','PG7914-mq-event-post-v1/manifest.json','ef08d9bb31f1878aa6b416764026f7b4b8eec9a7d43393798ec2e54e8eb4e803'),
      ('prior','PG7922-mq-event-review-v1/manifest.json','0939fdcd38a2fc63ad0b71ea2369391f4d4e73d1ffe4441c7509395b528649a2'),
      ('platform','PG7413-api-generated-value-review-v2/manifest.json','7d108ca7499763b5ed5526e60144276ace055c66aa88e380a0ccde0a3be2a82e'))
    proofs={};pins={}
    for key,name,digest in definitions:
        file=host.BASE/name;require(host.sha(file)==digest,'exact public witness')
        proofs[key]=json.loads(file.read_bytes());pins[key]=dict(path=name,sha256=digest)
    c=proofs['current'];p=proofs['physical'];t=proofs['trace'];old=proofs['old'];prior=proofs['prior']
    require(c['actualExit']==p['actualExit']==t['actualExit']==0 and c['source']==p['source']==t['source']==compilation.SOURCE
      and c['tests']==174 and c['suites']==21 and len(c['sourceFiles'])==43 and len(c['executableClasses'])==36
      and len(c['physicalClasses'])==38 and c['actualCrcMismatch']==0 and c['actualSessions']==1
      and all(v['missed']==0 and v['covered']>0 for v in c['counters'].values()),'actual174/singleexec/four100')
    raw=c['staticRaw']['pmd'];canonical=lambda r:json.dumps(r,sort_keys=True)
    new=[r for r in raw['findings'] if r['class'].startswith('ExactDurationMeterRegistry')]
    unchanged=[r for r in raw['findings'] if r not in new]
    require(raw['actualExit']==4 and raw['processingErrors']==0 and len(raw['findings'])==19 and len(new)==2
      and Counter(map(canonical,unchanged))==Counter(map(canonical,old['staticRaw']['pmd']['findings']))
      and prior['actualExit']==0 and prior['unclassified']==prior['actualViolationsOutstanding']==0 and len(prior['staticDispositions'])==17,'all old17 exact plus two context rows')
    dispositions=copy.deepcopy(prior['staticDispositions'])
    for row in dispositions:
        path=row['sourcePath'];require(c['sourceFiles'][path]==old['sourceFiles'][path],'every old issue-bearing Main unchanged')
        row.update(source=compilation.SOURCE,ordinaryTestWitness='PG8022-exact-duration-host-v4',currentRationaleWitness=pins['prior'])
    seen=set()
    for row in new:
        key=(row['method'],row['beginline'],row['begincolumn'])
        require(key in {('record','83','7'),('takeSnapshot','108','7')} and key not in seen
          and row['class']=='ExactDurationMeterRegistry.ExactSummary' and row['rule']=='AvoidSynchronizedStatement'
          and row['package']=='dev.codex.schubert.nk.api.monitoring','each exact raw position')
        seen.add(key);path='src/schubert-nk-api/src/main/java/'+PREFIX+'ExactDurationMeterRegistry.java'
        dispositions.append(dict(raw=row,classification='CONTEXT_NOT_APPLICABLE',sourcePath=path,sourceSha256=c['sourceFiles'][path],source=compilation.SOURCE,
          reason='411 private stateLock, constant five finite buckets; no callback, I/O or clock under lock. One atomic count/double sum/max/CDF tuple. EXDUR001..004/009 verify literal boundaries, extremes, defensive snapshots and four workers/consistent concurrent snapshots. Monitor preserves invariant; general ReentrantLock preference adds no required cancellation or timed-lock behavior here.',
          ordinaryTestWitness='PG8022-exact-duration-host-v4',suppressionAdded=False,sourceOrRulesChanged=False))
    require(c['spotbugs']['actualExit']==0 and c['spotbugs']['findings']==0 and c['staticRaw']['checkstyle']['actualExit']==0
      and not c['staticRaw']['checkstyle']['findings'],'actual SB/CS0')
    run=json.loads((execution.SLOT/'manifest.safe.json').read_bytes())
    require(run['actualExit']==0 and len(run['cases'])==174 and all(r['result']=='PASS' for r in run['cases']),'all174 actual PASS')
    old_source='23b74be401690ecb0f0007a66869c4ea2a699b02'
    oracle=[]
    for file,method,source in (
      ('DbQueryDurationMetricRecorderTest','dbTime003QueryAndOutcomeClosedParsersAndGeneratedFactoriesUseIndependentTypedConstants',old_source),
      ('MqProcessingDurationMetricRecorderTest','mqTime003ClosedOutcomeFactoriesAndUnknownLayoutCannotRegisterArbitraryNamespace',old_source),
      ('DbQueryDurationMetricRecorderTest','dbTime009ExtremeRangeOrdersKeepIndependentSmallBucketCountsAndFiniteTotals','0b78d18f241ca0f8c0f7bc48e8b9b80deb163544'),
      ('MqProcessingDurationMetricRecorderTest','mqTime009ExtremeRangeOrdersKeepIndependentSmallBucketCountsAndFiniteTotals','0b78d18f241ca0f8c0f7bc48e8b9b80deb163544')):
        path='src/schubert-nk-api/src/test/java/'+PREFIX+file+'.java'
        before=subprocess.check_output(['git','show',source+':'+path],cwd=host.ROOT,text=True)
        after=(host.ROOT/path).read_text();a=method_text(before,method);b=method_text(after,method)
        require(a==b and any(r['name']==method and r['result']=='PASS' for r in run['cases']),'independent old oracle unchanged and genuinely executed now')
        oracle.append(dict(path=path,method=method,originalSource=source,normalizedMethodSha256=hashlib.sha256(a.encode()).hexdigest(),currentOrdinaryPass=True))
    platform=proofs['platform']
    require(host.sha(host.TC/'jdk-25.0.4/lib/modules')==platform['jdkModulesSha256']
      and host.sha(host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar')==platform['jacocoCoreSha256'],'same official platform/filter bytes')
    generated=[];classes=execution.SLOT/'snapshot/tools/quality/harnesses/target/classes'
    for name,digest in c['physicalClasses'].items():
        if '$' not in name:continue
        done=subprocess.run([str(host.TC/'jdk-25.0.4/bin/javap'),'-p','-c','-s',str(classes/name)],capture_output=True,text=True,check=False)
        require(done.returncode==0,'noninitializing generated metadata read')
        if not re.search(r'extends java\.lang\.(Record|Enum)',done.stdout):continue
        require(old['physicalClasses'].get(name)==digest==host.sha(classes/name),'all unchanged generated type bytes, not old execution transfer')
        generated.append(dict(className=name,sha256=digest,metadataSha256=hashlib.sha256(done.stdout.encode()).hexdigest(),actualExit=0))
    require(len(generated)==prior['currentApiGeneratedTypes']==14
      and prior['currentApiGeneratedMethodsSeparatelyVerifiedNotAddedToCounters']==54,'all14/54 prior contract inventory with current byte and ordinary qualification')
    require(c['metadataClasses']==[PREFIX+'package-info.class',PREFIX+'ExactDurationSupport.class']
      and len(c['additionalMarkerMetadataProofs'])==1 and c['additionalMarkerMetadataProofs'][0]['methods']==0
      and c['additionalMarkerMetadataProofs'][0]['fields']==0 and c['additionalMarkerMetadataProofs'][0]['initializationMethods']==0,'retained empty marker metadata')
    previous={r['path']:r for r in proofs['previousTrace']['sourceRows']};counts=domains(t,c,p,previous);negative=[]
    history=next(i for i,r in enumerate(t['physicalRows']) if r['className'].startswith('batch:') and r['executable'])
    active=next(i for i,r in enumerate(t['sourceRows']) if r['path'] in c['sourceFiles'])
    changed=next(i for i,r in enumerate(t['sourceRows']) if r['sourceChangedSincePreviousTrace'])
    marker=next(i for i,r in enumerate(t['physicalRows']) if r['className']=='api:'+PREFIX+'ExactDurationSupport.class')
    for kind in ('history-current','role-alias','history-source','current-witness','previous-anchor','changed-flag','marker-executable'):
        mutant=copy.deepcopy(t)
        if kind=='history-current':mutant['physicalRows'][history]['currentSourceExecutionAccepted']=True
        elif kind=='role-alias':mutant['physicalRows'][history]['qualificationDomain']='CURRENT_API_QUALIFIED'
        elif kind=='history-source':mutant['physicalRows'][history]['executionSource']=c['source']
        elif kind=='current-witness':mutant['sourceRows'][active]['executionWitness']['source']=p['historicalBatch']['source']
        elif kind=='previous-anchor':mutant['sourceRows'][changed]['previousSourceByteSha256']='0'*64
        elif kind=='changed-flag':mutant['sourceRows'][changed]['sourceChangedSincePreviousTrace']=False
        else:mutant['physicalRows'][marker]['executable']=True
        try:domains(mutant,c,p,previous)
        except ValueError:negative.append(dict(kind=kind,rejected=True))
        else:raise ValueError('invalid provenance accepted')
    command=c['auditStages'][1]['command'];metadata_arg='--metadata='+PREFIX+'ExactDurationSupport'
    main=PREFIX+'ExactDurationMeterRegistry';audit_negative=[]
    for kind in ('omit-marker','duplicate-marker','executable-alias','executable-metadata','unknown-marker','missing-marker','missing-executable'):
        altered=list(command)
        if kind=='omit-marker':altered.remove(metadata_arg)
        elif kind=='duplicate-marker':altered.append(metadata_arg)
        elif kind=='executable-alias':altered.append('--metadata='+main)
        elif kind=='executable-metadata':altered.remove(main);altered.append('--metadata='+main)
        elif kind=='unknown-marker':altered[altered.index(metadata_arg)]='--metadata='+PREFIX+'UnknownMarker'
        elif kind=='missing-marker':altered.append('--metadata='+PREFIX+'MissingMarker')
        else:altered.remove(main)
        done=subprocess.run(altered,capture_output=True,text=True,check=False)
        require(done.returncode!=0,'metadata/executable mismatch rejected')
        audit_negative.append(dict(kind=kind,actualExit=done.returncode,rejected=True,command=altered,
          stdoutSha256=hashlib.sha256(done.stdout.encode()).hexdigest(),stderrSha256=hashlib.sha256(done.stderr.encode()).hexdigest(),targetInitialized=False,productPtExecuted=0))
    grammar=subprocess.run(['python3','-B',str(host.ROOT/'tools/quality/marker_metadata_contract_test.py')],cwd=host.ROOT,
      env={**os.environ,'PYTHONPATH':str(host.ROOT/'tools/quality')},capture_output=True,text=True,check=False)
    require(grammar.returncode==0 and 'Ran 6 tests' in grammar.stderr,'six metadata grammar contracts')
    value=dict(actualExit=0,source=c['source'],invocation=invocation,witnesses=pins,counters=c['counters'],staticDispositions=dispositions,
      rawPmdFindings=19,rawPmdExit=4,newStaticContextRows=2,unclassified=0,actualViolationsOutstanding=0,suppressionsAdded=0,
      currentApiGeneratedTypes=14,currentApiGeneratedMethodsSeparatelyVerifiedNotAddedToCounters=54,generatedCurrentByteAndMetadata=generated,
      generatedExistingTestContractsCurrentSourceQualified=True,independentOracleAnchors=oracle,additionalMarkerMetadataProofs=c['additionalMarkerMetadataProofs'],
      metadataGrammarTests=dict(tests=6,actualExit=0),metadataAuditNegativeGuards=audit_negative,negativeGuards=negative,editAnchorCounts=counts,
      sourceBugs=['BUG-1678','BUG-1679'],toolBug='BUG-1680',whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,
      customExclusionsAdded=False,coverageUnion=False,ptExecutedByReview=0,targetClassInitializedByReview=False,actualVmActions=0,actualDatabaseActions=0)
    verify(invocation);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rawFindings=19,unclassified=0,generatedMethods=54,domainNegative=7,metadataNegative=7,manifestSha256=host.sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
