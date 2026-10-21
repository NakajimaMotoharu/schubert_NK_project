"""Current ordinary diagnostic review and original-XML join; raw warnings/holds retained."""
import copy
import json
import os
import subprocess
import sys
from collections import Counter
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg5910_storage_static_rebind import ordered_pairs,SEMANTIC
from static_disposition_overlay import load,validate_rationales
from pg6638_current115_receivers import read_whole,body_at
from pg6282_current4040_static_join import current_reference

OLD='f39de2986cbe0dc4a552f64d55ac723002cc77f6'
PRIOR=BASE/'PG6528-current4073-static-join-v1/manifest.json'
CONTEXTS={
 'UserMutationApplicationService':'Owned mutation rollback/close, Temp graph before catalog; existing admin mutation result unchanged.',
 'UserQueryApplicationService':'Owned read rollback/close and Temp graph before catalog; USER/ADMIN scope unchanged.',
 'LogQueryApplicationService':'Owned log query rollback/close and Temp graph before fixed catalog; selection/order unchanged.',
 'MediaApplicationService':'Owned media transaction/rollback/close and Temp graph before catalog; file/Range contract unchanged.',
 'QuestionCommandService':'Temp graph before command persistence catalog; business result/token rules unchanged.',
 'QuestionMutationApplicationService':'Owned mutation rollback/close and Temp graph; token/replay/notification contract unchanged.',
 'QuestionQueryApplicationService':'Owned query rollback/close and Temp graph before catalog; owner/results unchanged.',
 'QuestionSubmissionService':'Owned submission transaction/rollback and Temp guard before SQLstate23505; bounded existing cancellation wait, no thread creation.',
 'QuestionWorkerService':'Owned worker transaction/rollback and Temp guard before catalog; existing cancellation flag/interrupt observation, no new thread.',
 'ScenarioApplicationService':'Owned Scenario transaction/rollback/close and Temp graph before catalog; row/media/result ordering unchanged.',
 'ApiDependencyReadiness':'SS330 DB/JMS one owned close, legacy primary/direct-close table, then ApiStartup graph before false/catalog; no real deployment probe.',
 'JdbcSyncRequestProcessor':'Owned request transaction rollback/close and Temp graph before rejection/reply classification; commit/ACK contract unchanged.',
 'TemporaryInfrastructureException':'Pure finite identity graph and secondary attachment, no I/O/provider material retained in new catalog.',
 'WebLogIngestService':'Owned log-ingest transaction/rollback/close and Temp graph before SQLstate23505/catalog; no duplicate business execution.',
 'InboxCleanup':'Owned cleanup transaction rollback only before commit, shared Temp attachment and final graph before catalog.',
 'InspectorDatabaseConnections':'Unreturned admission failure owns one close and shared Temp final classification; success connection remains caller-owned.',
 'OutboxDispatcher':'SS320322 owned JDBC rollback/close and direct-error table, final graph before mark/retry; SQL result/lease unchanged.',
 'OutboxJmsSender':'SS320322330 one owned JMS close, deferred typed graph carrier and fatal check before duplicate; suppressed is never duplicate evidence.',
 'QuestionQueryRepository':'Borrowed connection is never closed here; pure Temp graph before query catalog, known input/layout constraints unchanged.',
 'WebDependencyReadiness':'SS330 DB/JMS one owned close, legacy primary/direct-close table, then WebStartup graph before ordinary startup catalog.',
 'WebStartupException':'Pure module-local finite identity graph/secondary attachment; no startup I/O or privilege issuance.',
 'WebLogDispatcher':'SS323 owned rollback/remaining close and old component direct-error table before final graph/failed-cycle metric.',
 'WebLogMessageSender':'SS321323330 authenticated input then one JMS close; fatal-before-duplicate and typed carrier to existing dispatcher; plaintext finally wipe.',
 'WebRequestLogProducer':'SQL projection rollback/TWR close and Session graph before explicit FAILED projection; local sink callback semantics held separately.',
 'ArtemisRequestSender':'SS321330 one owned JMS close, deferred rollback graph, public final classifier only after cleanup; TTL/metadata/body unchanged.',
 'ReceiptReferenceRepository':'Approved manual row/statement/connection replace table; both-SQL fatal graph before discard, unknown-primary marker/direct-primary priority retained.',
 'RevocationRetryCoordinator':'Captured failure, rollback/combine protected by remaining-close finally, then final graph; lease/backoff/token unchanged.',
 'EncryptedWebSessionRepository':'Session graph before catalog and qualified secondary attachment within outer TWR; session/CSRF/crypto contract unchanged.'}
