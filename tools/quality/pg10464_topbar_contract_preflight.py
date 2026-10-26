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
from pg10398_role_view_preflight import canonical
from pg10430_pure_view_literal_plan import restored, BASE_SOURCE
from pg10459_topbar_contract_plan_v2 import TARGET, remove_additions, check as topbar_check

SOURCE = '73c18457afce837ecfc3687fc7aae84c04cca2c1'
OUT = data.BASE/'PG10464-topbar-contract-preflight-v1'
NORMAL = data.ROOT.parent/'pgpt-runs/PG379/pg10462-topbar-contract-six-compile-v1/snapshot'


SPECS = {
    'ScenarioHierarchyViewModelTest': ('006_NK-WEB-001_Scenario階層表示単体テスト仕様書.md','WBS-P016-04',12),
    'AnimationViewModelTest': ('016_NK-WEB-001_Animation一覧表示単体テスト仕様書.md','WBS-P016-08',8),
    'MusicHierarchyViewModelTest': ('020_NK-WEB-001_Music階層表示単体テスト仕様書.md','WBS-P016-11',8)}
SPEC_HASHES = {}
CASES = []
for cls,(name,owner,count) in SPECS.items():
    spec = data.ROOT/'evidence/01_PT/015_NK-WEB-001'/name
    text = spec.read_text()
    SPEC_HASHES[str(spec.relative_to(data.ROOT))] = data.sha(spec.read_bytes())
    rows = re.findall(r'(?m)^\| (PT-WEB-\d+) \| (web\w+) \|',text)
    assert len(rows) == count
    CASES.extend((cls,method,test_id,owner) for test_id,method in rows)
assert len(CASES) == 28 and len({(c,m) for c,m,_,_ in CASES}) == 28


def check(text, previous, constants):
    if "class ScenarioHierarchyViewModelTest" in text:
        text = remove_additions(text)
    if canonical(' '.join(restored(text,constants))) != canonical(previous):
        raise ValueError('only exact same-value Test constants and formatter allowed')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    contract_plan = data.read_checked(data.BASE/'PG10459-topbar-contract-plan-v2-v1/manifest.json',
        'e81eca37500886bd576802186dd95bf6126d53c6b600d485a11fc46f733a2a3e')
    assert contract_plan['actualExit'] == 0 and contract_plan['path'] == TARGET
    assert data.sha((data.ROOT/TARGET).read_bytes()) == contract_plan['sha256']
    assert len(contract_plan['metadataNegatives']) == 5
    normal_path = data.BASE/'PG10462-topbar-contract-six-compile-v1/manifest.json'
    normal = json.loads(normal_path.read_bytes())
    plan = data.read_checked(data.BASE/'PG10430-pure-view-literal-plan-v1/manifest.json',
        'aa1786cd6cb9efbaf8d6776c2aeaad72a2f7a8eb7170bd3220d4e8d4556fa167')
    static = data.read_checked(data.BASE/'PG10460-topbar-contract-static-v1/manifest.json',
        'fe30b85e0e7c678bf7b7352c830bcf31218bf1506ccc9a0a53c5c10eaa2a72ec')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((NORMAL/p).read_bytes()) == h for p,h in hashes.items())
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src'],cwd=data.ROOT) == b''
    negatives = []
    for p,row in plan['sourceChanges'].items():
        previous = subprocess.check_output(['git','show',BASE_SOURCE+':'+p],cwd=data.ROOT).decode()
        assert data.sha(previous.encode()) == row['beforeSha256']
        text = (NORMAL/p).read_text()
        if p == TARGET:
            previous_contract = subprocess.check_output(["git","show","65bcd70a1dec722bd70be03468d9343142a7e789:"+p],cwd=data.ROOT).decode()
            topbar_check(text,previous_contract)
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
    for cls in SPECS:
        source = NORMAL/('src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/'+cls+'.java')
        methods = re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',source.read_text())
        assert set(methods) == {method for name,method,_,_ in CASES if name == cls}
        assert len(methods) == SPECS[cls][2]
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
        'MusicCategoryViewModel','MusicCategoryViewModel$Card','MusicSectionViewModel','MusicSectionViewModel$Card','TopBarViewModel',
        'AnimationListViewModel','AnimationListViewModel$Video','AnimationListViewModel$Row',
        'RouteListViewModel','RouteListViewModel$Card','ScenarioFileListViewModel','ScenarioFileListViewModel$Card')
    with zipfile.ZipFile(normal['jars']['web']['path']) as archive:
        mains = {n:data.sha(archive.read(n)) for n in archive.namelist() if n in {'dev/codex/schubert/nk/web/view/'+s+'.class' for s in subjects}}
    assert len(mains) == 15
    helper = data.ROOT/'tools/quality/architecture/RoleLiteralViewJunitLauncher10452.java'
    review = 'evidence/01_PT/018_NK-OPS-001/2071_TopBar診断・null補完_同source15class閉鎖PT仕様.md'
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'cases.json',cases)
    data.write(OUT/'pmd-applicability.json',applicability)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        expectedTests=28,expectedSuites=3,caseCounts=dict(Counter(r['className'] for r in cases)),
        casesSha256=data.sha((OUT/'cases.json').read_bytes()),physicalTestFiles=physical,physicalMainClasses=mains,
        normalManifestSha256=data.sha(normal_path.read_bytes()),allCurrentSourceInputHashes=hashes,
        changedTestSourceHashes=static['sourceHashes'],normalSourceChanges=1,sameValueConstants=14,addedIndependentTopbarAssertions=2,
        topbarContractPlanSha256="e81eca37500886bd576802186dd95bf6126d53c6b600d485a11fc46f733a2a3e",
        allOriginalAssertionsAndOtherTokensPreserved=True,metadataNegatives=negatives,
        launcherSha256=data.sha(helper.read_bytes()),boundaryReview=review,boundaryReviewSha256=data.sha((data.ROOT/review).read_bytes()),
        applicabilitySha256=data.sha((OUT/'pmd-applicability.json').read_bytes()),
        originalSpecHashes=SPEC_HASHES,selectedOnly=True,packageOrClassDiscovery=False,springStartupPermitted=False,actualDbOrServicePermitted=False,
        heldOperationsPermitted=False,productTestsExecuted=0,newTestIds=0,externalActions=0,
        rawStaticExit=1,rawPmdFindings=6,contextuallyApplicableFindings=0,checkstyleFindings=0,suppressionsAdded=False,
        wholeF03Accepted=False,wholeG03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
