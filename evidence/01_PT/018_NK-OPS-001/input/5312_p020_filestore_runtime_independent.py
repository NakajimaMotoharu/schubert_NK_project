"""Verify the saved haruka preflight and its own coverage against the frozen tool bytes."""
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
import hashlib
import json
import runpy
import subprocess

E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
RUN = E / 'PG40160-p020-haruka-real-filestore-v1'
PREP = E / 'PG40162-p020-filestore-artifact-prep-v1' / 'manifest.json'
OLD = E / 'PG40128-p020-path-contract-green206-v2'
OLDER_RESULT = E / 'PG40132-p020-path-contract-independent-v1' / 'manifest.json'
JAVA_SOURCE = 'program/characterization/src/main/java/dev/codex/schubert/characterization/GateCli.java'
CLASS = 'dev/codex/schubert/characterization/GateCli'
MIN_BYTES = 20 * 1024**3


def read(p):
    return json.loads(Path(p).read_bytes())


def ref(p):
    return dict(path=str(p), sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())


def main():
    pre, run, old = map(read, (PREP, RUN / 'manifest.json', OLD / 'manifest.json'))
    begin, admission, output = map(read, (RUN/'begin.json', RUN/'admission.json', RUN/'preflight.json'))
    assert run['actualExit'] == run['sshExit'] == 0 and run['authPrompts'] == 1
    assert run['admission'] == admission and admission['activeOwnedWorkspaceJobs'] == 0
    assert admission['uid'] == 1000 and admission['workspaceMode'] == '0700' and admission['runAbsent']
    terminal = run['terminal']
    assert terminal['allocatedRun'] and terminal['boot'] == admission['boot']
    assert terminal['ownerUid'] == admission['uid'] and terminal['actualExit'] == 0
    assert terminal['productTests'] == terminal['realBackendActions'] == 0
    assert terminal['physical'] == pre['mainPhysical'] == old['mainPhysical'] and len(terminal['physical']) == 17
    assert run['toolSource'] == pre['priorToolSource'] == old['source']
    assert begin['input'] == ref(PREP)
    assert {name: stage['actualExit'] for name, stage in terminal['stages'].items()} == {'javac': 0, 'unit': 0, 'report': 0}
    found = [str(RUN/p) for p in ('preflight.json','coverage.xml','file-store.exec')]
    assert all(ref(p) == run['artifacts'][Path(p).name] for p in found)
    execute = terminal['stages']['unit']['command']
    assert execute[-3:-1] == [CLASS.replace('/', '.'), 'preflight']
    assert all('inject' not in item.casefold() for item in execute)
    assert output['status'] == 'PASS' and not output['failures'] and output['credentialPermission'] == '0600'
    assert output['hostAllowlist'] == ['localhost', '127.0.0.1']
    assert min(admission['freeBytes'], output['freeBytes'], *terminal['fileStoreIndependentBytes'].values()) >= MIN_BYTES
    assert output['postgresControl'].endswith('/non-executable-pgctl')
    assert output['runtimeRoot'] == terminal['workspace'] + '/runtime'

    root = ET.parse(RUN/'coverage.xml').getroot()
    cls, = [c for c in root.iter('class') if c.get('name') == CLASS]
    two, = [m for m in cls.findall('method')
            if m.get('name') == 'preflight' and m.get('desc') == '(Ljava/nio/file/Path;Ljava/nio/file/Path;)V']
    assert {i.get('type'): (int(i.get('covered')), int(i.get('missed'))) for i in two.findall('counter')} == {
        'INSTRUCTION': (5, 0), 'LINE': (2, 0), 'COMPLEXITY': (1, 0), 'METHOD': (1, 0)}
    source = subprocess.check_output(['git', 'show', f"{old['source']}:{JAVA_SOURCE}"], timeout=20)
    assert hashlib.sha256(source).hexdigest() == pre['sourceHashes'][JAVA_SOURCE]
    line, = [i for i, text in enumerate(source.decode().splitlines(), 1) if 'case "preflight" -> preflight(' in text]
    sourcerow, = [r for r in root.iter('sourcefile') if r.get('name') == 'GateCli.java']
    hit, = [r for r in sourcerow.findall('line') if r.get('nr') == str(line)]
    assert int(hit.get('ci')) > 0 and int(hit.get('mi')) == 0

    decode = runpy.run_path('tools/quality/jacoco_readonly_exec_subset.py')['decode']
    current = decode((RUN/'file-store.exec').read_bytes(), {CLASS})
    previous = decode((OLD/'jacoco.exec').read_bytes(), {CLASS})
    assert current['sessions'][0]['labelBytesHex'] == terminal['session'].encode().hex()
    assert previous['sessions'][0]['labelBytesHex'] == old['session'].encode().hex()
    assert terminal['session'] != old['session']
    a, b = current['classes'][CLASS], previous['classes'][CLASS]
    assert a['crc64'] == b['crc64'] and a['probeCount'] == b['probeCount']
    added = sorted(set(a['hitProbeIds']).intersection(b['missedProbeIds']))
    assert added
    assert terminal['methods']['preflight']['METHOD'] == dict(covered=1, missed=0)
    result = dict(actualExit=0, testId='PT-CHR-PREFLIGHT-FS-001', source=run['source'],
                  toolSource=run['toolSource'], productionCore=run['productionCore'],
                  admission=ref(RUN/'admission.json'), origin=ref(RUN/'manifest.json'), frozenInput=ref(PREP),
                  historicalToolDeficit=ref(OLDER_RESULT), historicalExec=ref(OLD/'jacoco.exec'),
                  artifacts=run['artifacts'], workingVolumeFreeBytes=output['freeBytes'], requiredBytes=MIN_BYTES,
                  reportedPass=True, physicalClassCount=17, normalDispatchCoveredLine=line,
                  methods=terminal['methods'], session=terminal['session'], gateCliClassCrc=a['crc64'],
                  earlierSessionMissingProbeCount=len(b['missedProbeIds']),
                  newlyObservedProbeIds=added, samePhysicalSeparateSessions=True,
                  mergedCoverageClaim=False, productTests=0, realBackendActions=0, newFormalAcceptance=0,
                  whole451Accepted=False, terminalAtUTC=datetime.now(timezone.utc).isoformat())
    folder = E/'PG40190-p020-haruka-filestore-independent-v1'
    folder.mkdir()
    output = folder/'manifest.json'
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(ref(output), result['workingVolumeFreeBytes'], added)


if __name__ == '__main__':
    main()
