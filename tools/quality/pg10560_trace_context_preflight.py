"""Exact ten local mock-request tests, fixed changed source, no target invocation."""
from pathlib import Path
import re
import subprocess
import zipfile
from classfile_code_metadata import decode
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10530_trace_fallback_plan import P
from pg10554_trace_context_final_plan import validate

SOURCE = 'c91916e8fe1d46768b4ffcd8607164e973aa1bde'
NORMAL = data.ROOT.parent/'pgpt-runs/PG379/pg10558-trace-context-final-compile-v1/snapshot'
OUT = data.BASE/'PG10560-trace-context-preflight-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    plan = data.read_checked(data.BASE/'PG10554-trace-context-final-plan-v1/manifest.json',
        'b052a510a2bae618206104de0f4cb68c7c487dba372268c5c7d3f95918f8c5a6')
    normal = data.read_checked(data.BASE/'PG10558-trace-context-final-compile-v1/manifest.json',
        'e4f64a5711e95d5b5a6362bcec7adb3fe641f878d2edb2809c7dcbc8770f5e49')
    static = data.read_checked(data.BASE/'PG10556-trace-context-final-static-v1/manifest.json',
        '207c80c308d607f5ccdb096acce19d3d1350fb973cba88581743b76359646637')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((NORMAL/p).read_bytes()) == h for p,h in hashes.items())
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src'],cwd=data.ROOT) == b''
    text = (NORMAL/P).read_text()
    assert hashes[P] == plan['sourceChanges'][P] == static['sourceHashes'][P]
    before = subprocess.check_output(['git','show',plan['baseSource']+':'+P],cwd=data.ROOT).decode()
    validate(before,text)
    assert not any(v in text for v in ('@Before','@After','@ExtendWith','@RegisterExtension','@Disabled','@TempDir'))
    assert not re.search(r'\bstatic\s*\{',text)
    methods = re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',text)
    assert methods == re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',before) and len(methods) == 10
    binary = 'dev.codex.schubert.nk.web.logging.WebRequestTraceTest'
    cases = [dict(className=binary,method=method,testId=method[:6].upper()+':'+method,
        canonicalOwner='WBS-P006-03',path=P,sourceSha256=hashes[P]) for method in methods]
    physical = {}
    directory = NORMAL/'src/schubert-nk-web/target/test-classes'
    for file in sorted((directory/'dev/codex/schubert/nk/web/logging').glob('WebRequestTraceTest*.class')):
        model = decode(file.read_bytes(),str(file.relative_to(directory)))
        assert model['sourceFile'] == 'WebRequestTraceTest.java'
        physical[str(file)] = data.sha(file.read_bytes())
    assert len(physical) == 2
    subjects = {'dev/codex/schubert/nk/web/'+name+'.class' for name in
        ('logging/WebRequestTrace','logging/WebRequestTrace$Scope','security/WebRequestContext',
         'logging/WebRequestRouteInterceptor','config/RequestLogMvcConfiguration')}
    with zipfile.ZipFile(normal['jars']['web']['path']) as jar:
        mains = {name:data.sha(jar.read(name)) for name in subjects}
    assert len(mains) == 5
    assert static['actualExit'] == 1 and static['reports']['pmd']['findings'] == 5
    assert static['reports']['checkstyle']['findings'] == 0
    assert all(r['processingErrors'] == 0 for r in static['reports'].values())
    applicability = []
    for finding in static['reports']['pmd']['details']:
        assert finding['rule'] == 'DoNotUseThreads'
        line = text.splitlines()[int(finding['beginline'])-1].strip()
        assert 'Executors.newVirtualThreadPerTaskExecutor(' in line or '.submit(' in line
        assert 'try (var pool = Executors.newVirtualThreadPerTaskExecutor())' in text and 'TimeUnit.SECONDS' in text
        applicability.append(dict(finding=finding,path=P,sourceSha256=hashes[P],sourceLine=line,
            disposition='NOT_APPLICABLE_STANDALONE_TEST_OWNED_EXECUTOR_NOT_J2EE_PRODUCTION',
            limitation='Static context only; actual concurrency results must come from selected run.'))
    helper = data.ROOT/'tools/quality/architecture/TraceFallbackJunitLauncher.java'
    spec = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2083_REQ006Context境界補完_単体テスト仕様.md'
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'cases.json',cases)
    data.write(OUT/'pmd-applicability.json',applicability)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        expectedTests=10,expectedSuites=1,casesSha256=data.sha((OUT/'cases.json').read_bytes()),
        caseCounts={binary:10},physicalTestFiles=physical,physicalMainClasses=mains,
        allCurrentSourceInputHashes=hashes,changedTestSourceHashes={P:hashes[P]},
        normalManifestSha256='e4f64a5711e95d5b5a6362bcec7adb3fe641f878d2edb2809c7dcbc8770f5e49',
        planManifestSha256='b052a510a2bae618206104de0f4cb68c7c487dba372268c5c7d3f95918f8c5a6',
        rawStaticManifestSha256='207c80c308d607f5ccdb096acce19d3d1350fb973cba88581743b76359646637',
        launcherSha256=data.sha(helper.read_bytes()),boundaryReview=str(spec.relative_to(data.ROOT)),
        boundaryReviewSha256=data.sha(spec.read_bytes()),rawStaticExit=1,rawPmdFindings=5,
        contextuallyApplicableFindings=0,suppressionsAdded=False,checkstyleFindings=0,
        exactMethodsOnly=True,classOrPackageDiscovery=False,actualDbOrServicePermitted=False,
        actualNetworkPermitted=False,springStartupPermitted=False,heldOperationsPermitted=False,
        selectedPublicControllerSourceReadsOnly=True,productTestsExecuted=0,externalActions=0,
        newTestIds=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
