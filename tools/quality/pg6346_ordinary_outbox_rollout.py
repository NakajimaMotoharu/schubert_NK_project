"""Whole-qualified ordinary Outbox rollout evidence; broader JDBC/native scopes stay open."""
import hashlib
import json
import os
import subprocess
from pathlib import Path
from pg5940_private_lock_compile import ROOT,W,BASE,TC,sha
from pg6334_current4048_trace import SOURCE,read_qualified
from pg6186_native_ownership_order import methods,instructions,one_call

OWNED={
 ('api','messaging.outbound.OutboxJmsSender'):(1,['dev.codex.schubert.nk.api.messaging.outbound.OutboxFailureOwnershipTest','dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatcherTest']),
 ('web','messaging.ArtemisRequestSender'):(1,['dev.codex.schubert.nk.web.messaging.ArtemisRequestSenderTest']),
 ('web','logging.WebLogMessageSender'):(1,['dev.codex.schubert.nk.web.logging.WebLogMessageSenderTest'])}
BORROWED={
 ('api','messaging.outbound.ReplySender'):(1,['dev.codex.schubert.nk.api.messaging.outbound.OutboundJmsAdapterTest']),
 ('api','messaging.outbound.DlqSender'):(2,['dev.codex.schubert.nk.api.messaging.outbound.OutboundJmsAdapterTest','dev.codex.schubert.nk.api.messaging.inbound.SyncRequestListenerTest']),
 ('web','messaging.ArtemisReplyDlqSender'):(1,['dev.codex.schubert.nk.web.messaging.ArtemisReplyConsumerTest'])}
GRAPH_CASES={
 'dev.codex.schubert.nk.api.messaging.outbound.OwnedOutboxDispatcherTest':['graph322001NestedFatalStopsOwnedWorkerBeforeAnotherDispatch'],
 'dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatcherTest':['graph322002NestedFatalNeverMarksOrdinaryFailureAndNonfatalCycleStillRetries','graph322003NullProviderEdgesKeepOrdinaryFailureAndExactRetryPostconditions'],
 'dev.codex.schubert.nk.web.logging.WebLogReplayWorkerTest':['graph323001ProviderFatalEdgesStopWithoutOrdinaryFailedCycle'],
 'dev.codex.schubert.nk.web.logging.WebLogDispatcherTest':['graph323002ProviderFatalNeverMarksOrdinaryFailureAndNullEdgesStillRetry']}


def bind_classes(classes,cases):
    refs=[]
    for cls in classes:
        found=[r for r in cases if r['class']==cls]
        if not found or any(r['source']!=SOURCE or r['result']!='PASS_ORIGINAL_XML'for r in found):raise ValueError('actual same-source whole semantic Test class')
        refs.extend({k:r[k]for k in ('testId','class','caseNameSha256','xmlSha256','source')}for r in found)
    return refs


