"""Frozen-source candidate inventory, not semantic acceptance or automatic blanket defect count."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SOURCE = 'e8ecff1bec1d7ddd51cdfbf803acda07c2f6cdb9'
OUT = ROOT / 'evidence/01_PT/003_NK-PRO-003/evidence/provisional/PG5134-scope-candidate-inventory-v1'


def objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values(): yield from objects(child)
    elif isinstance(value, list):
        for child in value: yield from objects(child)


def inventory(raw, load, owners):
    files = {}
    for line in raw.splitlines():
        source, path, nr, text = line.split(':', 3)
        if source != SOURCE or not path.startswith('src/') or '/src/main/java/' not in path or not path.endswith('.java'):
            raise ValueError('fixed canonical Main source rows only')
        if '..' in Path(path).parts or not nr.isdigit() or int(nr) <= 0 or 'ResourceScope.use(' not in text:
            raise ValueError('actual positive literal call candidates required')
        entry = files.setdefault(path, {'path': path, 'costOwner': owners.get(path), 'sites': []})
        if any(v['line'] == int(nr) for v in entry['sites']): raise ValueError('unique path/line')
        entry['sites'].append({'line': int(nr), 'callTextSha256': hashlib.sha256(text.encode()).hexdigest(),
                               'classification': 'UNKNOWN_REQUIRES_OUTER_OWNER_AND_BYTECODE_REVIEW',
                               'fixed': False, 'nonApplicableReason': None, 'retestEvidence': None})
    for path, entry in files.items():
        content = load(path)
        lines = content.decode().splitlines()
        for site in entry['sites']:
            text = lines[site['line'] - 1]
            if hashlib.sha256(text.encode()).hexdigest() != site['callTextSha256']:
                raise ValueError('source exact call line differs')
        entry['sourceSha256'] = hashlib.sha256(content).hexdigest()
    return sorted(files.values(), key=lambda row: row['path'])


def source_rows():
    return subprocess.check_output(['git', 'grep', '-n', '-F', 'ResourceScope.use(', SOURCE, '--',
                                    ':(glob)src/*/src/main/java/**/*.java'], cwd=ROOT, text=True)


def main():
    raw = source_rows()
    mapping = json.loads((ROOT / 'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    owners = {}
    for node in objects(mapping):
        if isinstance(node.get('path'), str) and isinstance(node.get('costOwner'), str):
            if node['path'] in owners and owners[node['path']] != node['costOwner']:
                raise ValueError('one actual shared cost owner per artifact')
            owners[node['path']] = node['costOwner']
    rows = inventory(raw, lambda path: subprocess.check_output(['git', 'show', SOURCE + ':' + path], cwd=ROOT), owners)
    count = sum(len(row['sites']) for row in rows)
    if len(rows) != 68 or count != 237: raise ValueError('exact frozen source68/237 inventory')
    value = {'source': SOURCE, 'fileCount': len(rows), 'literalCallSiteCandidates': count, 'files': rows,
             'unknownCostOwnerFiles': [r['path'] for r in rows if r['costOwner'] is None],
             'rootBytecodeWitnesses': ['RootServiceExecutableAdmission.admit open47/dynamic59,68/use73',
                                      'RootStartupPending$1.readLaunch open7/dynamic17,31/use36'],
             'bugs': ['BUG1414'], 'ykt': ['YKT1178'], 'ssc': ['SSC308'],
             'candidateInventoryOnly': True, 'allCandidatesAreDefects': False,
             'wholeHorizontalComplete': False, 'acceptedLeafDelta': 0, 'formalAccepted': False,
             'vmActions': 0, 'productionEdits': 0}
    os.umask(0o077); OUT.mkdir(parents=True)
    with (OUT / 'manifest.json').open('x') as target:
        json.dump(value, target, ensure_ascii=False, indent=2); target.write('\n'); target.flush(); os.fsync(target.fileno())
    print(json.dumps({'fileCount': len(rows), 'candidates': count, 'unknownCostOwnerFiles': value['unknownCostOwnerFiles'],
                      'sha256': hashlib.sha256((OUT / 'manifest.json').read_bytes()).hexdigest(), 'horizontalComplete': False}))


if __name__ == '__main__':
    main()
