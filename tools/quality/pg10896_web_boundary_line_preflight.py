"""Concrete8 original Scenario template methods after complete compound-boundary correction; no external runtime."""
import os
import json
from pathlib import Path
import re
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = 'f24d1649e170e46aafb59a37b9750c602206364c'
OUT = data.BASE/'PG10896-web-boundary-line-preflight-v1'
NAMES = ["ScenarioSearchTemplateTest"]
TRACES = {
    'PT-SCR-033.txt': 'template=search\nfixture=public-synthetic\nconcurrentRenders=64\nmaximumRows=100\nmaximumSpeakers=500\nactualNkGate=false\n',
}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal_path = data.BASE/'PG10892-web-boundary-line-six-compile-v1/manifest.json'
    normal = data.read_checked(normal_path,'345e989275ba9dd52da2356d303c7c1a818feeaf4a41244b6ba05b8e26bf2de9')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    snapshot = Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((snapshot/p).read_bytes()) == h for p,h in hashes.items())
    proof = data.read_checked(data.BASE/'PG10891-web-boundary-line-source-post-v1/manifest.json',
        '2623f20868d71b0a220e26c736b7861a5099c40b0f1670c49871bc303230f55c')
    assert proof['actualExit'] == 0
    static_path = data.BASE/'PG10894-web-boundary-line-static-v1/manifest.json'
    static = json.loads(static_path.read_bytes())
    assert static['source'] == SOURCE and static['actualExit'] == 1 and static['reports']['pmd']['findings'] == 17
    assert all(v['processingErrors'] == 0 for v in static['reports'].values())
    files = ['src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/'+n+'.java' for n in NAMES]
    cases,reviewed = [],[]
    for path in files:
        text = (snapshot/path).read_text()
        assert not any(marker in text for marker in ('@Before','@After','@ExtendWith','@RegisterExtension','@Disabled','@TempDir','@TestFactory','@ParameterizedTest'))
        assert not re.search(r'\bstatic\s*\{',text)
        imports = re.findall(r'^import (.*);',text,re.M)
        assert not any(word in text for word in ('java.net.','ProcessBuilder','Runtime.getRuntime','System.exit','System.getenv','System.getProperty','setAccessible','org.postgresql','org.apache.activemq','getConnection('))
        methods = re.findall(r'@Test\s+void (\w+)\(\s*\)',text)
        binary = 'dev.codex.schubert.nk.web.view.'+Path(path).stem
        for method in methods:
            cases.append(dict(className=binary,method=method,testId='PT-WEB-SCB-'+str(len(cases)+1).zfill(3),
                path=path,sourceSha256=hashes[path],changeOwner='WBS-F03',canonicalOwnerNotInferred=True))
        reviewed.append(dict(path=path,sha256=hashes[path],methods=len(methods),imports=imports,
            sideEffectDomain='DTO_FORM_VIEW_MEMORY_EXPLICIT_MVC_MOCK_SERVLET_FIXED_RESOURCE_READS_ONE_OWN_SNAPSHOT_TRACE'))
    assert len(cases) == 8 and len({r['className'] for r in cases}) == 1
    tc = data.ROOT.parent/'toolchain'
    directory = snapshot/'src/schubert-nk-web/target/test-classes'
    physical = {str(p):data.sha(p.read_bytes()) for p in sorted(directory.rglob('*.class'))}
    cwd = snapshot/'src/schubert-nk-web'
    trace_parent = cwd/'target/scenario-screen-traces'
    assert not trace_parent.exists() and not trace_parent.is_symlink()
    for parent in [cwd,cwd/'target',snapshot]:
        assert parent.is_dir() and not parent.is_symlink()
    libraries = (cwd/'target/pgpt-test-classpath.txt').read_text().strip().split(os.pathsep)
    jars = {module:item['path'] for module,item in normal['jars'].items()}
    bootstrap_tests = snapshot/'src/schubert-nk-bootstrap/target/schubert-nk-bootstrap-0.1.0-SNAPSHOT-tests.jar'
    assert bootstrap_tests.is_file() and not bootstrap_tests.is_symlink()
    assert libraries
    for item in libraries:
        path = Path(item)
        assert path.is_file() and not path.is_symlink()
        assert str(path).startswith(str(tc/'m2/repository')+'/') or item in jars.values() or path == bootstrap_tests
    launcher = tc/'m2/repository/org/junit/platform/junit-platform-launcher/1.13.4/junit-platform-launcher-1.13.4.jar'
    assert data.sha(launcher.read_bytes()) == '0b0beaeb6880a31149641d2d848b863712885469670c12099586d7f798522564'
    agent = tc/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar'
    dependencies = {str(p):data.sha(Path(p).read_bytes()) for p in [*jars.values(),*libraries,launcher,agent]}
    catalogs = {}
    for module,item in jars.items():
        with zipfile.ZipFile(item) as jar:
            catalogs[module] = {name:data.sha(jar.read(name)) for name in jar.namelist() if name.endswith('.class')}
    helper = data.ROOT/'tools/quality/architecture/ScenarioBoundaryJunitLauncher.java'
    helper_text = helper.read_text()
    assert all(r['className']+'#'+r['method'] in helper_text for r in cases)
    assert 'EXPECTED_TESTS = 8;' in helper_text and 'EXPECTED_SUITES = 1;' in helper_text
    assert 'junit.jupiter.extensions.autodetection.enabled' in helper_text
    assert not any(word in helper_text for word in ('Class.forName','selectPackage(', 'scanClasspath','WebStartupGraph','ApiStartupGraph'))
    resources = {p:h for p,h in hashes.items() if p.startswith('src/schubert-nk-web/src/main/resources/')}
    assert resources
    spec = data.ROOT/'evidence/01_PT/016_NK-WEB-002/108_Web八Test残十九・二境界意味名PGPT仕様.md'
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'cases.json',cases)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        normalManifestSha256=data.sha(normal_path.read_bytes()),casesSha256=data.sha((OUT/'cases.json').read_bytes()),
        expectedTestsPerLocale=8,expectedSuitesPerLocale=1,locales=['ja-JP'],expectedUniqueMethods=8,
        normalSnapshot=str(snapshot),testCwd=str(cwd),traceParent=str(trace_parent),expectedTraceText=TRACES,
        allCurrentSourceInputHashes=hashes,physicalTestFiles=physical,mainClassCatalogs=catalogs,
        dependencyHashes=dependencies,libraryClasspath=libraries,
        launcherJar=str(launcher),jacocoAgent=str(agent),moduleJars=jars,testClassesDirectory=str(directory),
        helperPath=str(helper),helperSha256=data.sha(helper.read_bytes()),specPath=str(spec.relative_to(data.ROOT)),specSha256=data.sha(spec.read_bytes()),
        reviewedSources=reviewed,fixedClasspathResources=resources,
        concreteReview=dict(reflection='closed bean introspection/getters only; no access override',
            concurrency='own8-worker/64-task executors, bounded Future10/20s and try-with-resources; own JVM timeout',
            resources='fixed snapshot classpath/file reads; writes only one exact public synthetic trace in fresh owned snapshot target',
            classpath='fixed captured Web dependencies; embedded backend/Root/runtime assemblers never selected',
            mvc='explicit WebMvcConfiguration only; Login/Menu/Error beans, MockServlet/MockMvc; no component scan, real HTTP or BrowserJS',
            purpose='required original8-method Scenario regression after compound-boundary correction; earlier16/8 Log successes stay historical, not summed; not held-fixture extraction or confirmation replay'),
        judgement='PT_DEFAULT_CONCRETE_WEB_VIEW_REGRESSION',actualNetworkPermitted=False,actualDatabasePermitted=False,
        actualVmRootServicePermitted=False,heldTestExtraction=False,newTestFixtureHarnessForHeldOperations=False,
        productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
