"""Link static framework canaries and offline DIF-015 tests to their exact public evidence."""
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
import hashlib
import json
import re
import subprocess

D = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
TOOL = 'tools/quality/architecture/ModuleDependencyAudit.java'
UI = 'documents/200_UI/260_引継ぎ・監査/264_現行互換性Characterization Test仕様.md'
SS = 'documents/300_SS/310_アプリケーション/311_モジュール・package・class責務設計.md'


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(value):
    return hashlib.sha256(value).hexdigest()


def ref(path):
    return dict(path=str(path), sha256=sha(Path(path).read_bytes()))


def git(*args):
    return subprocess.check_output(['git', *args], timeout=25)


def main():
    group = read(next(D.glob('617_G08*.json')))['values']
    head = git('rev-parse', 'HEAD').decode().strip()
    assert head == group['source']
    canary_ref, dif_ref = group['oracleReferences']
    assert all(ref(item['path']) == item for item in group['oracleReferences'])
    framework, dif = (read(item['path']) for item in group['oracleReferences'])
    assert framework['productionCoreMain'] == group['productionCoreMain']
    fw_ref = framework['after']
    assert ref(fw_ref['path']) == fw_ref
    fw_run = read(fw_ref['path'])
    assert fw_run['source'] == framework['source']
    assert fw_run['toolSha256'] == sha(git('show', f'{head}:{TOOL}'))
    assert fw_run['correct'] == 10 and fw_run['childAuditExit'] == 1
    fw_cases = []
    for record in fw_run['cases']:
        assert record['expected'] == record['observed']
        fw_cases.append(dict(testId=record['testId'], source=fw_run['source'],
                             owner='WBS-F02', contract=SS, target=record['target'],
                             expectedFrameworkFinding=record['expected'], evidence=fw_ref))
    assert {r['testId'] for r in fw_cases} == {f'PT-F02-ARCH-{n:03}' for n in range(13, 23)}

    unit_path = Path(dif['unit']['path'])
    unit = read(unit_path)
    assert ref(unit_path) == dif['unit'] and unit['source'] == dif['source']
    xml = unit_path.parent / 'xml/TEST-junit-jupiter.xml'
    assert ref(xml)['sha256'] == unit['xmlHashes'][xml.name]
    tests = [(r.get('classname'), r.get('name')) for r in ET.parse(xml).iter('testcase')]
    assert len(tests) == len(set(tests)) == 206
    dif_cases = []
    for test_id, (owner, method) in dif['testIds'].items():
        assert ('dev.codex.schubert.characterization.' + owner, method + '()') in tests
        dif_cases.append(dict(testId=test_id, source=unit['source'], owner='WBS-P020-01.02',
                              contract=UI, method=owner + '.' + method, evidence=ref(xml)))
    assert {r['testId'] for r in dif_cases} == {'PT-CHR-DEF077', 'PT-CHR-DEF078'}
    assert dif['actualNkChr'] is False and dif['newAcceptance'] == 0
    assert git('diff', '--name-only', unit['source'], head, '--', 'program/characterization') == b''

    # Make the original typed decoder receipts verifiable after a fresh checkout.
    probe_pins = [dif['failedReadOnly']['log'], unit['stages']['execinfo']['log']]
    first_unit = read(dif['firstUnit']['path'])
    probe_pins.append(first_unit['stages']['execinfo']['log'])
    for pin, session in zip(probe_pins, (read(dif['firstRejectedUnit']['path'])['session'],
                                         unit['session'], first_unit['session']), strict=True):
        assert ref(pin['path']) == pin
        text = Path(pin['path']).read_text()
        assert re.findall(r'^Session "([^"]+)":', text, re.M) == [session]
        assert not re.search(r'org/postgresql/|com/microsoft/playwright/|dev/codex/schubert/nk/', text)
    value = dict(actualExit=0, source=head, productCore=group['productionCoreMain'], canaries=fw_cases,
                 offlineToolCases=dif_cases, pinnedAudits=[canary_ref, dif_ref], typedPublicLogs=probe_pins,
                 testExecutions=0, runtimeOperations=0, newFormalAcceptance=0, wholeG08Accepted=False,
                 terminalAtUTC=datetime.now(timezone.utc).isoformat(), verifier=ref(__file__))
    out = E / group['run']
    out.mkdir()
    m = out / 'manifest.json'
    m.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    print(ref(m))


if __name__ == '__main__':
    main()
