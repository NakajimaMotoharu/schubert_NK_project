"""28 exact readiness exception/close contracts; normal static PG review, not refused PT waiver."""
import copy
import json
import os
from collections import Counter
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg5944_private_lock_whole import SOURCE
from pg5958_private_lock_reason_review import fragment, require_facts
from static_disposition_overlay import load, apply_decisions

GUARD = 'if (primary == null || closing instanceof Error && !(primary instanceof Error)) {'
SCOPES = {
    'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/dispatch/ApiDependencyReadiness.java': ('api', 'dev.codex.schubert.nk.api.dispatch.ApiDependencyReadinessTest', ('verify', 'probe'), ('API database unavailable', 'API Artemis receive queues unavailable')),
    'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebDependencyReadiness.java': ('web', 'dev.codex.schubert.nk.web.bootstrap.WebDependencyReadinessTest', ('verify',), ('Web technical database', 'Web Artemis reply Queue'))}

# Independent contract table, not computed from Production or treated as executed PT.
PRECEDENCE = [
    ['NONE', 'NONE', 'SUCCESS'], ['NONE', 'ORDINARY', 'CLOSE_ORDINARY'], ['NONE', 'FATAL', 'CLOSE_FATAL'],
    ['ORDINARY', 'NONE', 'PRIMARY_ORDINARY'], ['ORDINARY', 'ORDINARY', 'PRIMARY_ORDINARY'], ['ORDINARY', 'FATAL', 'CLOSE_FATAL'],
    ['FATAL', 'NONE', 'PRIMARY_FATAL'], ['FATAL', 'ORDINARY', 'PRIMARY_FATAL'], ['FATAL', 'FATAL', 'PRIMARY_FATAL']]


def require_source_contract(text):
    if text.count(GUARD) != 2 or text.count('primary = failure;') != 2 or text.count('connection.close();') != 1 or text.count('context.close();') != 1:
        raise ValueError('two owned resource scopes/primary assignment/close/fatal precedence guards exact')
    if any(s in text for s in ('catch (Throwable', 'getCause(', 'getSuppressed(', 'addSuppressed(', 'getMessage(', 'printStackTrace(', 'return true;', 'return false;')):
        raise ValueError('no graph traversal, secret diagnostics or success normalization')
    if text.count('} catch (RuntimeException failure) {') != 1 or text.count('} catch (SQLException | RuntimeException failure) {') != 1:
        raise ValueError('only ordinary failures redacted outside, never fatal Error')


