"""Explicit per-site JMS applicability review; whole/PT dependency remains pending."""
import json
import os
from collections import Counter
from pathlib import Path
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6082_web_factory_qualification import SOURCE
from pg5958_private_lock_reason_review import fragment
from pg5966_api_sql_selected import source_test_names

# Each line names a reviewed handler/state role, not a blanket catch/type exemption.
SITES = {
 'ApiMessagingRuntime': {
  116: 'assembly startup owns every registered group; notification and reverse cleanup run before fixed failure/retained fatal escape',
  120: 'notification failure preserves primary unless Error replaces a non-Error; a distinct failure is suppressed once',
  121: 'notification Error/non-Error discrimination preserves the declared fatal priority,not success',
  125: 'notification/failure identity prevents illegal self-suppression,not value comparison',
  129: 'cleanup wrapper is unpacked once; retained Error has priority and unknown cleanup never becomes normal',
  133: 'Error is direct; non-Error cleanup has a required nonnull first group cause; only fatal cleanup replaces nonfatal primary',
  135: 'cleanup/retained Throwable identity prevents self-suppression',
  161: 'reverse group close continues across every Exception/Error and retains fatal preference; close count/owner remain bounded',
  162: 'group cleanup Error has priority over the first non-Error; accumulated nonfatal outcome remains a fixed failure',
  164: 'closing/failure identity excludes self-suppression across group cleanup'},
 'QuestionWorkConsumers': {
  42: 'context is the identical already captured result.context; owner closes it on startup failure and ordinary stop',
  47: 'consumer is a child of the dedicated JMSContext; context owner closes all session children,not a separately published owner',
  62: 'unconfirmed isolation/rollback and Error mark halted/terminal and notify fatal stop; never ACK/reopen transaction',
  65: 'only actual Error requires the best-effort rollback before fatal stop notification',
  68: 'rollback failure cannot reverse already halted/terminal state; no ACK or provider diagnostic publication; fatal notification still follows',
  73: 'the listener propagates retryable failures only after confirmed rollback; broker delivery metadata/max4 govern retry,not local ACK',
  79: 'startup failure owns the context; notification and one owned close preserve declared primary/fatal priority',
  83: 'notification failure participates in primary/fatal retention,not normal retry',
  84: 'fatal notification replaces only a non-Error primary; Error/Error and nonfatal combinations retain primary',
  88: 'notification/failure exact identity is necessary before addSuppressed',
  92: 'startup cleanup is attempted once after notification even on failure,then retained failure escapes',
  93: 'Error cleanup replaces only non-Error retained startup failure',
  94: 'closing/retained exact identity prevents self-suppression',
  118: 'ordinary close RuntimeException remains fixed close failure,closed state does not assert success'},
 'WebLogConsumers': {
  25: 'ready reads closed without a lock; volatile publishes the owner stop write to observation thread; it does not make compound close atomic',
  50: 'opened is the identical runtime.context already captured before setup; startup/ordinary owner closes that context',
  56: 'consumer is owned by the transacted JMSContext; closing that context closes session children',
  71: 'fatal isolation/rollback/Error halts further delivery and signals fatal stop; no ACK or ordinary success',
  74: 'actual Error selects best-effort rollback before fatal notification',
  77: 'failed rollback stays unconfirmed/fatal; halted/terminal already set and fatal notification follows,without ACK/provider text',
  82: 'only confirmed-rollback listener failure reaches broker-owned redelivery; there is no manual ACK/reopen',
  88: 'startup captures primary,notifies fatal and closes already owned context before fixed failure or retained Error escape',
  92: 'notification failure is retained according to fatal priority,never treated as successful startup',
  93: 'only Error notification replaces non-Error startup failure; both Error retains primary',
  97: 'notification/failure identity excludes self-suppression',
  101: 'owned context cleanup is attempted after notification; cleanup cannot turn startup failure into success',
  102: 'Error cleanup replaces non-Error retained failure; otherwise retain original failure',
  103: 'closing/retained identity excludes self-suppression',
  127: 'ordinary close RuntimeException is a fixed failed-close outcome,not normal retry or success'},
 'ArtemisReplyConsumers': {
  24: 'ready reads stopping outside the start/close lock; volatile publishes stop admission state without pretending atomic compound updates',
  26: 'ready reads started outside the start lock; volatile publishes completed delivery-start state',
  57: 'startup failure closes the already bound runtime,retains distinct secondary and traverses transient fatal graph before fixed failure',
  60: 'startup cleanup failure is retained once; SessionStoreException.preserveFatal visits cause/suppressed by identity and preserves fatal outcome',
  61: 'failure/closing exact identity prevents self-suppression; equals is not Throwable identity',
  90: 'opened aliases final context acquired by bind; caller/runtime retains ownership before listener setup',
  95: 'consumer is a JMSContext child and is closed by that session owner; no separate ownership transfer',
  110: 'fatal isolation/rollback/Error marks halted/terminal and signals stop; actual Error is rethrown after notification',
  113: 'only actual Error selects rollback; isolated/unconfirmed failures are already terminal',
  116: 'best-effort rollback failure is not ACK or success; terminal state remains and fatal signal/rethrow follow',
  121: 'actual callback Error is rethrown after notification,not swallowed as retryable',
  122: 'only confirmed rollback reaches broker-owned redelivery; no manual ACK on retryable failure',
  149: 'close failure preserves transient fatal graph and fixed failure; closed becomes true only after close success,so caller may retry owned close'},
 'WebBrokerContexts': {
  50: 'configured factory transfers by exactly two same-reference final stores to prepared owner; real JVM has no post-acquire allocation/callback',
  94: 'all twelve settings are inside immediate typed ownership protection; one close then same primary except approved fatal cleanup priority',
  97: 'one configuration-failure close is protected independently; retain primary/secondary without self-suppression',
  98: 'close Error replaces only non-Error primary; both Error retains primary,other close is suppressed once',
  102: 'secondary/primary exact Throwable identity prevents self-suppression',
  125: 'credential supplier RuntimeException becomes a fixed unavailable outcome without retaining provider text; no credential copy was acquired',
  134: 'context creation RuntimeException becomes fixed unavailable; finally erases acquired password copy and outer finally unlocks',
  152: 'live close Exception preserves fatal graph and fixed outcome; closed is committed only after actual close success for owned retry'}
}
TEST_CLASSES = {
 'QuestionWorkConsumers': ['api.messaging.inbound.QuestionWorkConsumersTest'],
 'WebLogConsumers': ['api.messaging.inbound.WebLogConsumersTest'],
 'ApiMessagingRuntime': ['api.messaging.inbound.ApiMessagingRuntimeTest'],
 'ArtemisReplyConsumers': ['web.messaging.ArtemisReplyConsumersTest'],
 'WebBrokerContexts': ['web.messaging.WebBrokerContextsTest', 'web.messaging.WebBrokerFactoryOwnershipTest',
                       'api.file.WebBrokerContextsCredentialTest']}


