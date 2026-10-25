"""Finite ClassFile-API metadata reader for saved host artifacts, not product execution."""
from collections import Counter
import json
import os
from pathlib import Path
import g07_host_class_provenance_inputs as data
import pg9346_direct_companion_jdk_post as steps
from host_tool_invocation import capture, verify

ROOT = data.ROOT
SOURCE = '8ba82083ec65abc6373b8454576dcbaee7d3e621'
BASE = data.BASE
SLOT = ROOT.parent / 'pgpt-runs/PG379/pg9848-main-code-structure-v2'
OUT = BASE / 'PG9848-main-code-structure-v2'
HELD = frozenset(('api:dev/codex/schubert/nk/api/error/TemporaryInfrastructureException.class',
    'web:dev/codex/schubert/nk/web/bootstrap/WebStartupException.class'))
NORMAL_SHA = 'e074d972cbaf56b94ba4d25a77e7368b4f53ccd91489be0fbc27f07ef3975c95'
GAP_SHA = 'cd198bf12902c3d14d7f4f72ca436a2034c27b6c76a81dea1027aab4f080b627'


def classification(value, name):
    code = sum(m['hasCode'] for m in value['methods'])
    if code:
        return 'SYNTHETIC_CODE_REQUIRES_APPLICABILITY_REVIEW' if value['flags'] & 0x1000 else 'CODE_PRESENT_NOT_RUNTIME_QUALIFICATION'
    if name.endswith('/package-info.class') and not value['fields'] and not value['methods']:
        return 'NO_CODE_PACKAGE_ANNOTATION'
    if value['flags'] & 0x2000 and value['flags'] & 0x0200:
        return 'NO_CODE_ANNOTATION_INTERFACE'
    if value['flags'] & 0x0200:
        return 'NO_CODE_INTERFACE'
    return 'NO_CODE_OTHER_UNRESOLVED'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    normal = data.read_checked(BASE / 'PG9812-cleanup-values-six-compile-v1/manifest.json',NORMAL_SHA)
    gap = data.read_checked(BASE / 'PG9828-existing-host-gap-map-v1/manifest.json',GAP_SHA)
    assert normal['actualExit'] == gap['actualExit'] == 0 and normal['source'] == gap['source'] == SOURCE
    rows = data.read_checked(BASE / 'PG9828-existing-host-gap-map-v1/physical-class-gap-map.json',gap['physicalGapMapSha256'])
    assert len(rows) == len({r['physicalKey'] for r in rows}) == 1843
    assert all(data.sha((ROOT / p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    helper = ROOT / 'tools/quality/architecture/MainClassCodeStructureAuditV2.java'
    helper_sha = data.sha(helper.read_bytes())
    assert all(data.sha(Path(j['path']).read_bytes()) == j['sha256'] for j in normal['jars'].values())
    os.umask(0o077)
    SLOT.mkdir()
    classes = SLOT / 'reader'
    classes.mkdir()
    catalog = SLOT / 'jars.tsv'
    with catalog.open('x') as stream:
        stream.write(''.join(module+'\t'+j['path']+'\n' for module,j in sorted(normal['jars'].items())))
    snapshot = ROOT.parent / 'pgpt-runs/PG379/pg9812-cleanup-values-six-compile-v1/snapshot'
    tc = ROOT.parent / 'toolchain/jdk-25.0.4/bin'
    steps.SLOT = SLOT
    stages = [steps.step('compile-reader',[str(tc/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-d',str(classes),str(helper)])]
    assert stages[0]['actualExit'] == 0 and not stages[0]['timedOut']
    stages.append(steps.step('read-structures',[str(tc/'java'),'-cp',str(classes),helper.stem,str(snapshot),str(catalog)]))
    assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut']
    values,held = {},[]
    lines = (SLOT/'read-structures.stdout').read_text().splitlines()
    assert lines[-1] == 'TOTAL\t1841\t2'
    for line in lines[:-1]:
        f = line.split('\t')
        if f[0] == 'HOLD':
            assert len(f) == 2 and f[1] in HELD and f[1] not in held
            held.append(f[1])
        elif f[0] == 'CLASS':
            assert len(f) == 6 and f[1] not in values and f[1] not in HELD
            values[f[1]] = dict(flags=int(f[2]),sourceFile=f[3],fields=int(f[4]),expectedMethods=int(f[5]),methods=[])
        else:
            assert f[0] == 'METHOD' and len(f) == 7 and f[1] in values and f[5] in ('true','false')
            values[f[1]]['methods'].append(dict(name=f[2],descriptor=f[3],flags=int(f[4]),hasCode=f[5]=='true',codeLength=int(f[6])))
    result_rows = []
    for row in rows:
        key = row['physicalKey']
        if key in HELD:
            result_rows.append({**row,'structureStatus':'HOLD_GRAPH9_BINARY_NOT_PARSED','structure':None})
        else:
            value = values[key]
            assert len(value['methods']) == value.pop('expectedMethods')
            assert len(value['methods']) == len({(m['name'],m['descriptor']) for m in value['methods']})
            result_rows.append({**row,'structureStatus':classification(value,key),'structure':value})
    assert set(values) | set(held) == {r['physicalKey'] for r in rows} and set(held) == HELD
    assert data.sha(helper.read_bytes()) == helper_sha
    assert all(data.sha(Path(j['path']).read_bytes()) == j['sha256'] for j in normal['jars'].values())
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'class-structures.json',result_rows)
    result = dict(actualExit=0,source=SOURCE,normalManifestSha256=NORMAL_SHA,gapManifestSha256=GAP_SHA,
        invocation=invocation,helperSha256=helper_sha,stages=stages,physicalClasses=1843,parsedClasses=len(values),heldClasses=sorted(held),
        structureCounts=dict(Counter(r['structureStatus'] for r in result_rows)),
        classStructuresSha256=data.sha((OUT/'class-structures.json').read_bytes()),
        targetClasspathContainsProduct=False,targetDefinedOrInitialized=False,productTestsExecuted=0,
        newExclusionSettings=False,newAccepted=0,formalUpdated=False,currentCoverageComputed=False,
        historicalSuccessTransferred=False,wholeG01Accepted=False,whole451Accepted=False,effortPercent=None)
    data.write(OUT/'manifest.json',result)
    print(json.dumps(dict(actualExit=0,parsed=len(values),held=len(held),manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
