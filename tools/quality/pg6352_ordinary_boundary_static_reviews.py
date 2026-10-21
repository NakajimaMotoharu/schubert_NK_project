"""21 individually read ordinary boundaries; existing original4048 references, no PT invocation."""
import json
import hashlib
import os
import subprocess
from pathlib import Path
from collections import Counter
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6334_current4048_trace import SOURCE, read_qualified
from pg5958_private_lock_reason_review import fragment
from static_disposition_overlay import load, apply_decisions

INPUT = BASE/'PG6340-current4048-static-join-v1/manifest.json'
INPUT_SHA = '2af4fda6c43d3ed629d61ee9d75315370a14a285f7f5385d164de6b466671bef'
G = 'AvoidCatchingGenericException'
SPEC = {
    'ApiNativeCodecs': {(87, G): (2, 'Both Runtime/Error factory failures close only already-created local codec children and rethrow; finally wipes each acquired key copy. The key source remains borrowed. These fixed codec implementations and synthetic fixture checks do not certify real credentials or every arbitrary failing child close.')},
    'WebNativeCodecs': {(85, G): (2, 'Both Runtime/Error factory failures close created log/session codecs before rethrow; all three acquired copies are wiped by finally, including missing/invalid later-purpose failures. Successful returned owner alone retains children. This source review does not read actual keys or prove native admission.')},
    'JdbcSyncRequestProcessor': {
        (44, G): (1, 'SQL/RTE inside the owned short transaction attempts rollback before rethrow and TWR close. Handler response cannot escape before commit/close. An attached rollback SQL failure prevents permanent rejection from being treated as confirmed. Arbitrary compound provider graphs remain YKT1323, not blanket accepted.'),
        (56, G): (1, 'Outer SQL/RTE, including uncertain commit/close, becomes a fixed infrastructure retry signal, never a reply or automatic JDBC retry. The explicit PermanentProtocolException branch only preserves a clean permanent rejection; no provider text is emitted.')},
    'WebLogIngestService': {(55, G): (1, 'Projection insert/commit SQL/RTE attempts rollback, retains rollback SQL failure, and rethrows through owned connection close before JMS ACK owner returns. Duplicate source_message_id leaves original columns unchanged. This is not proof that arbitrary compound rollback/close graphs satisfy every fatal-ranking contract.')},
    'InboxCleanup': {
        (207, G): (1, 'Before commit, bounded owned-work SQL/RTE attempts rollback; after committed=true a late parent failure is not falsely rolled back. Transaction verification and parent checks precede commit; owned connection closes before a value escapes.'),
        (217, G): (1, 'Outer SQL/RTE emits only fixed InboxMaintenanceException, stripping bound values and unknown commit diagnostics. A fixed failure is not a successful durable inspection cursor or permission to repeat a committed mutation. No actual maintenance is performed by this review.')},
    'ContextHash': {(24, 'AvoidSynchronizedStatement'): (1, 'Private stateLock serializes the non-thread-safe retained MessageDigest across input ASCII conversion, digest and both finally wipes. No caller monitor is used; the returned hex is a repository lookup value, not logged raw authentication context. Independent hash vectors/concurrency are associated below, not new credential access.')},
    'ScenarioReadyFileInspector': {(42, G): (1, 'Outer StorageIo/RTE maps root capability or cleanup uncertainty to UNAVAILABLE. Only typed MISSING before entering the specific date/entry handle may become absence; opened/verified resource close failure cannot become PRESENT or clean MISSING. No mutation or real transfer file is inspected here.')},
    'WebRequestLogProducer': {
        (199, G): (1, 'The best-effort projection boundary marks a previously emitted local request record FAILED with fixed code, never treats encrypted enqueue/commit failure as successful projection. Wire is wiped in finally. This applicability reason does not promote arbitrary nested fatal provider policy to accepted; YKT1323 remains open.'),
        (271, G): (2, 'Both RTE/Error transaction-body spans attempt rollback and still close the owned connection before propagation. Direct Error is not consumed by the outer SQL/RTE projection catch. Null constructor/trace contracts are checked outside that best-effort scope.'),
        (274, G): (1, 'Rollback RTE becomes a distinct suppressed secondary on the body primary, guarded against self-suppression. It is not a successful enqueue or release of an unconfirmed transaction; the original proceeds through TWR cleanup.'),
        (276, G): (1, 'Rollback Error is rethrown as the same fatal object, with original failure attached only when identity differs; owned connection still closes through TWR. This does not claim a real rollback or physical resource release from source inspection.')},
    'ArtemisReplyConsumer': {
        (44, G): (1, 'Receive/decode/correlate/commit JMS/RTE failure calls rollback on the caller-borrowed transacted context and rethrows. A returned waiter completion requires actual commit; this consumer neither opens nor closes that shared context.'),
        (55, G): (1, 'DLQ-isolation JMS/RTE failure retains distinct protocol primary and attempts rollback. Failed rollback becomes FailedJmsIsolationException, not CommittedFatalReplyException/ACK. Actual DLQ send is not issued in this review.'),
        (71, G): (1, 'Rollback RTE retains distinct secondary and throws UnconfirmedJmsRollbackException; self-suppression is guarded. The caller cannot infer confirmed rollback or commit, and remains owner of its context.')},
    'InternalErrorDispatchRouter': {(35, G): (1, 'Error-filter init Servlet/RTE failure attempts errors.destroy and always business.destroy in finally, then fails rather than accepting initialized routing. Cleanup failure may replace init failure but is never successful init. Internal ERROR routing remains separate from business authorization, and thread security context always clears in doFilter.')},
    'JdbcWebSessionStore': {(60, G): (1, 'SQL/RTE findLocked failure preserves fatal cause/suppressed identity graph then emits only fixed SessionStoreException. A malformed row becomes deletable InvalidSessionRowException only after both owned JDBC resources close cleanly; the connection/transaction stays borrowed. Provider-linked graphs outside this helper contract are not globally certified.')}
}
TESTS = {
    'ApiNativeCodecs': ['api.bootstrap.ApiNativeCodecsTest'],
    'WebNativeCodecs': ['web.bootstrap.WebNativeCodecsTest'],
    'JdbcSyncRequestProcessor': ['api.security.LoginInboxServiceTest'],
    'WebLogIngestService': ['api.logging.WebLogIngestServiceTest'],
    'InboxCleanup': ['api.maintenance.InboxCleanupNonAuthenticationTest', 'api.maintenance.AuthenticationInboxCleanupTest', 'api.maintenance.QuestionQueryInboxCleanupTest'],
    'ContextHash': ['api.security.ContextHashTest'],
    'ScenarioReadyFileInspector': ['api.storage.ScenarioReadyFileInspectorTest'],
    'WebRequestLogProducer': ['web.logging.WebRequestLogProducerTest'],
    'ArtemisReplyConsumer': ['web.messaging.ArtemisReplyConsumerTest'],
    'InternalErrorDispatchRouter': ['web.session.ErrorMvcTest'],
    'JdbcWebSessionStore': ['web.logging.JdbcWebSessionStoreTest']
}


