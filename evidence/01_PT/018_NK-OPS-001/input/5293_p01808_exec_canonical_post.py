"""Verify the six decoder outcomes, writer authority and a preserved offline-tool stream."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import runpy
import subprocess

E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
RED = E / 'PG40148-p01808-exec-canonical-red-v1'
GREEN = E / 'PG40150-p01808-exec-canonical-green-v1'
ARCHIVE = E / 'PG40128-p020-path-contract-green206-v2'
TOOL = Path('tools/quality/jacoco_readonly_exec_subset.py')
TARGET = 'dev/codex/schubert/characterization/ArtifactComparator'


def ref(path):
    return dict(path=str(path), sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())


def json_file(path):
    return json.loads(Path(path).read_bytes())


def git(*args):
    return subprocess.check_output(['git', *args], timeout=20)


def main():
    pins = [ref(folder / 'manifest.json') for folder in (RED, GREEN)]
    before, after = (json_file(pin['path']) for pin in pins)
    assert after['source'] == git('rev-parse', 'HEAD').decode().strip() != before['source']
    assert before['actualExit'] == 1 and after['actualExit'] == 0
    assert before['tools'][1] == after['tools'][1] and ref(TOOL) == after['tools'][0]
    assert before['tests'] == after['tests']
    assert set(after['tests']) == {f'PT-P01808-BIN-{n:03}' for n in range(18, 24)}
    failed = {before['tests'][f'PT-P01808-BIN-{n:03}'] for n in range(18, 22)}
    for manifest in (before, after):
        log_file = Path(manifest['unitLog']['path'])
        assert ref(log_file) == manifest['unitLog']
        recorded = dict(re.findall(r'^(test_\w+) \(.+\) \.\.\. (.*)$', log_file.read_text(), re.M))
        assert recorded == manifest['outcomes']
        assert set(recorded) == set(manifest['tests'].values())
        assert {method for method, result in recorded.items() if result == 'FAIL'} == (
            failed if manifest is before else set())
        assert all(result in ('FAIL', 'ok') for result in recorded.values())
    assert before['writerProof'] == after['writerProof']
    writer = after['writerProof']
    assert ref(writer['jar']['path']) == writer['jar']
    assert ref(writer['output']['path']) == writer['output']
    bytecode = Path(writer['output']['path']).read_text()
    assert 'iushr' in bytecode and 'iconst_0' in bytecode and 'ishl' in bytecode
    assert 'arraylength' in bytecode and 'writeVarInt:(I)V' in bytecode

    historic = json_file(ARCHIVE / 'manifest.json')
    execfile = ARCHIVE / 'jacoco.exec'
    receipt = historic['stages']['execinfo']['log']
    assert ref(receipt['path']) == receipt and historic['stages']['execinfo']['actualExit'] == 0
    assert historic['stages']['execinfo']['command'][-1] == str(execfile.resolve())
    decoded = runpy.run_path(str(TOOL))['decode'](execfile.read_bytes(), {TARGET})
    text = Path(receipt['path']).read_text()
    (crc, hit, count), = re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+' + TARGET + r'$', text, re.M)
    assert re.findall(r'^Session "([^"]+)":', text, re.M) == [historic['session']]
    assert decoded['sessions'][0]['labelBytesHex'] == historic['session'].encode('ascii').hex()
    item = decoded['classes'][TARGET]
    assert int(item['crc64'], 16) == int(crc, 16)
    assert item['probeCount'] == int(count) and len(item['hitProbeIds']) == int(hit)
    assert len(item['missedProbeIds']) + int(hit) == int(count)
    result = dict(actualExit=0, source=after['source'], productionCore=after['currentCore'], evidence=pins,
                  failedBefore=4, firstSucceeded=2, succeededAfter=6, writerProof=writer,
                  archivedOfflineTool=dict(receipt=receipt, binary=ref(execfile), source=historic['source'],
                                           records=decoded['totalClassRecords'], probeCount=int(count), covered=int(hit)),
                  historicalScopeRerun=0, realNativeActions=0, productTests=0, newFormalAcceptance=0,
                  whole451Accepted=False, terminalAtUTC=datetime.now(timezone.utc).isoformat())
    out = E / 'PG40152-p01808-exec-canonical-independent-v1'
    out.mkdir()
    file = out / 'manifest.json'
    file.write_text(json.dumps(result, indent=2) + '\n')
    print(ref(file), int(count), int(hit))


if __name__ == '__main__':
    main()
