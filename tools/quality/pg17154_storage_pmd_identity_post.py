"""Independent original XML/global-row/reference multiset oracle, metadata only."""
from collections import Counter
import copy
import hashlib
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
RAW = data.BASE / 'PG17152-storage-pmd-identity-join-v1'
PIN = 'd0a07853a00831db903c91b2e462506be251e33df28a622ff4b292e0a5b003c8'
OUT = data.BASE / 'PG17154-storage-pmd-identity-post-v1'


def digest(value):
    return hashlib.sha256(value).hexdigest()


def wire(value):
    return json.dumps(value, sort_keys=True)


def assess(manifest, links, remaining, expected, expected_remaining):
    assert type(manifest['actualExit']) is int and manifest['actualExit'] == 0 and manifest['source'] == SOURCE
    for name, count in dict(newReferenceConnections=18, priorPurposeOrReferenceRows=706, combinedPurposeOrReferenceRows=724,
                            priorSelectedReferences=610, combinedSelectedReferences=628, remainingSelectedUnreferenced=767,
                            rawRowsRetained=18, uniqueSignatures=14, duplicateOccurrencesRetained=4, localXmlIdentities=18,
                            rawQualityGateExit=1, ambiguousIndividualMappingsGuessed=0, productTestsExecuted=0,
                            newManualReviews=0, externalActions=0, newAccepted=0).items():
        assert type(manifest[name]) is int and manifest[name] == count
    for name in ('qualityGatePass', 'wholeF03Accepted', 'whole451Accepted', 'formalUpdated', 'analyzersReexecuted',
                 'oldRuntimeTransferred', 'sourceChanged', 'rulesOrSuppressionChanged', 'privateRawRead'):
        assert manifest[name] is False
    assert manifest['actualApplicableViolations'] is manifest['effortPercent'] is None
    assert manifest['identityOrdinalDomain'] == 'PG14664_ORIGINAL_PMD_XML_NOT_GLOBAL_XML'
    assert wire(links) == wire(expected) and wire(remaining) == wire(expected_remaining)


