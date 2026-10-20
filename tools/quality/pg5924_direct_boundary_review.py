"""Thirteen exact fatal passthrough diagnostics; neither generic waiver nor PT alternative."""
import copy
import hashlib
import json
import os
import re
from collections import Counter
from pg5540_snapshot_scratch_selected import ROOT, sha
from static_disposition_overlay import BASE, load, apply_decisions
from pg5918_api_static_rebind import SOURCE, W

SCOPES = {
    'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/mq/ArtemisManagementReadinessClient.java': ({'putAcceptorsOperation', 'putRolesOperation', 'putExpiryOperation', 'putAddressSettingsOperation', 'query'}, 'java.lang.RuntimeException|java.lang.Error', 'Exception', 10),
    'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/LinuxSystemdSession.java': ({'invoke'}, 'java.lang.RuntimeException|java.lang.Error', 'Throwable', 2),
    'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/WebBrokerContexts.java': ({'close'}, 'java.lang.Error', 'Exception', 1)}
TESTS = {
    'batch': ('dev.codex.schubert.nk.batch.mq.ArtemisUnknownBoundaryTest', ('mqUnknown001EveryReaderAndExchangePreservesUnknownIdentity', 'mqUnknown004FatalQueryAndEveryEncoderPreserveIdentity')),
    'bootstrap': ('dev.codex.schubert.nk.bootstrap.LinuxSystemdSessionTest', ('nativeInvocationPreservesUnknownRuntimeFatalAndSanitizesCheckedFailures',)),
    'web': ('dev.codex.schubert.nk.web.messaging.WebBrokerContextsTest', ('closeIsIdempotentAndPreservesFatalOverOrdinary',))}


def direct_boundary(text, end, parameter, following):
    name = parameter.split()[-1]
    found = re.match(r'\s*\)\s*\{\s*throw\s+' + re.escape(name) + r'\s*;\s*\}\s*catch\s*\(\s*' + re.escape(following) + r'\s+\w+\s*\)\s*\{', text[end:])
    if not found:
        raise ValueError('one direct same-parameter throw only, before the declared broader checked boundary')
    return hashlib.sha256(text[end:end+found.end()].encode()).hexdigest()


def identity_refs(module, old_cases):
    cls, methods = TESTS[module]
    path = ROOT / ('src/schubert-nk-' + module + '/src/test/java/' + cls.replace('.', '/') + '.java')
    text = path.read_text(); result = []
    for method in methods:
        if text.count('void ' + method + '(') != 1:
            raise ValueError('independent existing test source method identity')
        hashes = {hashlib.sha256(s.encode()).hexdigest() for s in (method, method+'()')}
        found = [r for r in old_cases if r['class'] == cls and r['caseNameSha256'] in hashes]
        if len(found) != 1:
            raise ValueError('one historical semantic identity only; not current PASS')
        result.append(dict(klass=cls, **{'class': cls}, caseNameSha256=found[0]['caseNameSha256'], plannedMethod=method,
                           historicalIdentityOnly=True, currentTestSourceSha256=sha(path)))
    return result


