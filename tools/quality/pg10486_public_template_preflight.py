"""Closed14-method public template lane, normal resource and owned output binding."""
from collections import Counter
from pathlib import Path
import re
import subprocess
import zipfile
from classfile_code_metadata import decode
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = 'a82c44a678cce0ded7fda59cf84a2276ded51e30'
OUT = data.BASE/'PG10486-public-template-preflight-v1'
NORMAL = data.ROOT.parent/'pgpt-runs/PG379/pg10480-disjoint-six-literal-compile-v1/snapshot'
SPECS = {
    'AnimationTemplateTest': ('011_NK-WEB-002_Animation一覧template単体テスト仕様書.md','WBS-P016-09',8),
    'MusicHierarchyTemplateTest': ('015_NK-WEB-002_Music階層template単体テスト仕様書.md','WBS-P016-12',6)}
SUBJECTS = [
    'view/AnimationMenuViewModel','view/AnimationListViewModel','view/AnimationListViewModel$Video','view/AnimationListViewModel$Row',
    'view/MusicCategoryViewModel','view/MusicCategoryViewModel$Card','view/MusicSectionViewModel','view/MusicSectionViewModel$Card','view/TopBarViewModel',
    'config/WebMvcConfiguration','controller/ErrorController','controller/MenuController','controller/LoginController','error/ProblemViewFactory']


def declared_cases():
    cases, specs = [],{}
    for cls,(name,owner,count) in SPECS.items():
        path = data.ROOT/'evidence/01_PT/016_NK-WEB-002'/name
        rows = re.findall(r'(?m)^\| (PT-SCR-\d+) \| (\w+) \|',path.read_text())
        assert len(rows) == count
        specs[str(path.relative_to(data.ROOT))] = data.sha(path.read_bytes())
        cases.extend((cls,method,test_id,owner) for test_id,method in rows)
    assert len(cases) == 14 and len({(c,m) for c,m,_,_ in cases}) == 14
    return cases,specs


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal_path = data.BASE/'PG10480-disjoint-six-literal-compile-v1/manifest.json'
    normal = data.read_checked(normal_path,'11ca97be3c74142b3acfcac9c2612c0dd9230be17a4d91c5140a2abc28fbb179')
    proof = data.read_checked(data.BASE/'PG10482-disjoint-six-literal-post-v1/manifest.json',
        '1c4458f2db226efc0ffeb32bbbdaada06c7a25fd75b22fc7f03abe619f76beeb')
    assert normal['source'] == proof['source'] == SOURCE and normal['actualExit'] == proof['actualExit'] == normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((NORMAL/p).read_bytes()) == h for p,h in hashes.items())
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src'],cwd=data.ROOT) == b''
    raw_cases,specs = declared_cases()
    cases,physical,selected = [],{},{}
    for cls,(name,owner,count) in SPECS.items():
        p = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/'+cls+'.java'
        text = (NORMAL/p).read_text()
        expected = {m for c,m,_,_ in raw_cases if c == cls}
        methods = re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',text)
        assert len(methods) == count and set(methods) == expected
        assert not any(v in text for v in ('@Before','@After','@ExtendWith','@RegisterExtension','@Disabled','@TempDir'))
        assert not re.search(r'\bstatic\s*\{',text)
        assert 'try (var c = context()' in text and 'TimeUnit.SECONDS' in text
        assert hashes[p] == proof['sourceHashes'][p]
        selected[p] = hashes[p]
    for cls,method,test_id,owner in raw_cases:
        binary = 'dev.codex.schubert.nk.web.view.'+cls
        p = 'src/schubert-nk-web/src/test/java/'+binary.replace('.','/')+'.java'
        target = NORMAL/'src/schubert-nk-web/target/test-classes'/(binary.replace('.','/')+'.class')
        for file in target.parent.glob(target.stem+'*.class'):
            model = decode(file.read_bytes(),str(file.relative_to(NORMAL/'src/schubert-nk-web/target/test-classes')))
            assert model['sourceFile'] == cls+'.java'
            physical[str(file)] = data.sha(file.read_bytes())
        cases.append(dict(className=binary,method=method,testId=test_id,canonicalOwner=owner,path=p,sourceSha256=hashes[p]))
    prefix = 'dev/codex/schubert/nk/web/'
    module = NORMAL/'src/schubert-nk-web'
    resources = {p:h for p,h in hashes.items() if p.startswith(('src/schubert-nk-web/src/main/resources/templates/',
        'src/schubert-nk-web/src/main/resources/static/'))}
    assert len(resources) > 4
    with zipfile.ZipFile(normal['jars']['web']['path']) as archive:
        mains = {n:data.sha(archive.read(n)) for n in archive.namelist() if n in {prefix+s+'.class' for s in SUBJECTS}}
        assert len(mains) == 14
        for path,digest in resources.items():
            relative = path.removeprefix('src/schubert-nk-web/src/main/resources/')
            assert data.sha(archive.read(relative)) == digest
    trace = module/'target/scenario-screen-traces'
    assert module.is_dir() and not module.is_symlink() and not trace.exists()
    helper = data.ROOT/'tools/quality/architecture/PublicTemplate14JunitLauncher.java'
    review = 'evidence/01_PT/018_NK-OPS-001/2074_公開template14method_独立通常PT仕様.md'
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'cases.json',cases)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        expectedTests=14,expectedSuites=2,caseCounts=dict(Counter(r['className'] for r in cases)),
        casesSha256=data.sha((OUT/'cases.json').read_bytes()),physicalTestFiles=physical,physicalMainClasses=mains,
        allCurrentSourceInputHashes=hashes,changedTestSourceHashes=selected,
        normalManifestSha256=data.sha(normal_path.read_bytes()),sourceProofManifestSha256='1c4458f2db226efc0ffeb32bbbdaada06c7a25fd75b22fc7f03abe619f76beeb',
        originalSpecHashes=specs,publicResourceHashes=resources,normalTemplateModulePath=str(module),
        publicTraceDirectory=str(trace),expectedPublicTraceFileNames=['PT-SCR-053.txt','PT-SCR-071.txt'],
        traceDirectoryAbsentBeforeRun=True,launcherSha256=data.sha(helper.read_bytes()),
        boundaryReview=review,boundaryReviewSha256=data.sha((data.ROOT/review).read_bytes()),
        selectedOnly=True,packageOrClassDiscovery=False,productionStartupPermitted=False,
        actualNetworkOrDatabasePermitted=False,heldOperationsPermitted=False,
        publicSnapshotResourceReadsPermitted=True,freshOwnedCountTraceWritesPermitted=True,
        rawHtmlOrCsrfPublicationPermitted=False,productTestsExecuted=0,newTestIds=0,externalActions=0,
        rawWholeSixStaticFindings=26,rawSelectedTemplateStaticFindings=4,selectedContextualNonApplicable=4,
        otherSourceVolatilePending=10,wholeF03Accepted=False,wholeG03Accepted=False,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
