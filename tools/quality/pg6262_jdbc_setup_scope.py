"""Read original same-source JVM for all21 ordinary API/Web JDBC setup sites; no JDBC execution."""
import json
import os
import re
import subprocess
from pg5940_private_lock_compile import ROOT,W,BASE,TC,sha
from pg6186_native_ownership_order import methods,instructions
from pg6248_normal_phase_qualification import original_source

OWNERS={
 'api':('api.application.admin.UserMutationApplicationService','api.application.admin.UserQueryApplicationService',
    'api.application.log.LogQueryApplicationService','api.application.media.MediaApplicationService',
    'api.application.question.QuestionMutationApplicationService','api.application.question.QuestionQueryApplicationService',
    'api.application.question.QuestionSubmissionService','api.application.question.QuestionWorkerService',
    'api.application.scenario.ScenarioApplicationService','api.bootstrap.BootstrapAdminMain',
    'api.dispatch.JdbcSyncRequestProcessor','api.logging.WebLogIngestService','api.maintenance.InboxCleanup',
    'api.messaging.outbound.OutboxDispatcher'),
 'web':('web.logging.WebLogDispatcher','web.logging.WebRequestLogProducer','web.receipt.ReceiptReferenceRepository',
    'web.revocation.RevocationRetryCoordinator','web.session.EncryptedWebSessionRepository')}
PREFIX='dev.codex.schubert.nk.'


def main():
    source=original_source();qp=BASE/'PG6248-normal-phase-qualification-v1/manifest.json'
    if sha(qp)!='4495f3778a40c33c3de9f6fbd1082581fba8f7cf02caafae55687b32928b8bfe':raise ValueError('exact current original proof')
    q=json.loads(qp.read_bytes());private=W/'pg6248-normal-phase-qualification-v1/manifest.safe.json'
    if q['actualExit']!=0 or sha(private)!=q['privateManifestSha256']:raise ValueError('same-source original private map')
    proof=json.loads(private.read_bytes());snapshot=W/'pg6246-normal-phase-selected-v1/source'
    source_sites={}
    for module in OWNERS:
        for path in ROOT.glob('src/schubert-nk-'+module+'/src/main/java/**/*.java'):
            count=path.read_text().count('setAutoCommit(false)')
            if count:source_sites[module+':'+path.stem]=count
    if len(source_sites)!=19 or sum(source_sites.values())!=21:raise ValueError('all ordinary API/Web sites, not a sampled search')
    facts=[]
    for module,names in OWNERS.items():
        jar=snapshot/('src/schubert-nk-'+module+'/target/schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
        for name in names:
            path='src/schubert-nk-'+module+'/src/main/java/'+(PREFIX+name).replace('.','/')+'.java'
            if sha(ROOT/path)!=proof['allSourceHashes'][path]or sha(snapshot/path)!=sha(ROOT/path):raise ValueError('original exact source')
            blocks=methods(subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),'-p','-c','-s','-classpath',str(jar),PREFIX+name],text=True))
            actual=[]
            for method,body in blocks.items():
                ops=instructions(body)
                edges=[(int(a),int(b),int(c),t)for a,b,c,t in re.findall(r'(?m)^\s*(\d+)\s+(\d+)\s+(\d+)\s+(any|Class [\w/$]+)\s*$',body)]
                for i,(at,_,arg)in enumerate(ops):
                    if 'Connection.setAutoCommit:'not in arg:continue
                    if ops[i-1][1]!='iconst_0':raise ValueError('same literal false setup, not a different transaction mode')
                    covering=[e for e in edges if e[0]<=at<e[1]]
                    guards=[e for e in covering if e[3]in ('any','Class java/lang/Throwable','Class java/lang/Error')]
                    closes=[pc for pc,_,arg in ops if 'Connection.close:'in arg]
                    short=name.rsplit('.',1)[1]
                    helper=None
                    if short=='WebLogDispatcher':
                        selected=[(k,v)for k,v in blocks.items()if ' closeAfterFailure('in k]
                        if len(selected)!=1 or 'Method closeAfterFailure:'not in body:raise ValueError('explicit owned close helper port')
                        key,cleanup=selected[0]
                        cleanup_calls=[pc for pc,_,arg in instructions(cleanup)if 'Connection.close:'in arg]
                        if len(cleanup_calls)!=1:raise ValueError('one actual close inside exact Web-log helper')
                        helper=dict(method=key,actualCloseOffsets=cleanup_calls)
                    if short=='OutboxDispatcher':
                        if guards or closes:raise ValueError('expected existing unreturned setup defect changes unexpectedly')
                        kind='AFFECTED_BUG1567_UNRETURNED_SETUP'
                    elif short=='BootstrapAdminMain':
                        if 'getConnection:'in body or 'ConnectionProvider.open:'in body:raise ValueError('borrowed boundary cannot silently acquire a connection')
                        kind='NONAPPLICABLE_BORROWED_CONNECTION_CALLER_OWNS'
                    elif short=='RevocationRetryCoordinator':
                        if not guards or not closes or 'Method preserveFatal:'not in body:raise ValueError('explicit error-state then close before result/fatal')
                        kind='NONAPPLICABLE_EXPLICIT_ERROR_CAPTURE_AND_OWNED_CLOSE'
                    else:
                        if not guards or not(closes or helper):raise ValueError('owned setup protection '+name+' '+method+' edges='+str(covering)+' closes='+str(closes))
                        kind='NONAPPLICABLE_EXISTING_TWR_OR_FINALLY_PROTECTION'
                    actual.append(dict(method=method,setAutoCommitOffset=at,errorProtectedEdges=guards,
                        ownedCloseOffsets=closes,explicitCloseHelper=helper,classification=kind))
            if len(actual)!=source_sites[module+':'+name.rsplit('.',1)[1]]:raise ValueError('all lexical setup sites resolved in original methods')
            facts.append(dict(owner=module+':'+name,path=path,sourceSha256=sha(ROOT/path),jarSha256=sha(jar),sites=actual))
    if len(facts)!=19 or sum(len(v['sites'])for v in facts)!=21:raise ValueError('all19 owners/all21 methods')
    value=dict(actualExit=0,source=source,qualificationSha256=sha(qp),owners=facts,ownerCount=19,setupSites=21,
        affectedOwners=['api:api.messaging.outbound.OutboxDispatcher'],additionalAffectedOwners=[],
        scope='STATIC_ORIGINAL_JVM_FOR_UNRETURNED_SETUP_ERROR_ONLY_NOT_ALL_COMPOUND_FAILURES',
        jdbcCallsExecuted=0,testsExecuted=0,vmActions=0,newAcceptedLeaves=0,formalAccepted=False,
        residual=['BUG1567 direct target not yet reproduced/fixed','normal regression and new fault matrix still required',
            'TWR/other finally compound exception identity is outside this narrow non-returned setup gap and remains existing broader ledgers'])
    os.umask(0o077);out=BASE/'PG6262-jdbc-setup-scope-v1';out.mkdir()
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,owners=19,setupSites=21,affectedOwners=value['affectedOwners'],manifestSha256=sha(out/'manifest.json'))))


if __name__=='__main__':main()
