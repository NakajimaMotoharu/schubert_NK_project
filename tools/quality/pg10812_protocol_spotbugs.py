"""One offline Protocol SpotBugs check on frozen compiled Main; plugin has no executed phase/PT."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9346_direct_companion_jdk_post as steps

SOURCE = 'e73e9558971a81d30d7f81f6ab0bc5d9662667d2'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg10812-protocol-spotbugs-v1'
OUT = data.BASE/'PG10812-protocol-spotbugs-v1'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    path = data.BASE/'PG10800-protocol-quality-six-compile-v1/manifest.json'
    normal = data.read_checked(path,'ee02e1c29144a78486897564d0840a86c90bfe96f6fd19f5f75af8fbe4d311b4')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    snapshot = Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((snapshot/p).read_bytes()) == h for p,h in hashes.items())
    tc = data.ROOT.parent/'toolchain'
    plugin = tc/'m2/repository/com/github/spotbugs/spotbugs-maven-plugin/4.10.4.0/spotbugs-maven-plugin-4.10.4.0.jar'
    plugin_sha = data.sha(plugin.read_bytes())
    descriptor = ET.fromstring(zipfile.ZipFile(plugin).read('META-INF/maven/plugin.xml'))
    goals = {m.findtext('goal'):m for m in descriptor.findall('./mojos/mojo')}
    assert goals['check'].findtext('executeGoal') == 'spotbugs'
    assert goals['check'].findtext('executePhase') is None and goals['spotbugs'].findtext('executePhase') is None
    pom = (snapshot/'src/schubert-nk-protocol/pom.xml').read_text()
    assert '<effort>Max</effort>' in pom and '<threshold>Low</threshold>' in pom and '<includeTests>true' not in pom
    target = snapshot/'src/schubert-nk-protocol/target'
    assert not list(target.glob('spotbugs*.xml')) and not list(target.glob('surefire-reports/TEST-*.xml'))
    SLOT.mkdir(mode=0o700)
    command = [str(tc/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-o','--no-transfer-progress',
        '-Dmaven.repo.local='+str(tc/'m2/repository'),'-f',str(snapshot/'src/schubert-nk-protocol/pom.xml'),
        'com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check']
    data.write(SLOT/'begin.safe.json',dict(source=SOURCE,invocation=invocation,command=command,
        normalManifestSha256=data.sha(path.read_bytes()),pluginJarSha256=plugin_sha,sourceInputHashes=hashes,
        productTestsPermitted=False,actualExternalActions=0,executePhase=None))
    steps.SLOT = SLOT
    result = steps.step('spotbugs',command)
    reports = list(target.glob('spotbugs*.xml'))
    findings,errors,report_sha = None,None,None
    raw = None
    if len(reports) == 1:
        raw = reports[0].read_bytes()
        xml = ET.fromstring(raw)
        findings = len(xml.findall('BugInstance'))
        errors = xml.find('Errors')
        errors = int(errors.get('errors')) if errors is not None and errors.get('errors') is not None else None
        report_sha = data.sha(raw)
    assert not list(target.glob('surefire-reports/TEST-*.xml'))
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((snapshot/p).read_bytes()) == h for p,h in hashes.items())
    assert all(data.sha(Path(r['path']).read_bytes()) == r['sha256'] for r in normal['jars'].values())
    assert data.sha(plugin.read_bytes()) == plugin_sha
    verify(invocation)
    passed = result['actualExit'] == 0 and not result['timedOut'] and findings == errors == 0 and raw is not None
    OUT.mkdir()
    if raw is not None:
        with (OUT/'spotbugs.xml').open('xb') as stream:
            stream.write(raw)
    data.write(OUT/'manifest.json',dict(actualExit=0 if passed else 1,source=SOURCE,invocation=invocation,
        stage=result,normalManifestSha256=data.sha(path.read_bytes()),pluginJarSha256=plugin_sha,
        findings=findings,processingErrors=errors,reportSha256=report_sha,productTestsExecuted=0,
        bytecodeInputSha256=normal['jars']['protocol']['sha256'],externalActions=0,whole451Accepted=False,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0 if passed else 1,findings=findings,processingErrors=errors,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
