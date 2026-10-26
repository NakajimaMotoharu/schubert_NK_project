"""Recover original successful SpotBugs stage and two distinct report schemas; no tool/PT replay."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG10813-protocol-spotbugs-recovery-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    original_path = data.BASE/'PG10812-protocol-spotbugs-v1/manifest.json'
    original = data.read_checked(original_path,'c85541eea501a0db091ebc4fa110da5ece2212c5e026d2021ddb44aa0f448d11')
    assert original['actualExit'] == 1 and original['findings'] is original['processingErrors'] is None
    stage = original['stage']
    assert stage['actualExit'] == 0 and not stage['timedOut']
    work = data.ROOT.parent/'pgpt-runs/PG379/pg10812-protocol-spotbugs-v1'
    for label in ('stdout','stderr'):
        assert data.sha((work/('spotbugs.'+label)).read_bytes()) == stage[label+'Sha256']
    assert json.loads((work/'spotbugs-exit.safe.json').read_bytes()) == stage
    normal_path = data.BASE/'PG10800-protocol-quality-six-compile-v1/manifest.json'
    normal = data.read_checked(normal_path,'ee02e1c29144a78486897564d0840a86c90bfe96f6fd19f5f75af8fbe4d311b4')
    assert original['source'] == normal['source'] == 'e73e9558971a81d30d7f81f6ab0bc5d9662667d2'
    snapshot = Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((snapshot/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    assert all(data.sha(Path(r['path']).read_bytes()) == r['sha256'] for r in normal['jars'].values())
    target = Path(normal['jars']['protocol']['path']).parent
    primary = target/'spotbugsXml.xml'
    check = target/'spotbugs.xml'
    assert {p.name for p in target.glob('spotbugs*.xml')} == {primary.name,check.name}
    assert data.sha(primary.read_bytes()) == 'e65b6907501329fea7af0eee03055f964f30866e1966674bd6eba7d01a841f0d'
    assert data.sha(check.read_bytes()) == '66029ed4e07b8123f1210f2eb754f9853f0f34ea959a40afc248013b3bbaf288'
    root = ET.fromstring(primary.read_bytes())
    assert root.tag == 'BugCollection' and root.get('version') == '4.10.4'
    errors = root.find('Errors')
    assert errors is not None and errors.get('errors') == errors.get('missingClasses') == '0'
    assert not list(errors) and not root.findall('BugInstance')
    summary = root.find('FindBugsSummary')
    assert summary is not None and summary.get('total_classes') == '176' and summary.get('total_bugs') == '0'
    analyzed = root.findall('.//ClassStats')
    assert len(analyzed) == 176 and all(int(r.get('bugs')) == 0 for r in analyzed)
    names = {r.get('class').replace('.','/')+'.class' for r in analyzed}
    import zipfile
    with zipfile.ZipFile(normal['jars']['protocol']['path']) as jar:
        assert names == {n for n in jar.namelist() if n.endswith('.class')}
    assert [n.text for n in root.findall('Project/Jar')] == [str(target/'classes')]
    secondary = ET.fromstring(check.read_bytes())
    assert secondary.tag == 'BugCollection' and secondary.attrib == dict(version='4.10.4',threshold='low',effort='max')
    assert [c.tag for c in secondary] == ['Error','Project']
    placeholder = secondary.find('Error')
    assert placeholder is not None and not placeholder.attrib and len(placeholder) == 0 and not (placeholder.text or '').strip()
    assert [n.text for n in secondary.findall('Project/SrcDir')] == [str(target.parent/'src/main/java'),str(target.parent/'src/test/java')]
    assert not list(target.glob('surefire-reports/TEST-*.xml'))
    verify(invocation)
    OUT.mkdir()
    for path in (primary,check):
        with (OUT/path.name).open('xb') as stream:
            stream.write(path.read_bytes())
    data.write(OUT/'manifest.json',dict(actualExit=0,source=normal['source'],invocation=invocation,
        originalMetadataExit=1,originalMavenActualExit=0,originalManifestSha256=data.sha(original_path.read_bytes()),
        normalManifestSha256=data.sha(normal_path.read_bytes()),primaryReportSha256=data.sha(primary.read_bytes()),
        checkDiagnosticReportSha256=data.sha(check.read_bytes()),findings=0,processingErrors=0,missingClasses=0,
        allPhysicalProtocolMainClasses=176,analysisClassNames=sorted(names),bytecodeInputSha256=normal['jars']['protocol']['sha256'],
        productTestsExecuted=0,mavenReplayed=False,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
