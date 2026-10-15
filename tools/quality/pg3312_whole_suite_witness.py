"""Selected original XML/source witnesses after qualified whole3702; no test rerun."""
import hashlib
import inspect
import json
import os
import shlex
import subprocess

from lan_server import run
from pg3274_header_group_full_six import ROOT, SOURCE, W
from pg3286_protocol_existing_run_witness import project_suite, require

SERVER = r'''import hashlib,json,pathlib,re,xml.etree.ElementTree as ET
B=pathlib.Path('/home/mini/schubert-nk-pgpt');S=B/'source-full-PG3302';M=B/'runs/PG3302-six-v1/manifest.safe.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
require(sha(M)==INPUT['wholeSha256'],'qualified terminal whole manifest hash required')
v=json.loads(M.read_bytes());require(v['actualExit']==v['mavenExit']==0 and v['issues']==[] and v['sourceInputsUnchanged']is True and v['productionSource']==INPUT['source']and v['sourceSnapshotHead']==INPUT['snapshot'],'same completed whole source required')
result={};source_hashes={}
for module,names in INPUT['classes'].items():
 reports=S/('src/schubert-nk-'+module+'/target/surefire-reports')
 paths=sorted(reports.glob('TEST-*.xml'))if names is None else[reports/('TEST-'+name+'.xml')for name in names]
 suites=[]
 for path in paths:
  node=ET.parse(path).getroot();suite=project_suite(node,sha(path));name=suite['class'];java='src/schubert-nk-'+module+'/src/test/java/'+name.replace('.','/')+'.java'
  require(sha(S/java)==INPUT['testHashes'][java],'actual fixed Test source hash required')
  methods=set(re.findall(r'\bvoid\s+([A-Za-z][A-Za-z0-9_]*)\s*\(', (S/java).read_text()))
  require(all(case.split('(',1)[0]in methods for case in suite['tests']),'only actual static Java Test method names exported')
  suites.append(suite);source_hashes[java]=sha(S/java)
 result[module]=suites
require(len(result['protocol'])==17 and sum(s['counts']['tests']for s in result['protocol'])==85,'original Protocol85/17 required')
require(sha(M)==INPUT['wholeSha256'],'whole authority stable')
print(json.dumps({'actualExit':0,'productionSource':INPUT['source'],'sourceSnapshot':INPUT['snapshot'],'wholeManifestSha256':INPUT['wholeSha256'],'modules':result,'testSourceHashes':source_hashes,'xmlPropertiesExported':False,'newPtCredit':0,'vmActions':0,'formalUpdated':False}))
'''


def server_source(data):
    raw = 'INPUT=' + repr(data) + '\n' + inspect.getsource(require) + '\n' + inspect.getsource(project_suite) + '\n' + SERVER
    compile(raw, '<selected original whole3702 XML witnesses>', 'exec')
    return raw


def main():
    receipt = json.loads((W / 'pg3304-directional-group-full-qualified-v1/manifest.safe.json').read_bytes()); full = receipt['result']
    require(receipt['actualExit'] == full['actualExit'] == full['FESFlakyNotRun'] == 0
            and full['productionSource'] == SOURCE and full['tests'] == 3702 and full['staticSixModules'] == 0, 'completed independent whole3702 required')
    classes = {'protocol': None, 'web': ['dev.codex.schubert.nk.web.messaging.ArtemisRequestSenderTest', 'dev.codex.schubert.nk.web.messaging.JmsReplyDecoderTest']}
    tests = {}
    for module, names in classes.items():
        paths = (ROOT / f'src/schubert-nk-{module}/src/test/java').rglob('*Test.java') if names is None else [ROOT / ('src/schubert-nk-' + module + '/src/test/java/' + name.replace('.', '/') + '.java') for name in names]
        for path in paths:
            relative = str(path.relative_to(ROOT)); fixed = subprocess.check_output(['git', 'show', full['sourceSnapshot'] + ':' + relative], cwd=ROOT)
            require(hashlib.sha256(fixed).digest() == hashlib.sha256(path.read_bytes()).digest(), 'current selected Test must equal actual full snapshot')
            tests[relative] = hashlib.sha256(fixed).hexdigest()
    data = {'source': SOURCE, 'snapshot': full['sourceSnapshot'], 'wholeSha256': full['serverManifestSha256'], 'classes': classes, 'testHashes': tests}
    raw = server_source(data)
    os.umask(0o077); private = W / 'pg3312-whole-suite-witness-v1'; private.mkdir(mode=0o700)
    (private / 'witness.private.py').write_text(raw)
    rc, output = run('python3 -c ' + shlex.quote(raw), timeout=90)
    (private / 'observer.private.log').write_text(output)
    require(rc == 0, 'original selected XML witness must succeed')
    value = json.loads(next(line for line in output.splitlines() if line.startswith('{')))
    public = ROOT / 'evidence/01_PT/001_NK-PRO-001/evidence/provisional/PG3312-whole-suite-witness'
    public.mkdir(parents=True, exist_ok=False)
    with (public / 'manifest.json').open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2); stream.write('\n')
    print(json.dumps({'actualExit': 0, 'moduleWitnesses': {m: {'suites': len(suites), 'tests': sum(s['counts']['tests'] for s in suites)} for m, suites in value['modules'].items()}, 'newPtCredit': 0}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
