"""Web77 same-source18, existing8 plus explicit context5, generated16+11 and seven provenance guards."""
from collections import Counter
import copy
import json
import os
from pathlib import Path
import re
import pg6966_chr_adapter_host as host
import pg7944_web_outbox_host as execution
import pg7942_web_outbox_six_compile as compilation
import pg7950_web_outbox_trace as trace_tool
import pg7032_monitoring_six_artifact_post as steps
from pg7192_heap_quality_review import anchors
from host_tool_invocation import capture,verify
OUT=host.BASE/'PG7952-web-outbox-review-v1'
PREFIX='dev/codex/schubert/nk/web/monitoring/'
def require(value,message):
    if not value:raise ValueError(message)
def domains(trace,current,physical,previous):
    require(trace['source']==current['source']==physical['source']==compilation.SOURCE,'same source')
    counts=anchors(trace['sourceRows'],previous,dict(changed=0,unchanged=129,introduced=6))
    paths={r['path']:r for r in trace['sourceRows']}
    require(len(paths)==135 and len(trace['physicalRows'])==119
      and len({r['className'] for r in trace['physicalRows']})==119,'all unique135/119')
    for row in trace['sourceRows']:
        path=row['path'];require(row['currentSourceCoverageTransferred'] is False,'no transferred counters')
        if path in current['sourceFiles']:
            require(row['sha256']==current['sourceFiles'][path] and row['executionWitness']['source']==current['source']
              and row['executionWitness']['tests']==77 and row['executionWitness']['suites']==10
              and row['componentCounterScope']=='ALL_CURRENT_WEB_MONITORING_EXECUTABLES_ONLY','all current exact Web inputs')
        elif path.endswith('/pom.xml'):
            require(row['componentCounterScope']=='NOT_EXECUTABLE_CONFIGURATION' and row['compileWitness']['source']==current['source'],'POM not PT')
        else:require('executionWitness' not in row and row['componentCounterScope']=='HISTORICAL_ONLY_NO_CURRENT_COUNTERS','history is not current execution')
        if path not in previous:
            program=Path(path).stem.removesuffix('Test')
            require(program in trace_tool.FAMILIES and row['testIdFamily']==trace_tool.FAMILIES[program],'three distinct program/test families, no alias')
    for row in trace['physicalRows']:
        role,entry=row['className'].split(':',1);key={'web':'currentWeb','api':'historicalApi','batch':'historicalBatch'}[role]
        proof=physical[key];executable=not entry.endswith('package-info.class')
        source='src/schubert-nk-'+role+'/src/main/java/'+entry.removesuffix('.class').split('$',1)[0]+'.java'
        require(row['sourcePath']==source and row['owner']==paths[source]['owner'] and row['sha256']==proof['physicalClasses'][row['className']]
          and row['executionSource']==proof['source'] and row['executable'] is executable
          and row['currentSourceExecutionAccepted'] is (role=='web' and executable)
          and row['qualificationDomain']==('CURRENT_WEB_QUALIFIED' if role=='web' else 'HISTORICAL_'+role.upper()+'_BYTE_ONLY'),'all exact source/byte/role/current flags')
    require(sum(r['currentSourceExecutionAccepted'] for r in trace['physicalRows'])==18==len(current['executableClasses']),'only actual18 current executable classes')
    return counts
