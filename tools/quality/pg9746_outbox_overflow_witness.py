"""One fixed pre-fix pure constructor witness; preserve expected actual failure, no external IO."""
import json
import os
from pathlib import Path
import g07_host_class_provenance_inputs as data
import pg9346_direct_companion_jdk_post as steps
from host_tool_invocation import capture, verify

ROOT = data.ROOT
SOURCE = 'fd3d04df5710ca28f0e34f919cbc103e569a607b'
SLOT = ROOT.parent / 'pgpt-runs/PG379/pg9746-outbox-overflow-witness-v1'
OUT = data.BASE / 'PG9746-outbox-overflow-witness-v1'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    normal = data.read_checked(data.BASE / 'PG9694-semantic-direct-fixed-six-compile-v1/manifest.json',
        '7d2e18f86d2bc9e5c61473da8b8924aa7c6668bf8903541d5502902d2dac1d7a')
    assert normal['actualExit'] == 0 and normal['source'] == SOURCE
    jar = Path(normal['jars']['api']['path'])
    assert data.sha(jar.read_bytes()) == normal['jars']['api']['sha256']
    helper = ROOT / 'tools/quality/architecture/OutboxReportOverflowWitness.java'
    helper_sha = data.sha(helper.read_bytes())
    tc = ROOT.parent / 'toolchain'
    os.umask(0o077)
    SLOT.mkdir()
    reader = SLOT / 'reader'
    reader.mkdir()
    steps.SLOT = SLOT
    stages = [steps.step('compile-witness',[str(tc / 'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',str(jar),'-d',str(reader),str(helper)])]
    assert stages[0]['actualExit'] == 0
    stages.append(steps.step('old-artifact-fixed-overflow',[str(tc / 'jdk-25.0.4/bin/java'),'-cp',str(reader) + os.pathsep + str(jar),helper.stem]))
    code = stages[-1]['actualExit']
    assert not any(s['timedOut'] for s in stages)
    reproduced = code == 1 and (SLOT / 'old-artifact-fixed-overflow.stdout').read_text().strip() == 'inconsistentCountRejected=false;mathematicalSum=4294967296;claimed=0'
    assert data.sha(helper.read_bytes()) == helper_sha and data.sha(jar.read_bytes()) == normal['jars']['api']['sha256']
    verify(invocation)
    OUT.mkdir()
    for name in ('old-artifact-fixed-overflow.stdout','old-artifact-fixed-overflow.stderr'):
        with (OUT / name).open('xb') as stream:
            stream.write((SLOT / name).read_bytes())
    value = dict(actualExit=code,expectedPreFixWitnessExit=1,defectReproduced=reproduced,source=SOURCE,
        normalManifestSha256='7d2e18f86d2bc9e5c61473da8b8924aa7c6668bf8903541d5502902d2dac1d7a',
        invocation=invocation,stages=stages,helperSha256=helper_sha,jarPath=str(jar),jarSha256=normal['jars']['api']['sha256'],
        bug='BUG-1760',productPtPassCount=0,externalActions=0,newAccepted=0,formalUpdated=False)
    data.write(OUT / 'manifest.json',value)
    print(json.dumps(dict(actualExit=code,defectReproduced=reproduced,manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))
    assert reproduced
    raise SystemExit(code)


if __name__ == '__main__':
    main()
