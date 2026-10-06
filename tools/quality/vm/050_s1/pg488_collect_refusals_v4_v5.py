"""Preserve refused PG488 runs. No raw diagnostics or secret-bearing XML enters Git."""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET

ROOT = Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
for version, bugs in [(4, ['BUG-790', 'YKT-563']), (5, ['BUG-791'])]:
    name = f'pg488-retained-run-selected-v{version}'
    private = WORK / f'pg488-refused-host-v{version}'
    out = ROOT / f'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG488-selected-refused-v{version}'
    assert private.is_dir() and not out.exists()
    assert (WORK / (name + '.exit')).read_text().strip() == '1'
    suites = []
    for xml in sorted(private.rglob('TEST-*.xml')):
        data = ET.parse(xml).getroot().attrib
        suites.append({'name': data['name'], 'tests': int(data['tests']),
                       'failures': int(data['failures']), 'errors': int(data['errors']),
                       'skipped': int(data['skipped']),
                       'xmlSha256': hashlib.sha256(xml.read_bytes()).hexdigest()})
    value = {'run': name, 'actualExit': 1, 'branch': 'dev-foundation',
             'head': (WORK / (name + '.source')).read_text().strip(),
             'started': (WORK / (name + '.started')).read_text().strip(),
             'completed': (WORK / (name + '.completed')).read_text().strip(),
             'trackedDiffSha256': hashlib.sha256((WORK / (name + '.completed-source-diff.private')).read_bytes()).hexdigest(),
             'sourceBoundary': 'dirty limited run; untracked start hashes absent; no formal acceptance',
             'command': f'bash tools/quality/vm/050_s1/pg488_retained_run_selected_v{version}.sh',
             'suites': suites, 'notRunModules': ['batch'] if version == 4 else [],
             'related': ['SSC-201', *bugs], 'groupAccepted': False,
             'coverage100': False, 'native': False, 'formal': False, 'ITST': False,
             'rawSecretsIncluded': False}
    for key in ['tests', 'failures', 'errors', 'skipped']:
        value[key] = sum(s[key] for s in suites)
    encoded = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()
    out.mkdir(parents=True)
    (out / 'manifest.json').write_bytes(encoded)
    print(json.dumps({'run': name, 'tests': value['tests'], 'failures': value['failures'],
                      'errors': value['errors'], 'actualExit': 1,
                      'manifestSha256': hashlib.sha256(encoded).hexdigest()}))
