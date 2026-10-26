"""Freeze exactly four independently reviewed in-memory view-model methods."""
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import zipfile
from classfile_code_metadata import decode
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10130_uid_oracle_preflight import tokens
from pg10339_result_profile_oracle_post_v2 import folded
from pg10392_role_literal_plan import OLD, NEW

SOURCE = 'b98ab2b8a2e8868f07471a95530d1005b6121b10'
OUT = data.BASE/'PG10398-role-view-preflight-v1'
NORMAL = data.ROOT.parent/'pgpt-runs/PG379/pg10396-role-literal-six-compile-v1/snapshot'
CASES = [
    ('AnimationViewModelTest','web230AnimationMenuCounts','PT-WEB230','WBS-P016-08'),
    ('MusicHierarchyViewModelTest','web246CategorySnapshot','PT-WEB246','WBS-P016-11'),
    ('MusicHierarchyViewModelTest','web247SectionSnapshot','PT-WEB247','WBS-P016-11'),
    ('ScenarioHierarchyViewModelTest','web182GameDisplay','PT-WEB-182','WBS-P016-04')]


def canonical(text):
    values = []
    for value in tokens(text):
        if value.startswith('"'):
            try: value = json.dumps(json.loads(value),ensure_ascii=True)
            except json.JSONDecodeError: pass
        values.append(value)
    return folded(values)


def source_check(path,text,previous):
    if canonical(text) != canonical(previous.replace(OLD,NEW)):
        raise ValueError('only literal role expectations and equal compile-time strings allowed')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG10396-role-literal-six-compile-v1/manifest.json',
        '42e446d87c251b819592758cbadeee1d5ba4e785d91269edfb6ac873f71b8b5c')
    plan = data.read_checked(data.BASE/'PG10392-role-literal-plan-v1/manifest.json',
        'af9752f79f1a4af7be0264e301841f31dc1be0f3976115198ec6a112f8ab147c')
    static = data.read_checked(data.BASE/'PG10394-role-literal-static-v1/manifest.json',
        '0b1be65fb8da3963f2565090880365c7091fecc39578ccc17b13dbbc25299f38')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((NORMAL/p).read_bytes()) == h for p,h in hashes.items())
    negatives = []
    for p,row in plan['sourceChanges'].items():
        previous = subprocess.check_output(['git','show',plan['source']+':'+p],cwd=data.ROOT).decode()
        assert data.sha(previous.encode()) == row['beforeSha256']
        text = (NORMAL/p).read_text()
        source_check(p,text,previous)
        assert hashes[p] == static['sourceHashes'][p] and OLD not in text
        for label,corrupted in [('wrong-role',text.replace('case ADMIN -> "ADMIN";','case ADMIN -> "USER";',1)),
            ('missing-role',text.replace('case USER -> "USER";','',1))]:
            assert corrupted != text
            try: source_check(p,corrupted,previous)
            except ValueError: negatives.append(dict(path=p,mutation=label))
            else: raise AssertionError('incorrect role oracle accepted')
    assert len(negatives) == 26
    cases,physical = [],{}
    for cls,method,test_id,owner in CASES:
        binary = 'dev.codex.schubert.nk.web.view.'+cls
        path = 'src/schubert-nk-web/src/test/java/'+binary.replace('.','/')+'.java'
        text = (NORMAL/path).read_text()
        assert method in re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',text)
        assert not any(v in text for v in ('@Before','@After','@ExtendWith','@RegisterExtension','@Disabled','@TempDir'))
        assert not re.search(r'\bstatic\s*\{',text)
        target = NORMAL/'src/schubert-nk-web/target/test-classes'/(binary.replace('.','/')+'.class')
        for p in sorted(target.parent.glob(target.stem+'*.class')):
            model = decode(p.read_bytes(),str(p.relative_to(NORMAL/'src/schubert-nk-web/target/test-classes')))
            assert model['sourceFile'] == cls+'.java'
            physical[str(p)] = data.sha(p.read_bytes())
        model = decode(target.read_bytes(),binary.replace('.','/')+'.class')
        assert len([m for m in model['methods'] if m['name'] == method and m['descriptor'] == '()V' and m['hasCode']]) == 1
        cases.append(dict(className=binary,method=method,testId=test_id,canonicalOwner=owner,path=path,sourceSha256=hashes[path]))
    subjects = ('AnimationMenuViewModel','GameListViewModel','GameListViewModel$Card',
        'MusicCategoryViewModel','MusicCategoryViewModel$Card','MusicSectionViewModel','MusicSectionViewModel$Card','TopBarViewModel')
    with zipfile.ZipFile(normal['jars']['web']['path']) as archive:
        mains = {n:data.sha(archive.read(n)) for n in archive.namelist() if
            n in {'dev/codex/schubert/nk/web/view/'+s+'.class' for s in subjects}}
    assert len(mains) == 8
    helper = data.ROOT/'tools/quality/architecture/RoleLiteralViewJunitLauncher.java'
    review = 'evidence/01_PT/015_NK-WEB-001/032_NK-WEB-001_Role期待値独立化・限定PT仕様.md'
    assert static['actualExit'] == 1 and static['reports']['pmd']['findings'] == 250 and static['reports']['checkstyle']['findings'] == 0
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'cases.json',cases)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        expectedTests=4,expectedSuites=3,caseCounts=dict(Counter(r['className'] for r in cases)),
        casesSha256=data.sha((OUT/'cases.json').read_bytes()),physicalTestFiles=physical,physicalMainClasses=mains,
        normalManifestSha256='42e446d87c251b819592758cbadeee1d5ba4e785d91269edfb6ac873f71b8b5c',
        allCurrentSourceInputHashes=hashes,changedTestSourceHashes=static['sourceHashes'],
        normalSourceChanges=13,independentRoleExpressions=18,allOriginalAssertionsAndOtherTokensPreserved=True,
        roleOracleMetadataNegatives=negatives,javaStringCanonicalization='symmetric JSON-compatible literal decode and constant concatenation; unsupported escapes remain exact',
        launcherSha256=data.sha(helper.read_bytes()),boundaryReview=review,boundaryReviewSha256=data.sha((data.ROOT/review).read_bytes()),
        selectedOnly=True,packageOrClassDiscovery=False,springStartupPermitted=False,actualDbOrServicePermitted=False,
        heldOperationsPermitted=False,productTestsExecuted=0,newTestIds=0,externalActions=0,
        rawStaticExit=1,rawPmdFindings=250,pmdApplicabilityComplete=False,wholeF03Accepted=False,
        wholeG03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
