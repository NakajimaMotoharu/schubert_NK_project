"""Check immutable observations and missing API Outbox branches without replaying PT."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
B = ROOT / 'evidence/01_PT/018_NK-OPS-001'
E = B / 'evidence'
OUT = E / 'PG39582-p00405-api-outbox-raw-before-v1'
OLD = ROOT.parent / 'pgpt-runs/PG379/pg25450-api-outbox-jdbc-original-whole18-v1'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())}


def main():
    pre = next(E.glob('PG25448*preflight*/manifest.json'))
    producer = next(E.glob('PG25450*/manifest.json'))
    post = next(E.glob('PG25454*/manifest.json'))
    raw_tool = next(E.glob('PG39282*/raw-command.json'))
    p, original, checked = map(load, (pre, producer, post))
    assert checked['producerManifest'] == ref(producer) and checked['preflight'] == ref(pre)
    assert original['source'] == checked['source'] and original['actualExit'] == checked['actualExit'] == 0
    assert checked['tests'] == 18 and not any(checked[k] for k in ('failures', 'errors', 'aborted', 'skipped'))
    for name, expected in checked['files'].items():
        assert sha((post.parent / name).read_bytes()) == expected
    file_names = [OLD / 'component' / Path(name).name for name in p['targetClassHashes']]
    for path, expected in zip(file_names, p['targetClassHashes'].values(), strict=True):
        assert sha(path.read_bytes()) == expected
    input_matches = {key: sha((ROOT / key).read_bytes()) == expected for key, expected in p['inputHashes'].items()}
    assert list(k for k, v in input_matches.items() if not v) == ['src/schubert-nk-api/pom.xml']
    exec_file = OLD / 'jacoco.exec'
    command = load(raw_tool)[:5] + list(map(str, (exec_file, *file_names)))
    raw = subprocess.check_output(command, cwd=ROOT)
    lines = raw.decode().splitlines()
    missing = [line.split('\t') for line in lines if line.startswith('DEFICIT\t')]
    repository = 'dev/codex/schubert/nk/api/monitoring/persistence/OutboxObservationRepository'
    assert [int(row[4]) for row in missing] == [49, 53, 65, 66]
    assert all(row[1] == repository and row[2] == 'read' and 'BRANCH:1:1' in row for row in missing)
    (OUT / 'unfiltered.tsv').write_bytes(raw)
    result = {'actualExit': 0, 'analysisOnly': True, 'productTestsExecuted': 0,
              'archivedSource': original['source'], 'currentReadSource': 'd805cfc27bf5aff310a27429b8db5bedf1dfec35',
              'applicableMainAndTestsIdentical': input_matches,
              'coverageNotTransferredToCurrent': True, 'proofs': [ref(path) for path in (pre, producer, post, raw_tool)],
              'historicalExec': {'path': str(exec_file), 'sha256': sha(exec_file.read_bytes())},
              'classes': p['targetClassHashes'], 'command': command,
              'raw': ref(OUT / 'unfiltered.tsv'), 'rawBranches': {'missed': 4, 'covered': 28},
              'deficitLines': [49, 53, 65, 66], 'newAcceptance': 0}
    (OUT / 'manifest.json').write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
