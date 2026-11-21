"""Run the repository NullAway compiler on the admitted current Music/Web subset."""

from copy import deepcopy
from datetime import datetime, timezone
import importlib.util
import os
from pathlib import Path
import subprocess
from tempfile import mkdtemp
import xml.etree.ElementTree as ET
from zipfile import ZipFile

parent = Path(__file__).with_name('5686_scr011_012_template_current_six.py')
spec = importlib.util.spec_from_file_location('music_scope_helpers', parent)
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
NS = 'http://maven.apache.org/POM/4.0.0'
RUN = 'PG41504-f03-music-current-nullaway-subset-v1'


def tag(name):
    return f'{{{NS}}}{name}'


def put(element, name, text=None):
    child = ET.SubElement(element, tag(name))
    child.text = text
    return child


def main():
    group = h.read(next(h.PLAN.glob('1903_*')))
    source, core = group['values']['source'], group['values']['productionCoreMain']
    quota = group['quota']
    age = datetime.now(timezone.utc) - datetime.fromisoformat(quota['observedAtUTC'])
    assert quota['ordinaryUsageAllowed'] and 0 <= age.total_seconds() <= 120
    assert all(w is None or w['remainingPercent'] > 10 for w in (quota['primary'], quota['secondary']))
    assert h.git('rev-parse', 'HEAD').decode().strip() == source
    templates = h.evidence('41502')
    projection = h.evidence('41500')
    current_scope = {path: checksum for path, checksum in h.read(templates)['currentMainFixtureAndResourceHashes'].items()
                     if '/src/main/java/' in path}
    current_scope.update({row['path']: row['sha256'] for row in h.read(projection)['verifiedSourceInputs']
                          if '/src/main/java/' in row['path']})
    assert len(current_scope) == 30
    held = ('TemporaryInfrastructureException', 'FingerprintKeyRing', 'ResponseSnapshotCodec', 'WebStartupException')
    actual = {}
    for name, checksum in current_scope.items():
        path = Path(name)
        content = h.git('show', f'{source}:{path}')
        assert h.pin(path)['sha256'] == checksum and content == path.read_bytes()
        assert not any(key.encode() in content for key in held)
        actual[name] = content

    proof = h.read(h.evidence('41322'))['packagingProof']['artifacts']['protocol']
    protocol = Path(proof['artifact']['path'])
    assert h.pin(protocol)['sha256'] == proof['artifact']['sha256']
    assert not h.git('diff', '--name-only', proof['archiveSource'], source, '--', 'pom.xml', 'src/schubert-nk-protocol')
    with ZipFile(protocol) as archive:
        names = [x for x in archive.namelist() if x.endswith('.class')]
    assert len(names) == 176 and all(n.startswith('dev/codex/schubert/nk/protocol/') for n in names)
    assert not any(any(k in n for k in held) for n in names)
    deps = {protocol: h.pin(protocol)['sha256']}
    history = h.read(h.evidence('27750'))
    for name, checksum in history['dependencies'].items():
        p = Path(name)
        if not p.is_relative_to(h.TOOLS) or p.name.startswith('junit-'):
            continue
        assert h.pin(p)['sha256'] == checksum and not p.name.startswith('schubert-nk-')
        deps[p] = checksum

    root = ET.fromstring(h.git('show', f'{source}:pom.xml'))
    compiler = next(p for p in root.findall('.//' + tag('plugin'))
                    if p.findtext(tag('artifactId')) == 'maven-compiler-plugin')
    text = ET.tostring(compiler, encoding='unicode')
    assert 'NullAway:ERROR' in text and '-Werror' in text and 'JSpecifyMode=true' in text
    pom = ET.Element(tag('project'))
    for key, value in (('modelVersion','4.0.0'), ('groupId','dev.codex.schubert.quality'),
                       ('artifactId','music-current-source-scope'), ('version','0.1.0-SNAPSHOT')):
        put(pom, key, value)
    pom.append(deepcopy(root.find(tag('properties'))))
    requirements = put(pom, 'dependencies')
    for number, p in enumerate(deps):
        dep = put(requirements, 'dependency')
        for key, value in (('groupId','dev.codex.schubert.quality.cached'), ('artifactId',f'fixed-{number}'),
                           ('version','1'),('scope','system'),('systemPath',str(p))):
            put(dep, key, value)
    put(put(pom, 'build'), 'plugins').append(deepcopy(compiler))
    ET.register_namespace('', NS)

    work = Path(mkdtemp(prefix='pgpt-f03-music-current-', dir='/dev/shm'))
    for path, content in actual.items():
        out = work / 'src/main/java' / path.split('/src/main/java/', 1)[1]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(content)
    config = work / 'pom.xml'
    ET.ElementTree(pom).write(config, encoding='utf-8', xml_declaration=True)
    maven = h.TOOLS / 'm2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'
    repo = h.TOOLS / 'm2/repository'
    args = [str(maven), '-o', '--no-transfer-progress', '-Dmaven.repo.local='+str(repo),
            '-Dmaven.test.skip=true', 'compile']
    private = h.ROOT.parent / 'pgpt-runs/PG379' / RUN
    private.mkdir(mode=0o700)
    begin = dict(source=source, core=core, run=RUN, sourceScope=current_scope,
                 allowedProtocolClassNames=names, dependencies={str(k): v for k,v in deps.items()},
                 rootCompilerSha256=h.pin(Path('pom.xml'))['sha256'], normalizedTempPom=h.pin(config),
                 actualCommand=args, cwd=str(work))
    h.write(private / 'begin.json', begin)
    system = {**os.environ,'JAVA_HOME':str(h.JAVA.parent.parent),'LC_ALL':'C.UTF-8','TZ':'Asia/Tokyo'}
    start = h.now()
    result = subprocess.run(args, cwd=work, env=system, capture_output=True, timeout=120)
    (private/'compile.stdout').write_bytes(result.stdout)
    (private/'compile.stderr').write_bytes(result.stderr)
    terminal = dict(exit=result.returncode, startUTC=start, terminalAtUTC=h.now(),
                    stdoutSha=h.pin(private/'compile.stdout')['sha256'], stderrSha=h.pin(private/'compile.stderr')['sha256'])
    h.write(private/'compile.terminal.json', terminal)
    physical = {p.relative_to(work/'target/classes').as_posix(): h.pin(p)['sha256']
                for p in (work/'target/classes').rglob('*.class')}
    assert all(not any(key in n for key in held) for n in physical)
    verified = result.returncode == 0 and b'BUILD SUCCESS' in result.stdout and len(physical) == 36
    out = h.OPS / RUN
    out.mkdir()
    h.write(out/'manifest.json',dict(**begin, actualExit=result.returncode, compiler=terminal,
        compileScopeVerified=verified, physical=physical, applied=['-Xlint:all','-Werror','NullAway:ERROR'],
        noTestsExecuted=True, noHeldOrRuntimeOperations=True, nextStillRequired='Rest of all six modules. QA056, Root11, protected Tests and whole 451 are still open.',
        originalRequalification=[h.pin(templates),h.pin(projection)], formalAcceptanceId=None,
        whole451=False, terminalAtUTC=h.now()))
    print('Exit', result.returncode, 'sources', len(actual), 'physical', len(physical), 'verified', verified)


if __name__ == '__main__':
    main()
