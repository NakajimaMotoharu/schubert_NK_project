"""Find current-byte candidate coverage receipts in tracked public manifests; grants no acceptance."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HELD_NAMES = {'SnapshotKeyCloseWitness.java', 'pg9892_snapshot_key_close_witness.py',
              'RootFailedStartRecoveryTest.java', 'RootFailedStartPairRecoveryTest.java'}


def candidate(value, class_name, current_hash):
    if not re.fullmatch(r'[A-Za-z_$][\w$]*', class_name):
        raise ValueError('exact simple Java class name required')
    coverage = value.get('coverage')
    inputs = value.get('inputHashes')
    if not isinstance(coverage, dict) or not isinstance(inputs, dict):
        return None
    targets = [key for key in coverage if key.rsplit('/', 1)[-1] == class_name]
    sources = [key for key in inputs if key.endswith('/src/main/java/' + targets[0] + '.java')] if len(targets) == 1 else []
    if len(sources) != 1:
        return None
    counters = coverage[targets[0]]
    full = isinstance(counters, dict) and all(
        isinstance(counters.get(key), dict) and counters[key].get('missed') == 0
        and isinstance(counters[key].get('covered'), int) and counters[key]['covered'] >= 0
        for key in ['LINE', 'METHOD', 'CLASS', 'BRANCH'])
    full = full and all(counters[key]['covered'] > 0 for key in ['LINE', 'METHOD', 'CLASS'])
    return dict(source=value.get('source'), mainPath=sources[0], mainSha256=inputs[sources[0]],
                currentMainByteEqual=inputs[sources[0]] == current_hash,
                originalExit=value.get('actualExit'), tests=value.get('tests'),
                fourCounters=counters, allFourMissedZero=bool(full),
                acceptanceInferred=False, permissionInferred=False)


def lookup(root, class_name, main_path):
    if Path(main_path).name in HELD_NAMES or not main_path.startswith('src/') or '/../' in main_path:
        raise ValueError('unheld Production Main path required')
    target=root/main_path
    if target.is_symlink() or not target.is_file():
        raise ValueError('regular current Main required')
    current=hashlib.sha256(target.read_bytes()).hexdigest()
    names=subprocess.check_output(['git', 'ls-files', '-z', '--', 'evidence/01_PT'], cwd=root).decode().split('\0')
    rows=[];unread=[]
    for name in names:
        # Filename/type/scope exclusion precedes all file access; no private raw logs or source traversal.
        if not name.endswith('/manifest.json') or '.private.' in name or any(v in HELD_NAMES for v in Path(name).parts):
            continue
        p=root/name
        if p.is_symlink() or not p.is_file() or p.stat().st_size>2*1024*1024:
            unread.append(name)
            continue
        raw=p.read_bytes()
        if class_name.encode() not in raw:
            continue
        value=json.loads(raw)
        if not isinstance(value,dict):
            continue
        row=candidate(value,class_name,current)
        if row is not None:
            rows.append(dict(path=name,manifestSha256=hashlib.sha256(raw).hexdigest(),**row))
    return dict(className=class_name,currentMainSha256=current,candidates=rows,unreadBoundedManifests=unread,
                absenceIsNotUnimplemented=True,acceptanceInferred=False,permissionInferred=False,
                instruction='Read candidate original qualification and current-byte dependencies before selecting new PG/PT; do not replay existing success.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--class-name',required=True)
    parser.add_argument('--main-path',required=True)
    args=parser.parse_args()
    print(json.dumps(lookup(ROOT,args.class_name,args.main_path),ensure_ascii=False))
