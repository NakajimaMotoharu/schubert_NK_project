"""Disclose all four default-filtered switch-map raw probes; this never fills missing coverage."""
import json
import os
from pathlib import Path
import g07_host_class_provenance_inputs as data
import pg9346_direct_companion_jdk_post as steps
from host_tool_invocation import capture, verify

ROOT = data.ROOT
BASE = ROOT / 'evidence/01_PT/002_NK-PRO-002/evidence/provisional'
WORK = ROOT.parent / 'pgpt-runs/PG379'
SLOT = WORK / 'pg9726-protocol-generated-shape-post-v1'
OUT = BASE / 'PG9726-protocol-generated-shape-post-v1'
SOURCE = 'fd3d04df5710ca28f0e34f919cbc103e569a607b'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    post = data.read_checked(BASE / 'PG9724-protocol-module-post-v2/manifest.json',
        '5eb3672c1838e6ef522e57f724392e946c437b0499967f7623d889504227cd77')
    assert post['actualExit'] == 0 and post['source'] == SOURCE and post['wholeModuleFour100']
    detail = data.read_checked(BASE / 'PG9724-protocol-module-post-v2/whole-module-counters.json',post['moduleCounterDetailsSha256'])
    remaining = {n for n,v in detail['physicalClasses'].items() if n not in post['structuralNoCodeClasses'] and all(c['missed'] + c['covered'] == 0 for c in v['counters'].values())}
    assert len(remaining) == 4
    normal = data.read_checked(data.BASE / 'PG9694-semantic-direct-fixed-six-compile-v1/manifest.json',
        '7d2e18f86d2bc9e5c61473da8b8924aa7c6668bf8903541d5502902d2dac1d7a')
    jar = Path(normal['jars']['protocol']['path'])
    run_exec = WORK / 'pg9722-protocol-module-host-v1/jacoco.exec'
    assert data.sha(jar.read_bytes()) == normal['jars']['protocol']['sha256'] and data.sha(run_exec.read_bytes()) == post['execSha256']
    helper = ROOT / 'tools/quality/architecture/ProtocolGeneratedShapeMeasure.java'
    helper_sha = data.sha(helper.read_bytes())
    tc = ROOT.parent / 'toolchain'
    libraries = [tc / 'm2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',
        *[tc / f'm2/repository/org/ow2/asm/{n}/9.10.1/{n}-9.10.1.jar' for n in ('asm','asm-tree','asm-commons')]]
    deps = {str(p):data.sha(p.read_bytes()) for p in libraries}
    cp = os.pathsep.join(map(str,libraries))
    os.umask(0o077)
    SLOT.mkdir()
    reader = SLOT / 'reader'
    reader.mkdir()
    steps.SLOT = SLOT
    stages = [steps.step('compile-reader',[str(tc / 'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(reader),str(helper)])]
    assert stages[0]['actualExit'] == 0 and not stages[0]['timedOut']
    stages.append(steps.step('read-current-generated-shapes',[str(tc / 'jdk-25.0.4/bin/java'),'-cp',str(reader) + os.pathsep + cp,helper.stem,str(run_exec),str(jar)]))
    assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut']
    rows = {}
    for line in (SLOT / 'read-current-generated-shapes.stdout').read_text().splitlines():
        label,name,crc,fields,hit,missed = line.split('\t')
        assert label == 'GENERATED' and name in remaining and name not in rows
        assert crc == detail['physicalClasses'][name]['crc64']
        rows[name] = dict(crc64=crc,syntheticSwitchMapFields=int(fields),rawHitProbes=int(hit),rawMissedProbes=int(missed),
            jacocoCountersAllZero=True,physicalClassSha256=post['physicalClassHashes'][name],notCountedAsIndividuallyFour100=True)
    assert set(rows) == remaining
    assert data.sha(helper.read_bytes()) == helper_sha and all(data.sha(Path(p).read_bytes()) == h for p,h in deps.items())
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,classes=rows,reportStages=stages,
        reportHelperSha256=helper_sha,libraryHashes=deps,rawJacocoFour100=True,physicalInventory=176,
        coverageApplicableExecutableClasses=159,standardFilteredCompilerHelpers=4,structuralNonExecutableClasses=13,
        strictGeneratedInstructionCoverageQualified=False,allGeneratedInstructionProbesCovered=all(r['rawMissedProbes'] == 0 for r in rows.values()),
        exclusionsAdded=False,sourceChanged=False,productTestsExecuted=0,newTestIds=0,newAccepted=0,
        formalUpdated=False,whole451Accepted=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,classes=rows,strictGeneratedInstructionCoverageQualified=False,
        manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
