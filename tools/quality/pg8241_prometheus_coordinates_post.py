"""Independent correction of original preparation metadata; no downloads, PT or class loading."""
import ast
import hashlib
import json
from pathlib import Path
from host_tool_invocation import capture, verify

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG8241-prometheus-coordinates-post-v1'
SLOT = Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg8240-prometheus-maven-coordinates-v1')
RAW = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG8240-prometheus-maven-coordinates-v1/manifest.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(raw):
    rows = raw['entries']
    assert len(rows) == 8 and len({r['path'] for r in rows}) == 8
    assert all(Path(row['path']).is_file() and not Path(row['path']).is_symlink() and digest(Path(row['path'])) == row['sha256'] for row in rows)
    terminals = sorted(SLOT.glob('*.exit.safe.json'))
    assert len(terminals) == 4 and all(json.loads(p.read_text())['actualExit'] == 0 for p in terminals)
    process = sorted(SLOT.glob('*.process.safe.json'))
    assert len(process) == 4
    for path in process:
        row = json.loads(path.read_text())
        assert row['command'][:2] == ['/usr/bin/curl', '--disable']
        assert row['command'][-1].startswith('https://repo.maven.apache.org/maven2/io/prometheus/')
    assert raw['publicArtifactDownloads'] == 2  # Historical error preserved, not rewritten.
    return 4


def main():
    invocation = capture(Path(__file__))
    assert digest(RAW) == '1028c8ee59e21ddfa24853fac3c1e6f5505dde32768203d7f8ffa5bd1e53d403'
    raw = json.loads(RAW.read_text())
    actual = check(raw)
    # API contract guard: no new capture call omits its mandatory library argument.
    calls = []
    for name in ('pg8240_prometheus_maven_coordinates.py', 'pg8241_prometheus_coordinates_post.py', 'pg8170_prometheus_sdk_prepare.py', 'pg8234_histogram_backend_contract.py', 'scoped_prometheus_host.py'):
        path = ROOT / 'tools/quality' / name
        tree = ast.parse(path.read_text())
        found = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'capture']
        assert found and all(len(n.args) == 1 for n in found)
        calls.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path)))
    failures = 0
    for change in ('entries', 'publicArtifactDownloads'):
        bad = json.loads(json.dumps(raw))
        bad[change] = [] if change == 'entries' else 4
        try:
            check(bad)
        except AssertionError:
            failures += 1
    assert failures == 2
    verify(invocation)
    OUT.mkdir(exist_ok=False)
    value = dict(status='ORIGINAL_COORDINATES_VERIFIED_METADATA_CORRECTED', rawSha256=digest(RAW), actualPublicArtifactDownloads=actual, originalRecordedDownloads=2, sourceCalls=calls, negativeGuards=failures, coordinateCount=8, productionPT=0, targetActions=0, invocation=invocation, bugs=['BUG-1693', 'BUG-1694'])
    with (OUT / 'manifest.json').open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')
    print(json.dumps(dict(status=value['status'], manifestSha256=digest(OUT / 'manifest.json'))))


if __name__ == '__main__':
    main()
