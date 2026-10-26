"""Four changed pure Protocol methods in two new dedicated locale JVMs; no held domains."""
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9346_direct_companion_jdk_post as steps

SOURCE = '1f20074cdfd20e13527525ed8d0e57faff28e276'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg10760-protocol-semantic-host-v1'
OUT = data.BASE/'PG10760-protocol-semantic-host-v1'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    prepared_path = data.BASE/'PG10758-protocol-semantic-preflight-v1/manifest.json'
    prepared = data.read_checked(prepared_path,'7ed1324d2b7599679b27bc7484dc54dfc5d539bfd0db1db40aabb5a9c7472b4f')
    assert prepared['actualExit'] == 0 and prepared['source'] == SOURCE
    cases = data.read_checked(prepared_path.parent/'cases.json',prepared['casesSha256'])
    assert len(cases) == prepared['expectedTestsPerLocale'] == 4
    expected = {(r['className'],r['method']) for r in cases}
    assert len(expected) == 4 and prepared['locales'] == ['ja-JP','tr-TR']
    deps = prepared['dependencyHashes']
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**deps,**prepared['physicalTestFiles']}.items())
    snapshot = Path(prepared['normalSnapshot'])
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((snapshot/p).read_bytes()) == h for p,h in prepared['allCurrentSourceInputHashes'].items())
    helper = Path(prepared['helperPath'])
    assert data.sha(helper.read_bytes()) == prepared['helperSha256']
    os.umask(0o077)
    SLOT.mkdir()
    reader = SLOT/'launcher'
    reader.mkdir()
    catalog = SLOT/'frozen-methods.tsv'
    with catalog.open('x') as stream:
        stream.write(''.join(r['className']+'\t'+r['method']+'\n' for r in cases))
    cp = os.pathsep.join(map(str,[reader,prepared['testClassesDirectory'],prepared['protocolJar'],
        *prepared['libraryClasspath'],prepared['launcherJar']]))
    tc = data.ROOT.parent/'toolchain'
    begin = dict(source=SOURCE,invocation=invocation,preflightManifestSha256=data.sha(prepared_path.read_bytes()),
        dependencyHashes=deps,physicalTestFiles=prepared['physicalTestFiles'],sourceInputHashes=prepared['allCurrentSourceInputHashes'],
        helperSha256=prepared['helperSha256'],catalogSha256=data.sha(catalog.read_bytes()),classpath=cp,
        expectedTestsPerLocale=4,expectedSuitesPerLocale=1,expectedUniqueMethods=4,expectedLocaleRuns=['ja-JP','tr-TR'],
        environment=steps.ENV,actualNetworkActions=0,actualDatabaseActions=0,actualVmActions=0,
        actualRootActions=0,actualServiceActions=0,heldOperationsPermitted=False,normalCompileReplayed=False)
    data.write(SLOT/'begin.safe.json',begin)
    steps.SLOT = SLOT
    stages = [steps.step('compile-launcher',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror',
        '-cp',cp,'-d',str(reader),str(helper)])]
    observed = []
    if stages[0]['actualExit'] == 0 and not stages[0]['timedOut']:
        for language,country,label in [('ja','JP','JP'),('tr','TR','TR')]:
            locale = language+'-'+country
            directory = SLOT/label.lower()
            directory.mkdir()
            session = 'PG10760-PROTOCOL-'+label
            command = [str(tc/'jdk-25.0.4/bin/java'),'-Dfile.encoding=UTF-8','-Duser.language='+language,'-Duser.country='+country,
                '-Duser.timezone=Asia/Tokyo','-javaagent:'+prepared['jacocoAgent']+'=destfile='+str(directory/'jacoco.exec')+',append=false,sessionid='+session,
                '-Xlog:class+load=info:file='+str(directory/'classload-metadata.log'),'-cp',cp,helper.stem,
                str(directory/'xml'),str(catalog),locale]
            stage = steps.step('protocol-'+label.lower(),command)
            stages.append(stage)
            actual,xmls = [],{}
            for file in sorted((directory/'xml').glob('TEST-*.xml')):
                root = ET.parse(file).getroot()
                xmls[file.name] = data.sha(file.read_bytes())
                actual += [dict(classname=r.get('classname'),name=r.get('name'),nonPass=[n.tag for n in r]) for r in root.findall('testcase')]
            passed = stage['actualExit'] == 0 and not stage['timedOut'] and len(xmls) == 1 and len(actual) == 4
            passed = passed and {(r['classname'],r['name']) for r in actual} == expected and not any(r['nonPass'] for r in actual)
            if stage['actualExit'] == 0:
                assert passed and ('locale='+locale) in (SLOT/('protocol-'+label.lower()+'.stdout')).read_text()
            observed.append(dict(locale=locale,sessionId=session,actualExit=stage['actualExit'],passed=passed,cases=actual,xmlHashes=xmls,
                execSha256=data.sha((directory/'jacoco.exec').read_bytes()) if (directory/'jacoco.exec').exists() else None,
                loadedClassMetadataSha256=data.sha((directory/'classload-metadata.log').read_bytes()) if (directory/'classload-metadata.log').exists() else None))
            if not passed:
                break
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**deps,**prepared['physicalTestFiles']}.items())
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in prepared['allCurrentSourceInputHashes'].items())
    assert data.sha(helper.read_bytes()) == prepared['helperSha256'] and data.sha(catalog.read_bytes()) == begin['catalogSha256']
    verify(invocation)
    passed = len(observed) == 2 and all(r['passed'] for r in observed) and all(s['actualExit'] == 0 and not s['timedOut'] for s in stages)
    code = 0 if passed else stages[-1]['actualExit'] or 1
    result = dict(actualExit=code,source=SOURCE,begin=begin,stages=stages,localeRuns=observed,
        uniqueMethods=4,observedTestExecutions=sum(len(r['cases']) for r in observed),newTestMethods=0,
        whole451Accepted=False,coveragePendingIndependentPost=True,oldExecUnion=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    data.write(SLOT/'manifest.safe.json',result)
    OUT.mkdir()
    data.write(OUT/'manifest.json',result)
    print(json.dumps(dict(actualExit=code,localeRuns=len(observed),observedTestExecutions=result['observedTestExecutions'],
        uniqueMethods=4,manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))
    raise SystemExit(code)


if __name__ == '__main__':
    main()
