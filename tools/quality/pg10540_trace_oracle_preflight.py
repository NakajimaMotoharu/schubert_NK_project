"""Exact ten local mock-request tests, fixed changed source, no target invocation."""
from pathlib import Path
import re
import subprocess
import zipfile
from classfile_code_metadata import decode
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10530_trace_fallback_plan import P
from pg10534_trace_oracle_literals_plan import validate

SOURCE = '36c8d53dae2a333fe97ba8beef1a9c7f100033b2'
NORMAL = data.ROOT.parent/'pgpt-runs/PG379/pg10538-trace-oracle-compile-v1/snapshot'
OUT = data.BASE/'PG10540-trace-oracle-preflight-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    plan = data.read_checked(data.BASE/'PG10534-trace-oracle-literals-plan-v1/manifest.json',
        '1d240b682738bc78d9c7ae95f3d7384f052ef5209ee5dcbd81c467f9dd3379bf')
    normal = data.read_checked(data.BASE/'PG10538-trace-oracle-compile-v1/manifest.json',
        '56ed79534c2426ccd7ee115b0c11cf093b2ce74b72c46f655bda40d40872f28e')
    static = data.read_checked(data.BASE/'PG10536-trace-oracle-static-v1/manifest.json',
        'f7489316458b98966b2f3d13bf0e5de6cc112c8095a52a8969bbeacc866cd622')
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
    assert methods == plan['exactMethods'] and len(methods) == 10
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
    spec = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2081_REQ008固定fallback独立期待値_単体テスト仕様.md'
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'cases.json',cases)
    data.write(OUT/'pmd-applicability.json',applicability)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        expectedTests=10,expectedSuites=1,casesSha256=data.sha((OUT/'cases.json').read_bytes()),
        caseCounts={binary:10},physicalTestFiles=physical,physicalMainClasses=mains,
        allCurrentSourceInputHashes=hashes,changedTestSourceHashes={P:hashes[P]},
        normalManifestSha256='56ed79534c2426ccd7ee115b0c11cf093b2ce74b72c46f655bda40d40872f28e',
        planManifestSha256='1d240b682738bc78d9c7ae95f3d7384f052ef5209ee5dcbd81c467f9dd3379bf',
        rawStaticManifestSha256='f7489316458b98966b2f3d13bf0e5de6cc112c8095a52a8969bbeacc866cd622',
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
