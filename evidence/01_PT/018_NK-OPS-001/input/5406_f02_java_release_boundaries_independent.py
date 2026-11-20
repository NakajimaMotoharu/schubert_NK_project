"""Verify actual lower and upper Java rejection against the current root POM."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from xml.etree import ElementTree


OPS = Path('evidence/01_PT/018_NK-OPS-001/evidence')


def pin(path):
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def main():
    run = next(OPS.glob('PG40666-*'))
    terminal = run/'terminal.json'
    receipt = json.loads(terminal.read_bytes())
    begin = json.loads((run/'begin.json').read_bytes())
    assert all(receipt[key] == value for key, value in begin.items())
    assert receipt['productBuilds'] == receipt['productTests'] == 0
    for ref in (receipt['maven'], receipt['mavenCore']):
        assert pin(Path(ref['path'])) == ref
    core = receipt['productionCore']
    pom = subprocess.check_output(['git', 'show', f'{core}:pom.xml'])
    ns = {'p': 'http://maven.apache.org/POM/4.0.0'}
    xml = ElementTree.fromstring(pom)
    plugin = xml.find("p:build/p:plugins/p:plugin[p:artifactId='maven-enforcer-plugin']", ns)
    execution = plugin.find("p:executions/p:execution[p:id='toolchain-and-dependency-contract']", ns)
    constraint = execution.findtext('p:configuration/p:rules/p:requireJavaVersion/p:version', namespaces=ns)
    assert constraint == '[25,26)'
    assert set(receipt['cases']) == {'24', '26'}
    diagnostic = '[ERROR] Rule 0: org.apache.maven.enforcer.rules.version.RequireJavaVersion failed with message:'
    for major, runtime in (('24', '24.0.2'), ('26', '26')):
        test = receipt['cases'][major]
        assert test['actualExit'] == 1 and test['destinationCreated'] is False
        assert test['pomSha256'] == hashlib.sha256(pom).hexdigest()
        assert test['tools'] == ['Apache Maven 3.9.12', f'Java version: {runtime}, vendor: Eclipse Adoptium']
        path = Path(test['observed']['path'])
        assert pin(path) == test['observed']
        lines = path.read_text().splitlines()
        assert [line for line in lines if line.startswith('[INFO] --- ')] == [
            '[INFO] --- enforcer:3.6.3:enforce (toolchain-and-dependency-contract) @ schubert-nk ---']
        assert [line for line in lines if ' failed with message:' in line] == [diagnostic]
        assert '[INFO] Rule 1: org.apache.maven.enforcer.rules.version.RequireMavenVersion passed' in lines
        assert '[INFO] BUILD FAILURE' in lines
    retained = next(OPS.glob('PG40602-*/manifest.json'))
    successful = json.loads(retained.read_bytes())
    maven_bound = next(OPS.glob('PG40644-*/manifest.json'))
    original = json.loads(maven_bound.read_bytes())
    assert successful['productionCore'] == original['productionCore'] == core
    assert successful['actualExit'] == original['actualExit'] == 0
    assert original['matchingPomSha256'] == hashlib.sha256(pom).hexdigest()
    assert original['sameJavaBinary'] and original['retainedAcceptedToolchain'] == pin(retained)

    out = OPS/'PG40668-f02-java-release-boundaries-independent-v1'
    out.mkdir()
    target = out/'manifest.json'
    with target.open('x') as file:
        json.dump(dict(actualExit=0, source=receipt['source'], productionCore=core,
                       testIds=['PT-F02-JAVA-001', 'PT-F02-JAVA-002'], actualRejections=2,
                       observedProcessExits=[1, 1], originalReleaseConstraint=constraint,
                       acceptedJava25=pin(retained), samePomAtTwoRejections=True,
                       actualProductBuilds=0, earlierSuccessReexecuted=False,
                       fullF02Accepted=False, nativeRuntimeVerified=False,
                       originalTerminal=pin(terminal), terminalAtUTC=datetime.now(timezone.utc).isoformat()),
                  file, indent=2)
        file.write('\n')
    print(pin(target))


if __name__ == '__main__':
    main()
