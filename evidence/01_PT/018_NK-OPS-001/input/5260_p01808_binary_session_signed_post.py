"""Verify the signed timestamp fix against separate readers and preserved public streams."""
from datetime import datetime, timezone
from pathlib import Path
import ast
import hashlib
import json
import runpy
import struct
import subprocess

TOOLS=Path('tools/quality')
E=Path('evidence/01_PT/018_NK-OPS-001/evidence')
RED=E/'PG40022-p01808-binary-session-signed-red-v1'
GREEN=E/'PG40024-p01808-binary-session-signed-green-v1'
DECODER=TOOLS/'jacoco_readonly_exec_subset.py'
CLS='dev/codex/schubert/characterization/ArtifactComparator'
CURRENT=E/'PG39990-p020-search-empty170-v1'
EXPECTED_RED={'test_negative_end_is_rejected','test_two_minimum_java_longs_are_rejected',
              'test_two_negative_ones_are_rejected','test_negative_end_cannot_be_greater_than_latest_java_long'}


def pin(p):
    return dict(path=str(p),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())


def load(p):
    return json.loads(Path(p).read_bytes())


def main():
    r=load(RED/'manifest.json')
    g=load(GREEN/'manifest.json')
    assert r['inputs'][1]==g['inputs'][1] and g['earlierRed']==pin(RED/'manifest.json')
    assert r['actualExit']==1 and g['actualExit']==0 and set(r['failedMethods'])==EXPECTED_RED
    assert g['passed']==9 and all(g[k]==0 for k in ('failures','errors','skipped','notRun','productTests'))
    assert all(pin(m['log']['path'])==m['log'] for m in (r,g))
    assert pin(DECODER)==g['inputs'][0]
    original=subprocess.check_output(['git','show',f'{r["source"]}:{DECODER}'],timeout=15)
    current=DECODER.read_bytes()
    assert hashlib.sha256(original).hexdigest()==r['inputs'][0]['sha256']
    parsed=ast.parse(current)
    assert [node.name for node in parsed.body if isinstance(node,ast.FunctionDef)]==['decode','selftest']
    assert current.count(b"signed=True")==2 and b'not 0 <= start <= end' in current
    old_scope={'__name__':'decoder_previous'}
    exec(compile(original,str(DECODER),'exec'),old_scope)
    fixed=runpy.run_path(str(DECODER))
    public=runpy.run_path(str(TOOLS/'public_jacoco_exec_format_v1.py'))['parse']
    data=(CURRENT/'jacoco.exec').read_bytes()
    proof=load(E/'PG39994-p020-search-empty-independent-v1'/'manifest.json')
    assert proof['tests']==170 and proof['unit']==pin(CURRENT/'manifest.json')
    expected=old_scope['decode'](data,{CLS})
    assert fixed['decode'](data,{CLS})==expected
    assert public(data)['orderedSessions']==1 and len(expected['sessions'])==1
    vector=bytes.fromhex('01c0c0100710000352554e')+struct.pack('>qq',0,-1)
    assert public(vector)['orderedSessions']==0
    result=dict(actualExit=0,source=g['source'],productionCoreMain=g['productionCoreMain'],red=pin(RED/'manifest.json'),
                green=pin(GREEN/'manifest.json'),javaSignedLongAgreement=True,previousRedCases=sorted(EXPECTED_RED),
                publicOrdinaryProbe=pin(CURRENT/'jacoco.exec'),probeResultRetained=True,oldAndCurrentValidShapeEqual=True,
                separateReader=pin(TOOLS/'public_jacoco_exec_format_v1.py'),productTests=0,actualNativeStreams=0,
                measuredProductCoverage=0,whole451Accepted=False,newAcceptance=0,terminalAtUTC=datetime.now(timezone.utc).isoformat())
    with (GREEN/'independent.json').open('x') as f:
        json.dump(result,f,indent=2)
        f.write('\n')
    print(pin(GREEN/'independent.json'))


if __name__=='__main__':
    main()
