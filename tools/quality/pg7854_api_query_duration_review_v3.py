"""API138/28 same-source quality, existing16 individual reasons and generated41+4; no synthetic counters."""
from collections import Counter
import copy
import json
import os
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
import pg7858_api_query_duration_host_v3 as execution
import pg7862_api_query_duration_six_compile_v3 as compilation
import pg7032_monitoring_six_artifact_post as steps
from monitoring_api_domains import validate_domains
from host_tool_invocation import capture,verify
OUT=host.BASE/'PG7854-api-query-duration-review-v3'
PREFIX='dev/codex/schubert/nk/api/monitoring/'
def require(value,message):
    if not value:raise ValueError(message)
def domains(trace,current,physical,previous):
    return validate_domains(trace,current,physical,previous,previous_count=121,physical_count=108,test_count=138,current_executable=28)
def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only exact quality review')
    proofs={};pins={}
    for key,path,digest in (
      ('current','PG7864-api-query-duration-post-v4/manifest.json',None),
      ('physical','PG7850-api-query-duration-six-post-v2/manifest.json',None),
      ('trace','PG7852-api-query-duration-trace-v3/manifest.json',None),
      ('previousTrace','PG7822-restart-metric-trace-v1/manifest.json','03388f0c8341d76447cab3854085e16a783f2f5ca32f302916fdc2b3c303b318'),
      ('previousApi','PG7692-mq-pressure-connection-post-v1/manifest.json','c4a2b73e25ac971068a4c4a644fb343623dbb2c191880be4b3ccab74a2ccfb07'),
      ('previousReview','PG7700-mq-pressure-connection-review-v1/manifest.json','ebe1eb1a4cb4377a956a499e85b7ed5970986102f919b649a9fcab21aef521a4'),
      ('platform','PG7413-api-generated-value-review-v2/manifest.json','7d108ca7499763b5ed5526e60144276ace055c66aa88e380a0ccde0a3be2a82e'),
      ('firstFailed','PG7830-api-query-duration-host-v1/manifest.json',None),
      ('secondFailed','PG7844-api-query-duration-host-v2/manifest.json',None)):
        f=host.BASE/path;sha=host.sha(f);require(digest is None or sha==digest,'exact original witness')
        proofs[key]=json.loads(f.read_bytes());pins[key]=dict(path=path,sha256=sha)
    c=proofs['current'];p=proofs['physical'];t=proofs['trace'];old=proofs['previousApi'];prior=proofs['previousReview']
    require(c['actualExit']==p['actualExit']==t['actualExit']==0 and c['source']==p['source']==t['source']==compilation.SOURCE
      and c['tests']==138 and c['suites']==17 and len(c['sourceFiles'])==34 and len(c['executableClasses'])==28
      and len(c['physicalClasses'])==29 and c['actualCrcMismatch']==0 and c['actualSessions']==1
      and all(v['missed']==0 and v['covered']>0 for v in c['counters'].values()),'actual138/28 same-source/singleexec/four100')
    require(all(c['sourceFiles'].get(k)==v for k,v in old['sourceFiles'].items())
      and all(c['physicalClasses'].get(k)==v for k,v in old['physicalClasses'].items()),'all old32 Java/26 physical unchanged including debug')
    canonical=lambda r:json.dumps(r,sort_keys=True);raw=c['staticRaw']['pmd']
    require(raw['actualExit']==4 and raw['processingErrors']==0 and len(raw['findings'])==16
      and Counter(map(canonical,raw['findings']))==Counter(map(canonical,old['staticRaw']['pmd']['findings']))
      and prior['actualExit']==0 and prior['unclassified']==prior['actualViolationsOutstanding']==0
      and len(prior['staticDispositions'])==16,'all16 exact individual reason rows and no new issue')
    dispositions=copy.deepcopy(prior['staticDispositions'])
    for row in dispositions:
        source=row['sourcePath'];require(source in c['sourceFiles'] and c['sourceFiles'][source]==old['sourceFiles'][source],'every issue-bearing source unchanged')
        row.update(source=compilation.SOURCE,ordinaryTestWitness='PG7858-api-query-duration-host-v3',currentRationaleWitness=pins['previousReview'])
    require(c['spotbugs']['actualExit']==0 and c['spotbugs']['findings']==0
      and c['staticRaw']['checkstyle']['actualExit']==0 and not c['staticRaw']['checkstyle']['findings'],'actual SB/CS0')
    run=json.loads((execution.SLOT/'manifest.safe.json').read_bytes())
    require(run['actualExit']==0 and len(run['cases'])==138 and all(r['result']=='PASS' for r in run['cases']),'all current ordinary cases PASS')
    require(len([r for r in run['cases'] if r['classname'].endswith('.DbQueryDurationMetricRecorderTest')])==8
      and any(r['name']=='dbTime003QueryAndOutcomeClosedParsersAndGeneratedFactoriesUseIndependentTypedConstants' for r in run['cases']),
      'eight new cases include independent enum generated factories')
    require(prior['currentApiGeneratedTypes']==9 and prior['currentApiGeneratedMethodsSeparatelyVerifiedNotAddedToCounters']==41,'old41 separate generated contracts')
    platform=proofs['platform'];require(host.sha(host.TC/'jdk-25.0.4/lib/modules')==platform['jdkModulesSha256']
      and host.sha(host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar')==platform['jacocoCoreSha256'],'same official filters/platform')
    work=host.W/'pg7854-api-query-duration-review-v3';require(not work.exists(),'new-only metadata work');work.mkdir();steps.SLOT=work
    classes=execution.SLOT/'snapshot/tools/quality/harnesses/target/classes';generated=[]
    for suffix in ('Query','Outcome'):
        name=PREFIX+'DbQueryDurationMetricRecorder$'+suffix;f=classes/(name+'.class')
        require(host.sha(f)==c['physicalClasses'][name+'.class'],'exact current executed enum byte')
        receipt,stdout=steps.step('javap-'+suffix,[str(host.TC/'jdk-25.0.4/bin/javap'),'-p','-c','-s',str(f)])
        require(receipt['actualExit']==0 and 'values();' in stdout and 'valueOf(java.lang.String);' in stdout
          and 'clone:' in stdout and 'java/lang/Enum.valueOf:' in stdout,'two generated enum methods direct typed current ordinary plus noninitializing bytecode')
        generated.append(dict(className=name,sha256=host.sha(f),methods=['values','valueOf'],ordinaryTest='DBTIME003',receipt=receipt))
    main_path='src/schubert-nk-api/src/main/java/'+PREFIX+'DbQueryDurationMetricRecorder.java'
    test_path='src/schubert-nk-api/src/test/java/'+PREFIX+'DbQueryDurationMetricRecorderTest.java'
    current_main=(host.ROOT/main_path).read_bytes()
    require(current_main==subprocess.check_output(['git','show','9e579a97a:'+main_path],cwd=host.ROOT),'final fixture-only correction preserves Main byte')
    prior_test=subprocess.check_output(['git','show','9e579a97a:'+test_path],cwd=host.ROOT)
    require((host.ROOT/test_path).read_bytes()==prior_test.replace(b'"0.1", "1.0", "1.5"',b'"0.1", "1", "1.5"')
      and b'.publishPercentiles(.95)' in current_main and b'.publishPercentileHistogram()' in current_main,'one SDK auxiliary literal correction, independent CDF unchanged')
    failures=[]
    for key in ('firstFailed','secondFailed'):
        f=proofs[key];require(f['actualExit']==1 and len(f['cases'])==138
          and f['suites']['dev.codex.schubert.nk.api.monitoring.DbQueryDurationMetricRecorderTest']['failures']==6,'both original failed runs retained, no reused pass')
        failures.append(dict(witness=pins[key],source=f['source'],actualExit=1,failed=6,successTransferred=False))
    previous={r['path']:r for r in proofs['previousTrace']['sourceRows']};counts=domains(t,c,p,previous);negative=[]
    history=next(i for i,r in enumerate(t['physicalRows']) if r['className'].startswith('batch:') and r['executable'])
    active=next(i for i,r in enumerate(t['sourceRows']) if r['path'] in c['sourceFiles'])
    anchor=next(i for i,r in enumerate(t['sourceRows']) if r['path'] in previous)
    for kind in ('historical-current-flag','role-alias','historical-source','current-witness','previous-anchor'):
        mutant=copy.deepcopy(t)
        if kind=='historical-current-flag':mutant['physicalRows'][history]['currentSourceExecutionAccepted']=True
        elif kind=='role-alias':mutant['physicalRows'][history]['qualificationDomain']='CURRENT_API_QUALIFIED'
        elif kind=='historical-source':mutant['physicalRows'][history]['executionSource']=c['source']
        elif kind=='current-witness':mutant['sourceRows'][active]['executionWitness']['source']=p['historicalBatch']['source']
        else:mutant['sourceRows'][anchor]['previousSourceByteSha256']='0'*64
        try:domains(mutant,c,p,previous)
        except ValueError:negative.append(dict(kind=kind,rejected=True))
        else:raise ValueError('invalid provenance accepted')
    require(c['productionDependencyJarHashes']==p['unmeasuredProductionDependencyJarHashes']
      and p['protocolDependencyPhysicalBytesMatched']==176 and p['protocolDependencyCoverageTransferred'] is False,'no dependency counter transfer')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,witnesses=pins,staticDispositions=dispositions,
      rawPmdFindings=16,rawPmdExit=4,newMainRawFindings=0,unclassified=0,actualViolationsOutstanding=0,suppressionsAdded=0,
      currentApiGeneratedTypes=11,currentApiGeneratedMethodsSeparatelyVerifiedNotAddedToCounters=45,newGeneratedContracts=generated,
      existingGenerated41CurrentSourceAndOrdinaryQualified=True,generatedContractByteIdentityOnlyNotOldExecution=True,
      originalFailures=failures,negativeGuards=negative,editAnchorCounts=counts,counters=c['counters'],customExclusionsAdded=False,
      ptExecutedByReview=0,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,
      actualVmActions=0,actualDatabaseActions=0,targetClassInitializedByReview=False)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rawFindings=16,unclassified=0,generatedMethods=45,negativeGuards=5,manifestSha256=host.sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
