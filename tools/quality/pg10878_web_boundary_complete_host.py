"""Original8 Scenario template methods after compound-boundary correction in one new dedicated JP JVM; no held domains."""
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as steps

SOURCE = '787dc7da7c9643789326f7a4002931e9b7497f04'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg10878-web-boundary-complete-host-v1'
OUT = data.BASE/'PG10878-web-boundary-complete-host-v1'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    prepared_path = data.BASE/'PG10876-web-boundary-complete-preflight-v1/manifest.json'
    prepared = data.read_checked(prepared_path,'495a50ae870bfd35064155bc2b13159fa730ca97bf73e0d9336a1fdedadaaa4b')
    assert prepared['actualExit'] == 0 and prepared['source'] == SOURCE
    cases = data.read_checked(prepared_path.parent/'cases.json',prepared['casesSha256'])
    assert len(cases) == prepared['expectedTestsPerLocale'] == 8
    expected = {(r['className'],r['method']) for r in cases}
    assert len(expected) == 8 and prepared['locales'] == ['ja-JP']
    deps = prepared['dependencyHashes']
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**deps,**prepared['physicalTestFiles']}.items())
    snapshot = Path(prepared['normalSnapshot'])
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((snapshot/p).read_bytes()) == h for p,h in prepared['allCurrentSourceInputHashes'].items())
    helper = Path(prepared['helperPath'])
    assert data.sha(helper.read_bytes()) == prepared['helperSha256']
    os.umask(0o077)
    SLOT.mkdir()
    trace_parent = Path(prepared['traceParent'])
    assert not trace_parent.exists() and not trace_parent.is_symlink()
    reader = SLOT/'launcher'
    reader.mkdir()
    catalog = SLOT/'frozen-methods.tsv'
    with catalog.open('x') as stream:
        stream.write(''.join(r['className']+'\t'+r['method']+'\n' for r in cases))
    cp = os.pathsep.join(map(str,[reader,prepared['testClassesDirectory'],prepared['moduleJars']['web'],
        *prepared['libraryClasspath'],prepared['launcherJar']]))
    tc = data.ROOT.parent/'toolchain'
    begin = dict(source=SOURCE,invocation=invocation,preflightManifestSha256=data.sha(prepared_path.read_bytes()),
        dependencyHashes=deps,physicalTestFiles=prepared['physicalTestFiles'],sourceInputHashes=prepared['allCurrentSourceInputHashes'],
        helperSha256=prepared['helperSha256'],catalogSha256=data.sha(catalog.read_bytes()),classpath=cp,
        expectedTestsPerLocale=8,expectedSuitesPerLocale=1,expectedUniqueMethods=8,expectedLocaleRuns=['ja-JP'],
        environment=steps.ENV,actualNetworkActions=0,actualDatabaseActions=0,actualVmActions=0,
        actualRootActions=0,actualServiceActions=0,heldOperationsPermitted=False,normalCompileReplayed=False)
    data.write(SLOT/'begin.safe.json',begin)
    steps.SLOT = SLOT
    stages = [steps.step('compile-launcher',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror',
        '-cp',cp,'-d',str(reader),str(helper)],SLOT)]
    observed = []
    if stages[0]['actualExit'] == 0 and not stages[0]['timedOut']:
        for language,country,label in [('ja','JP','JP')]:
            locale = language+'-'+country
            directory = SLOT/label.lower()
            directory.mkdir()
            session = 'PG10878-WEBVIEW-'+label
            command = [str(tc/'jdk-25.0.4/bin/java'),'-Xmx768m','-Dfile.encoding=UTF-8','-Duser.language='+language,'-Duser.country='+country,
                '-Duser.timezone=Asia/Tokyo','-javaagent:'+prepared['jacocoAgent']+'=destfile='+str(directory/'jacoco.exec')+',append=false,sessionid='+session,
                '-Xlog:class+load=info:file='+str(directory/'classload-metadata.log'),'-cp',cp,helper.stem,
                str(directory/'xml'),str(catalog),locale]
            stage = steps.step('web-view-'+label.lower(),command,Path(prepared['testCwd']),timeout=240)
            stages.append(stage)
            actual,xmls = [],{}
            for file in sorted((directory/'xml').glob('TEST-*.xml')):
                root = ET.parse(file).getroot()
                xmls[file.name] = data.sha(file.read_bytes())
                actual += [dict(classname=r.get('classname'),name=r.get('name'),nonPass=[n.tag for n in r]) for r in root.findall('testcase')]
            passed = stage['actualExit'] == 0 and not stage['timedOut'] and len(xmls) == 1 and len(actual) == 8
            passed = passed and {(r['classname'],r['name']) for r in actual} == expected and not any(r['nonPass'] for r in actual)
            if stage['actualExit'] == 0:
                assert passed and ('locale='+locale) in (SLOT/('web-view-'+label.lower()+'.stdout')).read_text()
            observed.append(dict(locale=locale,sessionId=session,actualExit=stage['actualExit'],passed=passed,cases=actual,xmlHashes=xmls,
                execSha256=data.sha((directory/'jacoco.exec').read_bytes()) if (directory/'jacoco.exec').exists() else None,
                loadedClassMetadataSha256=data.sha((directory/'classload-metadata.log').read_bytes()) if (directory/'classload-metadata.log').exists() else None))
            if not passed:
                break
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**deps,**prepared['physicalTestFiles']}.items())
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in prepared['allCurrentSourceInputHashes'].items())
    assert data.sha(helper.read_bytes()) == prepared['helperSha256'] and data.sha(catalog.read_bytes()) == begin['catalogSha256']
    traces = {}
    if observed and observed[-1]['passed']:
        assert trace_parent.is_dir() and not trace_parent.is_symlink()
        assert {p.name for p in trace_parent.iterdir()} == set(prepared['expectedTraceText'])
        for name,text in prepared['expectedTraceText'].items():
            path = trace_parent/name
            assert not path.is_symlink() and path.read_bytes() == text.encode('utf-8')
            traces[name] = dict(path=str(path),sha256=data.sha(path.read_bytes()),expectedText=text,actualText=path.read_text())
    assert all(data.sha((snapshot/p).read_bytes()) == h for p,h in prepared['allCurrentSourceInputHashes'].items())
    verify(invocation)
    passed = len(observed) == 1 and all(r['passed'] for r in observed) and all(s['actualExit'] == 0 and not s['timedOut'] for s in stages)
    code = 0 if passed else stages[-1]['actualExit'] or 1
    result = dict(actualExit=code,source=SOURCE,begin=begin,stages=stages,localeRuns=observed,
        ownedPublicTraces=traces,uniqueMethods=8,observedTestExecutions=sum(len(r['cases']) for r in observed),newTestMethods=0,
        whole451Accepted=False,coveragePendingIndependentPost=True,oldExecUnion=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    data.write(SLOT/'manifest.safe.json',result)
    OUT.mkdir()
    data.write(OUT/'manifest.json',result)
    print(json.dumps(dict(actualExit=code,localeRuns=len(observed),observedTestExecutions=result['observedTestExecutions'],
        uniqueMethods=8,manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))
    raise SystemExit(code)


if __name__ == '__main__':
    main()
