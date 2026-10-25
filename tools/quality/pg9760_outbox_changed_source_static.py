"""Current changed API Main and new Test PMD/Checkstyle, no product execution."""
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
import pg9666_pagination_static as stage
from host_tool_invocation import capture, verify

ROOT = data.ROOT
SOURCE = 'e598a81bb4200b4e4930278b31479ff927aa025f'
BASE = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
SLOT = ROOT.parent / 'pgpt-runs/PG379/pg9760-outbox-changed-source-static-v1'
OUT = BASE / 'PG9760-outbox-changed-source-static-v1'
TEST = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxDispatchReportBoundaryTest.java'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    normal = data.read_checked(data.BASE / 'PG9750-outbox-report-six-compile-v1/manifest.json',
        '7b1c2b2e67dab622cc3e905e1c04ac5819a587f90992c404cf6cab3f0ceebb96')
    prior = data.read_checked(data.BASE / 'PG9754-outbox-value-host-v2/manifest.json',
        'affbf2ef4c901e34206b99fa6610cf839c6c89037d7c4e6bc7b4e0a22ddc91e4')
    assert normal['actualExit'] == prior['actualExit'] == 0 and normal['source'] == prior['source'] == SOURCE
    main_path = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxDispatchReport.java'
    changed = {main_path,TEST}
    assert all(subprocess.check_output(['git','show',SOURCE + ':' + path],cwd=ROOT) == (ROOT / path).read_bytes() for path in changed)
    delta = subprocess.check_output(['git','diff','--name-only','fd3d04df5710ca28f0e34f919cbc103e569a607b',SOURCE,'--','src'],cwd=ROOT,text=True).splitlines()
    assert set(delta) == changed and len(delta) == 2
    assert all(data.sha((ROOT / p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    deps = prior['begin']['dependencyHashes']
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in deps.items())
    test_sha = data.sha((ROOT / TEST).read_bytes())
    tc = ROOT.parent / 'toolchain'
    static = tc / 'static-gates-20261015'
    rules = ROOT / 'tools/quality/static'
    pmd = [static / 'record-fix-v1/pmd-record-1298.jar',*sorted((static / 'pmd-bin-7.28.0/lib').glob('*.jar'))]
    pinned = {str(p):data.sha(p.read_bytes()) for p in [*pmd,static / 'checkstyle-14.3.0-all.jar',rules / 'pmd.xml',rules / 'checkstyle.xml']}
    os.umask(0o077)
    SLOT.mkdir()
    stage.SLOT = SLOT
    listing = SLOT / 'source-list.txt'
    with listing.open('x') as stream:
        stream.write(''.join(str(ROOT / p) + '\n' for p in sorted(changed)))
    jdk = tc / 'jdk-25.0.4/bin'
    receipts = {}
    receipts['pmd'] = stage.step('pmd',[str(jdk / 'java'),'-cp',os.pathsep.join(map(str,pmd)),
        'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules / 'pmd.xml'),
        '--use-version','java-25','--minimum-priority','5','--aux-classpath',os.pathsep.join(deps),
        '--no-cache','--format','xml','--report-file',str(SLOT / 'pmd.xml')],SLOT)
    receipts['checkstyle'] = stage.step('checkstyle',[str(jdk / 'java'),'-jar',str(static / 'checkstyle-14.3.0-all.jar'),
        '-c',str(rules / 'checkstyle.xml'),'-f','xml','-o',str(SLOT / 'checkstyle.xml'),'@' + str(listing)],SLOT)
    reports = {}
    for label,tag in [('pmd','violation'),('checkstyle','error')]:
        path = SLOT / (label + '.xml')
        root = ET.parse(path).getroot()
        nodes = [n for n in root.iter() if n.tag.rpartition('}')[2] == tag]
        errors = [n for n in root.iter() if n.tag.rpartition('}')[2] in ('error','configerror')] if label == 'pmd' else []
        reports[label] = dict(findings=len(nodes),processingErrors=len(errors),sha256=data.sha(path.read_bytes()),
            details=[dict(n.attrib,message=' '.join(''.join(n.itertext()).split())) for n in nodes])
    passed = all(s['actualExit'] == 0 and not s['timedOut'] for s in receipts.values()) and all(r['findings'] == r['processingErrors'] == 0 for r in reports.values())
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**pinned,**deps}.items())
    assert data.sha((ROOT / TEST).read_bytes()) == test_sha
    verify(invocation)
    OUT.mkdir()
    for label in reports:
        with (OUT / (label + '.xml')).open('xb') as stream:
            stream.write((SLOT / (label + '.xml')).read_bytes())
    data.write(OUT / 'manifest.json',dict(actualExit=0 if passed else 1,source=SOURCE,invocation=invocation,
        testSource=TEST,testSourceSha256=test_sha,changedSourceHashes={p:data.sha((ROOT / p).read_bytes()) for p in changed},stages=receipts,reports=reports,toolAndRuleHashes=pinned,
        auxiliaryDependencyHashes=deps,auxiliaryWitnessSource=normal['source'],productionMainSourceUnchanged=False,
        oldProductPtResultsTransferred=False,productTestsExecuted=0,newTestIds=0,newAccepted=0,formalUpdated=False,
        wholeF03Accepted=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0 if passed else 1,reports=reports,manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