RULE_REASONS={
 'AvoidCatchingGenericException':'Runtime/Error handling is required at this owned-resource or catalog boundary; transient Error graphs are preserved, not accepted as ordinary success/retry.',
 'DoNotUseThreads':'This site observes current-thread interruption/cancellation in the bounded existing worker/wait contract, not an unmanaged thread creation.',
 'AvoidInstanceofChecksInCatchClause':'The type check implements the approved direct-primary/direct-cleanup or SQLstate23505 discriminator; replacing it with ordinary flattening would change fault semantics.',
 'CompareObjectsWithEquals':'Throwable reference identity is required for same-object/self-suppression and direct-fatal precedence; equals is not Throwable graph identity.',
 'DoNotThrowExceptionInFinally':'Owned resource close must run once and may report the approved selected failure; the explicit primary/secondary table prevents accidental masking. No normal result is fabricated.'}
SUPPLEMENT={
 'InboxCleanup':['api.maintenance.InboxCleanupNonAuthenticationTest','api.maintenance.AuthenticationInboxCleanupTest','api.maintenance.QuestionQueryInboxCleanupTest'],
 'JdbcSyncRequestProcessor':['api.dispatch.JdbcTransactionBoundary329Test','api.dispatch.JdbcTransactionFatal329Test','api.dispatch.JdbcRollbackAttachment330Test'],
 'TemporaryInfrastructureException':['api.error.TemporaryFailureGraph329Test','api.error.ApiStartupGraph330Test'],
 'WebStartupException':['web.bootstrap.WebStartupGraph330Test'],
 'ApiDependencyReadiness':['api.dispatch.ApiReadinessFailureGraph330Test'],
 'WebDependencyReadiness':['web.bootstrap.WebReadinessFailureGraph330Test'],
 'OutboxJmsSender':['api.messaging.outbound.OutboxSecondary330Test','api.messaging.outbound.OutboxFailureOwnershipTest'],
 'WebLogMessageSender':['web.logging.JmsSecondary330Test'],
 'ArtemisRequestSender':['web.logging.JmsSecondary330Test'],
 'WebLogDispatcher':['web.logging.WebOwnedAttachment329Test'],
 'WebRequestLogProducer':['web.logging.RequestProjectionFailureGraph329Test'],
 'ReceiptReferenceRepository':['web.receipt.ReceiptFailureGraph329Test'],
 'RevocationRetryCoordinator':['web.logging.WebOwnedAttachment329Test','web.revocation.RevocationJdbcGraph328Test'],
 'EncryptedWebSessionRepository':['web.session.SessionRollbackAttachment329Test','web.session.SessionJdbcGraph328Test'],
 'InspectorDatabaseConnections':['api.maintenance.InspectorFailureGraph329Test']}


def review_changed(row):
    path=row['sourcePath'];name=path.rsplit('/',1)[-1].removesuffix('.java')
    if name not in CONTEXTS:raise ValueError('explicit reviewed changed-source context only')
    text=(ROOT/path).read_text();lines=text.splitlines();line=int(row['beginline'])
    rule=row['rule'];scope=' | '.join(lines[max(0,line-2):min(len(lines),int(row['endline'])+2)])
    value=dict(row)
    if rule in ('AvoidCatchingGenericException','EmptyCatchBlock'):
        body=body_at(text,line);words=[word for word,_ in body]
        if name=='WebRequestLogProducer' and (not words or '"request audit terminal signal failed"' in words):
            value.update(reason='Local primitive sink/terminal callback graph applicability requires separate PG review. No current exception approval or successful dynamic check inferred.',
                         reviewHold='LOCAL_SINK_GRAPH_APPLICABILITY_PENDING',reviewedSourceSnippet=scope)
            return value
        if rule=='EmptyCatchBlock' or not any(w in words for w in ('throw','rollback','preserveFatal','attachSecondary','closeAfterSetupFailure','close','primary','failure','failedCycles')):
            raise ValueError('unexplained catch cannot be automatically approved')
    if rule not in RULE_REASONS:raise ValueError('new diagnostic rule requires individual review')
    value.update(status='REQUIRED_CONTRACT',reason=CONTEXTS[name]+' '+RULE_REASONS[rule],
                 reviewedSourceSnippet=scope,rawWarningRetained=True,ptAlternativeCompleted=0,
                 reviewMethod='CURRENT_EXACT_SOURCE_SPAN_AND_COMPONENT_CONTRACT',formalAccepted=False)
    return value


def original_refs(value,cases,source):
    if value['status']=='NOT_REVIEWED_CURRENT_SOURCE':return value
    result=copy.deepcopy(value);refs=[]
    if value.get('priorCurrentRefs') is not None:
        index={(r['class'],r['caseNameSha256']):r for r in cases}
        for ref in value['priorCurrentRefs']:
            match=index.get((ref['class'],ref['caseNameSha256']))
            if match is None:raise ValueError('all prior semantic case identities require current original XML')
            refs.append(current_reference(match))
    else:
        name=value['sourcePath'].rsplit('/',1)[1].removesuffix('.java')
        direct=value['sourcePath'].split('/src/main/java/')[1][:-5].replace('/','.')+'Test'
        names={direct}|{'dev.codex.schubert.nk.'+s for s in SUPPLEMENT.get(name,[])}
        refs=[current_reference(r) for r in cases if r['class'] in names]
    context=value.get('staticContextPremiseOnly') is True
    if not refs and not context:raise ValueError('no arbitrary empty current-case binding')
    if any(r['source']!=source for r in refs):raise ValueError('same-source actual references only')
    result.update(currentWholeCaseRefs=refs,currentWholeSource=source,currentWholeJoinPending=False,
                  perTestFaultCausalityProved=False,historicalSuccessImported=False,formalAccepted=False,F03Accepted=False)
    result.pop('priorCurrentRefs',None)
    return result


