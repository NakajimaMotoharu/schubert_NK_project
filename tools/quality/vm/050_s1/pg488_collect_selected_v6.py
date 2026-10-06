"""PG-D390 / RLOOK200001-002, CTERM200001. Limited run, never formal/native."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
STEM = WORK / 'pg488-retained-run-selected-v6'
FREEZE = WORK / 'pg488-host-v6'
OUT = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG488-retained-run-selected-v6'
assert not FREEZE.exists() and not OUT.exists()
assert STEM.with_suffix('.exit').read_text().strip() == '0'
diff = subprocess.check_output(['git', 'diff', '--', 'src', 'pom.xml'], cwd=ROOT)
assert diff == Path(str(STEM) + '.completed-source-diff.private').read_bytes()
FREEZE.mkdir(mode=0o700)
OUT.mkdir(parents=True)
modules = ['protocol', 'storage', 'bootstrap', 'api', 'batch']
suites = []
statics = []
for module in modules:
    target = ROOT / f'src/schubert-nk-{module}/target'
    dest = FREEZE / module
    dest.mkdir(mode=0o700)
    for name in ['surefire-reports', 'site/jacoco', 'classes']:
        shutil.copytree(target / name, dest / Path(name).name)
    shutil.copy2(target / 'jacoco.exec', dest / 'jacoco.exec')
    bugs = target / 'spotbugsXml.xml'
    assert len(ET.parse(bugs).getroot().findall('BugInstance')) == 0
    shutil.copy2(bugs, dest / bugs.name)
    statics.append({'module': module, 'bugInstances': 0})
    for report in sorted((target / 'surefire-reports').glob('TEST-*.xml')):
        data = ET.parse(report).getroot().attrib
        assert all(int(data[key]) == 0 for key in ['failures', 'errors', 'skipped'])
        suites.append({'name': data['name'], 'tests': int(data['tests']),
                       'xmlSha256': hashlib.sha256(report.read_bytes()).hexdigest()})
assert len(suites) == 23
source = {}
for path in sorted((ROOT / 'src').rglob('*')):
    if path.is_file() and 'target' not in path.parts:
        source[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
manifest = {'run': 'PG488-retained-run-selected-v6', 'actualExit': 0,
            'started': Path(str(STEM)+'.started').read_text().strip(),
            'completed': Path(str(STEM)+'.completed').read_text().strip(),
            'branch': 'dev-foundation', 'head': Path(str(STEM)+'.source').read_text().strip(),
            'dirtySourceSha256': hashlib.sha256(diff).hexdigest(), 'sourceFiles': source,
            'tests': sum(s['tests'] for s in suites), 'suites': suites,
            'failures': 0, 'errors': 0, 'skipped': 0, 'static': statics,
            'command': 'bash tools/quality/vm/050_s1/pg488_retained_run_selected_v2.sh',
            'environment': {'os': Path('/etc/os-release').read_text().split('PRETTY_NAME=')[1].splitlines()[0].strip('"'), 'jdk': '25.0.4', 'maven': '3.9.12', 'jacoco': '0.8.15'},
            'related': ['SSC-200', 'BUG-788', 'BUG-789', 'YKT-562', 'SSC-201', 'BUG-790', 'BUG-791', 'YKT-563'],
            'testIds': ['RLOOK200001', 'RLOOK200002', 'CTERM200001', 'EXP200001', 'WIRE200001', 'WIRE200002', 'REF201001', 'REF201002', 'REF201003', 'REF201004', 'REF201005'],
            'coverage100': False, 'fullRegression': False, 'native': False,
            'formalAcceptance': False, 'ITST': False, 'privateFreeze': str(FREEZE),
            'rawSecretsIncluded': False}
encoded = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode()
(OUT / 'manifest.json').write_bytes(encoded)
print(json.dumps({'tests': manifest['tests'], 'suites': len(suites), 'actualExit': 0,
                  'manifestSha256': hashlib.sha256(encoded).hexdigest(), 'formal': False}))
