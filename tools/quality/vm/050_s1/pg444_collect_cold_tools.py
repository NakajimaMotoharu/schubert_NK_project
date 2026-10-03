"""Fixed sanitized operator-test record; neither Production PT nor native acceptance."""
import datetime
import hashlib
import json
import pathlib
import re
import subprocess

root = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
work = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
target = root / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG444-cold-tools-v6'
assert not target.exists()
specs = [
    ('PG444-COLD-001', 'pg444-Pg428ColdBootPreparationTest-v6.log', 412),
    ('PG444-TRANSFER-001', 'pg444-Pg444TransferPreservationTest-v6.log', 21),
    ('PG444-OWNERSHIP-001', 'pg444-Pg444ColdOwnershipTest-v6.log', 25),
    ('ROOTPAIR008-TOOL', 'pg444-pair-v4.log', 94),
]
tests = []
for identifier, filename, assertions in specs:
    data = (work / filename).read_bytes()
    text = data.decode()
    assert re.fullmatch(r'[A-Z0-9_]+ .*\n', text)
    assert 'success=true' in text and f'independentAssertions={assertions}' in text
    assert 'productionTestCount=0' in text
    tests.append({'testId': identifier, 'exitCode': 0, 'independentAssertions': assertions,
                  'actual': text.strip(), 'logSha256': hashlib.sha256(data).hexdigest()})
assert (work / 'pg444-compile-v6.log').read_bytes() == b''
sources = ['Pg428ColdBootPreparation.java', 'Pg428ColdBootPreparationTest.java',
           'Pg431KnownPairRecovery.java', 'Pg431KnownPairRecoveryTest.java',
           'Pg444TransferPreservationTest.java', 'Pg444ColdOwnershipTest.java']
record = {
    'id': 'PG444-cold-tools-v6', 'formal': False, 'nativeAccepted': False,
    'sourceCommit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
    'sourceDirty': True, 'branch': 'dev-foundation',
    'timeUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'environment': 'Linux/JDK25.0.4; javac -Xlint:all -Werror; native FD allowed',
    'command': 'WorkPG379/pg444_tools_v6.sh (cold3) and pg444_tools_v4.sh (pair1)',
    'runtimeProductionSource': '91b010509e715e2b097c955d04f21c23f3529966',
    'runtimeProductionLabel': 'cold3: PG430 archived actual classes; pair1: PG443 fixed2b418 classes; no common formal source claim',
    'tests': tests, 'productionTestCount': 0, 'compileWarnings': 0, 'exitCode': 0,
    'sourceFiles': [{'path': 'tools/quality/vm/050_s1/' + n,
                     'sha256': hashlib.sha256((root / 'tools/quality/vm/050_s1' / n).read_bytes()).hexdigest()}
                    for n in sources],
    'classes': [{'name': p.name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                for p in sorted((work / 'pg444-tools-v6').glob('*.class'))],
    'bugs': ['BUG-544', 'BUG-595'], 'ykt': ['YKT-388', 'YKT-419'], 'ssc': ['SSC-174'],
    'independentOracle': 'literal full18 values/role policies, empty and abc known SHA vectors, '
                         '4800 public spaces JCE independent hash, held inode replacement, '
                         'exact exception identity/interrupt, actual historical watch hash only for correlation',
    'beforeFailure': {'exitCode': 1, 'path': 'WorkPG379/pg444-cold-before-repro.log',
                      'sha256': hashlib.sha256((work / 'pg444-cold-before-repro.log').read_bytes()).hexdigest()},
    'otherNonpassingRuns': [
        {'command': 'initial javac omitted provided annotations', 'result': 'compile failed, PT not run'},
        {'command': 'pair v3 runtime omitted API classes', 'result': 'NoClassDefFoundError, not accepted'},
        {'command': 'v5 compiled later PairEvidence tool against PG430 old ABI',
         'result': 'compile failed, PT not run; cold-only v6 explicitly excludes later Pair tool'},
        {'command': 'Transfer v2 invalid calendar negative omitted DateTimeException catch',
         'result': 'exit1, test corrected; production rejection was correct',
         'sha256': hashlib.sha256((work / 'pg444-transfer-v2.log').read_bytes()).hexdigest()},
    ],
    'coverage': 'operator assertions only; no Production/native coverage-100 claim',
    'limitations': ['native M/A/advisory/new INVALID-only preparation not yet run',
                    'old UNKNOWN/close remains unknown; no old intent reconstructed or retired',
                    'whole PG/PT/CHR/formal1964PT53scope unchanged'],
    'redaction': 'public test result and hash only; private watch/DB/epoch/backup bytes omitted',
}
target.mkdir(parents=True)
out = target / 'manifest.json'
out.write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({'success': True, 'productionTestCount': 0, 'operatorAssertions': 552,
                  'manifestSha256': hashlib.sha256(out.read_bytes()).hexdigest()}))
