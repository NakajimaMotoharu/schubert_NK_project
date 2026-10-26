"""Bind same-value Test changes and unchanged, previously reviewed four pure view methods."""
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import zipfile
from classfile_code_metadata import decode
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical, CASES
from pg10430_pure_view_literal_plan import restored, BASE_SOURCE

SOURCE = '65bcd70a1dec722bd70be03468d9343142a7e789'
OUT = data.BASE/'PG10436-pure-view-preflight-v1'
NORMAL = data.ROOT.parent/'pgpt-runs/PG379/pg10434-pure-view-six-compile-v1/snapshot'


def check(text, previous, constants):
    if canonical(' '.join(restored(text,constants))) != canonical(previous):
        raise ValueError('only exact same-value Test constants and formatter allowed')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal_path = data.BASE/'PG10434-pure-view-six-compile-v1/manifest.json'
    normal = json.loads(normal_path.read_bytes())
    plan = data.read_checked(data.BASE/'PG10430-pure-view-literal-plan-v1/manifest.json',
        'aa1786cd6cb9efbaf8d6776c2aeaad72a2f7a8eb7170bd3220d4e8d4556fa167')
    static = data.read_checked(data.BASE/'PG10432-pure-view-literal-static-v1/manifest.json',
        '62f26a899cfd66e3b5ea8b856049b057500a6d0297aa7169c1a88a97ff4f7e98')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((NORMAL/p).read_bytes()) == h for p,h in hashes.items())
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src'],cwd=data.ROOT) == b''
    negatives = []
    for p,row in plan['sourceChanges'].items():
        previous = subprocess.check_output(['git','show',BASE_SOURCE+':'+p],cwd=data.ROOT).decode()
        assert data.sha(previous.encode()) == row['beforeSha256']
        text = (NORMAL/p).read_text()
        check(text,previous,row['constants'])
        assert hashes[p] == static['sourceHashes'][p]
        for name,constant in row['constants'].items():
            pattern = r'(private\s+static\s+final\s+'+constant['type']+r'\s+'+name+r'\s*=\s*)'+re.escape(constant['literal'])
            wrong = '"WRONG_LITERAL"' if constant['type'] == 'String' else '9999'
            damaged,count = re.subn(pattern,lambda m:m[1]+wrong,text)
            assert count == 1
            try:
                check(damaged,previous,row['constants'])
            except ValueError:
                negatives.append(dict(path=p,constant=name))
            else:
                raise AssertionError('changed Test value accepted')
    assert len(negatives) == 14
    assert static['actualExit'] == 1 and static['reports']['pmd']['findings'] == 6
    assert static['reports']['checkstyle']['findings'] == 0 and all(r['processingErrors']==0 for r in static['reports'].values())
    applicability = []
    for row in static['reports']['pmd']['details']:
        assert row['rule'] == 'DoNotUseThreads'
        p, = [p for p in plan['sourceChanges'] if Path(p).stem == row['class']]
        text = (NORMAL/p).read_text()
        line = text.splitlines()[int(row['beginline'])-1].strip()
        assert any(v in line for v in ('Executors.newFixedThreadPool(','.submit('))
        assert 'TimeUnit.SECONDS' in text and ('try (var executor =' in text or 'try (var pool =' in text)
        applicability.append(dict(path=p,sourceSha256=hashes[p],line=int(row['beginline']),sourceLine=line,
            disposition='NOT_APPLICABLE_IN_EXACT_STANDALONE_TEST_CONTEXT',
            reason='Test-only owned try-resource executor and bounded future wait; JavaEE Production thread prohibition is not applicable. This concurrency method is not dynamically qualified by selected four methods.'))
    cases,physical = [],{}
    for cls,method,test_id,owner in CASES:
        binary = 'dev.codex.schubert.nk.web.view.'+cls
        p = 'src/schubert-nk-web/src/test/java/'+binary.replace('.','/')+'.java'
        text = (NORMAL/p).read_text()
        assert method in re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',text)
        assert not any(v in text for v in ('@Before','@After','@ExtendWith','@RegisterExtension','@Disabled','@TempDir'))
        assert not re.search(r'\bstatic\s*\{',text)
        target = NORMAL/'src/schubert-nk-web/target/test-classes'/(binary.replace('.','/')+'.class')
        for file in sorted(target.parent.glob(target.stem+'*.class')):
            model = decode(file.read_bytes(),str(file.relative_to(NORMAL/'src/schubert-nk-web/target/test-classes')))
            assert model['sourceFile'] == cls+'.java'
            physical[str(file)] = data.sha(file.read_bytes())
        cases.append(dict(className=binary,method=method,testId=test_id,canonicalOwner=owner,path=p,sourceSha256=hashes[p]))
    subjects = ('AnimationMenuViewModel','GameListViewModel','GameListViewModel$Card',
        'MusicCategoryViewModel','MusicCategoryViewModel$Card','MusicSectionViewModel','MusicSectionViewModel$Card','TopBarViewModel')
    with zipfile.ZipFile(normal['jars']['web']['path']) as archive:
        mains = {n:data.sha(archive.read(n)) for n in archive.namelist() if n in {'dev/codex/schubert/nk/web/view/'+s+'.class' for s in subjects}}
    assert len(mains) == 8
    helper = data.ROOT/'tools/quality/architecture/RoleLiteralViewJunitLauncher.java'
    review = 'evidence/01_PT/018_NK-OPS-001/2066_純粋表示モデル三Test_同値定数化・限定再試験仕様.md'
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'cases.json',cases)
    data.write(OUT/'pmd-applicability.json',applicability)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        expectedTests=4,expectedSuites=3,caseCounts=dict(Counter(r['className'] for r in cases)),
        casesSha256=data.sha((OUT/'cases.json').read_bytes()),physicalTestFiles=physical,physicalMainClasses=mains,
        normalManifestSha256=data.sha(normal_path.read_bytes()),allCurrentSourceInputHashes=hashes,
        changedTestSourceHashes=static['sourceHashes'],normalSourceChanges=3,sameValueConstants=14,
        allOriginalAssertionsAndOtherTokensPreserved=True,metadataNegatives=negatives,
        launcherSha256=data.sha(helper.read_bytes()),boundaryReview=review,boundaryReviewSha256=data.sha((data.ROOT/review).read_bytes()),
        applicabilitySha256=data.sha((OUT/'pmd-applicability.json').read_bytes()),
        selectedOnly=True,packageOrClassDiscovery=False,springStartupPermitted=False,actualDbOrServicePermitted=False,
        heldOperationsPermitted=False,productTestsExecuted=0,newTestIds=0,externalActions=0,
        rawStaticExit=1,rawPmdFindings=6,contextuallyApplicableFindings=0,checkstyleFindings=0,suppressionsAdded=False,
        wholeF03Accepted=False,wholeG03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
