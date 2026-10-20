"""Explicit re-review of56 changed-source reasons, preserving pending actual-whole join."""
import copy
import difflib
import json
import os
from collections import Counter, defaultdict
from pg5940_private_lock_compile import ROOT, W, BASE, OLD, plan, sha
from pg5944_private_lock_whole import SOURCE
from pg5956_static_private_lock_rebind import PRIOR, PRIOR_SHA
from static_disposition_overlay import load, apply_decisions


def fragment(text, row):
    lines = text.splitlines(keepends=True)
    if any(ord(c) > 0xffff for c in text):
        raise ValueError('non-BMP diagnostic coordinate review requires a separate adapter')
    a, b = int(row['beginline'])-1, int(row['endline'])-1
    return ''.join(lines[a:b+1])[int(row['begincolumn'])-1:sum(map(len, lines[a:b]))+int(row['endcolumn'])]


def moved_pairs(before_rows, current_rows, removed, before, current):
    kept = [r for r in before_rows if r['findingId'] not in removed]
    if len(kept) != len(current_rows):
        raise ValueError('all source-local diagnostics preserved except exact declared93')
    lines = {}
    for a, b, size in difflib.SequenceMatcher(None, before.splitlines(True), current.splitlines(True), autojunk=False).get_matching_blocks():
        for i in range(size):
            lines[a+i+1] = b+i+1
    result = {}
    metadata = ('sourcePath', 'rule', 'priority', 'diagnosticTextSha256', 'identitySchema')
    for rank, (old, new) in enumerate(zip(kept, current_rows), 1):
        if any(old[k] != new[k] for k in metadata):
            raise ValueError('entire actual diagnostic sequence/rule/priority/message fixed')
        if any(lines.get(int(old[k])) != int(new[k]) for k in ('beginline', 'endline')) or any(old[k] != new[k] for k in ('begincolumn', 'endcolumn')) or fragment(before, old) != fragment(current, new):
            raise ValueError('one independently mapped unchanged diagnostic span, not first equal text')
        result[new['findingId']] = (old, rank)
    return result


def current_references(previous):
    return [dict(klass=r['class'], **{'class': r['class']}, caseNameSha256=r['caseNameSha256']) for r in previous['currentWholeCaseRefs']]


def require_facts(fact):
    if fact.get('source') != SOURCE or any(type(fact.get(k)) is not int or fact[k] != 0 for k in ('actualExit', 'compileExit', 'independentFixtureExit')):
        raise ValueError('each current source/actual/compile/independent-fixture gate must individually be0')


