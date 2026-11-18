"""One new suite on the unchanged independent exec decoder, with no native activation."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys

E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
D = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
TOOL = Path('tools/quality/jacoco_readonly_exec_subset.py')
TEST = TOOL.with_name('jacoco_readonly_exec_subset_presence_test.py')
TEST_IDS = {
    'PT-P01808-BIN-010': 'test_absent_target_is_not_a_zero_probe_report',
    'PT-P01808-BIN-011': 'test_target_name_with_conflicting_crc_stays_unqualified',
    'PT-P01808-BIN-012': 'test_two_names_for_one_crc_stay_unqualified',
    'PT-P01808-BIN-013': 'test_missing_session_does_not_qualify_a_present_class',
    'PT-P01808-BIN-014': 'test_compact_count_outside_java_int_does_not_read_probe_data',
    'PT-P01808-BIN-015': 'test_unsigned_crc_and_probe_bits_keep_exact_identity',
    'PT-P01808-BIN-016': 'test_mutable_input_is_outside_readonly_contract',
    'PT-P01808-BIN-017': 'test_unicode_names_are_outside_explicit_ascii_subset',
}


def now():
    return datetime.now(timezone.utc).isoformat()


def pin(path):
    return dict(path=str(path), sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())


def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def main():
    start = json.loads(next(D.glob('598_P01808*.json')).read_text())
    values = start['values']
    pins = values['oracleReferences']
    assert all(pin(item['path']) == item for item in pins)
    assert pin(TOOL) == pins[-1]
    first = json.loads(Path(pins[0]['path']).read_text())
    assert first['actualExit'] == 0 and first['namedTests'] == 9
    assert first['inputs'][0] == pin(TOOL)
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True, timeout=15).strip()
    ref = subprocess.check_output(['git', 'show', f'{source}:{TEST}'], timeout=15)
    assert ref == TEST.read_bytes()
    assert subprocess.check_output(['git', 'show', f'{source}:{TOOL}'], timeout=15) == TOOL.read_bytes()
    out = E / values['run']
    out.mkdir()
    command = [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', str(TOOL.parent), '-p', TEST.name, '-v']
    started = now()
    process = subprocess.run(command, capture_output=True, timeout=25, check=False,
                             env={'PATH': os.defpath, 'LANG': 'C.UTF-8'})
    log = out / 'unittest-output.txt'
    log.write_bytes(process.stdout + process.stderr)
    seen = re.findall(r'^(test_\w+) \(.+\) \.\.\. (.*)$', log.read_text(), re.M)
    result_by_method = dict(seen)
    manifest = dict(actualExit=process.returncode, source=source,
        productionCoreMain=values['productionCoreMain'], run=values['run'], command=command,
        python=sys.version.split()[0], inputs=[pin(TOOL), pin(TEST)], log=pin(log), harness=pin(__file__),
        startedAtUTC=started, terminalAtUTC=now(), expectedCases=8, namedCases=len(seen),
        testIds=TEST_IDS, results=result_by_method, earlierNine=pin(pins[0]['path']),
        earlierSuiteReexecutions=0, productTests=0, realNativeOrHostOperations=0, measuredProductCounters=0,
        whole451Accepted=False, newAcceptance=0)
    write(out / 'manifest.json', manifest)
    assert process.returncode == 0
    assert len(seen) == len(result_by_method) == 8 and set(result_by_method) == set(TEST_IDS.values())
    assert set(result_by_method.values()) == {'ok'} and log.read_text().strip().endswith('OK')
    print(pin(out / 'manifest.json'), len(seen))


if __name__ == '__main__':
    main()
