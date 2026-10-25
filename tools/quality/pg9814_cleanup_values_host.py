"""Read-only current normal code/classes, one finite cleanup4 JUnit, own fresh XML/exec only."""
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
import pg9346_direct_companion_jdk_post as steps
from host_tool_invocation import capture, verify

ROOT = data.ROOT
BASE = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
WORK = ROOT.parent / 'pgpt-runs/PG379'
SOURCE = '8ba82083ec65abc6373b8454576dcbaee7d3e621'
NORMAL = WORK / 'pg9812-cleanup-values-six-compile-v1/snapshot'
SLOT = WORK / 'pg9814-cleanup-values-host-v1'
OUT = BASE / 'PG9814-cleanup-values-host-v1'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    prepared = data.read_checked(BASE / 'PG9813-cleanup-values-preflight-v1/manifest.json',
        '5f1a770473711ca42f1374d40e0456dd41580919d89d762e6520f161b9ca8344')
    assert prepared['actualExit'] == 0 and prepared['source'] == SOURCE and prepared['expectedTests'] == 4
    cases = data.read_checked(BASE / 'PG9813-cleanup-values-preflight-v1/cases.json',prepared['casesSha256'])
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in prepared['physicalTestFiles'].items())
    assert all(data.sha((ROOT / p).read_bytes()) == data.sha((NORMAL / p).read_bytes()) == h for p,h in prepared['allCurrentSourceInputHashes'].items())
    normal = data.read_checked(data.BASE / 'PG9812-cleanup-values-six-compile-v1/manifest.json',prepared['normalManifestSha256'])
    jar = Path(normal['jars']['batch']['path'])
    assert data.sha(jar.read_bytes()) == normal['jars']['batch']['sha256']
    tc = ROOT.parent / 'toolchain'
    cpfile = NORMAL / 'src/schubert-nk-batch/target/pgpt-test-classpath.txt'
    current_main = {Path(v['path']):v['sha256'] for v in normal['jars'].values()}
    bootstrap_tests = Path(normal['jars']['bootstrap']['path'].removesuffix('.jar') + '-tests.jar')
    excluded_current_internal = {}
    libraries = []
    for entry in cpfile.read_text().strip().split(os.pathsep):
        p = Path(entry)
        if '/dev/codex/schubert/' in entry:
            continue
        if p in current_main:
            assert data.sha(p.read_bytes()) == current_main[p]
            excluded_current_internal[entry] = current_main[p]
        elif p == bootstrap_tests:
            assert p.is_file() and not p.is_symlink()
            excluded_current_internal[entry] = data.sha(p.read_bytes())
        else:
            libraries.append(p)
    protocol_jar = Path(normal['jars']['protocol']['path'])
    assert data.sha(protocol_jar.read_bytes()) == normal['jars']['protocol']['sha256']
    assert libraries and all(p.is_relative_to(tc / 'm2/repository') and p.is_file() and '/dev/codex/schubert/' not in str(p) for p in libraries)
    launcher = tc / 'm2/repository/org/junit/platform/junit-platform-launcher/1.13.4/junit-platform-launcher-1.13.4.jar'
    assert data.sha(launcher.read_bytes()) == '0b0beaeb6880a31149641d2d848b863712885469670c12099586d7f798522564'
    agent = tc / 'm2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar'
    dependencies = {str(p):data.sha(p.read_bytes()) for p in [jar,protocol_jar,*libraries,launcher,agent]}
    helper = ROOT / 'tools/quality/architecture/CleanupValueJunitLauncher.java'
    helper_sha = data.sha(helper.read_bytes())
    os.umask(0o077)
    SLOT.mkdir()
    reader = SLOT / 'launcher'
    reader.mkdir()
    catalog = SLOT / 'frozen-methods.tsv'
    with catalog.open('x') as stream:
        stream.write(''.join(r['className'] + '\t' + r['method'] + '\n' for r in cases))
    cp = os.pathsep.join(map(str,[reader,NORMAL / 'src/schubert-nk-batch/target/test-classes',jar,protocol_jar,*libraries,launcher]))
    begin = dict(source=SOURCE,preflightManifestSha256='5f1a770473711ca42f1374d40e0456dd41580919d89d762e6520f161b9ca8344',
        expectedTests=20,expectedSuites=4,helperSha256=helper_sha,catalogSha256=data.sha(catalog.read_bytes()),
        dependencyHashes=dependencies,normalTestFiles=prepared['physicalTestFiles'],sourceInputHashes=prepared['allCurrentSourceInputHashes'],
        environment=steps.ENV,excludedCurrentNormalInternalClasspath=excluded_current_internal,normalCompileReplayed=False,sourceModified=False,actualNetworkActions=0,actualDatabaseActions=0,
        actualVmActions=0,actualRootActions=0,actualServiceActions=0,invocation=invocation)
    data.write(SLOT / 'begin.safe.json',begin)
    steps.SLOT = SLOT
    stages = [steps.step('compile-launcher',[str(tc / 'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(reader),str(helper)])]
    if stages[0]['actualExit'] == 0:
        stages.append(steps.step('batch-value-junit',[str(tc / 'jdk-25.0.4/bin/java'),'-Dfile.encoding=UTF-8','-Duser.language=ja',
            '-Duser.country=JP','-Duser.timezone=Asia/Tokyo','-javaagent:' + str(agent) + '=destfile=' + str(SLOT / 'jacoco.exec') + ',append=false,sessionid=PG9814-CLEANUP-VALUES',
            '-cp',cp,helper.stem,str(SLOT / 'xml'),str(catalog)]))
    actual = []
    xmls = {}
    for path in sorted((SLOT / 'xml').glob('TEST-*.xml')):
        root = ET.parse(path).getroot()
        xmls[path.name] = data.sha(path.read_bytes())
        for case in root.findall('testcase'):
            actual.append(dict(classname=case.get('classname'),name=case.get('name'),nonPass=[n.tag for n in case]))
    code = stages[-1]['actualExit']
    if code == 0:
        assert len(xmls) == 1 and len(actual) == 4 and not any(r['nonPass'] for r in actual)
        assert {(r['classname'],r['name']) for r in actual} == {(r['className'],r['method']) for r in cases}
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**dependencies,**prepared['physicalTestFiles']}.items())
    assert all(data.sha((ROOT / p).read_bytes()) == data.sha((NORMAL / p).read_bytes()) == h for p,h in prepared['allCurrentSourceInputHashes'].items())
    assert data.sha(helper.read_bytes()) == helper_sha and data.sha(catalog.read_bytes()) == begin['catalogSha256']
    verify(invocation)
    result = dict(actualExit=code,source=SOURCE,begin=begin,stages=stages,cases=actual,xmlHashes=xmls,
        execSha256=data.sha((SLOT / 'jacoco.exec').read_bytes()) if (SLOT / 'jacoco.exec').exists() else None,
        whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,newTestIds=4)
    data.write(SLOT / 'manifest.safe.json',result)
    OUT.mkdir()
    data.write(OUT / 'manifest.json',result)
    print(json.dumps(dict(actualExit=code,tests=len(actual),suites=len(xmls),manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))
    raise SystemExit(code)


if __name__ == '__main__':
    main()