def rebind_unchanged(row,previous):
    # BUG1599/YKT1352: the full per-file semantic sequence is paired upstream.
    # PMD2 IDs include global XML ordinal, which may change in an unchanged file.
    if any(previous[key]!=row[key] for key in SEMANTIC):
        raise ValueError('all original source/coordinates/rule/message/schema semantics exact')
    value=copy.deepcopy(previous)
    value.update({key:item for key,item in row.items() if key!='status'})
    value.update(priorReviewSource=OLD,priorReviewManifestSha256=sha(PRIOR),
                 priorFindingId=previous['findingId'],priorRawXmlOrdinal=previous['rawXmlOrdinal'],
                 diagnosticIdentityMapping='EXACT_ENTIRE_SOURCE_DIAGNOSTIC_SEQUENCE_CURRENT_RAW_ID_RETAINED',
                 priorCurrentRefs=previous.get('currentWholeCaseRefs',[]))
    return value


def main():
    qp,q,cases=read_whole();source=q['productionSource']
    prior=load(PRIOR,sha(PRIOR),OLD)
    sp=BASE/'PG6632-jms-secondary-qualification-v1/manifest.json'
    if sha(sp)!='12b0ae457468b7c9c52d4e2ad10da8daf6084f962ffb084236c78fa76db55f87':raise ValueError('current raw static qualification')
    selected=json.loads(sp.read_bytes());pp=W/'pg6632-jms-secondary-qualification-v1/manifest.safe.json'
    rp=pp.with_name('findings.safe.json');proof=json.loads(pp.read_bytes())
    if not(selected['source']==proof['source']==source and sha(pp)==selected['privateManifestSha256']
           and sha(rp)==selected['findingsSha256'] and proof['allSourceHashes']==q['allSourceHashes']
           and proof['allPhysicalMainSha256']==q['allPhysicalMainSha256']):raise ValueError('all8511667 original static/whole physical bytes identical')
    raw=json.loads(rp.read_bytes());pairs=ordered_pairs(prior,raw)
    if len(raw)!=1404 or len(pairs)!=1186:raise ValueError('exact full current raw and1186 entire-file identity matches')
    result=[];counts=Counter()
    for row in raw:
        if row['sourceSha256']!=q['allSourceHashes'][row['sourcePath']]:raise ValueError('each raw source hash')
        pair=pairs.get(row['findingId'])
        if pair is None:
            value=review_changed(row);counts['changedCurrentSourceReviewedOrHeld']+=1
        else:
            value=rebind_unchanged(row,pair[0])
            counts['unchangedPriorHeld' if value['status']=='NOT_REVIEWED_CURRENT_SOURCE' else 'exactCurrentSourceRationaleReauthenticated']+=1
        value=original_refs(value,cases,source)
        if value['status']!='NOT_REVIEWED_CURRENT_SOURCE':
            value.update(currentWholeQualificationSha256=sha(qp),currentWholeCasesSha256=sha(qp.with_name('cases.json')))
        result.append(value)
    if [r['findingId'] for r in raw]!=[r['findingId'] for r in result]:raise ValueError('all raw IDs/order retained')
    validate_rationales(result)
    out=BASE/'PG6640-current4158-static-join-v1';os.umask(0o077);out.mkdir()
    with (out/'findings.json').open('x') as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value=dict(actualExit=0,source=source,rawFindings=1404,inventoryFile='findings.json',inventorySha256=sha(out/'findings.json'),
        statusCounts=dict(Counter(r['status'] for r in result)),joined=dict(counts),priorManifestSha256=sha(PRIOR),
        currentWholeQualificationSha256=sha(qp),currentWholeCasesSha256=sha(qp.with_name('cases.json')),
        testsExecuted=0,pmdRawRemoved=0,checkstyleFindings=0,formalAccepted=False,F03Accepted=False,
        ptAlternativeCompleted=0,vmActions=0,newAcceptedLeaves=0,effortPercent=None,
        readerAttempt=2,priorReaderFailure='BUG-1599/session43398/ValueError/no public artifact; no PT replay',
        operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        operatorBranch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
        toolSha256=sha(ROOT/'tools/quality/pg6640_current4158_static_join.py'),pythonVersion=sys.version.split()[0],
        command='python3 -B tools/quality/pg6640_current4158_static_join.py',wholeReplayed=False,additionalBuildsIssued=0)
    with (out/'manifest.json').open('x') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,statusCounts=value['statusCounts'],manifestSha256=sha(out/'manifest.json'))))


if __name__=='__main__':main()
