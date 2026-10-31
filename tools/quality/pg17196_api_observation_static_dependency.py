"""Static four-Main review and 134 NOT_RUN bindings, never a dynamic qualification."""
from collections import Counter
import copy
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT = data.BASE / 'PG17196-api-observation-static-dependency-v1'
NORMAL = data.ROOT.parent / 'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/manifest.safe.json'
NORMAL_PIN = '1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
REG = ('PG17186-current2616-morning-terminal-observation-registry-v1', '1002c01948b4af7ff64030c999c31df682775f2461c194d052d4904186ed18d4')
COUNTS = {'OwnedApiObservationWorkerTest': 44, 'ApiOutboxObservationPumpTest': 32,
          'ApiReadOnlyObservationAttemptTest': 32, 'ApiObservationContextTest': 26}
MAIN_CALLS = {'OwnedApiObservationWorker': 5, 'ApiOutboxObservationPump': 0,
              'ApiReadOnlyObservationAttempt': 2, 'ApiObservationContext': 2}
STATUS = 'NOT_RUN_KNOWN_HELD_HELPER_DEPENDENCY'


def assess(value, rows, expected):
    assert value['source'] == SOURCE and type(value['productTestsExecuted']) is int and value['productTestsExecuted'] == 0
    assert value['candidateDeclaredMethods'] == 134 and value['candidateWholeSuites'] == 4
    assert value['reviewedMainSources'] == 4 and value['dynamicQualification'] is False
    assert value['coverage'] is None and value['newAccepted'] == 0 and value['formalUpdated'] is False
    assert value['currentWholeTestSemanticReviewComplete'] is False and value['oldRuntimeTransferred'] is False
    assert rows == expected and len(rows) == len({(r['className'], r['method']) for r in rows}) == 134
    assert all(r['dynamicStatus'] == STATUS and r['actualResult'] is None and r['coverage'] is None for r in rows)


