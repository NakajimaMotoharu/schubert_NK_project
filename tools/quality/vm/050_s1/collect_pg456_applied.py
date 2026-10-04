"""Safe deterministic proof: fixed flags/class hashes only; never copy DB, dumps or private state."""
import ast
import datetime
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
RUN = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
OUT = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG456-applied-v1'
OUT.mkdir(mode=0o750)
LOGS = OUT / 'logs'
LOGS.mkdir(mode=0o750)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
entries = []
jobs = [('pg456-applied-verify-v1.log', 1), ('pg456-applied-verify-v2.log', 1),
        ('pg456-applied-verify-v3.log', 1), ('pg456-applied-verify-v4.log', 0),
        ('pg456-applied-complete-v1.log', 0)]
for name, code in jobs:
    path = RUN / name
    lines = [line for line in path.read_text().splitlines()
             if re.fullmatch(r'PG456(?:_APPLIED_(?:REFUSED|FRAME|VERIFIED|COMPLETED)| STAGE) [A-Za-z0-9_.$:= /]+', line)]
    assert lines
    if code == 0:
        assert any(line.startswith('PG456_APPLIED_VERIFIED ') for line in lines)
        assert not any('REFUSED' in line for line in lines)
    if 'complete' in name:
        assert any(line.startswith('PG456_APPLIED_COMPLETED ') for line in lines)
    (LOGS / name).write_text('\n'.join(lines) + '\n')
    entries.append({'testIds': ['MIG456-APPLIED-PRESERVATION', 'MIG456-APPLIED-COMPLETE'],
                    'rawLogSha256': sha(path), 'safePath': 'logs/' + name,
                    'safeSha256': sha(LOGS / name), 'actualExitCode': code,
                    'accepted': code == 0, 'observedLogCompletedAt': datetime.datetime.fromtimestamp(path.stat().st_mtime, datetime.timezone.utc).isoformat(),
                    'exactStartTimestampRecorded': False})
tests = []
for name, count in [('Pg455ReleaseSchemaToolTest', 11), ('Pg421ReleaseSchemaToolTest', 4),
                    ('Pg456SignedMigrationTest', 68), ('Pg456AppliedCompletionTest', 27)]:
    path = RUN / ('pg456-' + name + '-v7.log')
    value = path.read_text().strip()
    assert ('assertions=' + str(count) in value or 'independentAssertions=' + str(count) in value)
    assert 'productionPtCount=0' in value and '\x1b' not in value
    (LOGS / path.name).write_text(value + '\n')
    tests.append({'tool': name, 'independentAssertions': count, 'actualExitCode': 0,
                  'path': 'logs/' + path.name, 'sha256': sha(LOGS / path.name)})
assert (RUN / 'pg456-compile-v7.log').stat().st_size == 0
names = next(ast.literal_eval(n.value) for n in ast.parse((ROOT / 'tools/quality/vm/050_s1/pg456_stage_applied_tools.py').read_text()).body
             if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'NAMES' for t in n.targets))
assert len(names) == 16
classes = {name + '.class': sha(RUN / 'pg456-tools-v7' / (name + '.class')) for name in names}
sources = {str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT / 'tools/quality/vm/050_s1').glob('Pg456*.java'))}
for filename in ['pg456_stage_applied_tools.py', 'pg456_applied_tools_v7.sh', 'pg456_stage_candidate.py', 'pg456_stage_mode_test.py', 'collect_pg456_applied.py']:
    p = ROOT / 'tools/quality/vm/050_s1' / filename
    sources[str(p.relative_to(ROOT))] = sha(p)
manifest = {'run': 'PG456-applied-v1', 'program': 'NK-OPS-001', 'status': 'provisional_tool_and_isolated_deployment_only',
            'branch': 'dev-foundation', 'productionSource': '559bf7eacb401d6d07037dbdd295b32f174976a0',
            'toolSourceFiles': sources, 'rootClosedOperatorClassSha256': classes,
            'sourceBinding': 'Production six-module classes/jars unchanged; operator source has separately pinned hashes',
            'signedManifestSha256': '21affa1850d60f3a7d54f5dbcc37e12c6460563865771fa49a52a433fe91b424',
            'privateRestorePointSha256': 'd77412eeeb88159bd56b2d2f099195480cc99baebf4843b2e4d069c790bd271e',
            'commands': ['bash tools/quality/vm/050_s1/pg456_applied_tools_v7.sh',
                         'Pg456AppliedCompletion <fixed-source40> <fixed-manifest64> verify',
                         'Pg456AppliedCompletion <fixed-source40> <fixed-manifest64> complete',
                         'python3 tools/quality/vm/050_s1/pg456_stage_mode_test.py'],
            'environment': {'hostJdk': '25.0.4', 'guestJdk': '25.0.4', 'guestPostgresql': '18.6',
                            'guestOs': 'Ubuntu 26.04', 'guestKernel': '7.0.0-34-generic', 'maven': '3.9.12', 'flyway': '13.4.0'},
            'toolTests': tests, 'nativeToolAttempts': entries, 'compileActualExit': 0, 'compileWarnings': 0,
            'expectations': {'historyBefore': 26, 'historyAfter': 28, 'existingBusinessTablesPreserved': 23,
                             'batchRowsPreserved': 251, 'batchColumnsPreserved': 14, 'backupEntriesPreserved': 20,
                             'postconditions': 11, 'partialPrivilegeRejected': True, 'productionDdlRepeated': 0,
                             'newPermitsIssued': 0, 'originalStillPending': True},
            'relatedBugs': list(range(663, 671)), 'relatedYkts': list(range(468, 476)),
            'productionPtCredit': 0, 'coverage100Accepted': False, 'wholeMorningAccepted': False,
            'formalAcceptanceUpdated': False, 'secretsCopied': False,
            'timestampLimitation': 'Native operator start timestamps were not emitted; actual invocation/completion and separately captured running time retained, not reconstructed'}
(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print('PG456_APPLIED_COLLECTED safeManifestSha256=' + sha(OUT / 'manifest.json') + ' productionPt0=true formalUpdated=false')
