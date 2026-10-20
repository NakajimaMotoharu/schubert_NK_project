"""Current8c strict582 rationale reauthentication plus24 individual JDBC ownership reviews."""
import copy
import json
import os
import re
from collections import Counter
from pathlib import Path
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6040_remaining33_whole import SOURCE
from pg6046_jdbc_ownership_facts import OWNERS, validate_scope
from pg5966_api_sql_selected import source_test_names
from pg5910_storage_static_rebind import ordered_pairs
from pg5758_static_rebind import bind_one
from static_disposition_overlay import load
from pg5958_private_lock_reason_review import fragment

OLD = 'bc0cac2f6a7055b938f581e8cd163db398f8a656'
STATIC_SHA = '9221ffadcdc28435bee4e2cb7a289f97dc813b24132c2e2fcc43bb53a0d1ea23'
QSHA = '0d11101550922d207fec3ba3f1d2fa9bbb3b35a5b5fabfc83cdb35a6ea950788'
CSHA = 'af2845e1a6c82581975e6a3362db9392696092542467040236d73212736528f1'


def current_refs(prior, index, context_only=False):
    if not prior:
        if not context_only:
            raise ValueError('empty PT references only for an explicit static-context premise')
        return []
    result = []
    for ref in prior:
        key = (ref['class'], ref['caseNameSha256'])
        if key not in index:
            raise ValueError('each prior semantic case must exist in genuine current whole')
        row = index[key]
        if row['source'] != SOURCE or row['result'] != 'PASS_ORIGINAL_XML':
            raise ValueError('current original XML only,never historical PASS')
        result.append({k: row[k] for k in ('testId', 'xmlSha256', 'class', 'caseNameSha256', 'source')})
    return result


def alias_binding(text, scope, helper_name='present'):
    if helper_name not in ('present', 'presentRead'):
        raise ValueError('explicit reviewed identity helper only')
    helper_token = re.escape(helper_name)
    helper = re.findall(r'private\s+static\s+<T>\s+T\s+'+helper_token+r'\s*\(@Nullable\s+T\s+value\)\s+throws\s+SQLDataException\s*\{\s*if\s*\(value\s*==\s*null\)\s*throw\s+new\s+SQLDataException\s*\(\s*"(?:\\.|[^"\\])*"\s*\)\s*;\s*return\s+value\s*;\s*\}', text)
    if len(helper) != 1 or text.count(scope['body']) != 1:
        raise ValueError('one exact identity-only helper and unambiguous AST protected body')
    match = re.match(r'\{\s*(?P<declaration>var\s+(?P<alias>\w+)\s*=\s*'+helper_token+r'\s*\(\s*'+re.escape(scope['variable'])+r'\s*\)\s*;)', scope['body'])
    if match is None:
        raise ValueError('first protected declaration is identity alias of this exact acquired resource')
    offset = text.index(scope['body'])
    first = text.count('\n', 0, offset+match.start('declaration'))+1
    last = text.count('\n', 0, offset+match.end('declaration')-1)+1
    return dict(alias=match.group('alias'), firstLine=first, lastLine=last,
                identityHelperSha256=__import__('hashlib').sha256(helper[0].encode()).hexdigest(), newResourceCreated=False)


