"""Bind actual current semantic tests/static to fixed inputs; prior Main static only by whole-byte equality."""
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

ROOT = data.ROOT
WORK = ROOT.parent / 'pgpt-runs/PG379'
BASE = ROOT / 'evidence/01_PT/002_NK-PRO-002/evidence/provisional'
SOURCE = 'fd3d04df5710ca28f0e34f919cbc103e569a607b'
TEST = 'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/layout/SemanticDirectBoundaryTest.java'
NORMAL = WORK / 'pg9694-semantic-direct-fixed-six-compile-v1/snapshot'
OUT = BASE / 'PG9702-semantic-fixed-quality-source-post-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE / 'PG9694-semantic-direct-fixed-six-compile-v1/manifest.json',
        '7d2e18f86d2bc9e5c61473da8b8924aa7c6668bf8903541d5502902d2dac1d7a')
    post = data.read_checked(BASE / 'PG9698-semantic-fixed-post-v1/manifest.json',
        'c4695d0343472bc44e4998c78e5ed331ae7c7cdedfd523e84493df4a7ce99839')
    static = data.read_checked(BASE / 'PG9700-semantic-direct-fixed-static-v1/manifest.json',
        '5c749b367ae03a141e6b6ba256a6900de0980b58d77d21e42af7a81dd0b5abee')
    assert all(v['actualExit'] == 0 and v['source'] == SOURCE for v in (normal,post,static))
    assert normal['testsExecuted'] == 0 and post['actualTests'] == 15 and post['suites'] == 4 and post['wholeClassFour100']
    assert post['wholeSourceUnitCounters'] == {'LINE':dict(missed=0,covered=315),'METHOD':dict(missed=0,covered=38),
        'CLASS':dict(missed=0,covered=1),'BRANCH':dict(missed=0,covered=197)}
    hashes = normal['begin']['inputHashes']
    assert not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)
    assert all(data.sha((ROOT / p).read_bytes()) == data.sha((NORMAL / p).read_bytes()) == h for p,h in hashes.items())
    prior_normal = data.read_checked(data.BASE / 'PG9660-pagination-six-compile-v1/manifest.json',
        'f2ae182bb3a88eff78542ce0c18f3a497263aaabb7ed7fdbea5237a9ab467c2c')
    old_hashes = prior_normal['begin']['inputHashes']
    assert set(hashes) - set(old_hashes) == {TEST} and not set(old_hashes) - set(hashes)
    assert all(hashes[p] == h for p,h in old_hashes.items())
    prior_static = data.read_checked(BASE / 'PG9666-pagination-static-v2/manifest.json',
        '41807eb5d29a989424939246359f8eb7f9162bd03c7fbc4d1f2bd8932546de08')
    assert prior_static['actualExit'] == 0 and prior_static['source'] == prior_normal['source']
    class_count = 0
    old_tests = 0
    current_tests = 0
    for module,item in normal['jars'].items():
        jar = Path(item['path'])
        assert data.sha(jar.read_bytes()) == item['sha256']
        with zipfile.ZipFile(jar) as archive:
            classes = {p:data.sha(archive.read(p)) for p in archive.namelist() if p.endswith('.class')}
        previous = prior_static['results'][module]
        assert classes == previous['physicalClasses']
        assert previous['findings'] == previous['processingErrors'] == previous['receipt']['actualExit'] == 0
        assert all(data.sha(Path(p).read_bytes()) == h for p,h in previous['dependencyHashes'].items())
        class_count += len(classes)
        current = NORMAL / ('src/schubert-nk-' + module) / 'target/test-classes'
        old = Path(prior_normal['jars'][module]['path']).parent / 'test-classes'
        before = {p.relative_to(old).as_posix():data.sha(p.read_bytes()) for p in old.rglob('*.class')}
        after = {p.relative_to(current).as_posix():data.sha(p.read_bytes()) for p in current.rglob('*.class')}
        assert all(after[p] == h for p,h in before.items())
        extra = set(after) - set(before)
        expected = {'dev/codex/schubert/nk/protocol/layout/SemanticDirectBoundaryTest.class'} if module == 'protocol' else set()
        assert extra == expected and not set(before) - set(after)
        old_tests += len(before)
        current_tests += len(after)
    assert class_count == 1843 and old_tests == 1911 and current_tests == 1912
    for label,tag in [('pmd','violation'),('checkstyle','error')]:
        assert static['stages'][label]['actualExit'] == 0 and not static['stages'][label]['timedOut']
        assert static['reports'][label]['findings'] == static['reports'][label]['processingErrors'] == 0
        path = BASE / 'PG9700-semantic-direct-fixed-static-v1' / (label + '.xml')
        assert data.sha(path.read_bytes()) == static['reports'][label]['sha256']
        assert not [n for n in ET.parse(path).getroot().iter() if n.tag.rpartition('}')[2] in (tag,'configerror')]
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**static['toolAndRuleHashes'],**static['auxiliaryDependencyHashes']}.items())
    assert static['testSourceSha256'] == hashes[TEST] == 'a1febb6ee40532721d36d3928b9957a2efe4fafd7d2dda6d6e9dfa49f0d3b459'
    current = (ROOT / TEST).read_text()
    original = subprocess.check_output(['git','show','0002706babad635c5ca7ade76cdbaee134ace432:' + TEST],cwd=ROOT).decode()
    restored = current.replace('  private static final String LOG_REQUEST = "LGSREQ01";\n','').replace('LOG_REQUEST','"LGSREQ01"')
    assert restored == original and original.count('"LGSREQ01"') == 7 and current.count('"LGSREQ01"') == 1
    assert current.count('@Test') == 3
    spec = 'evidence/01_PT/002_NK-PRO-002/011_Semantic未網羅条件_単体テスト仕様書.md'
    assert subprocess.check_output(['git','show',SOURCE + ':' + spec],cwd=ROOT) == (ROOT / spec).read_bytes()
    methods = {name:ident for name,ident in [('sem001PasswordCharacterByteAndUsernameLimits','PT-PRO-002-SEM001'),
        ('sem002InclusiveDateLimitsAndOneSidedFilters','PT-PRO-002-SEM002'),('sem003QuestionAndWebLogTextContracts','PT-PRO-002-SEM003')]}
    assert set(methods) == set(post['cases']['dev.codex.schubert.nk.protocol.layout.SemanticDirectBoundaryTest'])
    assert all(name in current and ident in (ROOT / spec).read_text() for name,ident in methods.items())
    master = ROOT / 'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json'
    inventory = json.loads(master.read_bytes())
    subject = [r for r in inventory['artifacts'] if r['path'].endswith('/layout/PayloadSemanticValidator.java')]
    assert len(subject) == 1 and subject[0]['owner'] == subject[0]['costOwner'] == 'WBS-P002-02'
    main = [p for p in hashes if '/src/main/java/' in p and p.endswith('.java')]
    tests = [p for p in hashes if '/src/test/java/' in p and p.endswith('.java')]
    assert len(main) == 965 and len(tests) == 826
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        normalManifestSha256='7d2e18f86d2bc9e5c61473da8b8924aa7c6668bf8903541d5502902d2dac1d7a',
        hostPostSha256='c4695d0343472bc44e4998c78e5ed331ae7c7cdedfd523e84493df4a7ce99839',
        currentTestStaticSha256='5c749b367ae03a141e6b6ba256a6900de0980b58d77d21e42af7a81dd0b5abee',
        mainClasses=class_count,priorSameByteMainStaticSource=prior_static['source'],sameByteStaticResultsNotReexecuted=True,
        currentMainSourceFiles=len(main),currentTestSourceFiles=len(tests),currentJavaSourceFiles=len(main)+len(tests),
        prior1911TestClassBytesPreserved=True,currentTestClassFiles=current_tests,methods=methods,specSha256=data.sha((ROOT / spec).read_bytes()),
        sourceOwnerCandidate=dict(path=TEST,owner='WBS-P002-02',costOwner='WBS-P002-02',masterRegistered=False),
        originalMainSubject=subject[0],literalRefactorExactlyReversible=True,testExpectedInputsAndAssertionsChanged=False,
        actualTestsInCurrentRun=15,newTestIds=3,productTestsExecutedByPost=0,wholeValidatorFour100=True,
        oldDynamicResultsTransferred=False,coverageUnion=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,
        wholeF03Accepted=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,tests=15,newTestIds=3,mainClasses=class_count,wholeValidatorFour100=True,
        manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
