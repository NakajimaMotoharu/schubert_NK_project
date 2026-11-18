"""Independently verify the three local JUnit results and single exact value-class probes."""
from datetime import datetime, timezone
from pathlib import Path
import gzip
import hashlib
import json
import re
import subprocess
from xml.etree import ElementTree as ET

O=Path('evidence/01_PT/018_NK-OPS-001/evidence/PG40008-p01810-broker-evidence-value-v2')
PREFIX='dev/codex/schubert/nk/batch/mq/'
NAME=PREFIX+'ArtemisStartupObservation$Evidence'
TEST='src/schubert-nk-batch/src/test/java/'+PREFIX+'ArtemisStartupEvidenceValueTest.java'
EXPECTED={
    'PT-P01810-CATALOG-062A':'ownsAllNestedValueInputsBeforeAndAfterCallerMutatesThem()',
    'PT-P01810-CATALOG-062B':'comparesOwnedValueDataWhileItsGeneralDiagnosticsStayFixed()',
    'PT-P01810-CATALOG-062C':'rejectsMissingNestedInputsWhileTakingOwnership()',
}


def pin(p):
    return dict(path=str(p),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())


def load(p):
    return json.loads(Path(p).read_bytes())


def crc64(content):
    crc=0
    for byte in content:
        crc^=byte
        for _ in range(8):
            crc=(crc >> 1) ^ (0xd800000000000000 if crc & 1 else 0)
    return f'{crc:016x}'


def main():
    m=load(O/'manifest.json')
    b=load(O/'begin.json')
    assert m['actualExit']==0 and m['testSource']==b['testSource']
    assert b['noArtemisSdk'] and b['hostServicesTouched']==0
    actual=ET.parse(m['testXml']['path'])
    assert {n.get('name') for n in actual.iter('testcase')}==set(EXPECTED.values())
    assert not any(n.tag in ('failure','error','skipped') for n in actual.iter())
    assert m['passed']==3 and all(m[k]==0 for k in ('failed','errors','skipped','notRun'))
    assert m['stages']['unit']['actualExit']==0 and load(O/'unit-exit.json')==m['stages']['unit']
    assert m['stages']['testcompile']['actualExit']==0
    line,=[x for x in (O/'raw.tsv').read_text().splitlines() if x.startswith('CLASS\t')]
    recorded=line.split('\t')[2]
    target=b['productFiles'][NAME+'.class']
    assert recorded==crc64(Path(target['path']).read_bytes()) and pin(target['path'])==target
    covered=re.search(rf'^{recorded}\s+(\d+) of\s+(\d+)\s+{re.escape(NAME)}$', (O/'execinfo.log').read_text(),re.M)
    assert covered and int(covered[1])>0
    assert m['counters']['BRANCH']==dict(missed=0,covered=0)
    assert all(c['missed']==0 for c in m['counters'].values())
    setup=load(b['firstFixtureCompile']['path'])
    assert setup['actualExit']==1 and list(setup['stages'])==['testcompile'] and setup['passed']==0
    source=subprocess.check_output(['git','show',f'{m["testSource"]}:{TEST}'],timeout=20)
    assert hashlib.sha256(source).hexdigest()==b['testInput']['sha256']
    assert b'ClientSession' not in source and b'new ArtemisStartupObservation()' not in source
    allocation={'missingField','missingPermission','missingPressure'}
    held=[]
    for finding in m['rawPmd']:
        line=source.decode().splitlines()[finding['line']-1]
        name,=[item for item in allocation if item in line]
        assert 'new HashMap<>()' in line and finding['rule']=='UseConcurrentHashMap'
        held.append(dict(finding,scope=name,applicable=False,
            reason='A single method owns the map and captures it only for synchronous assertThrows and constructor; no concurrent access. HashMap admits the deliberate null test input.'))
        allocation.remove(name)
    assert not allocation and len(held)==3
    init=gzip.decompress(Path(m['classInit']['path']).read_bytes())
    assert f"Initializing '{NAME}'".encode() in init
    assert not re.search(rb"Initializing '(?:org/apache/activemq/|dev/codex/schubert/nk/batch/mq/ArtemisStartupObservation'|org/postgresql/)",init)
    result=dict(actualExit=0,sourceCore=m['sourceCore'],testSource=m['testSource'],manifest=pin(O/'manifest.json'),
        recordCrc64=recorded,firstPreparationExit=1,firstDynamicSuccess=3,firstDynamicTotal=3,newTestDefinitions=3,
        counters=m['counters'],firstFixtureCompile=b['firstFixtureCompile'],testIds=EXPECTED,pmdRaw=3,
        pmdApplicable=0,pmdUnclassified=0,pmdPerSite=held,realBroker=0,actualNative=0,whole451Accepted=False,
        newAcceptance=0,terminalAtUTC=datetime.now(timezone.utc).isoformat())
    with (O/'independent.json').open('x') as stream:
        json.dump(result,stream,indent=2)
        stream.write('\n')
    print(pin(O/'independent.json'),recorded)


if __name__=='__main__':
    main()
