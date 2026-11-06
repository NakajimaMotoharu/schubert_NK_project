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
    schema = 'COVERAGE_INPUT_HASHES'
    normal_class_hash = None
    crc64 = None
    branch = value.get('branch')
    natural_zero = value.get('branchStatus') == 'NATURAL_ZERO_BRANCH' and value.get('branchRatio') is None
    if isinstance(coverage, dict) and isinstance(inputs, dict):
        targets = [key for key in coverage if key.rsplit('/', 1)[-1] == class_name]
        sources = [key for key in inputs if key.endswith('/src/main/java/' + targets[0] + '.java')] if len(targets) == 1 else []
        if len(sources) != 1:
            return None
        source_path = sources[0]
        source_hash = inputs[source_path]
        counters = coverage[targets[0]]
    elif 'sourceUnits' in value or 'sourcePins' in value:
        # Explicit per-class receipts only. An aggregate or ambiguous source pin
        # cannot be split into a claim about a guessed Main or source family.
        units, pins = value.get('sourceUnits'), value.get('sourcePins')
        if not isinstance(units, dict) or not isinstance(pins, dict):
            return None
        targets = [key for key in units if isinstance(key, str)
                   and key.rsplit('/', 1)[-1] == class_name]
        if len(targets) != 1 or not re.fullmatch(r'[A-Za-z_$][\w$]*(?:/[A-Za-z_$][\w$]*)+', targets[0]):
            return None
        target = targets[0]
        sources = [key for key in pins if isinstance(key, str)
                   and key.endswith('/src/main/java/' + target + '.java')]
        if len(sources) != 1:
            return None
        source_path = sources[0]
        if (not re.fullmatch(r'(?:src/[A-Za-z0-9_.-]+|program/characterization)/src/main/java/'
                             + re.escape(target) + r'\.java', source_path)
                or any(part in ('.', '..') for part in source_path.split('/'))):
            return None
        source_hash = pins[source_path]
        unit = units[target]
        if not isinstance(unit, dict):
            return None
        normal_class_hash, crc64 = unit.get('normalClassSha256'), unit.get('crc64')
        counters = unit.get('counters')
        if (not isinstance(source_hash, str) or not re.fullmatch('[0-9a-f]{64}', source_hash)
                or not isinstance(normal_class_hash, str) or not re.fullmatch('[0-9a-f]{64}', normal_class_hash)
                or not isinstance(crc64, str) or not re.fullmatch('[0-9a-f]{16}', crc64)
                or not isinstance(counters, dict)):
            return None
        classes = counters.get('CLASS')
        if (not isinstance(classes, dict)
                or any(type(classes.get(k)) is not int or classes[k] < 0 for k in ('covered', 'missed'))
                or classes['covered'] + classes['missed'] != 1):
            return None
        schema = 'SOURCE_UNITS_SOURCE_PINS'
    else:
        # Only the explicit single-target legacy receipt is supported. Never infer a
        # Main from a Test filename or apply aggregate counters to multiple targets.
        begin = value.get('begin')
        counters = value.get('counters')
        if not isinstance(begin, dict) or not isinstance(counters, dict):
            return None
        physical = begin.get('targetPhysicalClasses')
        source_hash = begin.get('targetMainSourceSha256')
        test_path = begin.get('testPath')
        if (not isinstance(physical, list) or len(physical) != 1
                or not isinstance(physical[0], str)
                or physical[0].rsplit('/', 1)[-1] != class_name
                or not re.fullmatch(r'[A-Za-z_$][\w$]*(?:/[A-Za-z_$][\w$]*)+', physical[0])
                or not isinstance(source_hash, str) or not re.fullmatch(r'[0-9a-f]{64}', source_hash)
                or not isinstance(test_path, str)
                or not re.fullmatch(r'src/[^/]+/src/test/java/[A-Za-z0-9_$/]+\.java', test_path)
                or value.get('sourcePhysicalScopeComplete') is not True):
            return None
        source_path = test_path.split('/src/test/java/', 1)[0] + '/src/main/java/' + physical[0] + '.java'
        schema = 'SINGLE_TARGET_COUNTERS_BEGIN'
        natural_zero = (isinstance(branch, dict) and branch.get('meaning') == 'NATURAL_ZERO_NO_SOURCE_CONDITIONAL_INSTRUCTIONS_NA'
                        and type(branch.get('covered')) is int and branch['covered'] == 0
                        and type(branch.get('missed')) is int and branch['missed'] == 0)
    if not isinstance(counters, dict):
        return None

    def zero_missed(key):
        item = counters.get(key)
        return (isinstance(item, dict) and type(item.get('missed')) is int and item['missed'] == 0
                and type(item.get('covered')) is int and item['covered'] >= 0)

    three = all(zero_missed(key) and counters[key]['covered'] > 0 for key in ['LINE', 'METHOD', 'CLASS'])
    full = three and zero_missed('BRANCH')
    # An omitted BRANCH counter remains omitted. Natural zero is not measured branch100.
    assessment = ('MEASURED_COUNTER' if 'BRANCH' in counters else
                  'EXPLICIT_NATURAL_ZERO_NOT_BRANCH100' if natural_zero else 'UNMEASURED')
    return dict(source=value.get('source'), mainPath=source_path, mainSha256=source_hash,
                currentMainByteEqual=source_hash == current_hash,
                originalExit=value.get('actualExit'), tests=value.get('tests'),
                fourCounters=counters, allFourMissedZero=bool(full),
                lineMethodClassMissedZero=three, evidenceSchema=schema, branchAssessment=assessment,
                declaredNormalClassSha256=normal_class_hash, declaredCrc64=crc64,
                counterScope='NAMED_CLASS_OR_METHOD_SUBSET_COUNTERS', wholeSourceQualificationInferred=False,
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