def calculate():
    qp, _ = read_qualified()
    if sha(qp) != '2b57d476af5f0d0e29c9b706220ba2f0c54ac8d2c4c22aac0685f45da14598d3':
        raise ValueError('immutable original4048 proof')
    rows = load(INPUT, INPUT_SHA, SOURCE)
    cp = qp.with_name('cases.json'); cases = json.loads(cp.read_bytes())
    pp = W/'pg6326-web-graph-qualification-v1/manifest.safe.json'
    public = json.loads((BASE/'PG6326-web-graph-qualification-v1/manifest.json').read_bytes())
    if sha(pp) != public['privateManifestSha256']:
        raise ValueError('original all8511667 physical proof')
    proof = json.loads(pp.read_bytes()); found = Counter(); decisions = []
    for row in rows:
        name = Path(row['sourcePath']).stem; key = (int(row['beginline']), row['rule'])
        if name not in SPEC or key not in SPEC[name]:
            continue
        count, reason = SPEC[name][key]; found[(name, key)] += 1
        path = ROOT/row['sourcePath']
        if row['status'] != 'NOT_REVIEWED_CURRENT_SOURCE' or sha(path) != row['sourceSha256'] or sha(path) != proof['allSourceHashes'][row['sourcePath']]:
            raise ValueError('exact still-unreviewed source identity')
        module = row['sourcePath'].split('/')[1].removeprefix('schubert-nk-')
        prefix = module+':'+row['sourcePath'].split('/src/main/java/')[1][:-5]
        family = {k: v for k, v in proof['allPhysicalMainSha256'].items() if k == prefix+'.class' or k.startswith(prefix+'$')}
        if not family:
            raise ValueError('actual physical owner family')
        refs = []
        if not TESTS[name]:
            raise ValueError('explicit semantic Test required')
        for short in TESTS[name]:
            cls = 'dev.codex.schubert.nk.'+short
            test = Path('src/schubert-nk-'+module+'/src/test/java')/(cls.replace('.', '/')+'.java')
            committed = subprocess.check_output(['git', 'show', SOURCE+':'+test.as_posix()], cwd=ROOT)
            if sha(ROOT/test) != hashlib.sha256(committed).hexdigest():
                raise ValueError('do not transfer old success to changed Test')
            matches = [c for c in cases if c['class'] == cls]
            if not matches or any(c['result'] != 'PASS_ORIGINAL_XML' or c['source'] != SOURCE for c in matches):
                raise ValueError('actual matching same-source semantic cases')
            refs.extend({k: c[k] for k in ('source', 'class', 'testId', 'caseNameSha256', 'xmlSha256')} for c in matches)
        decisions.append(dict(row, source=SOURCE, status='REQUIRED_CONTRACT', reason=reason,
            diagnosticFragment=fragment(path.read_text(), row), rawWarningRetained=True,
            owningPhysicalClassHashes=family, currentWholeCaseRefs=refs, currentWholeJoinPending=False,
            actualRuntimeProven=False, formalAccepted=False, F03Accepted=False, ptAlternativeCompleted=0,
            reviewScope='SOURCE_APPLICABILITY_WITH_ASSOCIATED_CASES_NOT_EVERY_BRANCH_OR_REAL_RUNTIME'))
    if found != Counter({(name, key): value[0] for name, sites in SPEC.items() for key, value in sites.items()}) or len(decisions) != 21:
        raise ValueError('all21 explicitly read span multiplicities')
    updated = apply_decisions(rows, decisions)
    return decisions, dict(actualExit=0, source=SOURCE, baseManifestPath=INPUT.relative_to(ROOT).as_posix(),
        baseManifestSha256=INPUT_SHA, rawFindings=1356, statusCounts=dict(Counter(r['status'] for r in updated)),
        reviewed=21, pmdRawRemoved=0, testsExecuted=0, additionalBuildsIssued=0,
        currentWholeQualificationSha256=sha(qp), currentWholeCasesSha256=sha(cp),
        newAcceptedLeaves=0, formalAccepted=False, F03Accepted=False, ptAlternativeCompleted=0, effortPercent=None,
        unresolved=['14 old missing semantic bindings retained', '296 other unreviewed spans',
                    'YKT1323 arbitrary compound application graphs and real runtime safety remain unaccepted',
                    'original sourceaed review is not new3deda whole/native qualification'])


def main():
    rows, value = calculate(); os.umask(0o077); out = BASE/'PG6352-ordinary-boundary-static-review-v1'; out.mkdir()
    for name, item in (('decisions.json', rows), ('manifest.json', value)):
        if name == 'manifest.json':
            value['decisionsSha256'] = sha(out/'decisions.json')
        with (out/name).open('x') as f:
            json.dump(item, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, reviewed=21, statusCounts=value['statusCounts'], manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
