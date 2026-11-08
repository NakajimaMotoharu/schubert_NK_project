"""Independently join frozen hand-written scopes to current declarations, then verify the seal."""
from pathlib import Path
from collections import Counter
import copy
import datetime
import hashlib
import json

B = Path('evidence/01_PT/018_NK-OPS-001')
C = B / 'input/645_pending12_method_oracle_seal_scope.json'
P = B / 'evidence/PG24142-pending12-method-oracle-seal-v1'
O = B / 'evidence/PG24144-pending12-method-oracle-independent-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def checked(ref):
    p = Path(ref['path'])
    assert sha(p) == ref['sha256']
    return load(p)


def key(row):
    return row['physicalKey'], row['method'], row['descriptor']


def validate(rows, manifest, expected, cases, metrics):
    assert type(rows) is list and len(rows) == len(expected)
    assert len({key(v) for v in rows}) == len(rows)
    actual_cases = set()
    for row in rows:
        assert key(row) in expected
        value = expected[key(row)]
        for field in ['sourcePath', 'sourceSha256', 'classSha256', 'canonicalOwner', 'costOwner',
                      'testIds', 'runCaseRefs', 'independentExpectations', 'originalReview', 'originalReviewMatrix']:
            assert row[field] == value[field], field
        assert row['requirementIds'] and row['uiRefs'] and row['ssRefs']
        assert row['exactAllMethodCasesOrOracleComplete'] is False
        assert row['caseSpecificCoverageMeasured'] is False and row['originalExecOrCounterUnion'] is False
        assert type(row['newAcceptance']) is int and row['newAcceptance'] == 0
        actual_cases.update(v.removesuffix('()') for v in row['runCaseRefs'])
    assert actual_cases == cases
    for name, value in metrics.items():
        assert type(manifest[name]) is int and manifest[name] == value
    assert manifest['boundedRelationCompletenessVerified'] is True
    for name in ['fullOracleOrScopeAcceptance', 'caseSpecificCoverageMeasured', 'originalExecOrCounterUnion',
                 'compilerOrJvmExecuted', 'wholeG13Accepted', 'whole451Accepted', 'formalUpdated']:
        assert manifest[name] is False
    for name in ['productTestsExecuted', 'newUniqueTests', 'actualBackendActions', 'newAcceptance',
                 'relationKeyMissing', 'relationKeyDuplicate']:
        assert type(manifest[name]) is int and manifest[name] == 0
    assert manifest['effortRate'] is None


