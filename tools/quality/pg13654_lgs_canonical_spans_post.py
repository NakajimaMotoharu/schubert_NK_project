"""Independent half-open PMD intervals and unchanged legacy reason/case, typed negative metadata."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg13652_lgs_canonical_spans as primary

OUT = data.BASE/'PG13654-lgs-canonical-spans-post-v1'
PIN = 'd8191dc68ec58533062f42b602d71db6767a7facedf819357d962b7fb642e666'

def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    m = data.read_checked(primary.OUT/'manifest.json', PIN)
    corrected = data.read_checked(primary.OUT/'corrections.json', m['correctionsSha256'])
    old_m = data.read_checked(data.BASE/primary.LEGACY[0]/'manifest.json', primary.LEGACY[1])
    legacy = data.read_checked(data.BASE/primary.LEGACY[0]/'review.json', old_m['reviewSha256'])
    originals = {r['id']:r for r in legacy['rows']}
    host = data.read_checked(data.BASE/'PG13604-lgs-remaining-whole-eight-pt-v1/manifest.json', '435f90a3c03be3755a5f1886b979497d1aedc4dc64a454e1edc282929e4f9485')
    assert host['source'] == old_m['source'] == m['source'] == primary.SOURCE
    cases = []
    run = data.ROOT.parent/'pgpt-runs/PG379/pg13604-lgs-remaining-whole-eight-pt-v1'
    for name, sha in host['xmlHashes'].items():
        p = run/'xml'/name
        assert data.sha(p.read_bytes()) == sha
        root = ET.parse(p).getroot()
        assert int(root.get('tests')) == 8 and all(int(root.get(k)) == 0 for k in ['failures','errors','skipped'])
        for node in root.findall('testcase'):
            assert not list(node)
            cases.append((node.get('classname'),node.get('name')))
    assert len(cases) == len(set(cases)) == 8

    def expected(identifier):
        row = originals[identifier]
        text = (data.ROOT/row['path']).read_bytes().decode('utf-8')
        assert data.sha(text.encode()) == row['sourceSha256'] == host['begin']['sourceHashes'][row['path']]
        a = row['attributes']
        lines = text.splitlines(keepends=True)
        start = sum(map(len, lines[:int(a['beginline'])-1])) + int(a['begincolumn'])-1
        end = sum(map(len, lines[:int(a['endline'])-1])) + int(a['endcolumn'])-1
        assert 0 <= start < end < len(text)
        assert row['sourceSpanSha256'] == data.sha(text[start:end+1].encode()) != data.sha(text[start:end].encode())
        witness = copy.deepcopy(row)
        witness['sourceSpanSha256'] = data.sha(text[start:end].encode())
        case = row['currentCase']
        assert (case['classname'],case['name']) in cases and case['result'] == 'PASS'
        return dict(id=identifier, path=row['path'], source=primary.SOURCE, sourceSha256=row['sourceSha256'],
            legacyReviewManifestSha256=primary.LEGACY[1], legacyExtendedWindowSha256=row['sourceSpanSha256'],
            legacyWindowStartOffset=start, legacyWindowEndOffsetExclusive=end+1,
            canonicalSpanStartOffset=start, canonicalSpanEndOffsetExclusive=end,
            canonicalSpanSha256=data.sha(text[start:end].encode()), convention='PMD_1_ORIGIN_EXCLUSIVE_END_TO_PYTHON_HALF_OPEN',
            correctedContextWitness=witness, dispositionReasonAndCaseUnchanged=True, rawRetained=True,
            currentWholeJoinPending=True, productTestsExecuted=0, oldResultsModified=False, oldRuntimeTransferred=False)

    def validate(row):
        if json.dumps(row,sort_keys=True) != json.dumps(expected(row['id']),sort_keys=True):
            raise ValueError('exact canonical interval and unchanged legacy reason/case required')

    rows = corrected['rows']
    assert len(rows) == 2 and {r['id'] for r in rows} == {'PMD-08082','PMD-08083'}
    for row in rows:
        validate(row)
    labels = []
    mutations = [('source',lambda r:r.update(source='0'*40)),
        ('inclusive-end',lambda r:r.update(canonicalSpanEndOffsetExclusive=r['canonicalSpanEndOffsetExclusive']+1)),
        ('hash',lambda r:r.update(canonicalSpanSha256='0'*64)),
        ('reason',lambda r:r['correctedContextWitness'].update(reason='')),
        ('raw',lambda r:r.update(rawRetained=False)),('rewrite-old',lambda r:r.update(oldResultsModified=True)),
        ('global-pending',lambda r:r.update(currentWholeJoinPending=False)),
        ('bool-counter',lambda r:r.update(productTestsExecuted=False))]
    for label, change in mutations:
        bad = copy.deepcopy(rows[0])
        change(bad)
        assert json.dumps(bad,sort_keys=True) != json.dumps(rows[0],sort_keys=True)
        try:
            validate(bad)
        except ValueError:
            labels.append(label)
        else:
            raise AssertionError('incorrect canonical span sidecar accepted')
    verify(old_m['invocation'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0, source=primary.SOURCE, invocation=invocation,
        correctionManifestSha256=PIN, correctedCurrentRows=2, legacyCurrentCaseWitnessUnchanged=True,
        metadataNegativeVectors=len(labels), labels=labels, spanToolVectors=m['spanToolVectors'],
        rawRetained=2, joinedContextWarningsUnchanged=3353, currentWholeJoinPendingUnchanged=2492,
        productTestsExecuted=0, coverage=None, oldResultsModified=False,
        globalHorizontalExpansionComplete=False, newAccepted=0, formalUpdated=False, whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