def main():
    qp,q=read_qualified();cases=json.loads(qp.with_name('cases.json').read_bytes())
    order=BASE/'PG6328-outbox-graph-order-v1/manifest.json'
    if sha(order)!='2a5c53cf4966a904d9380d4b7d928bc619942b9c695795bcebc002e8915d2a3c':raise ValueError('original current four-boundary order proof')
    op=json.loads(order.read_bytes())
    if op['source']!=SOURCE or not op['ownershipReviewed']or op['actualExit']!=0:raise ValueError('source-specific ordinary graph policy')
    run=W/'pg6324-web-graph-selected-v1/source';found={};evidence=[]
    wanted={m+':dev/codex/schubert/nk/'+m+'/'+n.replace('.','/')+'.java':v[0]for(m,n),v in(OWNED|BORROWED).items()}
    for module in ('api','web'):
        for p in(ROOT/('src/schubert-nk-'+module+'/src/main/java')).rglob('*.java'):
            count=p.read_text().count('.createProducer()')
            if count:found[module+':'+p.relative_to(ROOT/('src/schubert-nk-'+module+'/src/main/java')).as_posix()]=count
    if found!=wanted:raise ValueError('all ordinary API/Web producer creation sites individually accounted')
    for(module,name),(count,testclasses)in(OWNED|BORROWED).items():
        key=module+':dev/codex/schubert/nk/'+module+'/'+name.replace('.','/')+'.class'
        jar=run/('src/schubert-nk-'+module+'/target/schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
        blocks=methods(subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),'-p','-c','-s','-classpath',str(jar),
            'dev.codex.schubert.nk.'+module+'.'+name],text=True))
        one_call(blocks,'JMSContext.createProducer:',count)
        owned=(module,name)in OWNED
        if owned:
            close=one_call(blocks,'JMSContext.close:');helper=blocks[close[0][0]]
            if' closeAfterFailure('not in close[0][0]or not any(op=='if_acmpeq'for _,op,_ in instructions(helper)):
                raise ValueError('manual one-close helper with Throwable identity guard')
            for signature,body in blocks.items():
                if' send('in signature and any('JMSContext.close:'in arg for _,_,arg in instructions(body)):
                    raise ValueError('no generated TWR direct-close self-suppression in send')
            role='DIRECT_OWNED_SENDER_MANUAL_CLOSE_GUARD'
        else:
            for token in ('JMSContext.close:','JMSContext.commit:','JMSContext.rollback:',
                'JmsContextFactory.open:','TransactedJmsContextProvider.open:','createContext:'):
                one_call(blocks,token,0)
            if not any(' send('in k and'jakarta.jms.JMSContext'in k for k in blocks):raise ValueError('explicit borrowed JMSContext parameter')
            role='NON_APPLICABLE_BORROWED_STAGE_ONLY_NO_OWNED_CLOSE'
        import zipfile
        with zipfile.ZipFile(jar)as z:classsha=hashlib.sha256(z.read(key.split(':',1)[1])).hexdigest()
        if classsha!=q['allPhysicalMainSha256'][key]:raise ValueError('same original whole class bytes')
        sourcepath=Path('src/schubert-nk-'+module+'/src/main/java')/(key.split(':',1)[1][:-6]+'.java')
        if(ROOT/sourcepath).read_bytes()!=(run/sourcepath).read_bytes():raise ValueError('same original Main source')
        evidence.append(dict(className=name,module=module,sourcePath=sourcepath.as_posix(),sourceSha256=sha(ROOT/sourcepath),
            classSha256=classsha,producerSites=count,role=role,currentWholeCaseRefs=bind_classes(testclasses,cases)))
    actual={(r['class'],r['caseNameSha256']):r for r in cases};graphrefs=[]
    for cls,names in GRAPH_CASES.items():
        for name in names:
            row=actual.get((cls,hashlib.sha256(name.encode()).hexdigest()))
            if row is None or row['source']!=SOURCE or row['result']!='PASS_ORIGINAL_XML':raise ValueError('all five actual independent graph cases')
            graphrefs.append({k:row[k]for k in ('testId','class','caseNameSha256','xmlSha256','source')})
    value=dict(actualExit=0,source=SOURCE,wholeQualificationSha256=sha(qp),wholeCasesSha256=sha(qp.with_name('cases.json')),
        originalPgJvmSha256=sha(order),ordinaryProducerClasses=6,ownedSenderClasses=3,borrowedStageOnlyClasses=3,
        producerSourceSites=7,targets=evidence,independentGraphCases=graphrefs,ordinarySenderScopeVerified=True,
        ordinaryFourBoundaryGraphScopeVerified=True,testsExecuted=0,additionalBuildsIssued=0,productionClassesExecuted=0,
        vmActions=0,ptAlternativeCompleted=0,formalAccepted=False,
        unresolved=['YKT1323 broader JDBC/application compound contracts not blanket-certified',
            'consumer/factory/native owner lifetimes are distinct contracts; actual Root/current/cohort remain held',
            'global100/F03/native/CHR/451/QA051final/formal phase remain incomplete'])
    os.umask(0o077);out=BASE/'PG6346-ordinary-outbox-rollout-v1';out.mkdir()
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,source=SOURCE,owned=3,borrowed=3,graphCases=5,manifestSha256=sha(out/'manifest.json'))))


if __name__=='__main__':main()
