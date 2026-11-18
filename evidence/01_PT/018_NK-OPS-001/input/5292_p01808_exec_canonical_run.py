"""Collect the six new synthetic binary decoder tests with exact local source and writer pins."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

ROOT = Path('tools/quality')
TOOL = ROOT / 'jacoco_readonly_exec_subset.py'
TEST = ROOT / 'jacoco_readonly_exec_subset_encoding_test.py'
D = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
WRITER_TYPE = 'org.jacoco.cli.internal.core.internal.data.CompactDataOutput'
JAVAP = '/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/javap'
IDS = {
    'PT-P01808-BIN-018': 'test_rejects_nonminimal_zero',
    'PT-P01808-BIN-019': 'test_rejects_nonminimal_three',
    'PT-P01808-BIN-020': 'test_rejects_target_padding_above_last_probe',
    'PT-P01808-BIN-021': 'test_rejects_bad_padding_in_a_nonselected_record',
    'PT-P01808-BIN-022': 'test_pinned_counts_at_zero_and_near_single_byte_limit',
    'PT-P01808-BIN-023': 'test_full_probe_byte_and_partial_probe_byte',
}


def ref(path):
    return dict(path=str(path), sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())


def git(*args):
    return subprocess.check_output(['git', *args], timeout=20)


def main(phase):
    start = json.loads(next(D.glob('628_P01808*')).read_bytes())['values']
    before_tool, writer = start['oracleReferences']
    source = git('rev-parse', 'HEAD').decode().strip()
    assert git('show', f'{source}:{TEST}') == TEST.read_bytes()
    assert git('show', f'{source}:{TOOL}') == TOOL.read_bytes()
    assert (ref(TOOL) == before_tool) == (phase == 'red')
    assert writer == ref(writer['path'])
    run = start['run'] if phase == 'red' else 'PG40150-p01808-exec-canonical-green-v1'
    out = E / run
    out.mkdir()
    if phase == 'red':
        writer_command = [JAVAP, '-classpath', writer['path'], '-c', WRITER_TYPE]
        disassembly = out / 'pinned-compact-writer-javap.txt'
        disassembly.write_bytes(subprocess.check_output(writer_command, timeout=20))
        writer_proof = dict(jar=writer, command=writer_command, output=ref(disassembly))
    else:
        first = json.loads((E / start['run'] / 'manifest.json').read_bytes())
        writer_proof = first['writerProof']
        assert writer_proof['jar'] == writer
        assert ref(writer_proof['output']['path']) == writer_proof['output']
    command = [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', str(ROOT), '-p', TEST.name, '-v']
    unit = subprocess.run(command, capture_output=True, timeout=20, check=False)
    log = out / 'unit-output.txt'
    log.write_bytes(unit.stdout + unit.stderr)
    rows = re.findall(r'^(test_\w+) \(.+\) \.\.\. (.*)$', log.read_text(), re.M)
    by_name = dict(rows)
    assert len(rows) == len(by_name) == 6 and set(by_name) == set(IDS.values())
    expected = {name: ('FAIL' if phase == 'red' and name.startswith('test_rejects_') else 'ok')
                for name in IDS.values()}
    assert by_name == expected
    assert unit.returncode == int(phase == 'red')
    result = dict(actualExit=unit.returncode, source=source, currentCore=start['productionCoreMain'], run=run,
                  phase=phase, command=command, writerProof=writer_proof, tools=[ref(TOOL), ref(TEST)],
                  unitLog=ref(log), tests=IDS, outcomes=by_name, productTests=0, realNativeActions=0,
                  formalIntake=0, terminalAtUTC=datetime.now(timezone.utc).isoformat())
    p = out / 'manifest.json'
    p.write_text(json.dumps(result, indent=2) + '\n')
    print(ref(p), sum(result == 'ok' for result in by_name.values()))


if __name__ == '__main__':
    main(sys.argv[1])