def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    m = data.read_checked(RAW / 'manifest.json', PIN)
    links = data.read_checked(RAW / 'links.json', m['linksSha256'])
    remaining = data.read_checked(RAW / 'remaining-selected-review-queue.json', m['queueSha256'])
    def saved(name):
        folder, pin = m['inputManifestPins'][name]
        return data.BASE / folder, data.read_checked(data.BASE / folder / 'manifest.json', pin)
    af, a = saved('analysis'); rf, r = saved('review'); cf, c = saved('current'); pf, p = saved('prior')
    assert all(v['actualExit'] == 0 and v['source'] == SOURCE for v in (a, r, c, p))
    xml = (af / 'pmd.xml').read_bytes()
    assert digest(xml) == a['reports']['pmd']['sha256']
    original = [node for node in ET.fromstring(xml).iter() if node.tag.rpartition('}')[2] == 'violation']
    reviews = data.read_checked(rf / 'review.json', r['reviewSha256'])
    current = data.read_checked(cf / 'current-main-observations.json', c['observationsSha256'])
    queue = data.read_checked(pf / 'remaining-selected-review-queue.json', p['queueSha256'])
    path = 'src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/ResourceScope.java'
    sha = '639d3e7a51ad7d4fd2b45a9d5b8f7536ece257f08b0db9955249704009d00bbf'
    assert digest((data.ROOT / path).read_bytes()) == sha and len(original) == len(reviews) == 18
    expected = []
    for row in [v for v in current if v['path'] == path]:
        attrs = row['attributes']
        candidates = []
        for ordinal, node in enumerate(original, 1):
            message = ''.join(node.itertext()).strip()
            if dict(node.attrib) != attrs or message != row['message']:
                continue
            fields = dict(sourcePath=path, sourceSha256=sha, **{k: node.get(k) for k in ('rule', 'beginline', 'endline', 'priority')})
            legacy = 'F03-PMD-' + digest(wire(fields).encode())
            fields.update({k: node.get(k) for k in ('begincolumn', 'endcolumn')})
            fields.update(diagnosticTextSha256=digest(message.encode()), rawXmlOrdinal=ordinal, identitySchema=2)
            candidates.append(dict(findingId='F03-PMD2-' + digest(wire(fields).encode()), legacyFindingId=legacy,
                                   **fields, status='NOT_REVIEWED_CURRENT_SOURCE'))
        refs = [dict(reviewOrdinal=i, originalFindingId=v['id'], rowSha256=digest(wire(v).encode()))
                for i, v in enumerate(reviews) if v['raw']['attributes'] == attrs and v['raw']['message'] == row['message']
                and v['raw']['path'] == path and v['raw']['sourceSha256'] == sha]
        assert candidates and len(refs) == len(candidates)
        expected.append(dict(currentObservationId=row['staticObservationId'], path=path, sourceSha256=sha,
                             attributes=attrs, diagnosticTextSha256=digest(row['message'].encode()),
                             sameCoordinateOccurrence=row['sameCoordinateOccurrence'], multiplicity=len(candidates),
                             identityCandidates=candidates, reviewCandidates=refs,
                             association='UNIQUE' if len(candidates) == 1 else 'MULTISET_ONLY_NO_INDIVIDUAL_BIJECTION_GUESSED',
                             reviewManifest=str((rf / 'manifest.json').relative_to(data.BASE)), reviewManifestSha256=m['inputManifestPins']['review'][1],
                             applicabilityAccepted=False, actualViolation=None, ptExecutionExempt=False))
    ids = {v['currentObservationId'] for v in expected}
    expected_remaining = [v for v in queue if v['id'] not in ids]
    assert len(ids) == 18 and len(expected_remaining) == 767 and Counter(v['multiplicity'] for v in expected) == {1: 10, 2: 8}
    assess(m, links, remaining, expected, expected_remaining)
    mutations = []
    for name, value in [('source', 'old'), ('rawRowsRetained', 17), ('duplicateOccurrencesRetained', 0),
                        ('newReferenceConnections', True), ('rawQualityGateExit', 0), ('qualityGatePass', True),
                        ('actualApplicableViolations', 0), ('wholeF03Accepted', True), ('whole451Accepted', True),
                        ('productTestsExecuted', 26), ('oldRuntimeTransferred', True), ('effortPercent', 1)]:
        changed = copy.deepcopy(m); changed[name] = value
        mutations.append((changed, links, remaining))
    for name in ('sourceSha256', 'diagnosticTextSha256', 'currentObservationId', 'association'):
        changed = copy.deepcopy(links); changed[0][name] = 'incorrect'
        mutations.append((m, changed, remaining))
    for name in ('rawXmlOrdinal', 'begincolumn', 'endcolumn', 'findingId', 'legacyFindingId'):
        changed = copy.deepcopy(links); changed[0]['identityCandidates'][0][name] = 'incorrect'
        mutations.append((m, changed, remaining))
    mutations.extend([(m, links[:-1], remaining), (m, links, remaining[:-1])])
    for args in mutations:
        try:
            assess(*args, expected, expected_remaining)
        except AssertionError:
            pass
        else:
            raise ValueError('mutated metadata accepted')
    verify(m['invocation']); verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json', dict(actualExit=0, invocation=invocation, source=SOURCE,
        primaryManifestSha256=PIN, independentMetadataNegativeVectors=len(mutations), independentlyReconstructedRows=18,
        ambiguousOccurrenceRows=8, duplicateExcessOccurrences=4, productTestsExecuted=0, analyzersReexecuted=False,
        wholeF03Accepted=False, whole451Accepted=False, formalUpdated=False, newAccepted=0, effortPercent=None, externalActions=0))
    print(digest((OUT / 'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