def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    normal = data.read_checked(NORMAL, NORMAL_PIN)
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    r = data.read_checked(data.BASE / REG[0] / 'manifest.json', REG[1])
    ref = r['currentOrdinaryTestDeclarationReference']
    folder = data.BASE / 'PG15950-g13-current-test-declaration-inventory-v1'
    inventory = data.read_checked(folder / 'manifest.json', ref['inventoryManifestSha256'])
    all_rows = data.read_checked(folder / 'exact-ordinary-bindings.json', inventory['files']['exact-ordinary-bindings.json'])
    selected = [v for v in all_rows if v['className'] in {'dev.codex.schubert.nk.api.monitoring.' + n for n in COUNTS}]
    assert Counter(v['className'].rsplit('.', 1)[1] for v in selected) == COUNTS
    assert not {(v['className'], v['method']) for v in selected} & {(v['classname'], v['name']) for v in r['cases']}
    test_hashes = {}
    for row in selected:
        path = row['path']
        assert row['sourceSha256'] == normal['begin']['inputHashes'][path] == data.sha((data.ROOT / path).read_bytes())
        test_hashes[path] = row['sourceSha256']
    prefix = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/'
    mains = {}
    for name, calls in MAIN_CALLS.items():
        path = prefix + name + '.java'; text = (data.ROOT / path).read_text()
        digest = data.sha(text.encode())
        assert digest == normal['begin']['inputHashes'][path]
        found = [dict(line=text[:m.start()].count('\n') + 1, method=m.group(1))
                 for m in re.finditer(r'TemporaryInfrastructureException\.(attachSecondary|preserveFatal)\(', text)]
        assert len(found) == calls
        mains[path] = dict(sha256=digest, fullSourceReadForStaticReview=True, heldHelperCalls=found,
                           dynamicTestEligibility=STATUS, productCodeChanged=False)
    intermediate = data.ROOT / (prefix + 'ApiOutboxObservationSource.java')
    intermediate_text = intermediate.read_text()
    assert data.sha(intermediate.read_bytes()) == normal['begin']['inputHashes'][str(intermediate.relative_to(data.ROOT))]
    assert 'Optional.of(attempt.read())' in intermediate_text
    old = data.read_checked(data.BASE / 'PG9610-observation-worker44-oracle-trace-v1/manifest.json', 'e2d953b07c08be7c455724b1b1d001fd0e45ef8819a2525a15eb6c6002f6e286')
    old_main = {p: h for p, h in old['sourceHashes'].items() if '/src/main/' in p}
    assert len(old_main) == 3 and all(mains[p]['sha256'] == h for p, h in old_main.items())
    changed_old_tests = [p for p, h in old['sourceHashes'].items() if '/src/test/' in p and normal['begin']['inputHashes'].get(p) != h]
    assert len(changed_old_tests) == 4
    design = {}
    for number in ('311', '332', '342', '351'):
        paths = list((data.ROOT / 'documents/300_SS').glob('*/' + number + '_*.md')); assert len(paths) == 1
        path = paths[0]; relative = str(path.relative_to(data.ROOT)); blob = path.read_bytes()
        assert blob == subprocess.check_output(['git', 'show', 'origin/main:' + relative], cwd=data.ROOT)
        design[relative] = data.sha(blob)
    rows = [dict(className=v['className'], method=v['method'], path=v['path'], sourceSha256=v['sourceSha256'],
                 dynamicStatus=STATUS, actualResult=None, coverage=None, reason='CURRENT_MAIN_TRANSITIVE_KNOWN_HELD_HELPER_NO_PARTIAL_EXTRACTION') for v in selected]
    value = dict(actualExit=0, invocation=invocation, source=SOURCE, normalManifestSha256=NORMAL_PIN,
        registryManifestSha256=REG[1], currentDeclarationInventorySha256=ref['inventoryManifestSha256'],
        reviewedMainSources=4, currentWholeTestSemanticReviewComplete=False, candidateDeclaredMethods=134,
        candidateWholeSuites=4, productTestsExecuted=0, dynamicQualification=False, coverage=None,
        oldMainStaticBytesEquivalent=old_main, oldTestOracleReuseRejectedPaths=changed_old_tests,
        heldHelperCallsTotal=9, currentOriginalRefusalTargetIdentified=False, oldRuntimeTransferred=False,
        sourceChanged=False, actualVmActions=0, actualDatabaseActions=0, actualServiceActions=0,
        actualThreadStarts=0, actualCredentialOperations=0, privateRawRead=False,
        newAccepted=0, formalUpdated=False, wholeF03Accepted=False, whole451Accepted=False, effortPercent=None)
    assess(value, rows, rows)
    negatives = 0
    for key, replacement in [('productTestsExecuted', 134), ('dynamicQualification', True), ('source', 'old'),
                             ('coverage', {'LINE': 100}), ('newAccepted', 4), ('oldRuntimeTransferred', True),
                             ('currentWholeTestSemanticReviewComplete', True)]:
        bad = copy.deepcopy(value); bad[key] = replacement
        try:
            assess(bad, rows, rows)
        except AssertionError:
            negatives += 1
        else:
            raise ValueError('static evidence promoted to dynamic qualification')
    for altered in (rows[:-1], rows + rows[:1], [dict(rows[0], actualResult='PASS'), *rows[1:]]):
        try:
            assess(value, altered, rows)
        except AssertionError:
            negatives += 1
        else:
            raise ValueError('case missing/duplicated/fake PASS accepted')
    verify(invocation); OUT.mkdir()
    data.write(OUT / 'not-run-methods.json', rows)
    data.write(OUT / 'main-review-dependencies.json', dict(mains=mains, originalTestHashes=test_hashes,
        pumpIntermediateSourceSha256=data.sha(intermediate.read_bytes()), approvedDesignHashes=design))
    value.update(independentMetadataNegativeVectors=negatives,
        methodsSha256=data.sha((OUT / 'not-run-methods.json').read_bytes()),
        reviewsSha256=data.sha((OUT / 'main-review-dependencies.json').read_bytes()))
    data.write(OUT / 'manifest.json', value)
    print(data.sha((OUT / 'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
