"""RO witnesses from completed current whole3704, never a test or VM replay."""
import hashlib
import inspect
import json
import os
import shlex
import subprocess

import lan_server
from pg3274_header_group_full_six import ROOT, SOURCE, W
from pg3286_protocol_existing_run_witness import project_suite, require

SELECTED = {
    'protocol': None,
    'storage': None,
    'api': ['application.media.MediaApplicationServiceTest',
            'application.media.MediaReplayServiceTest', 'persistence.MediaRepositoryTest',
            'file.HeldMediaFileInspectorTest', 'storage.ScenarioFileWriterTest',
            'storage.ScenarioRecordStreamTest', 'application.scenario.ScenarioDetailDeliveryTest',
            'application.scenario.ScenarioApplicationServiceTest',
            'application.scenario.ScenarioReplayServiceTest',
            'application.scenario.ScenarioFileRegeneratorTest',
            'messaging.inbound.SyncRequestListenerTest',
            'messaging.config.ArtemisBrokerConfigurationTest',
            'messaging.config.ArtemisFileJournalTest'],
    'web': ['media.MediaResponseDecoderTest', 'media.MediaRangeServiceTest',
            'media.HttpByteRangeParserTest', 'media.ContentDispositionFactoryTest',
            'media.MediaBodyStreamerTest', 'session.MediaControllerTest',
            'storage.LargeResultReaderTest', 'storage.ScenarioRecordReaderTest',
            'messaging.ScenarioWireClientTest'],
    'batch': ['file.TransferCleanupTest', 'file.TransferCleanupFailureTest',
              'platform.MorningStopPassTest'],
}

SERVER = r'''
B=pathlib.Path('/home/mini/schubert-nk-pgpt');S=B/'source-full-PG3350';M=B/'runs/PG3350-six-v1/manifest.safe.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
require(sha(M)==INPUT['wholeSha256'],'qualified original whole manifest hash')
v=json.loads(M.read_bytes())
require(v['actualExit']==v['mavenExit']==0 and v['issues']==[] and v['sourceInputsUnchanged']is True
        and v['productionSource']==INPUT['source'] and v['sourceSnapshotHead']==INPUT['snapshot'],'genuine terminal same source')
result={};source_hashes={}
for module,names in INPUT['classes'].items():
 reports=S/('src/schubert-nk-'+module+'/target/surefire-reports')
 paths=sorted(reports.glob('TEST-*.xml'))if names is None else[reports/('TEST-'+n+'.xml')for n in names]
 suites=[]
 for path in paths:
  node=ET.parse(path).getroot();suite=project_suite(node,sha(path));name=suite['class']
  java='src/schubert-nk-'+module+'/src/test/java/'+name.replace('.','/')+'.java'
  require(sha(S/java)==INPUT['testHashes'][java],'actual fixed Test bytes')
  methods=set(re.findall(r'\bvoid\s+([A-Za-z][A-Za-z0-9_]*)\s*\(', (S/java).read_text()))
  require(all(case.split('(',1)[0]in methods for case in suite['tests']),'actual static Java method names only')
  suite['caseNameHashes']=[hashlib.sha256(n.encode()).hexdigest()for n in suite['tests']]
  suite['tests']=[n.split('(',1)[0]for n in suite['tests']]
  suite['uniqueIdentity']='class plus original ordinal plus name SHA256; arguments not exported'
  suites.append(suite);source_hashes[java]=sha(S/java)
 result[module]=suites
for module,counts in INPUT['completeModuleCounts'].items():
 require(len(result[module])==counts['suites'] and sum(s['counts']['tests']for s in result[module])==counts['tests'],'exact complete module XML set')
require(set(source_hashes)==set(INPUT['testHashes']),'all selected Test source files witnessed')
require(sha(M)==INPUT['wholeSha256'],'stable original terminal authority')
print(json.dumps({'actualExit':0,'productionSource':INPUT['source'],'run':'PG3350-six-v1','sourceSnapshot':INPUT['snapshot'],
 'wholeManifestSha256':INPUT['wholeSha256'],'modules':result,'testSourceHashes':source_hashes,
 'propertiesStdoutArgumentsExported':False,'newPtCredit':0,'vmActions':0,'formalUpdated':False}))
'''


def server_source(data):
    raw = ('import hashlib,json,pathlib,re,xml.etree.ElementTree as ET\nINPUT=' + repr(data)
           + '\n' + inspect.getsource(require) + '\n' + inspect.getsource(project_suite) + '\n' + SERVER)
    compile(raw, '<current3704 selected XML witnesses>', 'exec')
    return raw


def main():
    receipt = json.loads((W / 'pg3352-oracle-boundary-full-qualified-v1/manifest.safe.json').read_bytes())
    full = receipt['result']
    require(receipt['actualExit'] == full['actualExit'] == full['FESFlakyNotRun'] == full['staticSixModules'] == 0
            and full['productionSource'] == SOURCE and full['tests'] == 3704, 'independently completed whole3704 required')
    classes = {m: None if names is None else ['dev.codex.schubert.nk.' + m + '.' + n for n in names]
               for m, names in SELECTED.items()}
    tests = {}
    for module, names in classes.items():
        paths = ((ROOT / f'src/schubert-nk-{module}/src/test/java').rglob('*Test.java') if names is None else
                 [ROOT / ('src/schubert-nk-' + module + '/src/test/java/' + n.replace('.', '/') + '.java') for n in names])
        for path in paths:
            relative = str(path.relative_to(ROOT))
            fixed = subprocess.check_output(['git', 'show', full['sourceSnapshot'] + ':' + relative], cwd=ROOT)
            require(fixed == path.read_bytes(), 'current selected Test equals actual executed source')
            tests[relative] = hashlib.sha256(fixed).hexdigest()
    data = {'source': SOURCE, 'snapshot': full['sourceSnapshot'], 'wholeSha256': full['serverManifestSha256'],
            'classes': classes, 'testHashes': tests,
            'completeModuleCounts': {m: full['modules'][m] for m, names in classes.items() if names is None}}
    raw = server_source(data)
    os.umask(0o077); private = W / 'pg3356-current-file-media-suite-witness-v1'; private.mkdir(mode=0o700)
    (private / 'witness.private.py').write_text(raw)
    rc, output = lan_server.run('python3 -c ' + shlex.quote(raw), timeout=90)
    (private / 'observer.private.log').write_text(output)
    require(rc == 0, 'original XML witness succeeds')
    value = json.loads(next(line for line in output.splitlines() if line.startswith('{')))
    with (private / 'manifest.safe.json').open('x') as stream:
        json.dump(value, stream)
    public = ROOT / 'evidence/01_PT/003_NK-PRO-003/evidence/provisional/PG3356-current-file-media-witness'
    public.mkdir(parents=True, exist_ok=False)
    with (public / 'manifest.json').open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2); stream.write('\n')
    print(json.dumps({'actualExit': 0, 'moduleWitnesses': {m: {'suites': len(suites),
        'tests': sum(s['counts']['tests'] for s in suites)} for m, suites in value['modules'].items()}, 'newPtCredit': 0}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
