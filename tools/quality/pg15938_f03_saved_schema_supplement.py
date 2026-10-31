"""Explicit five saved-schema adapters; references only, never runtime/applicability PASS."""
import collections
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg15930_f03_current_main_review_join_v2 as prior

OUT = data.BASE / 'PG15938-f03-saved-schema-supplement-v1'
PRIOR_PIN = '7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983'
PINS = [
    ('PG10822-global-thread-context-v1', 'ea2f5a8c9056874991de9a40bf9b9395ad1364be0cf3a0aca941257e855758c8', 'dispositions.json', 'dispositionsSha256', 'COORDINATES'),
    ('PG10828-classloader-context-v1', '38fa14db4463903e7485623a1f4d923eb7b93b25a7236543323474b3b36416db', 'dispositions.json', 'dispositionsSha256', 'COORDINATES'),
    ('PG10810-protocol-static-context-v1', '1fd906c89fcff0804b8f4fb6b3644c850b1e9103108b89048246daf2ef1afadb', 'contexts.json', 'contextsSha256', 'ACTUAL_ATTRIBUTES'),
    ('PG10726-json-peek-locale-context-v1', '412995d03337a68d8e8b2ab5f1462bfb429e4bb362d2e11c73444b8438bb6726', 'contexts.json', 'rowsSha256', 'ORIGINAL_FINDING'),
    ('PG13044-reference-identity-context-v2', 'f7345a09e4b83152111b83b56a48534a9223f66f6704df8a6d870adefe5e8d06', 'review.json', 'reviewSha256', 'REVIEWED_ROWS_IDENTITY'),
]

def require(ok, message):
    if not ok:
        raise ValueError(message)

def decode(schema, row, original_findings):
    if schema == 'COORDINATES':
        require(row['productTestsExecuted'] == 0 and row['qualityGatePass'] is False and row['dynamicAuthorizationUnchanged'] is True, 'static disposition only')
        return row['path'], row['sourceSha256'], row['rule'], row['coordinates']
    if schema == 'ACTUAL_ATTRIBUTES':
        require(row['newProductExecutions'] == 0 and row['rawSuppressed'] is row['reviewIsNewTestExecution'] is False, 'static protocol context only')
        return row['path'], row['sourceSha256'], row['rule'], row['actualAttributes']
    if schema == 'ORIGINAL_FINDING':
        require(row['productTestsExecuted'] == 0 and row['dynamicQualification'] is False, 'static JSON context only')
        original = row['originalFinding']
        return original['path'], row['sourceSha256'], original['rule'], original['attributes']
    require(schema == 'REVIEWED_ROWS_IDENTITY', 'explicit known schema')
    require(row['manualPurposeReviewComplete'] is True and row['dynamicExecutionQualificationInferred'] is False and row['actualViolation'] is None, 'identity purpose review is not runtime or actual violation')
    original = original_findings[row['id']]
    attrs = original['attributes']
    require(row['operator'] in ('EQUAL_TO', 'NOT_EQUAL_TO') and row['originalLine'] == int(attrs['beginline']) and row['originalColumn'] == int(attrs['begincolumn']), 'fixed identity finding coordinates')
    if row['astLine'] != row['originalLine'] or row['astColumn'] != row['originalColumn']:
        return None
    return row['path'], row['sourceSha256'], original['rule'], attrs

