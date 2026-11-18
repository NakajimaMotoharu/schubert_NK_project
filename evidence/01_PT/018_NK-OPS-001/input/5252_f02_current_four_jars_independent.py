"""Independently check the Maven terminal and the four JAR payloads without invoking Maven."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
OUT = E/'PG39980-f02-current-four-production-jars-v1'
COMPILE = E/'PG39862-service-db-state-lock-four-main-v1/manifest.json'
MODEL = E/'PG38522-f02-six-resolved-maven-dependency-model-v1/manifest.json'
EDGES = E/'PG39870-f02-service-state-lock-edges-and-trace-v1/manifest.json'


def load(path):
    return json.loads(Path(path).read_bytes())


def trace(path):
    return dict(path=str(path), sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())


def main():
    manifest = load(OUT/'manifest.json')
    begin = load(OUT/'maven-jar-begin.json')
    terminal = load(OUT/'maven-jar-exit.json')
    compile = load(COMPILE)
    edges = load(EDGES)
    model = load(MODEL)
    core = manifest['sourceCore']
    assert compile['sourceCore'] == edges['source'] == core
    assert manifest['execution'] == terminal
    assert terminal['actualExit'] == 0 and begin['command'] == terminal['command']
    assert begin['startUTC'] < terminal['terminalAtUTC'] < manifest['terminalAtUTC']
    assert trace(terminal['log']['path']) == terminal['log']
    log = Path(terminal['log']['path']).read_text().splitlines()
    assert sum('[INFO] BUILD SUCCESS' in row for row in log) == 1
    assert sum(row.startswith('[INFO] Building jar:') for row in log) == 4
    witness = {}
    assert set(manifest['jars']) == {'protocol','storage','bootstrap','batch'}
    for name, record in manifest['jars'].items():
        location = Path(record['artifact']['path'])
        assert trace(location) == record['artifact']
        result = subprocess.run(['/usr/bin/unzip','-tqq',str(location)], capture_output=True, check=False, timeout=10)
        assert result.returncode == 0 and not result.stdout and not result.stderr
        with zipfile.ZipFile(location) as jar:
            entries = Counter(z.filename for z in jar.infolist() if not z.is_dir())
            assert set(entries.values()) == {1}
            files = {n: hashlib.sha256(jar.read(n)).hexdigest() for n in entries if n.endswith('.class')}
            assert files == compile['physicalClassHashes'][name]
            module = 'schubert-nk-' + name
            pom_entry = f'META-INF/maven/dev.codex.schubert/{module}/pom.xml'
            pom_sha = hashlib.sha256(jar.read(pom_entry)).hexdigest()
            assert pom_sha == compile['sourceInputs'][f'src/{module}/pom.xml']
            witness[name] = dict(archive=trace(location), verifiedClasses=len(files), entries=len(entries),
                                 unzipExit=result.returncode, embeddedPomSha256=pom_sha)
    assert sum(row['verifiedClasses'] for row in witness.values()) == 1102
    assert sum(module['nodeCount'] for module in model['modules']) == 309
    typed = edges['currentTypedEdges']
    assert (typed['total'], typed['internal'], typed['internalUnresolved']) == (17867,6009,[])
    value = dict(actualExit=0, sourceCore=core, packageEvidence=trace(OUT/'manifest.json'), jars=witness,
                 originalMavenTerminal=trace(OUT/'maven-jar-exit.json'), compile=trace(COMPILE),
                 resolvedModel=trace(MODEL), typedFour=trace(EDGES), modelNodes=309, physicalEdges=17867,
                 newProductTests=0, wholeF02Accepted=False,
                 priorVerifierGuard=dict(actualExit=1, reason='Stored unresolved field is a list, not a count',
                                         mavenRepeated=False),
                 terminalAtUTC=datetime.now(timezone.utc).isoformat())
    with (OUT/'independent.json').open('x') as output:
        json.dump(value, output, indent=2)
        output.write('\n')
    print('Independent 4/4, 1102/1102, model 309, physical edges 17867')


if __name__ == '__main__':
    main()