def main():
    bp = BASE/'PG5958-private-lock-reasons56-v1/manifest.json'; bsha = 'c8c7e6f0627746f0888597625db25c4b8d7113ccb07a0fa9e63945c53487e33c'
    rows = load(bp, bsha, SOURCE)
    cp = W/'pg5952-current-catch-facts-v1/manifest.safe.json'
    if sha(cp) != 'd52d27c514a96948c432476e2c948462deed6dbd4cf8fd7635a4d9380a81ca8c':
        raise ValueError('actual current Main-only catch types')
    facts = json.loads(cp.read_bytes()); require_facts(facts)
    q = BASE/'PG5926-current3973-cases/qualification.json'; casesp = q.with_name('cases.json')
    if sha(q) != '89bdeed7bf69067bb0a20c766c8e59cbb780d0fd83dffa7e71c9e1255b1115cf' or sha(casesp) != '706d48d8a43c7e80876ecf9fedd6cddf935bb88bba207dc04998015b6bbc0904':
        raise ValueError('old semantic Test identities only, never old PASS import')
    cases = json.loads(casesp.read_bytes()); decisions = []; scope_proofs = []
    for path, (module, cls, methods, fixed_messages) in SCOPES.items():
        text = (ROOT/path).read_text(); require_source_contract(text)
        if sha(ROOT/path) != facts['identity']['sourceHashes'][path] or not all('"'+s+'"' in text for s in fixed_messages):
            raise ValueError('actual current source/fixed redaction contract')
        testp = ROOT/('src/schubert-nk-'+module+'/src/test/java/'+cls.replace('.', '/')+'.java')
        matches = [c for c in cases if c['class'] == cls]
        if not matches:
            raise ValueError('existing independent readiness test identities')
        refs = [dict(klass=cls, **{'class': cls}, caseNameSha256=c['caseNameSha256'], currentTestSourceSha256=sha(testp)) for c in matches]
        chosen = [r for r in rows if r['sourcePath'] == path and r['status'] == 'NOT_REVIEWED_CURRENT_SOURCE' and r['rule'] in ('AvoidCatchingGenericException', 'DoNotThrowExceptionInFinally', 'AvoidInstanceofChecksInCatchClause')]
        if Counter(r['rule'] for r in chosen) != Counter(AvoidCatchingGenericException=10, DoNotThrowExceptionInFinally=2, AvoidInstanceofChecksInCatchClause=2):
            raise ValueError('exact14 diagnostics in each readiness owner')
        for row in chosen:
            resolved = []
            if row['rule'] == 'AvoidCatchingGenericException':
                resolved = [f for f in facts['rows'] if f['path'] == path and int(f['firstLine']) <= int(row['beginline']) <= int(f['lastLine'])]
                if len(resolved) != 1 or resolved[0]['method'].split('#', 1)[1].split('(', 1)[0] not in methods or 'java.lang.RuntimeException' not in resolved[0]['type'] or resolved[0]['returns'] != '0':
                    raise ValueError('exact resolved expected typed non-success catch scope')
                detail = 'This catch either retains/rethrows the exact inspection failure, handles a close failure using explicit fatal precedence, or emits only a fixed ordinary startup diagnostic. Fatal Error is outside the ordinary redaction catch. '
            elif row['rule'] == 'DoNotThrowExceptionInFinally':
                body = fragment(text, row)
                if GUARD not in body or 'throw closing;' not in body or body.count('.close();') != 1:
                    raise ValueError('one owned cleanup/fatal-close precedence block')
                detail = 'Throwing from this exact finally is intentional only for no primary failure or a fatal close over an ordinary primary. It never replaces an existing fatal primary, and ordinary close failures never hide an ordinary primary. Unconditional throw, ignored close or ordinary TWR precedence would change the established startup contract. '
            else:
                if GUARD not in text.splitlines()[int(row['beginline'])-1]:
                    raise ValueError('exact Error category precedence condition, not general type probing')
                detail = 'This Error category check distinguishes fatal ownership cleanup from an ordinary SQL/JMS failure; it is not serialization/type guessing or recovery. The explicit primary/close matrix keeps fatal identity and prevents ordinary unavailable conversion from swallowing a fatal close. '
            reason = 'SS311/321/342/352; existing PG221/234/266/BUG248/249/250/321 startup and redaction contracts. '+detail+'No message consumption/DB mutation/retry/normal-success fallback is implemented here. Actual provider state, parent budget/Root DONE and DB/lock release require their independent downstream gates.'
            value = copy.deepcopy(row)
            value.update(status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING', priorDisposition='REQUIRED_CONTRACT', reason=reason, priorReason=reason,
                         rawWarningRetained=True, currentWholeCaseRefs=[], currentWholeJoinPending=True, plannedCurrentTestRefs=refs,
                         currentCatchFacts=resolved, currentTypeFactsSha256=sha(cp), reviewSource=SOURCE, implementationReviewedNoChangeRequired=True,
                         historicalPtImportedAsCurrent=False, ptAlternativeCompleted=False)
            decisions.append(value)
        scope_proofs.append(dict(path=path, sourceSha256=sha(ROOT/path), classMethods=list(methods), testSourcePath=testp.relative_to(ROOT).as_posix(),
                                 testSourceSha256=sha(testp), plannedExistingCaseReferences=len(refs), sourceCodeChanged=False, independentPrecedenceTable=PRECEDENCE))
    result = apply_decisions(rows, decisions); out = BASE/'PG5960-readiness-boundaries28-v1'; os.umask(0o077); out.mkdir(); dp = out/'decisions.json'
    with dp.open('x') as f:
        json.dump(decisions, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    value = dict(actualExit=0, source=SOURCE, baseManifestPath=bp.relative_to(ROOT).as_posix(), baseManifestSha256=bsha, decisionsSha256=sha(dp), rawFindings=1451,
                 newIndividualDispositions=28, statusCounts=dict(Counter(r['status'] for r in result)), scopes=scope_proofs, currentWholeJoinPending=True,
                 implementationReviewedNoChangeRequired=True, sourceCodeChanged=False, executedPtAdded=0, ptAlternativeCompleted=0, F03Accepted=False, formalAccepted=False, vmActions=0)
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, newReasons=28, pendingWhole=573, unreviewed=878, raw=1451, manifestSha256=sha(out/'manifest.json'), decisionsSha256=sha(dp))))


if __name__ == '__main__':
    main()
