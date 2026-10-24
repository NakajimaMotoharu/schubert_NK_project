"""New-only public parent POM/existing checked SDK artifacts, no product execution."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
from host_tool_invocation import capture, verify

ROOT = Path(__file__).resolve().parents[2]
TC = Path('/home/mini/codex/project1/work/toolchain')
SDK = TC / 'prometheus-sdk-1.17.1-client-1.7.0-new-v1'
SLOT = Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg8240-prometheus-maven-coordinates-v1')
OUT = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG8240-prometheus-maven-coordinates-v1'
M2 = TC / 'm2/repository'
NS = {'m': 'http://maven.apache.org/POM/4.0.0'}
ARTIFACTS = ('prometheus-metrics-config', 'prometheus-metrics-model', 'prometheus-metrics-exposition-textformats')


def sha(path, algorithm='sha256'):
    return hashlib.new(algorithm, path.read_bytes()).hexdigest()


def save(path, data):
    with path.open('x') as stream:
        json.dump(data, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')


def place(source, target):
    if target.is_symlink():
        raise ValueError('symlink destination not accepted')
    if target.exists():
        if sha(target) != sha(source):
            raise ValueError('existing Maven coordinate differs; no overwrite')
        state = 'REUSED_IDENTICAL'
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write(source.read_bytes())
            stream.flush()
            os.fsync(stream.fileno())
        state = 'CREATED_NEW_COORDINATE'
    return dict(path=str(target), sha256=sha(target), state=state)


def parent(coordinate, depth=0):
    if depth > 3 or any(re.fullmatch(r'[A-Za-z0-9_.-]+', value) is None for value in coordinate):
        raise ValueError('bounded literal parent coordinates required')
    group, artifact, version = coordinate
    filename = artifact + '-' + version + '.pom'
    path = SLOT / filename
    for suffix, limit in (('', 1048576), ('.sha1', 128)):
        url = 'https://repo.maven.apache.org/maven2/' + group.replace('.', '/') + '/' + artifact + '/' + version + '/' + filename + suffix
        command = ['/usr/bin/curl', '--disable', '--fail', '--silent', '--show-error', '--proto', '=https', '--max-time', '45', '--max-filesize', str(limit), url]
        start = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with (SLOT / (filename + suffix)).open('xb') as stream:
            child = subprocess.Popen(command, stdout=stream, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, env={'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'}, cwd=SLOT)
            save(SLOT / (filename + suffix + '.process.safe.json'), dict(pid=child.pid, ownerPid=os.getpid(), command=command, startUTC=start))
            try:
                _, err = child.communicate(timeout=50)
            except subprocess.TimeoutExpired:
                child.kill()
                child.communicate()
                raise
        save(SLOT / (filename + suffix + '.exit.safe.json'), dict(actualExit=child.returncode, endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(), stderr=err.decode('utf-8', 'replace')))
        if child.returncode != 0:
            raise ValueError('public artifact failed; no retry or alternative route')
    expected = Path(str(path) + '.sha1').read_text().strip()
    if re.fullmatch('[a-f0-9]{40}', expected) is None or sha(path, 'sha1') != expected:
        raise ValueError('parent checksum mismatch')
    data = path.read_bytes()
    if b'<!DOCTYPE' in data or b'<!ENTITY' in data:
        raise ValueError('parent contains DTD/entity')
    doc = ET.fromstring(data)
    ancestor = doc.find('m:parent', NS)
    rows = []
    if ancestor is not None:
        rows.extend(parent(tuple(ancestor.findtext('m:' + field, namespaces=NS) or '' for field in ('groupId', 'artifactId', 'version')), depth + 1))
    dest = M2 / group.replace('.', '/') / artifact / version / filename
    rows.append(dict(coordinate=coordinate, repositorySha1=expected, **place(path, dest)))
    return rows


def main():
    invocation = capture(Path(__file__))
    SLOT.mkdir(exist_ok=False)
    OUT.mkdir(exist_ok=False)
    rows = parent(('io.prometheus', 'client_java', '1.7.0'))
    for artifact in ARTIFACTS:
        for suffix in ('.pom', '.jar'):
            source = SDK / (artifact + '-1.7.0' + suffix)
            expected = Path(str(source) + '.sha1').read_text().strip()
            if re.fullmatch('[a-f0-9]{40}', expected) is None or sha(source, 'sha1') != expected:
                raise ValueError('prepared SDK checksum differs')
            rows.append(dict(coordinate=['io.prometheus', artifact, '1.7.0'], repositorySha1=expected, **place(source, M2 / 'io/prometheus' / artifact / '1.7.0' / source.name)))
    verify(invocation)
    downloads = list(SLOT.glob('*.exit.safe.json'))
    result = dict(status='PUBLIC_MAVEN_COORDINATES_PREPARED', entries=rows, invocation=invocation, productionPT=0, productClassInitialization=0, targetNetworkOperations=0, publicArtifactDownloads=len(downloads), vendorSignatureAvailable=False, preexistingDifferentCoordinateOverwrites=0)
    save(SLOT / 'manifest.json', result)
    save(OUT / 'manifest.json', result)
    print(json.dumps(dict(status=result['status'], coordinates=len(rows), manifestSha256=sha(OUT / 'manifest.json'))))


if __name__ == '__main__':
    main()
