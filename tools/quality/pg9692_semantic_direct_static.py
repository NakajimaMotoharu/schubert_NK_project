"""PMD/Checkstyle new Test source; prior same Main type libraries are inputs, not PT results."""
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
import pg9666_pagination_static as stage
from host_tool_invocation import capture, verify

ROOT = data.ROOT
SOURCE = '0002706babad635c5ca7ade76cdbaee134ace432'
BASE = ROOT / 'evidence/01_PT/002_NK-PRO-002/evidence/provisional'
SLOT = ROOT.parent / 'pgpt-runs/PG379/pg9692-semantic-direct-static-v1'
OUT = BASE / 'PG9692-semantic-direct-static-v1'
TEST = 'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/layout/SemanticDirectBoundaryTest.java'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    normal = data.read_checked(data.BASE / 'PG9660-pagination-six-compile-v1/manifest.json',
        'f2ae182bb3a88eff78542ce0c18f3a497263aaabb7ed7fdbea5237a9ab467c2c')
    prior = data.read_checked(BASE / 'PG9662-pagination-boundary-host-v1/manifest.json',
        'c5dfb7e4137c0c96833bcba4a3a3c6ec5cba04a54b3134d13b7395d808cbc19e')
    assert subprocess.check_output(['git','show',SOURCE + ':' + TEST],cwd=ROOT) == (ROOT / TEST).read_bytes()
    delta = subprocess.check_output(['git','diff','--name-only',normal['source'],SOURCE,'--','src'],cwd=ROOT,text=True).splitlines()
    assert delta == [TEST]
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
        stream.write(str(ROOT / TEST) + '\n')
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
        testSource=TEST,testSourceSha256=test_sha,stages=receipts,reports=reports,toolAndRuleHashes=pinned,
        auxiliaryDependencyHashes=deps,auxiliaryWitnessSource=normal['source'],productionMainSourceUnchanged=True,
        oldProductPtResultsTransferred=False,productTestsExecuted=0,newTestIds=0,newAccepted=0,formalUpdated=False,
        wholeF03Accepted=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0 if passed else 1,reports=reports,manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