def site_role(name, line, rule):
    if name == 'ArtemisReplyConsumers' and line == 23 and rule == 'AvoidUsingVolatile':
        return None  # Every closed access is under stateLock; necessity is not established.
    return SITES.get(name, {}).get(line)


def main():
    qp = BASE/'PG6082-web-factory-qualification-v1/manifest.json'
    if sha(qp) != '134e8181764a40b725fd0fa9365f5d18fa714b66221e4f46b992d3f84cd7e735':
        raise ValueError('actual source870925/static inputs')
    q = json.loads(qp.read_bytes()); folder = W/'pg6082-web-factory-qualification-v1'
    for name, key in (('manifest.safe.json', 'privateManifestSha256'), ('cases.safe.json', 'casesSha256'), ('findings.safe.json', 'findingsSha256')):
        if sha(folder/name) != q[key]:
            raise ValueError('immutable original artifact/static receipt')
    typed = {}
    for name, wanted in (('pg6094-jms-catch-facts-v1', '9e3c38f0eba7fcdda01cb53a4e4b83ea11b2876320f652bc5095bb95591af0f1'),
                         ('pg6096-jms-reference-facts-v1', '2fc6510396459911f3199639b34e61a41b021ae1cbac41b55a7915d459556fd1')):
        path = W/name/'manifest.safe.json'
        if sha(path) != wanted:
            raise ValueError('fresh exact source870 resolved symbols')
        data = json.loads(path.read_bytes())
        if data['actualExit'] != 0 or data['source'] != SOURCE or data['identity']['sourceHashes'] != json.loads((folder/'manifest.safe.json').read_bytes())['allSourceHashes']:
            raise ValueError('all851 current source/type inputs')
        typed[name] = data['rows']
    catch = typed['pg6094-jms-catch-facts-v1']; refs = typed['pg6096-jms-reference-facts-v1']
    rows = json.loads((folder/'findings.safe.json').read_bytes()); reviews, held = [], []
    for row in rows:
        name = Path(row['sourcePath']).stem
        if name not in SITES:
            continue
        path = ROOT/row['sourcePath']; text = path.read_text(); token = fragment(text, row).strip()
        if sha(path) != row['sourceSha256']:
            raise ValueError('exact current individual diagnostic source bytes')
        line = int(row['beginline']); role = site_role(name, line, row['rule'])
        if role is None:
            held.append(dict(findingId=row['findingId'], sourcePath=row['sourcePath'], line=line, reason='NECESSITY_UNRESOLVED_LOCKED_CLOSED_VOLATILE'))
            continue
        types = [v for v in catch if v['path'] == row['sourcePath'] and v['firstLine'] == row['beginline']]
        if row['rule'] in ('AvoidCatchingGenericException', 'EmptyCatchBlock') and len(types) != 1:
            raise ValueError('each catch diagnostic resolves to one actual bounded catch parameter')
        if row['rule'] == 'CompareObjectsWithEquals':
            resolved = [v for v in refs if v['path'] == row['sourcePath'] and v['firstLine'] == row['beginline']]
            if len(resolved) != 1 or any(resolved[0][k] != 'java.lang.Throwable' for k in ('leftType', 'rightType')) or resolved[0]['operator'] != 'NOT_EQUAL_TO':
                raise ValueError('current identity site has actual Throwable operands,not equals based on spelling')
            if resolved[0]['leftExpression']+' != '+resolved[0]['rightExpression'] not in token:
                raise ValueError('exact independently resolved identity expression')
        declared = []
        for cls in TEST_CLASSES[name]:
            module = 'api' if name in ('QuestionWorkConsumers', 'WebLogConsumers', 'ApiMessagingRuntime') else 'web'
            full = 'dev.codex.schubert.nk.'+cls
            test = ROOT/('src/schubert-nk-'+module+'/src/test/java')/(full.replace('.', '/')+'.java')
            declared.append(dict(className=full, module=module, sourceSha256=sha(test), methods=sorted(source_test_names(test))))
        reviews.append(dict(row, source=SOURCE, status='FALSE_POSITIVE' if row['rule'] == 'CloseResource' else 'REQUIRED_CONTRACT',
            reason='1279 individual PG review; SS312321342343354/SSC311: '+role+'. Independent fixture/oracle references are declared below; actual whole XML join remains pending.',
            diagnosticFragment=token, reviewSpec='018/1279', rawWarningRetained=True,
            implementationReviewedNoChangeRequired=True, staticContextPremiseOnly=False,
            declaredIndependentTests=declared, typedCatchFacts=types, currentWholeCaseRefs=[], currentWholeJoinPending=True,
            formalAccepted=False, ptAlternativeCompleted=0))
    if len(reviews) != 98 or len(held) != 1 or Counter(r['status'] for r in reviews) != Counter(REQUIRED_CONTRACT=91, FALSE_POSITIVE=7):
        raise ValueError('explicit98 site dispositions and one unresolved volatile;do not invent all99 acceptance')
    fatal = ROOT/'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/SessionStoreException.java'
    if not all(s in fatal.read_text() for s in ('new java.util.IdentityHashMap<>()', 'if (!seen.add(candidate)) continue;',
            'if (candidate instanceof Error fatal) throw fatal;', 'candidate.getSuppressed()')):
        raise ValueError('referenced fatal graph traversal and identity-cycle guard unchanged')
    os.umask(0o077); out = BASE/'PG6098-jms-individual-review-v1'; out.mkdir()
    for filename, value in (('reviews.json', reviews), ('manifest.json', dict(actualExit=0, source=SOURCE, reviewed=98,
            statusCounts=dict(Counter(r['status'] for r in reviews)), unresolved=held,
            staticManifestSha256=sha(qp), catchFactsSha256='9e3c38f0eba7fcdda01cb53a4e4b83ea11b2876320f652bc5095bb95591af0f1',
            referenceFactsSha256='2fc6510396459911f3199639b34e61a41b021ae1cbac41b55a7915d459556fd1',
            preserveFatalSourceSha256=sha(fatal), currentWholeJoinPending=True, testsExecuted=0,
            newPtPassesClaimed=0, currentRawFindings=1315, rawWarningsRemoved=0,
            ptAlternativeCompleted=0, actualRuntimeProven=False, F03Accepted=False, formalAccepted=False))):
        with (out/filename).open('x') as f:
            json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, reviewed=98, held=1, manifestSha256=sha(out/'manifest.json'), reviewsSha256=sha(out/'reviews.json'))))


if __name__ == '__main__':
    main()
