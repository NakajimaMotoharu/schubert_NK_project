"""Independently reconstruct saved Main diagnostics and verify candidate reference joins."""
import collections
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import wbs_candidate_trace as trace
import pg15930_f03_current_main_review_join_v2 as original

PIN = '7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983'
OUT = data.BASE / 'PG15932-f03-current-main-review-post-v1'

def require(ok, message):
    if not ok:
        raise ValueError(message)

def raw_key(row):
    return json.dumps([row['path'], row['sourceSha256'], row.get('tool', 'pmd'), row.get('rule', row['attributes'].get('rule')), row['attributes']], sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()

def assess(p, rows, queue, hashes, expected, references, changed):
    require(p['actualExit'] == 0 and p['source'] == original.SOURCE and p['baselineManifestSha256'] == original.BASELINE[1] and p['freshManifestSha256'] == original.FRESH[1], 'source/measurements')
    require((p['mainSources'], p['unchangedMainSources'], p['changedMainSources'], p['supplementalMainSources'], p['observationCount']) == (965, 954, 11, 8, 1491), 'all cumulative changes and observations')
    require(p['priorAuxiliaryContextNotRequalified'] is p['currentWholeAnalyzerNotIssued'] is True, 'source-only saved observation domain')
    for key in ('testSourceScopeIncluded', 'characterizationJavaIncluded', 'analyzerReexecuted', 'applicabilityAcceptedFromReference', 'oldRuntimeTransferred', 'wholeF03Accepted', 'whole451Accepted', 'formalUpdated', 'privateRawRead'):
        require(p[key] is False, 'no false qualification: ' + key)
    for key in ('newAccepted', 'productTestsExecuted', 'productClassesLoaded', 'externalActions'):
        require(type(p[key]) is int and p[key] == 0, 'no execution/acceptance')
    require(p['actualViolationCount'] is None and p['effortPercent'] is None, 'unknown actual violations/effort')
    require(len(hashes) == 965 and len(rows) == len({r['staticObservationId'] for r in rows}) == 1491, 'full source/occurrence set')
    observed = collections.Counter(json.dumps({k: r[k] for k in ('tool', 'path', 'sourceSha256', 'module', 'kind', 'attributes', 'rule', 'message')}, sort_keys=True) for r in rows)
    require(observed == expected, 'all raw source-matched observations independently reconstructed')
    seen = collections.Counter()
    for row in rows:
        key = raw_key(row)
        ordinal = seen[key]
        seen[key] += 1
        require(row['sourceSha256'] == hashes[row['path']] and row['currentSource'] == original.SOURCE, 'current full source byte')
        require(row['sameCoordinateOccurrence'] == ordinal and row['staticObservationId'] == 'CURRENT-MAIN-' + data.sha(key + b':' + str(ordinal).encode()), 'unique occurrence identity')
        require(row['contextReferences'] == references.get(key, []), 'exact saved review references, not inferred')
        require(row['applicability'] == 'NOT_DETERMINED_BY_REFERENCE_JOIN' and row['currentWholeQualification'] is row['ptExecutionExempt'] is False and row['actualViolation'] is None, 'review is not PASS or exempt')
        if row['path'] not in changed:
            require(row['measurementDomain'] == 'UNCHANGED_MAIN_INPUT_PG13253', 'unchanged source measurement')
        else:
            require(row['measurementDomain'] in ('FRESH_THREE_MAIN_PG14226', 'SAVED_EXACT_BYTE_EIGHT_MAIN_PG13505_13534'), 'every changed source measured')
    pending = [dict(id=r['staticObservationId'], path=r['path'], sourceSha256=r['sourceSha256'], rule=r['rule'], attributes=r['attributes']) for r in rows if not r['contextReferences']]
    require(queue == pending and len(pending) == p['unreferencedMain'] == 1208 and p['exactByteCoordinateReferenced'] == 283 and p['reviewInputManifests'] == 67, 'exact finite selected-review queue, not all unreviewed claims')

def main():
    invocation = capture(__file__)
    require(not OUT.exists(), 'new-only')
    p = data.read_checked(original.OUT / 'manifest.json', PIN)
    rows = data.read_checked(original.OUT / 'current-main-observations.json', p['observationsSha256'])
    queue = data.read_checked(original.OUT / 'unreferenced-main-queue.json', p['queueSha256'])
    hashes = data.read_checked(original.OUT / 'main-source-inputs.json', p['sourceInputsSha256'])
    reviews = data.read_checked(original.OUT / 'review-inputs.json', p['reviewInputsSha256'])
    current = trace.git_artifacts(original.SOURCE, sorted(hashes))
    old = trace.git_artifacts(original.OLD_SOURCE, sorted(hashes))
    require({x for x in trace.git_files(original.SOURCE) if x.startswith('src/') and '/src/main/java/' in x and x.endswith('.java')} == set(hashes), 'full actual Main domain')
    require(all(data.sha(current[x]) == hashes[x] and (data.ROOT / x).read_bytes() == current[x] for x in hashes), 'independent current965 bytes')
    changed = {x for x in hashes if current[x] != old[x]}
    b = data.read_checked(data.BASE / original.BASELINE[0] / 'manifest.json', original.BASELINE[1])
    baseline = data.read_checked(data.BASE / original.BASELINE[0] / 'findings.json', b['findingsSha256'])
    expected_rows = [r for r in baseline if r['kind'] == 'main' and r['path'] not in changed]
    f = data.read_checked(data.BASE / original.FRESH[0] / 'manifest.json', original.FRESH[1])
    fresh = data.read_checked(data.BASE / original.FRESH[0] / 'findings.json', f['findingsSha256'])
    expected_rows += fresh
    measured = {r['path'] for r in fresh}
    for ref in p['supplementalReferences']:
        m = data.read_checked(data.BASE / ref['manifest'], ref['sha256'])
        selected = set(ref['selectedPaths'])
        require(len(selected) == 4 and not measured & selected and all(m['candidateSourceHashes'][x] == hashes[x] for x in selected), 'exact saved four paths')
        measured |= selected
        for tool in ('pmd', 'checkstyle'):
            report = (data.BASE / ref['manifest']).parent / (tool + '.xml')
            require(data.sha(report.read_bytes()) == m['reports'][tool], 'saved XML hash')
            for node in ET.fromstring(report.read_bytes()):
                if node.tag.rpartition('}')[2] != 'file':
                    continue
                path = 'src/schubert-nk-' + node.get('name').split('/src/schubert-nk-', 1)[1]
                if path not in selected:
                    continue
                for item in node:
                    attrs = dict(item.attrib)
                    expected_rows.append(dict(tool=tool, path=path, sourceSha256=hashes[path], module=path.split('/')[1][len('schubert-nk-'):], kind='main', attributes=attrs, rule=attrs.get('rule', attrs.get('source', 'UNKNOWN')), message=' '.join(''.join(item.itertext()).split()) if tool == 'pmd' else attrs.get('message', '')))
    require(measured == changed and len(changed) == 11, 'all changed11, not original false three')
    expected = collections.Counter(json.dumps(r, sort_keys=True) for r in expected_rows)
    references = collections.defaultdict(list)
    for ref in reviews:
        m = data.read_checked(data.ROOT / ref['manifest'], ref['sha256'])
        require(m['actualExit'] == 0 and m['reviewSha256'] == ref['reviewSha256'], 'saved public review identity')
        v = data.read_checked((data.ROOT / ref['manifest']).parent / 'review.json', ref['reviewSha256'])
        rr = v['rows'] if isinstance(v, dict) else v
        require(len(rr) == ref['rows'], 'saved review count')
        for ordinal, row in enumerate(rr):
            if not isinstance(row, dict) or row.get('path') not in hashes or not isinstance(row.get('attributes'), dict) or row.get('sourceSha256') != hashes[row['path']] or row.get('rawRetained') is not True or row.get('productTestsExecuted') != 0:
                continue
            references[raw_key(row)].append(dict(manifest=ref['manifest'], manifestSha256=ref['sha256'], reviewSha256=ref['reviewSha256'], reviewOrdinal=ordinal, oldFindingId=row.get('id'), meaning='EXACT_BYTE_COORDINATE_REVIEW_REFERENCE_NOT_APPLICABILITY_OR_RUNTIME_PASS'))
    assess(p, rows, queue, hashes, expected, references, changed)
    negatives = []
    for key, value in [('source', '0'*40), ('changedMainSources', 3), ('unchangedMainSources', 962), ('supplementalMainSources', 0), ('observationCount', 1502), ('actualViolationCount', 0), ('effortPercent', 0), ('newAccepted', True), ('wholeF03Accepted', True), ('oldRuntimeTransferred', True), ('applicabilityAcceptedFromReference', True), ('analyzerReexecuted', True), ('priorAuxiliaryContextNotRequalified', False), ('exactByteCoordinateReferenced', 1491)]:
        bad = copy.deepcopy(p)
        bad[key] = value
        try:
            assess(bad, rows, queue, hashes, expected, references, changed)
        except ValueError:
            negatives.append(key)
        else:
            raise ValueError('unrejected manifest: ' + key)
    for label, mutate in [('drop-row', lambda r, q: r.pop()), ('duplicate', lambda r, q: r.__setitem__(0, r[1])), ('byte', lambda r, q: r[0].update(sourceSha256='0'*64)), ('coordinates', lambda r, q: r[0]['attributes'].update(beginline='0')), ('review-PASS', lambda r, q: r[0].update(applicability='PASS')), ('PT-exempt', lambda r, q: r[0].update(ptExecutionExempt=True)), ('runtime', lambda r, q: r[0].update(currentWholeQualification=True)), ('missing-queue', lambda r, q: q.pop()), ('reference-drop', lambda r, q: next(x for x in r if x['contextReferences']).update(contextReferences=[])), ('false-ref', lambda r, q: next(x for x in r if not x['contextReferences']).update(contextReferences=[{}]))]:
        rr, qq = copy.deepcopy(rows), copy.deepcopy(queue)
        mutate(rr, qq)
        try:
            assess(p, rr, qq, hashes, expected, references, changed)
        except ValueError:
            negatives.append(label)
        else:
            raise ValueError('unrejected row: ' + label)
    require(data.sha((data.ROOT / 'tools/quality/pg15928_f03_current_main_review_join.py').read_bytes()) == 'ff7c6b8b20d8194e4069197fa84e337bed03fda1b233387af399c00686daf91d', 'old failed tool immutable')
    verify(p['invocation'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'prior-failure.safe.json', dict(bug='BUG2152', horizontal='YKT1899', oldTool='tools/quality/pg15928_f03_current_main_review_join.py', oldToolSha256='ff7c6b8b20d8194e4069197fa84e337bed03fda1b233387af399c00686daf91d', actualExit=1, oldOutputCreated=False, reason='ExpectedThreeMainButActualEleven_GuardStoppedBeforeOutput', oldResultPromoted=False))
    data.write(OUT / 'manifest.json', dict(actualExit=0, invocation=invocation, source=original.SOURCE, parentManifestSha256=PIN,
        independentNegativeVectors=len(negatives), negativeLabels=negatives, allMainSources=965, cumulativeChangedMain=11,
        observations=1491, selectedReviewReferenced=283, selectedReviewUnreferenced=1208,
        priorFailureSha256=data.sha((OUT / 'prior-failure.safe.json').read_bytes()), originalAnalyzersReexecuted=False,
        wholeF03Accepted=False, whole451Accepted=False, productTestsExecuted=0, externalActions=0,
        newAccepted=0, formalUpdated=False, actualViolationCount=None, effortPercent=None))
    print(data.sha((OUT / 'manifest.json').read_bytes()))
    print(json.dumps(dict(actualExit=0, independentNegativeVectors=len(negatives), observations=1491)))

if __name__ == '__main__':
    main()
