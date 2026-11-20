"""Match the real Maven negative run to the positive current Protocol receipt."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from xml.etree import ElementTree


OPS = Path('evidence/01_PT/018_NK-OPS-001/evidence')


def pin(path):
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def read(ref):
    path = Path(ref['path'])
    assert pin(path) == ref
    return json.loads(path.read_bytes())


def main():
    negative = next(OPS.glob('PG40642-*')) / 'terminal.json'
    bad = json.loads(negative.read_bytes())
    start = read(bad['begin'])
    core = bad['productionCore']
    assert core == start['productionCore'] and bad['source'] == start['source']
    pom = subprocess.check_output(['git', 'show', f'{core}:pom.xml'])
    assert hashlib.sha256(pom).hexdigest() == start['rootPomSha256']
    ns = {'p': 'http://maven.apache.org/POM/4.0.0'}
    document = ElementTree.fromstring(pom)
    plugin = document.find("p:build/p:plugins/p:plugin[p:artifactId='maven-enforcer-plugin']", ns)
    assert plugin.findtext('p:version', namespaces=ns) == '3.6.3'
    execution = plugin.find("p:executions/p:execution[p:id='toolchain-and-dependency-contract']", ns)
    rules = execution.find('p:configuration/p:rules', ns)
    assert rules.findtext('p:requireMavenVersion/p:version', namespaces=ns) == '[3.9.12,4)'
    assert rules.findtext('p:requireJavaVersion/p:version', namespaces=ns) == '[25,26)'
    assert '-N' in start['command'] and '-o' in start['command'] and start['command'][-1] == 'validate'
    assert start['toolVersions'][0] == 'Apache Maven 3.9.11'
    assert start['toolVersions'][1].startswith('Java version: 25.0.4,')
    assert bad['actualExit'] == 1 and bad['targetCreated'] is False
    report = Path(bad['output']['path'])
    assert pin(report) == bad['output']
    lines = report.read_text().splitlines()
    assert lines == [
        '[INFO] --- enforcer:3.6.3:enforce (toolchain-and-dependency-contract) @ schubert-nk ---',
        '[INFO] Rule 0: org.apache.maven.enforcer.rules.version.RequireJavaVersion passed',
        '[INFO] Rule 2: org.apache.maven.enforcer.rules.dependency.DependencyConvergence passed',
        '[INFO] BUILD FAILURE',
        '[ERROR] Rule 1: org.apache.maven.enforcer.rules.version.RequireMavenVersion failed with message:',
        '[ERROR] Detected Maven Version: 3.9.11 is not in the allowed range [3.9.12,4).',
    ]
    assert bad['observedStages'] == lines[:1]

    positive = next(OPS.glob('PG40602-*')) / 'manifest.json'
    old = json.loads(positive.read_bytes())
    original = read(old['mavenVerify'])
    original_start = read(original['begin'])
    inventory = read(original_start['sourceInventory'])
    assert old['productionCore'] == original['productionCore'] == original_start['productionCore'] == core
    assert original['actualExit'] == old['actualExit'] == 0
    assert inventory['pom.xml']['sha256'] == start['rootPomSha256']
    assert original_start['java']['sha256'] == start['javaSha256']
    launcher = Path(original_start['maven']['path'])
    assert pin(launcher) == original_start['maven']
    assert 'apache-maven-3.9.12' in launcher.parts
    core_jar = pin(launcher.parent.parent / 'lib/maven-core-3.9.12.jar')
    original_steps = Path(original['filteredMavenSteps']['path'])
    assert pin(original_steps) == original['filteredMavenSteps']
    assert '[INFO] --- enforcer:3.6.3:enforce (toolchain-and-dependency-contract) @ schubert-nk-protocol ---' in original_steps.read_text()

    destination = OPS / 'PG40644-f02-maven-lower-bound-independent-v1'
    destination.mkdir()
    manifest = destination / 'manifest.json'
    with manifest.open('x') as output:
        json.dump(dict(testId='PT-F02-MAVEN-001', workIds=['WBS-F02', 'WBS-F02-a'],
                       source=bad['source'], productionCore=core, actualExit=0,
                       terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                       expectedRejectionExit=1, observedRejectionExit=bad['actualExit'],
                       onlyEnforcerInvoked=True, matchingPomSha256=start['rootPomSha256'],
                       sameJavaBinary=True, actualMavenFloor='3.9.12',
                       retainedAcceptedToolchain=pin(positive), installedMavenCore=core_jar,
                       negativeEvidence=pin(negative), observedEnforcerText=pin(report),
                       earlierSuccessReplayCount=0, newBuildOrProductTestCount=0,
                       wholeF02Accepted=False, whole451Accepted=False), output, indent=2)
        output.write('\n')
    print(pin(manifest))


if __name__ == '__main__':
    main()
