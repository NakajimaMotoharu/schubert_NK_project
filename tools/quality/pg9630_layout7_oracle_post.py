"""Independent frozen method/ID relations, public artifact bytes, and fixture-only reuse limits."""
import datetime as dt
import json
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

BASE = data.BASE
SUBJECT = BASE / 'PG9628-layout7-oracle-trace-v2'
OUT = BASE / 'PG9630-layout7-oracle-post-v1'
EXPECTED = {
    'registryMatchesIndependentUi233Catalog': ['L01', 'L03'],
    'registryRejectsEmptyNullDuplicateAndKindMismatches': ['L02'],
    'layoutDefinitionChecksEveryLengthAndKindInvariant': ['L02'],
    'layoutIdAndFieldDefinitionAreStrictAndOneBased': ['F01', 'L02'],
    'catalogMatchesIndependentUi234To236Fixture': ['F02', 'L03'],
    'parserRejectsMalformedUnknownAndDuplicateRows': ['F03'],
    'layoutFieldsRejectWrongAreaGapLengthAndNull': ['F03', 'F01'],
}


def relations(records):
    result = []
    for record in records:
        method = record['method']['method']
        for reference in record['oracleReferences']:
            result.append((method, reference['testId']))
    if len(result) != len(set(result)):
        raise ValueError('duplicate method-family relation')
    expected = {(method, 'PT-PRO-001-' + identifier) for method, ids in EXPECTED.items() for identifier in ids}
    if set(result) != expected:
        raise ValueError('missing or unexpected method-family relation')
    return result


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    primary = json.loads((SUBJECT / 'manifest.json').read_bytes())
    assert primary['actualExit'] == 0 and primary['source'] == data.SOURCE
    records = data.read_checked(SUBJECT / 'method-oracle-review.json', primary['methodOracleReviewSha256'])
    pairs = relations(records)
    assert len(pairs) == 11 and len(set(identifier for _, identifier in pairs)) == 6
    manifest = data.read_checked(BASE / 'PG9592-current-test-method-post-v1/manifest.json',
        'd73ffe203a58ca9fab7f19f0b4baa7b2588fb25ad7e13c75c0c6411f5a719a18')
    methods = data.read_checked(BASE / 'PG9592-current-test-method-post-v1/method-declaration-bindings.json', manifest['bindingsSha256'])
    by_key = {row['methodDeclarationKey']: row for row in methods}
    oracle = (data.ROOT / primary['oraclePath']).read_bytes()
    assert data.sha(oracle) == primary['oracleSha256']
    for record in records:
        method = record['method']
        assert method == by_key[method['methodDeclarationKey']] and not record['productExecuted']
        for ref in record['oracleReferences']:
            row = oracle.decode().splitlines()[ref['line'] - 1]
            assert row.startswith('| ' + ref['testId'] + ' |') and data.sha(row.encode()) == ref['rowSha256']
    for path, digest in primary['sourceHashes'].items():
        assert data.sha((data.ROOT / path).read_bytes()) == data.sha((data.NORMAL / path).read_bytes()) == digest
    for path, digest in primary['canonicalHashes'].items():
        assert data.sha(subprocess.check_output(['git', 'show', primary['canonicalCommit'] + ':' + path], cwd=data.ROOT)) == digest
    assert primary['reusedPureFixtureProofOnly'] and not primary['oldSourceQualifiedOrDynamicTransferred']
    assert primary['currentRegistryLiteralTuples'] == 64 and primary['currentFieldLiteralRows'] == 389
    assert primary['productTestsExecuted'] == primary['newAccepted'] == 0 and primary['coverage'] is None
    # Negative relations use exact current rows; do not execute target code or repeat successful PT.
    rejected = []
    import copy
    for label, edit in [('missing', lambda x: x[0]['oracleReferences'].pop()),
                        ('duplicate', lambda x: x[0]['oracleReferences'].append(copy.deepcopy(x[0]['oracleReferences'][0])))]:
        changed = copy.deepcopy(records)
        edit(changed)
        try:
            relations(changed)
        except ValueError:
            rejected.append(label)
        else:
            raise AssertionError('invalid relation accepted')
    # Prior matrices are recounted from their saved rows, not by replaying prior producers.
    previous = {}
    for directory, expected_methods, expected_relations in [('PG9610-observation-worker44-oracle-trace-v1', 44, 44),
                                                           ('PG9618-header8-oracle-trace-v1', 8, 9)]:
        path = BASE / directory / 'method-oracle-review.json'
        rows = json.loads(path.read_bytes())
        if directory.startswith('PG9610-'):
            assert all(row['existingTestId'] == 'OBSOWN' + str(i).zfill(3) for i, row in enumerate(rows, 1))
            count = len(rows)
        else:
            count = sum(len(row['oracleReferences']) for row in rows)
        assert len(rows) == expected_methods and count == expected_relations
        previous[directory] = dict(methods=len(rows), relations=count, sha256=data.sha(path.read_bytes()), affected=False)
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json', dict(actualExit=0, source=data.SOURCE, timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
        invocation=invocation, subjectManifestSha256=data.sha((SUBJECT / 'manifest.json').read_bytes()),
        methods=7, existingFamilies=6, relations=11, relationCounterexamples=rejected,
        previousMatricesRecounted=previous, semanticReviewIsParentRecord=True,
        literalSourceComparisonIsStaticNotProductionExecution=True, productTestsExecuted=0,
        coverage=None, newAccepted=0, formalUpdated=False, effortPercent=None, wholeG13Accepted=False))
    print(json.dumps(dict(actualExit=0, methods=7, relations=11, previousMatrices=2)))
    print('manifestSha256=' + data.sha((OUT / 'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
