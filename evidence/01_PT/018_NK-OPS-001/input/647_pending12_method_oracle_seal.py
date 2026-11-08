"""Seal an explicit limited relation set. No test, counter, exec or session aggregation."""
from pathlib import Path
from collections import Counter
import datetime
import hashlib
import json

B = Path('evidence/01_PT/018_NK-OPS-001')
C = B / 'input/645_pending12_method_oracle_seal_scope.json'
O = B / 'evidence/PG24142-pending12-method-oracle-seal-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def checked(ref):
    path = Path(ref['path'])
    assert sha(path) == ref['sha256']
    return load(path)


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    assert not O.exists()
    config = load(C)
    for name, digest in config['inputPins'].items():
        assert sha(Path(name)) == digest
    current = load(Path(config['methodInventory']))
    coverage = load(Path(config['perSourceCoverage']))
    trace = load(Path(config['originalSourceTrace']))
    inventory = load(Path(config['wbsInventory']))
    snapshot = load(Path(config['wbsSnapshot']))
    assert snapshot['inventorySha256'] == sha(Path(config['wbsInventory']))
    artifacts = {v['path']: v for v in inventory['artifacts']}
    selected_sources = {v['sourcePath'] for v in coverage}
    by_physical = {v['physicalKey']: v for v in current if v['sourcePath'] in selected_sources}
    models = []
    expected = set()
    for source in coverage:
        for physical in source['physical']:
            for method in physical['methods']:
                key = physical['physicalKey'], method['name'], method['descriptor']
                models.append(dict(sourcePath=source['sourcePath'], physicalKey=key[0], method=key[1],
                                   descriptor=key[2], status=method['coverageStatus']))
                if method['coverageStatus'] == 'MEASURED_IN_ORIGINAL_RUN':
                    expected.add(key)
    rows, cases, seen = [], set(), set()
    snippets = 0
    for ref in config['reviewRefs']:
        manifest, matrix, scope = checked(ref['manifest']), checked(ref['matrix']), checked(ref['config'])
        assert manifest['source'] == config['source'] and manifest['actualExit'] == 0
        assert manifest['productTestsExecuted'] == manifest['newAcceptance'] == 0
        assert manifest['formalUpdated'] is False and manifest['effortRate'] is None
        assert manifest['wholeG13Accepted'] is False and manifest['whole451Accepted'] is False
        assert manifest['exactAllMethodCasesOrOracleComplete'] is False
        assert ref['config'] == manifest['config'] and len(matrix) == manifest['explicitlyRelatedMethods']
        snippets += manifest['assertionSnippetChecks']
        scopes = scope['subjects'] if 'subjects' in scope else [scope]
        oracle_by_source = {}
        for subject in scopes:
            path = subject.get('mainPath')
            if path is None:
                # The first wrapper scope has two explicit method source paths and shared cases.
                paths = {v['sourcePath'] for v in subject['methods']}
            else:
                paths = {path}
            for path in paths:
                oracle_by_source[path] = {v['testId']: v for v in subject['oracles']}
        for index, row in enumerate(matrix):
            path = row['sourcePath']
            assert path in selected_sources
            candidates = [v for v in by_physical.values()
                          if v['sourcePath'] == path and v['classSha256'] == row['classSha256']]
            if 'className' in row:
                candidates = [v for v in candidates if v['physicalKey'].split(':')[1] == row['className'] + '.class']
            assert len(candidates) == 1
            physical = candidates[0]
            key = physical['physicalKey'], row['method'], row['descriptor']
            assert key in expected and key not in seen
            seen.add(key)
            assert row['sourceSha256'] == physical['sourceSha256']
            assert row['exactAllMethodCasesOrOracleComplete'] is False
            assert row['testIds'] and row['runCases']
            oracles = oracle_by_source[path]
            chosen = [oracles[n] for n in row['testIds']]
            assert {v['runCase'] for v in chosen} == set(row['runCases'])
            cases.update(v.removesuffix('()') for v in row['runCases'])
            owner = artifacts[path]
            assert owner['owner'] == owner['costOwner']
            rows.append(dict(sourcePath=path, physicalKey=key[0], method=key[1], descriptor=key[2],
                             sourceSha256=physical['sourceSha256'], classSha256=physical['classSha256'],
                             canonicalOwner=owner['owner'], costOwner=owner['costOwner'],
                             originalReview=ref['manifest'], originalReviewMatrix=ref['matrix'], reviewRowIndex=index,
                             testIds=row['testIds'], runCaseRefs=row['runCases'],
                             independentExpectations=[dict(testId=v['testId'], caseRef=v['runCase'], expected=v['expected']) for v in chosen],
                             requirementIds=row['requirementIds'], uiRefs=row['uiRefs'], ssRefs=row['ssRefs'],
                             relationStatus='LIMITED_METHOD_TEST_ORACLE_LINK_REVIEWED',
                             exactAllMethodCasesOrOracleComplete=False, caseSpecificCoverageMeasured=False,
                             originalExecOrCounterUnion=False, newAcceptance=0))
    assert seen == expected
    original_cases = {v.removesuffix('()') for row in trace for v in row['executedCaseIds']}
    assert cases == original_cases
    counts = Counter(v['status'] for v in models)
    metrics = dict(sourcePrograms=len(selected_sources), physicalClasses=len(by_physical), allKnownMethodMetadata=len(models),
                   measuredMethodRelations=len(rows), originalCompilerFilteredMethods=counts['ORIGINAL_STANDARD_COMPILER_FILTER_NOT_CLAIMED_EXECUTED'],
                   abstractNoCodeMethods=counts['ABSTRACT_NO_CODE'], originalIndependentProofGroups=len({v['proof']['path'] for v in trace}),
                   originalUniqueCaseRefs=len(cases), reviewGroups=len(config['reviewRefs']), assertionSnippetChecks=snippets)
    assert metrics == config['expected']
    O.mkdir()
    write(O / 'method-oracle-relations.json', sorted(rows, key=lambda v: (v['physicalKey'], v['method'], v['descriptor'])))
    write(O / 'method-status-boundary.json', sorted(models, key=lambda v: (v['physicalKey'], v['method'], v['descriptor'])))
    write(O / 'manifest.json', dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(), source=config['source'],
          config={'path': str(C), 'sha256': sha(C)}, **metrics, relationKeyMissing=0, relationKeyDuplicate=0,
          boundedRelationCompletenessVerified=True, fullOracleOrScopeAcceptance=False, caseSpecificCoverageMeasured=False,
          sourceResponsibilityDoesNotImplyRequirementAcceptance=True, originalExecOrCounterUnion=False,
          productTestsExecuted=0, newUniqueTests=0, compilerOrJvmExecuted=False, actualBackendActions=0,
          wholeG13Accepted=False, whole451Accepted=False, newAcceptance=0, formalUpdated=False, effortRate=None,
          files={p.name: sha(p) for p in O.iterdir()}, tool={'path': str(Path(__file__)), 'sha256': sha(Path(__file__))}))
    print(json.dumps(dict(actualExit=0, **metrics, manifestSha256=sha(O / 'manifest.json'))))


if __name__ == '__main__':
    main()
