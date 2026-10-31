"""Lossless saved ResourceScope review/reference join; no Product or analyzer execution."""
from collections import Counter, defaultdict
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pmd_diagnostic_identity import diagnostic_row

SOURCE = '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT = data.BASE / 'PG17152-storage-pmd-identity-join-v1'
MAIN = 'src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/ResourceScope.java'
MAIN_PIN = '639d3e7a51ad7d4fd2b45a9d5b8f7536ece257f08b0db9955249704009d00bbf'
PINS = {
    'analysis': ('PG14664-storage-two-qualified-main-static-v1', '4fb789834a8906d782f42acda3d8dc8a41cf403be5bb9938dbdfeacc025100a2'),
    'review': ('PG14665-storage-resource-eighteen-context-review-v1', 'cfa9dd6df1b5dba34bec67b2d922e5073a2a5342477e217645f919eff9a485fd'),
    'reviewPost': ('PG14667-storage-resource-eighteen-context-post-v1', '215f05a23772d089a00daac25bede611ecdf4bc009fc4a40fee417912e318be3'),
    'current': ('PG15930-f03-current-main-review-join-v2', '7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983'),
    'prior': ('PG16075-four-repository-saved-reference-join-v2', '44b10dd7416d940b650c77325dd48e195fdf2dacc749fa98e75b063464bc874d'),
}


def key(row):
    return json.dumps([row['path'], row['sourceSha256'], row['rule'], row['attributes'], row['message']], sort_keys=True)


def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    manifests = {name: data.read_checked(data.BASE / folder / 'manifest.json', pin) for name, (folder, pin) in PINS.items()}
    assert all(v['actualExit'] == 0 and v['source'] == SOURCE for v in manifests.values())
    a, r, p, c, prior = [manifests[k] for k in ('analysis', 'review', 'reviewPost', 'current', 'prior')]
    assert a['qualityGateExit'] == 1 and r['qualityGatePass'] is False and r['actualApplicableViolations'] is None
    assert p['actualExit'] == 0 and r['rawFindingRows'] == r['reviewedRows'] == 18
    assert data.sha((data.ROOT / MAIN).read_bytes()) == MAIN_PIN
    raw = data.read_checked(data.BASE / PINS['analysis'][0] / 'findings.json', a['findingsSha256'])
    reviews = data.read_checked(data.BASE / PINS['review'][0] / 'review.json', r['reviewSha256'])
    observations = data.read_checked(data.BASE / PINS['current'][0] / 'current-main-observations.json', c['observationsSha256'])
    pending = data.read_checked(data.BASE / PINS['prior'][0] / 'remaining-selected-review-queue.json', prior['queueSha256'])
    assert len(pending) == 785 and prior['combinedPurposeOrReferenceRows'] == 706 and prior['combinedSelectedReferences'] == 610
    selected = [v for v in observations if v['path'] == MAIN]
    assert len(raw) == len(reviews) == len(selected) == 18
    assert Counter(key(v) for v in raw) == Counter(key(v) for v in selected) == Counter(key(v['raw']) for v in reviews)
    assert all(v['sourceSha256'] == MAIN_PIN and not v['contextReferences'] and v['actualViolation'] is None for v in selected)
    assert all(v['qualityGatePass'] is False and v['rawRetained'] is True and v['currentWholeJoinPending'] is True for v in reviews)
    xml_bytes = (data.BASE / PINS['analysis'][0] / 'pmd.xml').read_bytes()
    assert data.sha(xml_bytes) == a['reports']['pmd']['sha256']
    nodes = list(ET.fromstring(xml_bytes).iter())
    violations = [node for node in nodes if node.tag.rpartition('}')[2] == 'violation']
    assert len(violations) == 18
    buckets, refs = defaultdict(list), defaultdict(list)
    for ordinal, (node, row) in enumerate(zip(violations, raw), 1):
        assert dict(node.attrib) == row['attributes'] and ''.join(node.itertext()).strip() == row['message']
        buckets[key(row)].append(diagnostic_row(MAIN, MAIN_PIN, node, ordinal))
    for ordinal, row in enumerate(reviews):
        refs[key(row['raw'])].append(dict(reviewOrdinal=ordinal, originalFindingId=row['id'], rowSha256=data.sha(json.dumps(row, sort_keys=True).encode())))
    links = []
    for row in selected:
        signature = key(row)
        candidates = buckets[signature]
        links.append(dict(currentObservationId=row['staticObservationId'], path=MAIN, sourceSha256=MAIN_PIN,
            attributes=row['attributes'], diagnosticTextSha256=data.sha(row['message'].encode()),
            sameCoordinateOccurrence=row['sameCoordinateOccurrence'], multiplicity=len(candidates),
            identityCandidates=candidates, reviewCandidates=refs[signature],
            association='UNIQUE' if len(candidates) == 1 else 'MULTISET_ONLY_NO_INDIVIDUAL_BIJECTION_GUESSED',
            reviewManifest=PINS['review'][0] + '/manifest.json', reviewManifestSha256=PINS['review'][1],
            applicabilityAccepted=False, actualViolation=None, ptExecutionExempt=False))
    ids = {v['currentObservationId'] for v in links}
    assert len(ids) == 18 and {v['id'] for v in pending if v['path'] == MAIN} == ids
    assert len(buckets) == 14 and sum(len(v) - 1 for v in buckets.values()) == 4
    assert len({x['findingId'] for v in buckets.values() for x in v}) == 18
    remaining = [v for v in pending if v['id'] not in ids]
    assert len(remaining) == 767
    for witness in manifests.values():
        verify(witness['invocation'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'links.json', links)
    data.write(OUT / 'remaining-selected-review-queue.json', remaining)
    data.write(OUT / 'manifest.json', dict(actualExit=0, invocation=invocation, source=SOURCE, inputManifestPins=PINS,
        linksSha256=data.sha((OUT / 'links.json').read_bytes()), queueSha256=data.sha((OUT / 'remaining-selected-review-queue.json').read_bytes()),
        newReferenceConnections=18, priorPurposeOrReferenceRows=706, combinedPurposeOrReferenceRows=724,
        priorSelectedReferences=610, combinedSelectedReferences=628, remainingSelectedUnreferenced=767,
        rawRowsRetained=18, uniqueSignatures=14, duplicateOccurrencesRetained=4, localXmlIdentities=18,
        identityOrdinalDomain='PG14664_ORIGINAL_PMD_XML_NOT_GLOBAL_XML', ambiguousIndividualMappingsGuessed=0,
        rawQualityGateExit=1, actualApplicableViolations=None, qualityGatePass=False,
        wholeF03Accepted=False, whole451Accepted=False, formalUpdated=False, newAccepted=0, effortPercent=None,
        productTestsExecuted=0, analyzersReexecuted=False, newManualReviews=0, oldRuntimeTransferred=False,
        sourceChanged=False, rulesOrSuppressionChanged=False, externalActions=0, privateRawRead=False))
    print(data.sha((OUT / 'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
