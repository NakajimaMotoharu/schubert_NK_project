"""Verify raw single-execution coverage for the Outbox report and retry conditions."""
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
PREPARE = WORK/'pg38288-outbox-report-retry-prepare-v2/component'
SLOT = WORK/'pg38292-outbox-report-retry-unit-v1'
UNIT = EVID/'PG38292-outbox-report-retry-unit-v1'
OUT = EVID/'PG38294-outbox-report-retry-independent-v1'
TARGETS = {f'dev/codex/schubert/nk/api/messaging/outbound/{suffix}'
           for suffix in ('OutboxDispatchReport','OutboxRetrySchedule')}

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
prepare = read(EVID/'PG38288-outbox-report-retry-prepare-v2/manifest.json')
context = read(next((ROOT/'documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117').glob('221_*')))
prepare['productCodeCore'] = context['baseCore']
assert subprocess.run(['git','diff','--quiet',prepare['productCodeCore'],begin['source'],'--',*[v['path'] for v in context['mains'].values()]],check=False).returncode==0

expected = {(row['classname'], row['name']) for row in begin['expectedCases']}
assert len(expected) == 10
assert Counter(name.rsplit('.',1)[-1] for name, _ in expected)=={
    'OutboxPolicyTest':4,'OutboxDispatchReportBoundaryTest':3,'OutboxValueContractTest':3}
xml_cases = []
for path in (SLOT/'xml').glob('TEST-*.xml'):
    root = ET.parse(path).getroot()
    assert all(int(root.get(key, 0)) == 0 for key in ('errors', 'failures', 'skipped'))
    for case in root.findall('.//testcase'):
        assert all(case.find(name) is None for name in ('failure', 'error', 'skipped'))
        xml_cases.append((case.attrib['classname'], case.attrib['name']))
assert len(xml_cases) == len(set(xml_cases)) == 10 and set(xml_cases) == expected
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
assert len(identities) == 3 and all(probe_by_class[name][0] == value for name, value in identities.items())
assert all(probe_by_class[name][1]>0 for name in TARGETS)
init_log = (SLOT/'class-init.log').read_text()
init_classes = set(re.findall(r"Initializing '([^']+)'", init_log))
assert TARGETS <= init_classes
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
target_methods=[]
counters={}
for target in sorted(TARGETS):
    methods=[entry for entry in method_rows if entry['className']==target]
    metadata=decode((PREPARE/(target+'.class')).read_bytes(),target+'.class')
    assert {(row['name'],row['descriptor']) for row in methods}=={
        (row['name'],row['descriptor']) for row in metadata['methods'] if row['hasCode']}
    target_methods.extend(methods)
    counters[target]=measured[target]['counters']
full=all(counters[n][metric]['missed']==0 for n in TARGETS for metric in ('LINE','METHOD','CLASS','BRANCH','INSTRUCTION'))
OUT.mkdir()
(OUT/'xml').mkdir()
for source in (SLOT/'xml').glob('TEST-*.xml'):
    copy_public_evidence(source, OUT/'xml'/source.name)
assert Counter((case.get('classname'), case.get('name')) for path in (OUT/'xml').glob('TEST-*.xml')
    for case in ET.parse(path).getroot().findall('.//testcase')) == Counter(xml_cases)
for name, data in {'execinfo.stdout': exec_result.stdout, 'unfiltered.stdout': raw_result.stdout,
                   'jacoco.exec': execfile.read_bytes(), 'class-init.log.gz': gzip.compress(init_log.encode(), mtime=0),
                   'proof-kind.txt': b'Memory-only synthetics\n'}.items():
    (OUT/name).write_bytes(data)
proof = dict(actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),source=begin['source'],
    sourceCore=prepare['productCodeCore'],run=begin['run'],tests=10,failed=0,errors=0,skipped=0,notRun=0,
    jdk='25.0.4',jacoco='0.8.15',actualUnit=ref(UNIT/'begin.json'),exitReceipt=ref(UNIT/'exit.json'),
    currentClassCRCs=identities,initializedHeld=0,allCodesReport=len(measured),targetCode=target_methods,
    targetRawCounters=counters,targetFour100=full,manualExclusions=0,oldExecCombined=False,
    original10CasesRetained=True,independentRetryOracle=True,
    ownSyntheticTraceOnly=True,rawCommands=[exec_cmd,raw_cmd],formalAcceptanceDelta=0,
    files={path.relative_to(OUT).as_posix():sha(path) for path in OUT.rglob('*') if path.is_file()})
with (OUT/'manifest.json').open('x') as stream:
    stream.write(json.dumps(proof, ensure_ascii=False, indent=2)+'\n')
print(proof['tests'], counters, sha(OUT/'manifest.json'))
