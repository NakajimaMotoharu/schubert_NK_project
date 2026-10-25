"""Freeze complete current protocol test declarations/classes/fixtures, no target execution."""
from collections import Counter
import json
from pathlib import Path
import subprocess
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

ROOT = data.ROOT
SOURCE = 'fd3d04df5710ca28f0e34f919cbc103e569a607b'
NORMAL = ROOT.parent / 'pgpt-runs/PG379/pg9694-semantic-direct-fixed-six-compile-v1/snapshot'
OUT = ROOT / 'evidence/01_PT/002_NK-PRO-002/evidence/provisional/PG9720-protocol-module-preflight-v1'
PREFIX = 'src/schubert-nk-protocol/'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE / 'PG9694-semantic-direct-fixed-six-compile-v1/manifest.json',
        '7d2e18f86d2bc9e5c61473da8b8924aa7c6668bf8903541d5502902d2dac1d7a')
    assert normal['actualExit'] == 0 and normal['source'] == SOURCE and normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT / p).read_bytes()) == data.sha((NORMAL / p).read_bytes()) == h for p,h in hashes.items())
    assert not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)
    old = data.read_checked(data.BASE / 'PG9592-current-test-method-post-v1/manifest.json',
        'd73ffe203a58ca9fab7f19f0b4baa7b2588fb25ad7e13c75c0c6411f5a719a18')
    binding_path = data.BASE / 'PG9592-current-test-method-post-v1/method-declaration-bindings.json'
    bindings = data.read_checked(binding_path,old['bindingsSha256'])
    rows = [r for r in bindings if r['path'].startswith(PREFIX + 'src/test/java/')]
    assert len(rows) == 96 and len({r['path'] for r in rows}) == 20
    cases = []
    for row in rows:
        assert row['annotationKind'] == 'org.junit.jupiter.api.Test' and row['compiledDescriptor'] == '()V' and row['parameterCount'] == 0
        assert hashes[row['path']] == row['sourceSha256']
        target = NORMAL / PREFIX / 'target/test-classes' / (row['className'].replace('.','/') + '.class')
        assert data.sha(target.read_bytes()) == row['physicalClassSha256']
        cases.append(dict(className=row['className'],method=row['method'],path=row['path'],sourceSha256=hashes[row['path']],
            normalTestClassSha256=data.sha(target.read_bytes()),declarationOriginSource=old['source'],oldDynamicResultTransferred=False))
    for cls,names in {
        'PayloadPaginationBoundaryTest':['page001SecondPageHasIndependentExpectedBounds','page002MaximumEffectivePageKeepsExactNineDigitArithmetic','page003RejectsIndependentRangeAndOneFieldArithmeticChanges'],
        'SemanticDirectBoundaryTest':['sem001PasswordCharacterByteAndUsernameLimits','sem002InclusiveDateLimitsAndOneSidedFilters','sem003QuestionAndWebLogTextContracts']}.items():
        qualified = 'dev.codex.schubert.nk.protocol.layout.' + cls
        path = PREFIX + 'src/test/java/' + qualified.replace('.','/') + '.java'
        target = NORMAL / PREFIX / 'target/test-classes' / (qualified.replace('.','/') + '.class')
        text = (ROOT / path).read_text()
        assert text.count('@Test') == 3 and all(('void ' + name + '()') in text for name in names)
        for name in names:
            cases.append(dict(className=qualified,method=name,path=path,sourceSha256=hashes[path],normalTestClassSha256=data.sha(target.read_bytes()),
                declarationOriginSource=SOURCE,oldDynamicResultTransferred=False))
    assert len(cases) == len({(r['className'],r['method']) for r in cases}) == 102
    source_files = {p for p in hashes if p.startswith(PREFIX + 'src/test/java/') and p.endswith('Test.java')}
    assert {r['path'] for r in cases} == source_files and len(source_files) == 22
    physical_tests = {str(p):data.sha(p.read_bytes()) for p in (NORMAL / PREFIX / 'target/test-classes').rglob('*') if p.is_file()}
    assert physical_tests
    resources = {}
    for path in sorted((ROOT / PREFIX / 'src/test/resources').rglob('*')):
        if path.is_file():
            relative = str(path.relative_to(ROOT))
            target = NORMAL / PREFIX / 'target/test-classes' / path.relative_to(ROOT / PREFIX / 'src/test/resources')
            assert relative in hashes and data.sha(path.read_bytes()) == data.sha(target.read_bytes()) == hashes[relative]
            resources[relative] = dict(sha256=hashes[relative],target=str(target))
    assert len(resources) == 5 and all(p.endswith('.tsv') for p in resources)
    jar = Path(normal['jars']['protocol']['path'])
    assert data.sha(jar.read_bytes()) == normal['jars']['protocol']['sha256']
    with zipfile.ZipFile(jar) as archive:
        main = {n:data.sha(archive.read(n)) for n in archive.namelist() if n.endswith('.class')}
    assert len(main) == 176
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'cases.json',sorted(cases,key=lambda r:(r['className'],r['method'])))
    data.write(OUT / 'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,expectedTests=102,expectedSuites=22,
        normalManifestSha256='7d2e18f86d2bc9e5c61473da8b8924aa7c6668bf8903541d5502902d2dac1d7a',
        casesSha256=data.sha((OUT / 'cases.json').read_bytes()),caseCounts=dict(Counter(r['className'] for r in cases)),
        physicalTestFiles=physical_tests,fixtureFiles=resources,physicalMainClasses=main,
        allCurrentSourceInputHashes=hashes,declarationPriorSha256=data.sha(binding_path.read_bytes()),
        declarationReuseNotProductPtTransfer=True,productTestsExecuted=0,newTestIds=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,expectedTests=102,expectedSuites=22,mainClasses=176,manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
