"""Exact API146/current30, old16 plus private-owner context1, generated45+5 and five domain guards."""
from collections import Counter
import copy
import json
import os
from pathlib import Path
import pg6966_chr_adapter_host as host
import pg7872_api_query_collection_host as execution
import pg7876_api_query_collection_six_compile as compilation
import pg7032_monitoring_six_artifact_post as steps
from monitoring_api_domains import validate_domains
from host_tool_invocation import capture,verify
OUT=host.BASE/'PG7882-api-query-collection-review-v1'
PREFIX='dev/codex/schubert/nk/api/monitoring/'
def require(value,message):
    if not value:raise ValueError(message)
def domains(trace,current,physical,previous):
    return validate_domains(trace,current,physical,previous,previous_count=123,physical_count=110,test_count=146,current_executable=30)
def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only same-source review')
    proofs={};pins={}
    for key,path,digest in (
      ('current','PG7874-api-query-collection-post-v1/manifest.json',None),
      ('physical','PG7878-api-query-collection-six-post-v1/manifest.json',None),
      ('trace','PG7880-api-query-collection-trace-v1/manifest.json',None),
      ('previousTrace','PG7852-api-query-duration-trace-v3/manifest.json','1190a6b099334bcd2bd30c4cd199e27d97e00227b65efc64f2d1b51071843b28'),
      ('old','PG7864-api-query-duration-post-v4/manifest.json','e03a785b0e5c4ebcd047a4f52327b3616aeb4e018b3ae4f3f9f0657a53f03f2c'),
      ('prior','PG7854-api-query-duration-review-v3/manifest.json','c2748ccf8b1a824c21f67da3a9f7cf9b960e3511a8bd1f3f6f4135f81a149179'),
      ('platform','PG7413-api-generated-value-review-v2/manifest.json','7d108ca7499763b5ed5526e60144276ace055c66aa88e380a0ccde0a3be2a82e')):
        f=host.BASE/path;sha=host.sha(f);require(digest is None or sha==digest,'exact original witness')
        proofs[key]=json.loads(f.read_bytes());pins[key]=dict(path=path,sha256=sha)
    c=proofs['current'];p=proofs['physical'];t=proofs['trace'];old=proofs['old'];prior=proofs['prior']
    require(c['actualExit']==p['actualExit']==t['actualExit']==0 and c['source']==p['source']==t['source']==compilation.SOURCE
      and c['tests']==146 and c['suites']==18 and len(c['sourceFiles'])==36 and len(c['executableClasses'])==30
      and len(c['physicalClasses'])==31 and c['actualCrcMismatch']==0 and c['actualSessions']==1
      and all(v['missed']==0 and v['covered']>0 for v in c['counters'].values()),'current146/30 same-source/singleexec/four100')
    require(all(c['sourceFiles'].get(k)==v for k,v in old['sourceFiles'].items())
      and all(c['physicalClasses'].get(k)==v for k,v in old['physicalClasses'].items()),'old34 Java/29 physical incl debug unchanged')
    raw=c['staticRaw']['pmd'];canonical=lambda r:json.dumps(r,sort_keys=True)
    unchanged=[r for r in raw['findings'] if r['class']!='DbQueryDurationMetricCollector']
    new=[r for r in raw['findings'] if r['class']=='DbQueryDurationMetricCollector']
    require(raw['actualExit']==4 and raw['processingErrors']==0 and len(raw['findings'])==17 and len(new)==1
      and Counter(map(canonical,unchanged))==Counter(map(canonical,old['staticRaw']['pmd']['findings']))
      and prior['actualExit']==0 and prior['unclassified']==prior['actualViolationsOutstanding']==0
      and len(prior['staticDispositions'])==16,'exact old16 reasons plus only one new context row')
    main_path='src/schubert-nk-api/src/main/java/'+PREFIX+'DbQueryDurationMetricCollector.java'
    row=new[0];require((row['rule'],row['beginline'],row['begincolumn'],row['method'],row['package'])
      ==('AvoidSynchronizedStatement','35','5','collect','dev.codex.schubert.nk.api.monitoring'),'exact private-owner sync row')
    dispositions=copy.deepcopy(prior['staticDispositions'])
    for reason in dispositions:
        path=reason['sourcePath'];require(c['sourceFiles'][path]==old['sourceFiles'][path],'each issue-bearing byte unchanged')
        reason.update(source=compilation.SOURCE,ordinaryTestWitness='PG7872-api-query-collection-host-v1',currentRationaleWitness=pins['prior'])
    dispositions.append(dict(raw=row,classification='CONTEXT_NOT_APPLICABLE',sourcePath=main_path,sourceSha256=c['sourceFiles'][main_path],
      source=compilation.SOURCE,ordinaryTestWitness='PG7872-api-query-collection-host-v1',sourceOrRulesChanged=False,suppressionAdded=False,
      reason='411 owner-private read through complete validated event publication; never synchronizes borrowed provider/registry. DBCONN001/006/007 verify pre-publication state, actual owned contender BLOCKED, precomputed identity/count/sum and independent owner; unknown/failure is no synthetic event.'))
    require(c['spotbugs']['actualExit']==0 and c['spotbugs']['findings']==0 and c['staticRaw']['checkstyle']['actualExit']==0
      and not c['staticRaw']['checkstyle']['findings'],'actual SB/CS zero')
    run=json.loads((execution.SLOT/'manifest.safe.json').read_bytes())
    require(run['actualExit']==0 and len(run['cases'])==146 and all(r['result']=='PASS' for r in run['cases'])
      and len([r for r in run['cases'] if r['classname'].endswith('.DbQueryDurationMetricCollectorTest')])==8
      and any(r['name'].startswith('dbConn005ImmutableObservation') for r in run['cases']),'all current146 and eight direct new contracts')
    require(prior['currentApiGeneratedTypes']==11 and prior['currentApiGeneratedMethodsSeparatelyVerifiedNotAddedToCounters']==45,'old45 separate generated contracts')
    platform=proofs['platform'];require(host.sha(host.TC/'jdk-25.0.4/lib/modules')==platform['jdkModulesSha256']
      and host.sha(host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar')==platform['jacocoCoreSha256'],'same official record/enum filters and JDK')
    work=host.W/'pg7882-api-query-collection-review-v1';require(not work.exists(),'new-only metadata work');work.mkdir();steps.SLOT=work
    name=PREFIX+'DbQueryDurationMetricCollector$Observation';f=execution.SLOT/'snapshot/tools/quality/harnesses/target/classes'/(name+'.class')
    require(host.sha(f)==c['physicalClasses'][name+'.class'],'exact executed record byte')
    receipt,stdout=steps.step('javap-Observation',[str(host.TC/'jdk-25.0.4/bin/javap'),'-p','-c','-s',str(f)])
    require(receipt['actualExit']==0 and all(x in stdout for x in ('extends java.lang.Record','toString();','hashCode();','equals(java.lang.Object);',
      'outcome();','elapsedNanoseconds();','descriptor: ()J','InvokeDynamic')),'five generated record contracts current typed oracle plus noninitializing bytecode')
    code=''.join((host.ROOT/main_path).read_text().split())
    require('privatefinalObjectlock=newObject();' in code and 'synchronized(lock){' in code
      and 'if(!metrics.detailedMetricsRequested())returnOptional.empty();' in code
      and 'Objects.requireNonNull(observation.apply(query),"DBdurationobservation")' in code
      and 'metrics.record(query,value.outcome(),value.elapsedNanoseconds());' in code
      and '.close(' not in code and 'catch(' not in code and 'nanoTime(' not in code,'complete publication and natural original propagation, no real clock/query/ownership side effect')
    require(code.index('if(!metrics.detailedMetricsRequested())')<code.index('observation.apply(query)')<code.index('metrics.record(query,')<code.index('returnsupplied;'),'exact source ordering')
    previous={r['path']:r for r in proofs['previousTrace']['sourceRows']};counts=domains(t,c,p,previous);negative=[]
    history=next(i for i,r in enumerate(t['physicalRows']) if r['className'].startswith('batch:') and r['executable'])
    active=next(i for i,r in enumerate(t['sourceRows']) if r['path'] in c['sourceFiles']);anchor=next(i for i,r in enumerate(t['sourceRows']) if r['path'] in previous)
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
    require(c['productionDependencyJarHashes']==p['unmeasuredProductionDependencyJarHashes'] and p['protocolDependencyPhysicalBytesMatched']==176
      and p['protocolDependencyCoverageTransferred'] is False,'exact protocol dependency bytes, no counters transferred')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,witnesses=pins,staticDispositions=dispositions,
      rawPmdFindings=17,rawPmdExit=4,newMainRawFindings=1,unclassified=0,actualViolationsOutstanding=0,suppressionsAdded=0,
      currentApiGeneratedTypes=12,currentApiGeneratedMethodsSeparatelyVerifiedNotAddedToCounters=50,
      newGeneratedContracts=[dict(className=name,sha256=host.sha(f),methods=['outcome','elapsedNanoseconds','equals','hashCode','toString'],ordinaryTest='DBCONN005',receipt=receipt)],
      existingGenerated45CurrentSourceAndOrdinaryQualified=True,negativeGuards=negative,editAnchorCounts=counts,counters=c['counters'],
      ptExecutedByReview=0,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,targetClassInitializedByReview=False)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rawFindings=17,unclassified=0,generatedMethods=50,negativeGuards=5,manifestSha256=host.sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