def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only same-source review')
    proofs={};pins={}
    for key,path,digest in (
      ('current','PG7946-web-outbox-post-v1/manifest.json',None),
      ('physical','PG7948-web-outbox-six-post-v1/manifest.json',None),
      ('trace','PG7950-web-outbox-trace-v1/manifest.json',None),
      ('previousTrace','PG7920-mq-event-trace-v1/manifest.json','014dded23795c0b234456d1952e0b55413d981d0904d75f20d39c3e0fc064735'),
      ('old','PG7774-media-bytes-post-v1/manifest.json','f9e8f54f29fe79b739802c520182b211e28d2aa89b450f35d43064198702dcdd'),
      ('prior','PG7780-media-bytes-review-v1/manifest.json','76ac5423f1cf1ded3940935571c63daee24ebaf43948300043b481119fa5609d'),
      ('platform','PG7444-web-generated-review-v1/manifest.json','ff4749fc88d61a0b094162ded43128bfac41c4fc9ddb8875c8425c530771b52c')):
        f=host.BASE/path;sha=host.sha(f);require(digest is None or sha==digest,'pinned original witness')
        proofs[key]=json.loads(f.read_bytes());pins[key]=dict(path=path,sha256=sha)
    c=proofs['current'];p=proofs['physical'];trace=proofs['trace'];old=proofs['old'];prior=proofs['prior']
    require(c['actualExit']==p['actualExit']==trace['actualExit']==0 and c['source']==p['source']==trace['source']==compilation.SOURCE
      and c['tests']==77 and c['suites']==10 and len(c['sourceFiles'])==20 and len(c['physicalClasses'])==19
      and len(c['executableClasses'])==18 and c['actualCrcMismatch']==0 and c['actualSessions']==1
      and all(v['missed']==0 and v['covered']>0 for v in c['counters'].values()),'actual77/18/same-source singleexec four100')
    require(all(c['sourceFiles'].get(k)==v for k,v in old['sourceFiles'].items())
      and all(c['physicalClasses'].get(k)==v for k,v in old['physicalClasses'].items()),'all old14 Java/14 physical including debug unchanged')
    raw=c['staticRaw']['pmd'];canonical=lambda row:json.dumps(row,sort_keys=True)
    unchanged=[r for r in raw['findings'] if not r['class'].startswith('WebOutbox')]
    new=[r for r in raw['findings'] if r['class'].startswith('WebOutbox')]
    require(raw['actualExit']==4 and raw['processingErrors']==0 and len(raw['findings'])==13 and len(new)==5
      and Counter(map(canonical,unchanged))==Counter(map(canonical,old['staticRaw']['pmd']['findings']))
      and prior['actualExit']==0 and prior['unclassified']==prior['actualViolationsOutstanding']==0
      and len(prior['individualRationaleRows'])==8,'all old8 exact raw/rationale rows and only five declared new context rows')
    dispositions=copy.deepcopy(prior['individualRationaleRows'])
    for row in dispositions:
        row.update(source=compilation.SOURCE,ordinaryTestWitness='PG7944-web-outbox-host-v1',currentRationaleWitness=pins['prior'])
    expected={
      ('WebOutboxMetricCollector','AvoidSynchronizedStatement','29','5'):'PRIVATE_OWNER_COMPLETE_PUBLICATION',
      ('WebOutboxMetricCollector','AvoidCatchingGenericException','35','31'):'ORIGINAL_RUNTIME_PROPAGATES_AFTER_UNKNOWN',
      ('WebOutboxMetricCollector','AvoidCatchingGenericException','35','50'):'ORIGINAL_ERROR_PROPAGATES_AFTER_UNKNOWN',
      ('WebOutboxObservationRepository','CloseResource','38','33'):'CHECKED_NULLABLE_PREPARED_STATEMENT_EXTENDED_TWR',
      ('WebOutboxObservationRepository','CloseResource','42','27'):'CHECKED_NULLABLE_RESULT_SET_EXTENDED_TWR'}
    seen=set()
    for row in new:
        key=(row['class'],row['rule'],row['beginline'],row['begincolumn'])
        require(key in expected and key not in seen and row['package']=='dev.codex.schubert.nk.web.monitoring'
          and row['method']==('collect' if row['class'].endswith('Collector') else 'read'),'each exact new rule/source position')
        seen.add(key);path='src/schubert-nk-web/src/main/java/'+PREFIX+row['class']+'.java'
        reason=('411 private owner lock across read/resource close/complete publication; Runtime/Error only clears unknown then rethrows same identity, never retry/format/normal return. WEBOBXCONN001/003/005/006/007 prove close timing, actual contender BLOCKED, original problem and independent tuple vectors.'
          if row['class'].endswith('Collector') else
          'JDK extended try-with-resources on separately declared @Nullable local after explicit null rejection; both resources close on normal/SQL/Runtime/Error paths, connection is borrowed and unchanged. WEBOBXDB001/006/007/008/009/010 and WEBOBXCONN001/005 independently verify exact SQL, all acquisition/read/close failures, order/suppressed identity and no connection mutation. This is a syntax-sensitive CloseResource heuristic, not a suppressed leak.')
        if row['rule']=='CloseResource':require(row['variable']==('statement' if row['beginline']=='38' else 'rows'),'each actual acquired resource variable')
        dispositions.append(dict(raw=row,classification='CONTEXT_NOT_APPLICABLE' if row['class'].endswith('Collector') else 'HEURISTIC_FALSE_POSITIVE_WITH_EXTENDED_TWR_AND_EXECUTED_RESOURCE_ORACLE',
          reasonKind=expected[key],reason=reason,sourcePath=path,sourceSha256=c['sourceFiles'][path],source=compilation.SOURCE,
          ordinaryTestWitness='PG7944-web-outbox-host-v1',sourceOrRulesChanged=False,suppressionAdded=False))
    require(seen==set(expected) and len(dispositions)==13 and all(c['staticRaw'][k]['actualExit']==0 and not c['staticRaw'][k]['findings']
      and c['staticRaw'][k]['processingErrors']==0 for k in ('checkstyle','spotbugs')),'all13 individually classified and SB/CS0')
    run=json.loads((execution.SLOT/'manifest.safe.json').read_bytes())
    require(run['actualExit']==0 and run['begin']['expectedTests']==77 and len(run['cases'])==77 and all(r['result']=='PASS' for r in run['cases'])
      and run['begin']['prerequisiteMetadataReceipt']==c['prerequisiteMetadataReceipt'],'genuine77 and exact metadata prerequisite')
    for name,count in (('GeneratedWebValueContractTest',4),('MediaBytesMetricRecorderTest',8),('WebOutboxMetricRecorderTest',8),
      ('WebOutboxObservationRepositoryTest',10),('WebOutboxMetricCollectorTest',8)):
        require(len([r for r in run['cases'] if r['classname'].endswith('.'+name)])==count,'all old generated/current26 case contracts ran now')
    require(len(prior['generatedTypes'])==6 and prior['generatedMethodCount']==16
      and all(c['physicalClasses'][r['className']+'.class']==r['sha256'] and c['sourceFiles'][r['sourcePath']]==r['sourceSha256'] for r in prior['generatedTypes']),
      'old16 generated methods unchanged source/byte and current ordinary, not old execution transfer')
    platform=proofs['platform'];require(host.sha(host.TC/'jdk-25.0.4/lib/modules')==platform['jdkModulesSha256']
      and host.sha(host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar')==platform['jacocoCoreSha256'],'same official platform/filter bytes')
    mainpath='src/schubert-nk-web/src/main/java/'+PREFIX+'WebOutboxObservationRepository.java'
    code=''.join((host.ROOT/mainpath).read_text().split())
    require('if(statement==null)thrownewSQLException(INVALID);try(statement){' in code
      and 'if(rows==null)thrownewSQLException(INVALID);try(rows){' in code
      and 'FROMschubert_web_session.web_log_outboxGROUPBYstatus' in code
      and not any(x in code for x in ('.commit(','.rollback(','.setAutoCommit(','.setReadOnly(','.setTransactionIsolation(','.abort(')),
      'explicit null safety/extended TWR/fixed technical SELECT and no caller ownership changes')
    collector=''.join((host.ROOT/'src/schubert-nk-web/src/main/java'/PREFIX/'WebOutboxMetricCollector.java').read_text().split())
    require('privatefinalObjectlock=newObject();' in collector and 'synchronized(lock){' in collector
      and 'if(!metrics.detailedMetricsRequested())returnOptional.empty();' in collector
      and 'catch(SQLException|RuntimeException|ErrorunavailableObservation){metrics.missing();throwunavailableObservation;}' in collector
      and '.close(' not in collector,'owner publication and original unchecked failures are never normalized')
    previous={r['path']:r for r in proofs['previousTrace']['sourceRows']};counts=domains(trace,c,p,previous);negative=[]
    active=next(i for i,r in enumerate(trace['sourceRows']) if r['path'] in c['sourceFiles'])
    anchor=next(i for i,r in enumerate(trace['sourceRows']) if r['path'] in previous)
    added=next(i for i,r in enumerate(trace['sourceRows']) if r['path'] not in previous)
    history=next(i for i,r in enumerate(trace['physicalRows']) if r['className'].startswith('api:') and r['executable'])
    for kind in ('historical-current','role-alias','historical-source','current-witness','previous-anchor','new-program-family','physical-byte'):
        mutant=copy.deepcopy(trace)
        if kind=='historical-current':mutant['physicalRows'][history]['currentSourceExecutionAccepted']=True
        elif kind=='role-alias':mutant['physicalRows'][history]['qualificationDomain']='CURRENT_WEB_QUALIFIED'
        elif kind=='historical-source':mutant['physicalRows'][history]['executionSource']=c['source']
        elif kind=='current-witness':mutant['sourceRows'][active]['executionWitness']['source']=p['historicalApi']['source']
        elif kind=='previous-anchor':mutant['sourceRows'][anchor]['previousSourceByteSha256']='0'*64
        elif kind=='new-program-family':mutant['sourceRows'][added]['testIdFamily']='UNREGISTERED'
        else:mutant['physicalRows'][history]['sha256']='0'*64
        try:domains(mutant,c,p,previous)
        except ValueError:negative.append(dict(kind=kind,rejected=True))
        else:raise ValueError('invalid provenance accepted')
    work=host.W/'pg7952-web-outbox-review-v1';require(not work.exists(),'new-only static javap work');work.mkdir();steps.SLOT=work
    generated=copy.deepcopy(prior['generatedTypes'])
    for suffix,methods,testid in (
      ('Status',['values','valueOf'],'WEBOBXMET003'),
      ('Observation',['pending','sent','error','pendingAge','sentAge','errorAge','equals','hashCode','toString'],'WEBOBXMET006')):
        name=PREFIX+'WebOutboxMetricRecorder$'+suffix;file=execution.COMPILE/'snapshot/src/schubert-nk-web/target/classes'/(name+'.class')
        require(host.sha(file)==c['physicalClasses'][name+'.class'],'exact executed generated byte')
        receipt,stdout=steps.step('javap-'+suffix,[str(host.TC/'jdk-25.0.4/bin/javap'),'-p','-c','-s',str(file)])
        require(receipt['actualExit']==0,'noninitializing javap zero')
        if suffix=='Status':
            require('clone:' in stdout and 'java/lang/Enum.valueOf:' in stdout
              and 'descriptor: ()[L'+name+';' in stdout and 'descriptor: (Ljava/lang/String;)L'+name+';' in stdout,'both enum factories and direct typed oracle')
        else:
            require('extends java.lang.Record' in stdout and 'InvokeDynamic' in stdout
              and all(re.search(r'\b'+m+r'\(',stdout) for m in methods)
              and 'descriptor: ()J' in stdout and 'descriptor: ()Ljava/time/Duration;' in stdout,'all nine exact record contracts and fixed independent literal/hash oracle')
        source='src/schubert-nk-web/src/main/java/'+PREFIX+'WebOutboxMetricRecorder.java'
        generated.append(dict(className=name,sha256=host.sha(file),sourcePath=source,sourceSha256=c['sourceFiles'][source],
          testIds=testid,directOrdinaryContractsVerified=True,methods=[dict(name=m) for m in methods],javapReceipt=receipt,customExclusionAdded=False))
    require(len(generated)==8 and sum(len(r['methods']) for r in generated)==27,'16 plus11 separate generated contracts, not numeric counters')
    helper=execution.HELPER.read_text();selected=re.findall(r'"(dev\.codex\.schubert\.nk\.web\.monitoring\.[A-Za-z]+Test)"',helper)
    require(set(selected)=={'dev.codex.schubert.nk.web.monitoring.'+n for n in execution.COUNTS} and len(selected)==10
      and 'getTestsFoundCount() == 77' in helper and 'getTestsSucceededCount() == 77' in helper and 'results.size() == 77' in helper
      and 'DiscoverySelectors::selectClass' in helper and '.getMessage(' not in helper and '.getCause(' not in helper and '.getSuppressed(' not in helper,
      'exact ten safe selectors/77 fail closed; diagnostics never format raw exception data')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,witnesses=pins,tests=77,suites=10,newProductionCases=26,necessaryExistingCases=51,
      counters=c['counters'],generatedTypes=generated,generatedMethodCount=27,individualRationaleRows=dispositions,rawPmdFindings=13,rawPmdExit=4,newMainRawFindings=5,
      unclassified=0,actualViolationsOutstanding=0,suppressionsAdded=0,customExclusionsAdded=False,metadataNegativeGuards=negative,editAnchorCounts=counts,
      prerequisiteReceipt=c['prerequisiteMetadataReceipt'],helperSha256=host.sha(execution.HELPER),registryLifetime='BORROWED_CALLER_OWNED',
      actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,coverageUnion=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,ptExecutedByReview=0)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,tests=77,generatedMethods=27,rawFindings=13,unclassified=0,negativeGuards=7,manifestSha256=host.sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
