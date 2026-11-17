"""Verify raw single-execution coverage and the unchanged synthetic golden vector."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import gzip
import json
import re
import subprocess
import xml.etree.ElementTree as ET

from classfile_code_metadata import decode
from pgpt_public_unit_xml import copy_public_evidence

ROOT = Path.cwd()
WORK = ROOT.parent/'pgpt-runs/PG379'
TC = ROOT.parent/'toolchain'
JAVA = TC/'jdk-25.0.4/bin/java'
EVID = ROOT/'evidence/01_PT/018_NK-OPS-001/evidence'
PREPARE = WORK/'pg38222-backup-manifest17-prepare-v1/component'
SLOT = WORK/'pg38226-backup-manifest17-unit-v1'
UNIT = EVID/'PG38226-backup-manifest17-unit-v1'
OUT = EVID/'PG38228-backup-manifest17-independent-v1'
TARGET = 'dev/codex/schubert/nk/batch/file/BackupManifestCodec'

def read(path):
    return json.loads(path.read_bytes())

def sha(path):
    return sha256(path.read_bytes()).hexdigest()

def ref(path):
    return dict(path=str(path.relative_to(ROOT)), sha256=sha(path))

def crc(raw):
    assert int.from_bytes(raw[6:8], 'big') == 69
    value = 0
    for byte in raw:
        value ^= byte
        for _ in range(8):
            value = (value >> 1) ^ 0xd800000000000000 if value & 1 else value >> 1
    return f'{value:016x}'

begin = read(UNIT/'begin.json')
exit_data = read(UNIT/'exit.json')
assert exit_data['actualExit'] == 0 and not exit_data['timedOut']
assert begin['source'] == subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
assert not any((SLOT/'tmp').iterdir())
prepare = read(EVID/'PG38222-backup-manifest17-prepare-v1/manifest.json')
old_unit = read(EVID/'PG28166-backup-manifest16-independent-v1/unit-manifest.json')
expected = {(row['classname'], row['name']) for row in begin['expectedCases']}
old_cases = {(row['classname'], row['name'] if row['name'].endswith('()') else row['name']+'()')
             for row in old_unit['cases']}
assert len(expected) == 17 and len(old_cases) == 16 and old_cases < expected
xml_cases = []
for path in (SLOT/'xml').glob('TEST-*.xml'):
    root = ET.parse(path).getroot()
    assert all(int(root.get(key, 0)) == 0 for key in ('errors', 'failures', 'skipped'))
    for case in root.findall('.//testcase'):
        assert all(case.find(name) is None for name in ('failure', 'error', 'skipped'))
        xml_cases.append((case.attrib['classname'], case.attrib['name']))
assert len(xml_cases) == len(set(xml_cases)) == 17 and set(xml_cases) == expected
golden = ROOT/'src/schubert-nk-batch/src/test/resources/backup/manifest-golden.json'
output = SLOT/'target/backup-manifest-traces/PT-BAT-186-manifest.json'
assert output.resolve() == output
assert output.read_bytes() == golden.read_bytes()
execfile = SLOT/'jacoco.exec'
exec_cmd = [str(JAVA), '-jar', str(TC/'org.jacoco.cli-0.8.15-nodeps.jar'), 'execinfo', str(execfile)]
exec_result = subprocess.run(exec_cmd, capture_output=True, timeout=60, check=True)
text = exec_result.stdout.decode()
assert text.count('Session "') == 1 and f'Session "{begin["run"]}"' in text
probe_by_class = {name: (identity, int(hits), int(total)) for identity, hits, total, name in
    re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$', text, re.M)}
identities = {}
for name, digest in prepare['physicalClassHashes'].items():
    path = PREPARE/name
    assert sha(path) == digest
    identities[name.removesuffix('.class')] = crc(path.read_bytes())
assert len(identities) == 7 and all(probe_by_class[name][0] == value for name, value in identities.items())
assert probe_by_class[TARGET][1] > 0
init_log = (SLOT/'class-init.log').read_text()
init_classes = set(re.findall(r"Initializing '([^']+)'", init_log))
assert TARGET in init_classes
forbidden = ('TemporaryInfrastructureException', 'FingerprintKeyRing', 'ResponseSnapshotCodec', 'WebStartupException',
             'LinuxDirectoryCalls', 'LinuxInodeSecurity', 'RootStartupContext', 'BackupManifestPublisher')
assert not any(chunk in name for name in init_classes for chunk in forbidden)
tool = read(EVID/'PG31432-generated-code-supplemental-tool-v1/compile.json')
assert read(EVID/'PG31434-generated-code-tool-selftest-v1/manifest.json')['toolTests'] == 12
for dep in tool['dependencies']:
    assert sha(Path(dep['path'])) == dep['sha256']
raw_cmd = [str(JAVA), '-cp', ':'.join([str(WORK/'pg31432-generated-code-supplemental-tool-v1/toolclasses'),
                                       *(pin['path'] for pin in tool['dependencies'])]),
           'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement', str(execfile),
           *(str(PREPARE/(name+'.class')) for name in identities)]
raw_result = subprocess.run(raw_cmd, capture_output=True, timeout=60, check=True)
measured = {}
method_rows = []
for line in raw_result.stdout.decode().splitlines():
    fields = line.split('\t')
    if fields[0] == 'CLASS':
        row = {'name': fields[1], 'id': fields[2], 'counters': {}}
        measured[fields[1]] = row
        offset = 6
    else:
        assert fields[0] == 'METHOD'
        row = {'className': fields[1], 'name': fields[2], 'descriptor': fields[3], 'counters': {}}
        method_rows.append(row)
        offset = 5
    for counter in fields[offset:]:
        kind, missed, covered = counter.split(':')
        row['counters'][kind] = {'missed': int(missed), 'covered': int(covered)}
assert measured.keys() == identities.keys() and all(measured[key]['id'] == value for key, value in identities.items())
target_methods = [entry for entry in method_rows if entry['className'] == TARGET]
metadata = decode((PREPARE/(TARGET+'.class')).read_bytes(), TARGET+'.class')
assert {(entry['name'], entry['descriptor']) for entry in target_methods} == {
    (entry['name'], entry['descriptor']) for entry in metadata['methods'] if entry['hasCode']}
assert len(target_methods) == 7 and any(m['name'] == '<init>' for m in target_methods)
counters = measured[TARGET]['counters']
assert all(counters[mode]['missed'] == 0 and counters[mode]['covered'] > 0
           for mode in ('LINE', 'METHOD', 'CLASS', 'BRANCH', 'INSTRUCTION'))
OUT.mkdir()
(OUT/'xml').mkdir()
for source in (SLOT/'xml').glob('TEST-*.xml'):
    copy_public_evidence(source, OUT/'xml'/source.name)
assert Counter((case.get('classname'), case.get('name')) for path in (OUT/'xml').glob('TEST-*.xml')
    for case in ET.parse(path).getroot().findall('.//testcase')) == Counter(xml_cases)
for name, data in {'execinfo.stdout': exec_result.stdout, 'unfiltered.stdout': raw_result.stdout,
                   'jacoco.exec': execfile.read_bytes(), 'class-init.log.gz': gzip.compress(init_log.encode(), mtime=0),
                   'actual-synthetic-manifest.json': output.read_bytes()}.items():
    (OUT/name).write_bytes(data)
proof = dict(actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),source=begin['source'],
    sourceCore=begin['source'],run=begin['run'],tests=17,failed=0,errors=0,skipped=0,notRun=0,
    jdk='25.0.4',jacoco='0.8.15',actualUnit=ref(UNIT/'begin.json'),exitReceipt=ref(UNIT/'exit.json'),
    currentClassCRCs=identities,initializedHeld=0,allCodesReport=len(measured),targetCode=target_methods,
    targetRawCounters=counters,targetFour100=True,manualExclusions=0,oldExecCombined=False,
    original16CasesRetained=True,independentGolden=ref(golden),goldenActualSHA256=sha(output),
    ownSyntheticTraceOnly=True,rawCommands=[exec_cmd,raw_cmd],formalAcceptanceDelta=0,
    files={path.relative_to(OUT).as_posix():sha(path) for path in OUT.rglob('*') if path.is_file()})
with (OUT/'manifest.json').open('x') as stream:
    stream.write(json.dumps(proof, ensure_ascii=False, indent=2)+'\n')
print(proof['tests'], counters, sha(OUT/'manifest.json'))