def main():
    bp = BASE/'PG5956-private-lock-dispositions-v1/manifest.json'
    bsha = '5347be0cce1fcd7967ede709f9e42fb56da6e59bcc1babf5e36d9fbb8d1859a9'
    rows = load(bp, bsha, SOURCE); old = load(PRIOR, PRIOR_SHA, OLD)
    cp, rp = (W/name/'manifest.safe.json' for name in ('pg5952-current-catch-facts-v1', 'pg5954-current-reference-facts-v1'))
    if sha(cp) != 'd52d27c514a96948c432476e2c948462deed6dbd4cf8fd7635a4d9380a81ca8c' or sha(rp) != 'aec023eafaae15c916f27d43735d477ec417578481334535d3b08c997076eeef':
        raise ValueError('current851/1666 Main-only independent type facts')
    catches, references = (json.loads(p.read_bytes()) for p in (cp, rp))
    for fact in (catches, references):
        require_facts(fact)
    left, right = defaultdict(list), defaultdict(list)
    for row in old:
        left[row['sourcePath']].append(row)
    for row in rows:
        right[row['sourcePath']].append(row)
    snapshot = W/'pg5912-api-expression-selected35-v1/source'; decisions = []
    prefixes = {
        'DoNotUseThreads': 'Current standalone batch/service actor interrupt restoration, fixed owner-thread identity or privately owned management executor remains the same; no Jakarta EE container or new thread policy is introduced by the private lock wrapper. This is a source-context premise, not operational ownership proof. ',
        'CompareObjectsWithEquals': 'Fresh current resolved operands retain required reference identity: self-suppression, fixed thread owner, exact servlet repository or exact session repository owner; equals substitution remains incorrect. ',
        'UseConcurrentHashMap': 'Current constructor/operation-local map and synchronous retained-handle callbacks still return only immutable/defensive copies or individual digests; no map escapes or asynchronous callback is introduced. ',
        'NullAssignment': 'Current decoded byte-array ownership is transferred to the returned credential; clearing only the temporary reference before finally prevents erasing the returned live buffer. Input/encoded/unmoved bytes still wipe. ',
        'AvoidCatchingGenericException': 'Current WebBrokerContexts.close still directly rethrows the same fatal Error parameter before the ordinary checked redaction boundary; lock finally only releases the same exclusive scope. '}
    for declaration in plan()['sourcePlans']:
        path = declaration['path']; before = (snapshot/path).read_text(); current = (ROOT/path).read_text()
        if sha(snapshot/path) != declaration['beforeSha256'] or sha(ROOT/path) != declaration['predictedAfterSha256']:
            raise ValueError('exact declared same-body source change only')
        pairs = moved_pairs(left[path], right[path], set(declaration['findingIds']), before, current)
        for row in right[path]:
            previous, rank = pairs[row['findingId']]
            if previous['status'] == 'NOT_REVIEWED_CURRENT_SOURCE':
                continue
            if row['status'] != 'NOT_REVIEWED_CURRENT_SOURCE' or row['rule'] not in prefixes:
                raise ValueError('explicit changed-source re-review, never double classification')
            evidence = []
            if row['rule'] == 'CompareObjectsWithEquals':
                evidence = [r for r in references['rows'] if r['path'] == path and r['firstLine'] == row['beginline'] and r['firstColumn'] == row['begincolumn']]
                if len(evidence) != 1:
                    raise ValueError('fresh actual reference-identity typed span')
            elif row['rule'] == 'AvoidCatchingGenericException':
                evidence = [r for r in catches['rows'] if r['path'] == path and r['firstLine'] == row['beginline'] and r['type'] == 'java.lang.Error']
                if len(evidence) != 1 or evidence[0]['sameThrows'] != '1' or evidence[0]['finalDirect'] != 'true':
                    raise ValueError('fresh exact fatal identity passthrough catch')
            reason = prefixes[row['rule']]+previous['priorReason']
            value = copy.deepcopy(row)
            value.update(status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING', priorDisposition=previous['priorDisposition'], reason=reason, priorReason=reason,
                         rawWarningRetained=True, currentWholeCaseRefs=[], currentWholeJoinPending=True, plannedCurrentTestRefs=current_references(previous),
                         priorFindingId=previous['findingId'], priorReviewSource=OLD, explicitCurrentSourceRereview=True, sourceFileOccurrenceRank=rank,
                         diagnosticMapping='ENTIRE_SOURCE_SEQUENCE_EXCEPT93_DECLARED_MONITORS_AND_EXACT_UNCHANGED_LINE_SPANS',
                         currentResolvedEvidence=evidence, currentTypeCatchSha256=sha(cp), currentTypeReferenceSha256=sha(rp),
                         sameCriticalBodyPlanSha256='0f0100343ccfb402be11dfb829ae33120a8a5eea055b6798ad4d8d5c943fccc2',
                         historicalPtImportedAsCurrent=False, ptAlternativeCompleted=False)
            decisions.append(value)
    if Counter(r['rule'] for r in decisions) != Counter(DoNotUseThreads=39, CompareObjectsWithEquals=10, UseConcurrentHashMap=5, NullAssignment=1, AvoidCatchingGenericException=1):
        raise ValueError('all and only56 explicitly reviewed changed-source diagnostics')
    result = apply_decisions(rows, decisions); out = BASE/'PG5958-private-lock-reasons56-v1'; os.umask(0o077); out.mkdir(); dp = out/'decisions.json'
    with dp.open('x') as f:
        json.dump(decisions, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    value = dict(actualExit=0, source=SOURCE, baseManifestPath=bp.relative_to(ROOT).as_posix(), baseManifestSha256=bsha, decisionsSha256=sha(dp), rawFindings=1451,
                 explicitChangedSourceRereviews=56, newIndividualDispositions=0, statusCounts=dict(Counter(r['status'] for r in result)),
                 currentWholeJoinPending=True, sourceCodeChanged=False, executedPtAdded=0, ptAlternativeCompleted=0, F03Accepted=False, formalAccepted=False, vmActions=0)
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, changedSourceReasonsRereviewed=56, pendingCurrentWhole=545, unreviewed=906, rawFindings=1451, manifestSha256=sha(out/'manifest.json'), decisionsSha256=sha(dp))))


if __name__ == '__main__':
    main()