def main():
    assert not O.exists()
    cfg = load(C)
    for path, pin in cfg['inputPins'].items():
        assert sha(Path(path)) == pin
    inventory = load(Path(cfg['wbsInventory']))
    owners = {v['path']: (v['owner'], v['costOwner']) for v in inventory['artifacts']}
    models = load(Path(cfg['methodInventory']))
    statuses = load(Path(cfg['perSourceCoverage']))
    original_trace = load(Path(cfg['originalSourceTrace']))
    source_names = {v['mainPath'] for v in original_trace}
    selected = [v for v in models if v['sourcePath'] in source_names]
    expected, all_cases = {}, set()
    for ref in cfg['reviewRefs']:
        subject_scope = checked(ref['config'])
        review = checked(ref['manifest'])
        assert review['actualExit'] == 0 and review['source'] == cfg['source']
        groups = subject_scope['subjects'] if 'subjects' in subject_scope else [subject_scope]
        for group in groups:
            oracles = {v['testId']: v for v in group['oracles']}
            for definition in group['methods']:
                path = definition['sourcePath'] if 'sourcePath' in definition else group['mainPath']
                possible = [v for v in selected if v['sourcePath'] == path]
                if 'className' in definition:
                    possible = [v for v in possible if v['physicalKey'].split(':')[1][:-6] == definition['className']]
                possible = [v for v in possible if any(m['name'] == definition['method'] and m['descriptor'] == definition['descriptor']
                                                      and m['hasCode'] for m in v['structure']['methods'])]
                assert len(possible) == 1
                physical = possible[0]
                identity = physical['physicalKey'], definition['method'], definition['descriptor']
                assert identity not in expected
                chosen = [oracles[v] for v in definition['testIds']]
                assert {v['runCase'] for v in chosen} == set(definition['runCases'])
                expected[identity] = dict(sourcePath=path, sourceSha256=physical['sourceSha256'],
                     classSha256=physical['classSha256'], canonicalOwner=owners[path][0], costOwner=owners[path][1],
                     testIds=definition['testIds'], runCaseRefs=definition['runCases'],
                     independentExpectations=[dict(testId=v['testId'], caseRef=v['runCase'], expected=v['expected']) for v in chosen],
                     originalReview=ref['manifest'], originalReviewMatrix=ref['matrix'])
                all_cases.update(v['runCase'].removesuffix('()') for v in chosen)
    boundary = []
    measured = set()
    for source in statuses:
        for physical in source['physical']:
            for method in physical['methods']:
                record = dict(sourcePath=source['sourcePath'], physicalKey=physical['physicalKey'],
                              method=method['name'], descriptor=method['descriptor'], status=method['coverageStatus'])
                boundary.append(record)
                if method['coverageStatus'] == 'MEASURED_IN_ORIGINAL_RUN':
                    measured.add(key(record))
    assert set(expected) == measured
    assert all_cases == {v.removesuffix('()') for row in original_trace for v in row['executedCaseIds']}
    count = Counter(v['status'] for v in boundary)
    metrics = dict(sourcePrograms=len(source_names), physicalClasses=len(selected), allKnownMethodMetadata=len(boundary),
                   measuredMethodRelations=len(expected), originalCompilerFilteredMethods=count['ORIGINAL_STANDARD_COMPILER_FILTER_NOT_CLAIMED_EXECUTED'],
                   abstractNoCodeMethods=count['ABSTRACT_NO_CODE'], originalIndependentProofGroups=len({v['proof']['path'] for v in original_trace}),
                   originalUniqueCaseRefs=len(all_cases), reviewGroups=len(cfg['reviewRefs']),
                   assertionSnippetChecks=sum(checked(v['manifest'])['assertionSnippetChecks'] for v in cfg['reviewRefs']))
    assert metrics == cfg['expected']
    manifest = load(P / 'manifest.json')
    for name, pin in manifest['files'].items():
        assert sha(P / name) == pin
    rows = load(P / 'method-oracle-relations.json')
    actual_boundary = load(P / 'method-status-boundary.json')
    assert actual_boundary == sorted(boundary, key=lambda v: key(v))
    validate(rows, manifest, expected, all_cases, metrics)
    negatives = []
    for label, alter in [
        ('missing', lambda r, m: r.pop()), ('duplicate', lambda r, m: r.append(copy.deepcopy(r[0]))),
        ('wrong-descriptor', lambda r, m: r[0].update(descriptor='()X')),
        ('wrong-source', lambda r, m: r[0].update(sourceSha256='0' * 64)),
        ('wrong-class', lambda r, m: r[0].update(classSha256='0' * 64)),
        ('wrong-owner', lambda r, m: r[0].update(canonicalOwner='WBS-G13.07')),
        ('missing-case', lambda r, m: r[0]['runCaseRefs'].pop()),
        ('missing-expectation', lambda r, m: r[0]['independentExpectations'].pop()),
        ('percase-probe-claim', lambda r, m: r[0].update(caseSpecificCoverageMeasured=True)),
        ('exec-union', lambda r, m: m.update(originalExecOrCounterUnion=True)),
        ('oracle-full-claim', lambda r, m: m.update(fullOracleOrScopeAcceptance=True)),
        ('acceptance', lambda r, m: m.update(newAcceptance=1)),
        ('fake67bool', lambda r, m: m.update(measuredMethodRelations=True)),
        ('filter-count', lambda r, m: m.update(originalCompilerFilteredMethods=0)),
        ('NoCode-claim', lambda r, m: m.update(abstractNoCodeMethods=0)),
        ('case-doublecount', lambda r, m: m.update(originalUniqueCaseRefs=98)),
        ('new-PT', lambda r, m: m.update(productTestsExecuted=96)),
        ('formal', lambda r, m: m.update(formalUpdated=True)),
    ]:
        bad_rows, bad_manifest = copy.deepcopy(rows), copy.deepcopy(manifest)
        alter(bad_rows, bad_manifest)
        try:
            validate(bad_rows, bad_manifest, expected, all_cases, metrics)
        except AssertionError:
            negatives.append(label)
        else:
            raise AssertionError(label)
    O.mkdir()
    result = dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(), source=cfg['source'], **metrics,
                  producerManifest={'path': str(P / 'manifest.json'), 'sha256': sha(P / 'manifest.json')},
                  metadataNegativeChecks=negatives, boundedRelationCompletenessVerified=True,
                  fullOracleOrScopeAcceptance=False, caseSpecificCoverageMeasured=False, originalExecOrCounterUnion=False,
                  productTestsExecuted=0, newUniqueTests=0, actualBackendActions=0, wholeG13Accepted=False,
                  whole451Accepted=False, newAcceptance=0, formalUpdated=False, effortRate=None,
                  verifier={'path': str(Path(__file__)), 'sha256': sha(Path(__file__))})
    (O / 'manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(actualExit=0, measuredMethodRelations=67, originalCases=96,
                         metadataNegatives=len(negatives), manifestSha256=sha(O / 'manifest.json'))))


if __name__ == '__main__':
    main()