def main():
    bp = BASE / 'PG5920-buffer-map-contracts-v2/manifest.json'
    bsha = '7a874e49cbcc7946f9651784dbd092af3a791c035f152761e3619e2133bd365e'
    rows = load(bp, bsha, SOURCE)
    cp = W / 'pg5922-current-catch-facts-v1/manifest.safe.json'
    if sha(cp) != 'bd5bf95bc9b301958f6f0cac23437f79cb3889fd6bc74cbb5f1ed9ec5323fc2b':
        raise ValueError('actual current1094 resolved catch facts')
    facts = json.loads(cp.read_bytes())
    proof = json.loads((W / 'pg5914-api-expression-static-v1/manifest.safe.json').read_bytes())
    if not (facts['source'] == SOURCE == proof['source'] and facts['actualExit'] == facts['compileExit'] == facts['independentFixtureExit'] == proof['actualExit'] == 0 and len(facts['rows']) == 1094 and facts['identity']['physicalMainSha256'] == proof['auxClassHashes'] and facts['identity']['sourceHashes'] == proof['allSourceHashes']):
        raise ValueError('all851/1666 actual type/class input identity')
    oldp = BASE / 'PG5886-current3973-cases/cases.json'
    if sha(oldp) != '1ea9bbc5a6266704ae03f9776a49994add2aff5e9aec04db7feecb17ba8abd95':
        raise ValueError('historical3973 method identity only, no old PASS import')
    old_cases = json.loads(oldp.read_bytes())
    decisions = []; scopes = []; used = set()
    for path, (methods, caught, following, expected_count) in SCOPES.items():
        text = (ROOT / path).read_text()
        if sha(ROOT / path) != facts['identity']['sourceHashes'][path] or any(ord(s) > 0xffff for s in text):
            raise ValueError('immutable source and exact javac UTF16 offsets')
        refs = identity_refs(path.split('/')[1].removeprefix('schubert-nk-'), old_cases)
        chosen = [f for f in facts['rows'] if f['path'] == path and '#' in f['method'] and f['method'].split('#', 1)[1].split('(', 1)[0] in methods and f['type'] == caught]
        if len(chosen) != len(methods):
            raise ValueError('one declared typed direct catch per method')
        per_path = 0
        for fact in chosen:
            if fact['finalDirect'] != 'true' or fact['sameThrows'] != '1' or any(fact[k] != '0' for k in ('otherThrows', 'returns', 'assignments', 'breaks', 'continues')):
                raise ValueError('resolved original Throwable only; no assignment/return/normalization')
            start, end = int(fact['start']), int(fact['end'])
            body_sha = direct_boundary(text, end, text[start:end], following)
            hits = []
            for row in rows:
                if row['sourcePath'] != path or row['rule'] != 'AvoidCatchingGenericException' or row['status'] != 'NOT_REVIEWED_CURRENT_SOURCE':
                    continue
                lines = text.splitlines(keepends=True)
                a = sum(map(len, lines[:int(row['beginline'])-1])) + int(row['begincolumn'])-1
                b = sum(map(len, lines[:int(row['endline'])-1])) + int(row['endcolumn'])-1
                if start <= a < b <= end:
                    hits.append(row)
            if len(hits) != (1 if caught == 'java.lang.Error' else 2):
                raise ValueError('all and only typed Runtime/Error parameter diagnostics')
            for row in hits:
                if row['findingId'] in used or row['sourceSha256'] != sha(ROOT / path):
                    raise ValueError('unique actual current diagnostic/source')
                used.add(row['findingId'])
                reason = 'SS343/352 and existing unknown/fatal identity contract: this exact catch only rethrows the resolved original RuntimeException/Error parameter before the broader ' + following + ' redaction boundary. Removing it would normalize unknown/fatal failure to a checked/ordinary fixed error. No mutation, successful return, retry, resource release or exception-graph traversal occurs in this catch. This rationale does not certify the following checked catch, root ownership, DB/lock postconditions or actual provider state.'
                value = copy.deepcopy(row)
                value.update(status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING', priorDisposition='REQUIRED_CONTRACT', reason=reason,
                             priorReason=reason, rawWarningRetained=True, currentWholeCaseRefs=[], currentWholeJoinPending=True,
                             plannedCurrentTestRefs=refs, currentCatchFact=fact, directBoundarySha256=body_sha,
                             reviewSource=SOURCE, currentTypeFactsSha256=sha(cp), historicalPtImportedAsCurrent=False,
                             implementationReviewedNoChangeRequired=True, ptAlternativeCompleted=False)
                decisions.append(value); per_path += 1
            scopes.append(dict(path=path, method=fact['method'], catchFirstLine=fact['firstLine'], type=caught, followingCheckedBoundary=following, bodySha256=body_sha, diagnostics=len(hits)))
        if per_path != expected_count:
            raise ValueError('exact declared per-owner diagnostic count')
    if len(decisions) != 13 or len(scopes) != 7:
        raise ValueError('only seven narrow scopes/thirteen diagnostics')
    result = apply_decisions(rows, decisions)
    out = BASE / 'PG5924-direct-boundary13-v1'; os.umask(0o077); out.mkdir()
    dp = out / 'decisions.json'
    with dp.open('x') as f:
        json.dump(decisions, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    value = dict(actualExit=0, source=SOURCE, baseManifestPath=bp.relative_to(ROOT).as_posix(), baseManifestSha256=bsha,
                 decisionsSha256=sha(dp), rawFindings=1544, newIndividualDispositions=13, exactDirectRethrowScopes=7,
                 currentCatchFactsSha256=sha(cp), statusCounts=dict(Counter(r['status'] for r in result)), scopes=scopes,
                 currentWholeJoinPending=True, historicalPtImportedAsCurrent=False, executedPtAdded=0, ptAlternativeCompleted=0,
                 sourceCodeChanged=False, implementationReviewedNoChangeRequired=True, wholeReplayed=False, F03Accepted=False, formalAccepted=False, vmActions=0)
    with (out / 'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps({k: v for k, v in value.items() if k != 'scopes'})); print(json.dumps(dict(manifestSha256=sha(out/'manifest.json'), decisionsSha256=sha(dp))))


if __name__ == '__main__':
    main()