def main():
    sp = BASE/'PG6044-remaining33-static-v2/manifest.json'; qp = BASE/'PG6040-current3976-cases/qualification.json'; cp = qp.with_name('cases.json')
    if (sha(sp), sha(qp), sha(cp)) != (STATIC_SHA, QSHA, CSHA):
        raise ValueError('current genuine3976/8511667/raw1296 immutable proof')
    q = json.loads(qp.read_bytes()); current = json.loads(sp.with_name('findings.json').read_bytes()); cases = json.loads(cp.read_bytes())
    if q['productionSource'] != SOURCE or (q['tests'], q['suites'], q['mainClasses']) != (3976, 593, 1667):
        raise ValueError('same source whole identity')
    index = {(r['class'], r['caseNameSha256']): r for r in cases}
    if len(index) != 3976:
        raise ValueError('all actual case identities unique')
    for row in cases:
        if row['xmlSha256'] != q['modules'][row['module']]['xmlHashes'][row['sourceXml']]:
            raise ValueError('each original case stays linked to its actual module XML')
    if {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')} != q['allSourceHashes']:
        raise ValueError('all851 current Main fixed')
    oldsha = 'ad7bed36b819324657ac34b504ccf5086fa25bf3e94f845505fa153977ceb390'
    old = load(BASE/'PG6024-current-static3973-v1/manifest.json', oldsha, OLD)
    oldq = BASE/'PG6014-current3973-cases/qualification.json'
    if sha(oldq) != '50285cd7e326b7709269caeca141abb287978e6e69fc3892863a1e1cc4a7e120':
        raise ValueError('actual previous physical map,not guessed byte equivalence')
    before = json.loads(oldq.read_bytes())['allPhysicalMainSha256']; pairs = ordered_pairs(old, current)
    decided = {r['findingId']: r for r in old if r['status'] != 'NOT_REVIEWED_CURRENT_SOURCE'}
    result, used, static_only = [], set(), 0
    for row in current:
        pair = pairs.get(row['findingId']); prior = copy.deepcopy(decided.get(pair[0]['findingId'])) if pair else None
        if prior:
            prior['reason'] = prior.get('reason') or prior.get('priorReason')
        value, kind = bind_one(row, [prior] if prior else [], (ROOT/row['sourcePath']).read_bytes(), before, q['allPhysicalMainSha256'])
        if kind == 'REBOUND':
            used.add(prior['findingId']); context = prior.get('staticContextPremiseOnly') is True
            if context and prior['status'] != 'CONTEXT_NOT_APPLICABLE':
                raise ValueError('only an existing explicit context premise may have no PT')
            refs = current_refs(prior['currentWholeCaseRefs'], index, context)
            static_only += not bool(refs)
            value.update(status=prior['status'], reason=prior['reason'], priorReviewSource=OLD, priorReviewManifestSha256=oldsha,
                currentWholeCaseRefs=refs, currentWholeJoinPending=False, currentQualificationSha256=QSHA, currentCasesSha256=CSHA,
                currentWholePhysicalProofSha256=QSHA, historicalPtImportedAsCurrent=False, staticContextPremiseOnly=context,
                sourceFileOccurrenceRank=pair[1], diagnosticIdentityMapping='EXACT_ENTIRE_SOURCE_DIAGNOSTIC_SEQUENCE_WITHIN_FILE')
        result.append(value)
    if len(used) != 582 or static_only != 211:
        raise ValueError('only observed582 byte/source/diagnostic-identical reasons;211 static-context-only')
    fp = W/'pg6046-jdbc-ownership24-facts-v3/manifest.safe.json'
    if sha(fp) != 'a934bea216fd8d59ded4eeafe9dfee3dd6ab70bee3a81beaf6e10bc2129fb27e':
        raise ValueError('actual24 parse-only source scope facts fixed')
    facts = json.loads(fp.read_bytes())
    if facts['source'] != SOURCE or facts['actualExit'] != 0 or facts['counts'] != OWNERS or facts['productionMethodsInvoked'] != 0:
        raise ValueError('six current source owners/24 protected allocations,no Production execution')
    by_id = {r['findingId']: i for i, r in enumerate(result)}; reviews, scopes_seen, test_refs_used = [], set(), set()
    for scope in facts['scopes']:
        path = scope['sourcePath']; name = Path(path).stem; ownership = validate_scope(scope)
        if sha(ROOT/path) != scope['sourceSha256'] or q['allSourceHashes'][path] != scope['sourceSha256']:
            raise ValueError('each actual source scope matches current full source')
        text = (ROOT/path).read_text(); alias = alias_binding(text, scope)
        chosen = [r for r in current if r['sourcePath'] == path and r['rule'] == 'CloseResource' and int(alias['firstLine']) <= int(r['beginline']) <= int(r['endline']) <= int(alias['lastLine']) and fragment(text, r).strip() == alias['alias']]
        if len(chosen) != 1 or result[by_id[chosen[0]['findingId']]]['status'] != 'NOT_REVIEWED_CURRENT_SOURCE':
            raise ValueError('one genuinely unreviewed diagnostic for each individual allocation')
        row = copy.deepcopy(chosen[0]); klass = 'dev.codex.schubert.nk.batch.repository.'+name+'Test'
        tp = ROOT/('src/schubert-nk-batch/src/test/java/'+klass.replace('.', '/')+'.java')
        names = source_test_names(tp); refs = [r for r in cases if r['class'] == klass]
        if len(refs) != len(names) or any(len([r for r in refs if r['caseNameSha256'] in {__import__('hashlib').sha256(n.encode()).hexdigest(), __import__('hashlib').sha256((n+'()').encode()).hexdigest()}]) != 1 for n in names):
            raise ValueError('every unchanged named owner Test linked once to current original XML')
        counts = q['allActualClassCounters']['batch:'+path.split('/src/main/java/')[1][:-5]+'.class']
        if set(counts) != {'LINE', 'METHOD', 'CLASS', 'BRANCH'} or any(v['missed'] != 0 or v['covered'] <= 0 for v in counts.values()):
            raise ValueError('all six owners have actual explicit four100,not inferred')
        currentrefs = current_refs(refs, index); test_refs_used.update(r['testId'] for r in currentrefs)
        reason = ('SS331/332 SSC063/199/200: this individual local JDBC allocation enters its protected try before any executable action; '
                  'only the listed initializer-free local declaration may intervene. A nullable resource is checked inside protection; '
                  'its own finally closes it once, capturing the actual primary and using JdbcResourceFailures only for the approved SQL/unknown precedence. '
                  'No borrowed Connection close/config/commit/rollback or resource return occurs. The parser facts, actual compile/Jar bytes and '
                  'independent current owner Tests (normal/null/projection/SQL/unknown/fatal/combined close/rollback/concurrency) refute this leak warning. '
                  'Initializer/callback gaps, another binding or a missing guard fail validation. This is not evidence of live DB/lock/Root termination; '
                  'Expiry plain-finally scopes are expressly excluded and remain BUG1530/SSC310 open.')
        row.update(status='FALSE_POSITIVE', reason=reason, rawWarningRetained=True, newDispositionCreated=True,
            implementationReviewedNoChangeRequired=True, reviewSource=SOURCE, ownership=ownership,
            warningOnIdentityAlias=alias,
            sourceScopeFactsSha256=sha(fp), sourceMethod=scope['method'], actualCounters=counts,
            currentWholeCaseRefs=currentrefs, currentWholeJoinPending=False, currentQualificationSha256=QSHA,
            currentCasesSha256=CSHA, testSourceSha256=sha(tp), independentOracleSource='JdbcResourceCases.java plus owner literal SQL/value expectations',
            independentOracleSha256=sha(tp.with_name('JdbcResourceCases.java')), ptAlternativeCompleted=False, historicalPtImportedAsCurrent=False)
        result[by_id[row['findingId']]] = row; reviews.append(row); scopes_seen.add((path, scope['method'], scope['variable'], scope['firstLine']))
    if len(reviews) != 24 or len(scopes_seen) != 24 or len(test_refs_used) != 68 or len(result) != 1296 or [r['findingId'] for r in result] != [r['findingId'] for r in current]:
        raise ValueError('all24 individually distinct/68 current owner Test refs/all1296 raw retained')
    statuses = Counter(r['status'] for r in result)
    if statuses != Counter(REQUIRED_CONTRACT=352, CONTEXT_NOT_APPLICABLE=226, FALSE_POSITIVE=28, NOT_REVIEWED_CURRENT_SOURCE=690):
        raise ValueError('only strict582 plus new24,current606 reasons/690 unreviewed')
    out = BASE/'PG6048-current-jdbc24-v2'; os.umask(0o077); out.mkdir()
    inventory = out/'findings.json'
    with inventory.open('x') as f:
        json.dump(result, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    value = dict(actualExit=0, source=SOURCE, currentRawFindings=1296, currentStaticManifestSha256=STATIC_SHA,
        priorReviewSource=OLD, priorReviewManifestSha256=oldsha, reauthenticatedUnchangedDispositions=582,
        priorReasonsNotReused=sorted(set(decided)-used), newIndividualDispositions=24, sourceAndWholeJoinedDispositions=606,
        staticContextPremiseOnly=211, uniqueCurrentOwnerTestReferences=68, inventoryFile='findings.json', inventorySha256=sha(inventory),
        statusCounts=dict(statuses), currentWholeQualificationSha256=QSHA, currentWholeCasesSha256=CSHA,
        sourceCodeChanged=False, currentWholeJoinPending=False, executedPtAdded=0, ptAlternativeCompleted=0,
        unreviewedExpiryReadScopes=2, openFunctionalBug='BUG1530', F03Accepted=False, formalAccepted=False, vmActions=0)
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, strictReauthenticated=582, newlyReviewed=24, currentReasons=606, unreviewed=690,
        manifestSha256=sha(out/'manifest.json'), inventorySha256=sha(inventory), executedPtAdded=0)))


if __name__ == '__main__':
    main()
