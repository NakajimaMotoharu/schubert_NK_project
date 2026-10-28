"""Independent four current source/span mappings, ownership reasoning and metadata-only negatives."""
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from f03_literal_batch_sources import tokens
import pg13633_repository_resource_context_recovery as primary

OUT = data.BASE/'PG13637-repository-resource-context-post-recovery-v3'
PIN = 'ad792dd4e5b1b81d24476c98144099b86c974ba46dcd3ba81d1d7a5ca2428aab'

def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    m = data.read_checked(primary.OUT/'manifest.json', PIN)
    review = data.read_checked(primary.OUT/'review.json', m['reviewSha256'])
    normal = data.read_checked(data.BASE/primary.NORMAL[0]/'manifest.json', primary.NORMAL[1])
    measurement = data.read_checked(data.BASE/primary.MEASURED[0]/'manifest.json', primary.MEASURED[1])
    measured = data.read_checked(data.BASE/primary.MEASURED[0]/'findings.json', measurement['findingsSha256'])
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json', '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    assert review['source'] == m['source'] == normal['source'] == primary.SOURCE
    expected_map = {'PMD-00386': ('AsyncJobCountRepository', 'statement'), 'PMD-00387': ('AsyncJobCountRepository', 'rows'),
                    'PMD-00388': ('OutboxObservationRepository', 'statement'), 'PMD-00389': ('OutboxObservationRepository', 'rows')}

    def validate(row):
        stem, variable = expected_map[row['id']]
        path = primary.BASE+stem+'.java'
        text = (data.ROOT/path).read_text()
        original_row, = [r for r in original if r['id'] == row['id']]
        measured_row, = [r for r in measured if r['path'] == path and r['attributes'].get('variable') == variable]
        attrs = measured_row['attributes']
        lines = text.splitlines(keepends=True)
        start = sum(map(len, lines[:int(attrs['beginline'])-1])) + int(attrs['begincolumn'])-1
        end = sum(map(len, lines[:int(attrs['endline'])-1])) + int(attrs['endcolumn'])-1
        assert text[start:end] == variable and text[start:end+1] != variable
        expected = dict(path=path, source=primary.SOURCE, sourceSha256=primary.PATHS[path], attributes=attrs,
            originalRowSha256=original_row['rowSha256'], sourceSpanSha256=data.sha(text[start:end].encode()),
            spanConvention='PMD_1_ORIGIN_EXCLUSIVE_END_TO_PYTHON_HALF_OPEN', spanStartOffset=start, spanEndOffsetExclusive=end,
            ownership=primary.ownership(text), canonicalOwner='WBS-P018-09', canonicalCostOwner='WBS-P018-09',
            disposition='CONTEXT_NOT_APPLICABLE', reason=primary.REASON, rawRetained=True, currentWholeJoinPending=True,
            productTestsExecuted=0, historicalRuntimeTransferred=False, currentRuntimeQualification=False)
        if any(json.dumps(row.get(k), sort_keys=True) != json.dumps(v, sort_keys=True) for k, v in expected.items()):
            raise ValueError('exact retained diagnostic, half-open source span and current static context required')
        assert data.sha(text.encode()) == measured_row['sourceSha256'] == normal['begin']['inputHashes'][path] == primary.PATHS[path]
        body = ''.join(tokens(text))
        for name in ['statement', 'rows']:
            assert body.count('try('+name+'){') == 1
            assert body.index('if('+name+'==null)thrownewSQLException(INVALID);') < body.index('try('+name+'){')
        assert body.index('try(statement){') < body.index('try(rows){')

    rows = review['rows']
    assert len(rows) == 4 and {r['id'] for r in rows} == set(expected_map)
    for row in rows:
        validate(row)
    labels = []
    for key, value in [('source', '0'*40), ('spanEndOffsetExclusive', rows[0]['spanEndOffsetExclusive']+1),
                       ('sourceSpanSha256', '0'*64), ('canonicalCostOwner', 'WBS-F03'), ('reason', ''),
                       ('rawRetained', False), ('currentRuntimeQualification', True), ('currentWholeJoinPending', False),
                       ('productTestsExecuted', False), ('ownership', {})]:
        bad = copy.deepcopy(rows[0])
        bad[key] = value
        assert json.dumps(bad, sort_keys=True) != json.dumps(rows[0], sort_keys=True)
        try:
            validate(bad)
        except ValueError:
            labels.append(key)
        else:
            raise AssertionError('false current static qualification accepted')
    source_negatives = 0
    for path in primary.PATHS:
        text = (data.ROOT/path).read_text()
        assert primary.ownership(' '.join(tokens(text))) == primary.ownership(text)
        for before, after in [('if (statement == null)', 'if (statement != null)'), ('if (rows == null)', 'if (rows != null)'),
                              ('try (statement)', 'try (rows)'), ('try (rows)', 'try (statement)')]:
            assert text.count(before) == 1
            changed = text.replace(before, after, 1)
            try:
                primary.ownership(changed)
            except (AssertionError, ValueError):
                source_negatives += 1
            else:
                raise AssertionError('wrong guard/alias ownership source accepted')
    assert source_negatives == 8
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json', dict(actualExit=0, source=primary.SOURCE, invocation=invocation,
        reviewManifestSha256=PIN, sourceContexts=4, newSourceReasons=4, rawRetained=4,
        metadataNegativeVectors=len(labels), metadataLabels=labels, sourceOwnershipNegativeVectors=source_negatives,
        productTestsExecuted=0, coverage=None, oldRuntimeTransferred=False, sourceChanged=False,
        newAccepted=0, formalUpdated=False, whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
