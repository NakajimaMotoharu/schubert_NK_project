"""Independent finite supplement verification; old diagnostic and runtime domains stay fixed."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg15938_f03_saved_schema_supplement as original

PIN = 'a907cb510165be0cba32f9700d5efe23248bbe27ba03aa1f0766b75ec69b1218'
OUT = data.BASE / 'PG15940-f03-saved-schema-supplement-post-v1'

def require(ok, message):
    if not ok:
        raise ValueError(message)

def key(path, digest, rule, attrs):
    return json.dumps([path, digest, 'pmd', rule, attrs], sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def assess(p, supplement, queue, expected, expected_queue):
    require(p['actualExit'] == 0 and p['source'] == original.prior.SOURCE and p['priorObservationManifestSha256'] == original.PRIOR_PIN, 'same current source/observations')
    require((p['originalObservationCount'], p['priorReferenced'], p['priorUnreferenced'], p['newReferenceConnections'], p['combinedReferenced'], p['remainingSelectedUnreferenced']) == (1491, 283, 1208, 279, 562, 929), 'exact additive reference domains')
    require(supplement == expected and queue == expected_queue and p['referenceSupplementOccurrences'] == len(expected), 'complete exact independent supplement/queue')
    for field in ('referenceIsApplicabilityPass', 'unknownSchemasGuessed', 'rawObservationsModified', 'oldRuntimeTransferred', 'formalUpdated', 'wholeF03Accepted', 'whole451Accepted', 'analyzerReexecuted'):
        require(p[field] is False, 'no promotion/change: ' + field)
    for field in ('newManualReviews', 'newAccepted', 'productTestsExecuted', 'externalActions'):
        require(type(p[field]) is int and p[field] == 0, 'not new review/PT/acceptance')
    require(p['effortPercent'] is None, 'no invented effort')

def main():
    invocation = capture(__file__)
    require(not OUT.exists(), 'new-only')
    p = data.read_checked(original.OUT / 'manifest.json', PIN)
    supplement = data.read_checked(original.OUT / 'reference-supplement.json', p['referencesSha256'])
    queue = data.read_checked(original.OUT / 'remaining-selected-review-queue.json', p['queueSha256'])
    prior = data.read_checked(original.prior.OUT / 'manifest.json', original.PRIOR_PIN)
    rows = data.read_checked(original.prior.OUT / 'current-main-observations.json', prior['observationsSha256'])
    hashes = data.read_checked(original.prior.OUT / 'main-source-inputs.json', prior['sourceInputsSha256'])
    require(p['priorObservationsSha256'] == prior['observationsSha256'] and all(data.sha((data.ROOT / path).read_bytes()) == digest for path, digest in hashes.items()), 'all original current965 bytes unchanged')
    baseline = {r['id']: r for r in data.read_checked(data.BASE / 'PG10690-current-global-static-post-v1/findings.json', '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')}
    observed = {key(r['path'], r['sourceSha256'], r['rule'], r['attributes']) for r in rows}
    refs = collections.defaultdict(list)
    require(len(p['fixedInputs']) == 5 and [(x['manifest'].rsplit('/', 1)[0], x['sha256'], x['file'], x['schema']) for x in p['fixedInputs']] == [(a, b, c, e) for a, b, c, d, e in original.PINS], 'fixed exact five schema input identities')
    for entry in p['fixedInputs']:
        m = data.read_checked(data.BASE / entry['manifest'], entry['sha256'])
        value = data.read_checked((data.BASE / entry['manifest']).parent / entry['file'], entry['fileSha256'])
        rr = value['reviewedRows'] if entry['schema'] == 'REVIEWED_ROWS_IDENTITY' else value
        require(len(rr) == entry['inputRows'] and m['actualExit'] == 0, 'all fixed input rows')
        matched = 0
        for ordinal, row in enumerate(rr):
            path = row.get('path', row.get('originalFinding', {}).get('path'))
            if path not in hashes or row.get('sourceSha256') != hashes[path]:
                continue
            schema = entry['schema']
            if schema == 'COORDINATES':
                require(row['productTestsExecuted'] == 0 and row['qualityGatePass'] is False and row['dynamicAuthorizationUnchanged'] is True, 'thread/classloader static boundary')
                attrs, rule = row['coordinates'], row['rule']
            elif schema == 'ACTUAL_ATTRIBUTES':
                require(row['newProductExecutions'] == 0 and row['rawSuppressed'] is row['reviewIsNewTestExecution'] is False, 'protocol static boundary')
                attrs, rule = row['actualAttributes'], row['rule']
            elif schema == 'ORIGINAL_FINDING':
                require(row['productTestsExecuted'] == 0 and row['dynamicQualification'] is False, 'JSON static boundary')
                attrs, rule = row['originalFinding']['attributes'], row['originalFinding']['rule']
            else:
                require(schema == 'REVIEWED_ROWS_IDENTITY' and row['manualPurposeReviewComplete'] is True and row['dynamicExecutionQualificationInferred'] is False and row['actualViolation'] is None, 'explicit identity static boundary')
                old = baseline[row['id']]
                attrs, rule = old['attributes'], old['rule']
                require(row['originalLine'] == int(attrs['beginline']) and row['originalColumn'] == int(attrs['begincolumn']) and row['operator'] in ('EQUAL_TO', 'NOT_EQUAL_TO'), 'fixed original identity coordinates')
                if (row['astLine'], row['astColumn']) != (row['originalLine'], row['originalColumn']):
                    continue
            signature = key(path, row['sourceSha256'], rule, attrs)
            if signature not in observed:
                continue
            refs[signature].append(dict(manifest=entry['manifest'], manifestSha256=entry['sha256'], file=entry['file'], fileSha256=entry['fileSha256'], schema=schema, rowOrdinal=ordinal, originalId=row.get('id', row.get('originalFindingId', row.get('originalFinding', {}).get('id'))), meaning='EXISTING_STATIC_REFERENCE_ONLY_NO_NEW_REVIEW_OR_APPLICABILITY_PASS'))
            matched += 1
        require(matched == entry['matchedRows'], 'all exact matched input occurrences')
    expected = [dict(id=r['staticObservationId'], path=r['path'], sourceSha256=r['sourceSha256'], attributes=r['attributes'], rule=r['rule'], addedReferences=refs[key(r['path'], r['sourceSha256'], r['rule'], r['attributes'])], originalReferencesUnchanged=True) for r in rows if key(r['path'], r['sourceSha256'], r['rule'], r['attributes']) in refs]
    expected_queue = [dict(id=r['staticObservationId'], path=r['path'], sourceSha256=r['sourceSha256'], rule=r['rule'], attributes=r['attributes']) for r in rows if not r['contextReferences'] and key(r['path'], r['sourceSha256'], r['rule'], r['attributes']) not in refs]
    assess(p, supplement, queue, expected, expected_queue)
    negatives = []
    for field, value in [('source', '0'*40), ('newReferenceConnections', 1208), ('combinedReferenced', 1491), ('remainingSelectedUnreferenced', 0), ('originalObservationCount', 8022), ('effortPercent', 0), ('newAccepted', True), ('newManualReviews', 279), ('productTestsExecuted', 279), ('referenceIsApplicabilityPass', True), ('rawObservationsModified', True), ('oldRuntimeTransferred', True), ('wholeF03Accepted', True), ('unknownSchemasGuessed', True)]:
        bad = copy.deepcopy(p)
        bad[field] = value
        try:
            assess(bad, supplement, queue, expected, expected_queue)
        except ValueError:
            negatives.append(field)
        else:
            raise ValueError('unrejected field: ' + field)
    for label, mutate in [('drop-reference', lambda r, q: r.pop()), ('duplicate', lambda r, q: r.__setitem__(0, r[1])), ('wrong-source-byte', lambda r, q: r[0].update(sourceSha256='0'*64)), ('wrong-coordinate', lambda r, q: r[0]['attributes'].update(beginline='0')), ('wrong-review-hash', lambda r, q: r[0]['addedReferences'][0].update(fileSha256='0'*64)), ('wrong-schema', lambda r, q: r[0]['addedReferences'][0].update(schema='INFERRED')), ('false-PASS', lambda r, q: r[0]['addedReferences'][0].update(meaning='PASS')), ('old-reference-erasure', lambda r, q: r[0].update(originalReferencesUnchanged=False)), ('drop-queue', lambda r, q: q.pop())]:
        rr, qq = copy.deepcopy(supplement), copy.deepcopy(queue)
        mutate(rr, qq)
        try:
            assess(p, rr, qq, expected, expected_queue)
        except ValueError:
            negatives.append(label)
        else:
            raise ValueError('unrejected row: ' + label)
    verify(p['invocation'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json', dict(actualExit=0, source=original.prior.SOURCE, invocation=invocation,
        parentManifestSha256=PIN, priorObservationsSha256=p['priorObservationsSha256'], independentNegativeVectors=len(negatives), negativeLabels=negatives,
        newReferenceConnections=279, combinedReferenced=562, remainingSelectedUnreferenced=929,
        oldReferencesAndRawObservationsUnchanged=True, newManualReviews=0, productTestsExecuted=0,
        wholeF03Accepted=False, whole451Accepted=False, newAccepted=0, formalUpdated=False, effortPercent=None, externalActions=0))
    print(data.sha((OUT / 'manifest.json').read_bytes()))
    print(json.dumps(dict(actualExit=0, independentNegativeVectors=len(negatives), newReferenceConnections=279)))

if __name__ == '__main__':
    main()