def main():
    invocation = capture(__file__)
    require(not OUT.exists(), 'new-only')
    p = data.read_checked(prior.OUT / 'manifest.json', PRIOR_PIN)
    require(p['source'] == prior.SOURCE and p['actualExit'] == 0 and p['observationCount'] == 1491, 'current original observation ledger')
    rows = data.read_checked(prior.OUT / 'current-main-observations.json', p['observationsSha256'])
    hashes = data.read_checked(prior.OUT / 'main-source-inputs.json', p['sourceInputsSha256'])
    require(all(data.sha((data.ROOT / x).read_bytes()) == h for x, h in hashes.items()), 'same current965 source bytes')
    original_findings = {r['id']: r for r in data.read_checked(data.BASE / 'PG10690-current-global-static-post-v1/findings.json', '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')}
    matched = collections.defaultdict(list)
    row_keys = {prior.signature(r) for r in rows}
    inputs = []
    rejected = collections.Counter()
    for folder, pin, filename, key, schema in PINS:
        m = data.read_checked(data.BASE / folder / 'manifest.json', pin)
        require(m['actualExit'] == 0, 'saved successful metadata review')
        value = data.read_checked(data.BASE / folder / filename, m[key])
        rr = value['reviewedRows'] if schema == 'REVIEWED_ROWS_IDENTITY' else value
        require(isinstance(rr, list), 'explicit saved list schema')
        count = 0
        for ordinal, row in enumerate(rr):
            path = row.get('path', row.get('originalFinding', {}).get('path'))
            if path not in hashes:
                rejected['OUTSIDE_MAIN_DOMAIN'] += 1
                continue
            if row.get('sourceSha256') != hashes[path]:
                rejected['SOURCE_BYTE_MISMATCH'] += 1
                continue
            decoded = decode(schema, row, original_findings)
            if decoded is None:
                rejected['IDENTITY_AST_ORIGINAL_COORDINATE_DIFFERENCE'] += 1
                continue
            path, digest, rule, attrs = decoded
            candidate = prior.signature(dict(path=path, sourceSha256=digest, rule=rule, attributes=attrs))
            if candidate not in row_keys:
                rejected['NO_EXACT_CURRENT_RAW_COORDINATE'] += 1
                continue
            matched[candidate].append(dict(manifest=folder + '/manifest.json', manifestSha256=pin, file=filename,
                fileSha256=m[key], schema=schema, rowOrdinal=ordinal, originalId=row.get('id', row.get('originalFindingId', row.get('originalFinding', {}).get('id'))),
                meaning='EXISTING_STATIC_REFERENCE_ONLY_NO_NEW_REVIEW_OR_APPLICABILITY_PASS'))
            count += 1
        inputs.append(dict(manifest=folder + '/manifest.json', sha256=pin, file=filename, fileSha256=m[key], schema=schema, inputRows=len(rr), matchedRows=count))
    supplement = [dict(id=r['staticObservationId'], path=r['path'], sourceSha256=r['sourceSha256'], attributes=r['attributes'], rule=r['rule'], addedReferences=matched[prior.signature(r)], originalReferencesUnchanged=True) for r in rows if prior.signature(r) in matched]
    new_ids = {r['staticObservationId'] for r in rows if not r['contextReferences'] and prior.signature(r) in matched}
    remaining = [dict(id=r['staticObservationId'], path=r['path'], sourceSha256=r['sourceSha256'], rule=r['rule'], attributes=r['attributes']) for r in rows if not r['contextReferences'] and r['staticObservationId'] not in new_ids]
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'reference-supplement.json', supplement)
    data.write(OUT / 'remaining-selected-review-queue.json', remaining)
    data.write(OUT / 'manifest.json', dict(actualExit=0, source=prior.SOURCE, invocation=invocation,
        priorObservationManifestSha256=PRIOR_PIN, priorObservationsSha256=p['observationsSha256'], fixedInputs=inputs,
        originalObservationCount=1491, priorReferenced=283, priorUnreferenced=1208, newReferenceConnections=len(new_ids),
        referenceSupplementOccurrences=len(supplement), combinedReferenced=283 + len(new_ids), remainingSelectedUnreferenced=len(remaining),
        referencesSha256=data.sha((OUT / 'reference-supplement.json').read_bytes()), queueSha256=data.sha((OUT / 'remaining-selected-review-queue.json').read_bytes()),
        rejectedRows=dict(rejected), newManualReviews=0, referenceIsApplicabilityPass=False, unknownSchemasGuessed=False,
        rawObservationsModified=False, oldRuntimeTransferred=False, newAccepted=0, formalUpdated=False, effortPercent=None,
        wholeF03Accepted=False, whole451Accepted=False, productTestsExecuted=0, analyzerReexecuted=False, externalActions=0))
    print(data.sha((OUT / 'manifest.json').read_bytes()))
    print(json.dumps(dict(actualExit=0, newReferenceConnections=len(new_ids), combinedReferenced=283 + len(new_ids), remaining=len(remaining))))

if __name__ == '__main__':
    main()
