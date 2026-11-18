"""Independently verify G07 results while publishing no scanner candidate values."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import re
import subprocess
import sys

E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
TOOLS = Path('/home/mini/codex/project1/work/toolchain')
HEX40 = re.compile(rb'(?<![a-f0-9])[a-f0-9]{40}(?![a-f0-9])')
HEX64 = re.compile(rb'(?<![a-f0-9])[a-f0-9]{64}(?![a-f0-9])')


def sha(value):
    return hashlib.sha256(value).hexdigest()


def ref(path):
    return {'path': str(path), 'sha256': sha(path.read_bytes())}


def load(path):
    return json.loads(path.read_text())


def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def git_bytes(commit, path):
    return subprocess.check_output(['git', 'show', commit + ':' + path])


def verify_history(line, finding, record, confirmed, proof):
    digest = sha(line)
    key = (record['path'], finding['RuleID'], digest)
    if key in confirmed:
        return {'kind': 'PREVIOUS_EXACT_RULE_AND_LINE', 'evidence': ref(proof)}
    assert finding['RuleID'] == 'sourcegraph-access-token'
    nearby = [x for x in HEX40.finditer(line) if abs(x.start()+1-finding['StartColumn']) <= 2
              and abs(x.end()-finding['EndColumn']) <= 2]
    assert len(nearby) == 1
    token = nearby[0][0].decode()
    assert subprocess.check_output(['git', 'cat-file', '-t', token]) == b'commit\n'
    public_refs = subprocess.check_output(
        ['git', 'for-each-ref', '--contains', token, '--format=%(refname)', 'refs/remotes/origin']
    ).splitlines()
    assert public_refs
    return {'kind': 'EXACT_TRACKED_GIT_COMMIT_OBJECT', 'status': 'REACHABLE_FROM_ORIGIN_TRACKING_REF',
            'remoteTrackingReferenceCount': len(public_refs)}


def verify_artifact(line, finding, build, build_manifest):
    key = re.match(rb'\s*"([^"]+)"\s*:', line)[1].decode()
    nearby = [x[0].decode() for x in HEX64.finditer(line) if x.start() < finding['EndColumn']
              and x.end() >= finding['StartColumn']-1]
    assert len(nearby) == 1
    digest = nearby[0]
    if key.startswith('src/') and key in build['sourceInputs']:
        assert sha(git_bytes(build['sourceCore'], key)) == digest == build['sourceInputs'][key]
        return {'kind': 'GIT_SOURCE_SHA256', 'path': key, 'source': build['sourceCore']}
    if key.endswith('.class'):
        matches = [m for m, items in build['physicalClassHashes'].items() if items.get(key) == digest]
        assert len(matches) == 1
        module = matches[0]
        actual = Path(build['cwd']) / f'src/schubert-nk-{module}/target/classes' / key
        assert sha(actual.read_bytes()) == digest
        return {'kind': 'EXACT_CLASS_ARTIFACT_SHA256', 'module': module, 'relativeClass': key,
                'build': ref(build_manifest)}
    file = Path(key)
    assert file.is_relative_to(TOOLS) and file.suffix == '.jar' and not file.is_symlink() and file.is_file()
    assert sha(file.read_bytes()) == digest
    return {'kind': 'EXACT_DECLARED_PMD_JAR_SHA256', 'declaredFile': str(file.relative_to(TOOLS))}


def binary_evidence(record, work):
    assert record['path'].endswith('/jacoco.exec') and not record['losslessGzipExpanded']
    path = work / record['prefix']
    manifest_name = str(Path(record['path']).parent / 'manifest.json')
    manifest = json.loads(git_bytes(record['firstCommit'], manifest_name))
    assert sha(path.read_bytes()) == manifest['files']['jacoco.exec'] == record['rawSha256']
    command = [str(TOOLS / 'jdk-25.0.4/bin/java'), '-jar',
               str(TOOLS / 'org.jacoco.cli-0.8.15-nodeps.jar'), 'execinfo', str(path)]
    lines = subprocess.check_output(command, text=True).splitlines()
    sessions = [line.split('"')[1] for line in lines if line.startswith('Session "')]
    assert len(sessions) == 1 and re.fullmatch(r'PG[0-9]+(?:-[A-Z0-9]+)+', sessions[0])
    rows = [line for line in lines if re.match(r'^[0-9a-f]{16}\s+\d+ of \d+\s+[^\s]+\s*$', line)]
    assert rows and all('/' in row.split()[-1] for row in rows)
    return dict(record, format='JaCoCo exec', matchingPublicPostManifest=True, session=sessions[0],
                probeRows=len(rows), productInitialization=False, onlyCrcProbeAndClassLabels=True)


def main():
    work = Path(sys.argv[1])
    out = E / 'PG38796-g07-current-public-delta-survey-v1'
    project = load(work / 'projection.json')
    idx = {item['prefix']: item for item in project['versions']}
    proof = next(E.glob('PG38671-*/manifest.json'))
    previous = load(proof)
    confirmed = {(r['path'], r['rule'], r['sha256']) for r in previous['existingFindings']}
    build_manifest = next(E.glob('PG38760-*/compile/manifest.json'))
    build = load(build_manifest)
    cache = {}
    results = []
    for found in load(work / 'report.json'):
        file = Path(found['File'])
        record = idx[str(file.relative_to(work))]
        path = record['path']
        line_number = found['StartLine']
        line = file.read_bytes().splitlines()[line_number-1]
        if path not in cache:
            old = subprocess.run(['git', 'show', project['from'] + ':' + path], capture_output=True)
            cache[path] = old.stdout.splitlines() if old.returncode == 0 else []
        if line in cache[path]:
            evidence = verify_history(line, found, record, confirmed, proof)
        else:
            evidence = verify_artifact(line, found, build, build_manifest)
        results.append({'path': path, 'blob': record['blob'], 'line': line_number,
                        'rule': found['RuleID'], 'lineSha256': sha(line), 'ground': evidence})
    binary = [binary_evidence(item, work) for item in project['versions'] if not item['text']]
    assert len(results) == 133 and len(binary) == 5
    assert load(work / 'terminal.json')['genuineExit'] == 1
    save(out / 'text-adjudication.json', results)
    save(out / 'binary-qualification.json', binary)
    m = {'actualExit': 0, 'scannerActualExit': 1, 'terminalAtUTC': datetime.now(timezone.utc).isoformat(),
         'fromCommit': project['from'], 'throughCommit': project['to'], 'commits': len(project['commits']),
         'trackedBlobVersions': len(project['versions']), 'secretScannerText': sum(x['text'] for x in project['versions']),
         'compressedExpanded': sum(x['losslessGzipExpanded'] for x in project['versions']),
         'positionFindings': len(results), 'classifiedProvenance': Counter(r['ground']['kind'] for r in results),
         'freshUnresolvedFindings': 0, 'qualifiedBinary': len(binary),
         'binaryProbeRows': sum(r['probeRows'] for r in binary),
         'publicCounts': [ref(out / 'text-adjudication.json'), ref(out / 'binary-qualification.json')],
         'rawReportSha256': sha((work / 'report.json').read_bytes()),
         'rawProjectionManifestSha256': sha((work / 'projection.json').read_bytes()),
         'initialIndependentInventoryConservative': 'Six historic findings needed Git object and remote-tracking reachability proof before they could be adjudicated; saved scan reused.',
         'untrackedRead': 0, 'privateLogRead': 0, 'wholeG07Accepted': False, 'newAcceptance': 0}
    save(out / 'manifest.json', m)
    print(json.dumps({k: m[k] for k in ('classifiedProvenance', 'binaryProbeRows', 'freshUnresolvedFindings')}))


if __name__ == '__main__':
    main()
