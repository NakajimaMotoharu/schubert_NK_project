"""Before source freeze: explicit value query three-file PMD/Checkstyle diagnostic only, PT0."""
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as runner
from pg13071_monitor_test_inverse import inverse, negative

SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13072-monitor-test-preflight-v1'
OUT = data.BASE/'PG13072-monitor-test-preflight-v1'

def main():
    invocation = capture(__file__); assert not SLOT.exists() and not OUT.exists()
    normal = data.read_checked(data.BASE/'PG13056-time-header-six-compile-v1/manifest.json','fa52be739663760cd603ff1e00bdf963499c75038c6fac9504ab6caa92a007f6')
    h = data.read_checked(data.BASE/'PG13058-time-header-host-v1/manifest.json','535b37b54a8922e4633320f99d95ce69f355c84f70e360ea4ad1352037867a4d')
    assert normal['source'] == h['source'] == '7ced2d7078bf508afcb22dbc8e1d82cc15d56573'
    assert normal['actualExit'] == h['actualExit'] == 0
    original_manifest = data.read_checked(data.BASE/'PG13070-monitor-test-originals-v1/manifest.json','faa795bf1bc06a56b4a926f48fdda20b60e7b8da7d0672439e0ab479628c598f')
    original = data.read_checked(data.BASE/'PG13070-monitor-test-originals-v1/originals.json',original_manifest['originalsSha256'])
    paths = list(original['tests']); inverses = {}; negative_vectors = {}
    assert len(paths) == 10
    assert all(data.sha((data.ROOT/p).read_bytes()) == digest for p,digest in normal['begin']['inputHashes'].items() if p not in paths)
    for path,record in original['tests'].items():
        current = (data.ROOT/path).read_text(); transfer = path.endswith('/TransferHealthMonitorTest.java')
        inverses[path] = inverse(record['text'],current,transfer)
        negative_vectors[path] = negative(record['text'],current,transfer)
    hashes = {p:data.sha((data.ROOT/p).read_bytes()) for p in paths}
    static = runner.TC/'static-gates-20261015'; rules = data.ROOT/'tools/quality/static'
    pmd = [static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))]
    tools = {str(p):data.sha(p.read_bytes()) for p in [*pmd,static/'checkstyle-14.3.0-all.jar',rules/'pmd.xml',rules/'checkstyle.xml']}
    deps = h['begin']['dependencyHashes']
    assert all(data.sha(Path(p).read_bytes()) == digest for p,digest in deps.items())
    SLOT.mkdir(); runner.SLOT = SLOT; listing = SLOT/'source-list.txt'
    with listing.open('x') as f: f.write(''.join(str(data.ROOT/p)+'\n' for p in paths))
    java = str(runner.TC/'jdk-25.0.4/bin/java')
    stages = {}
    stages['pmd'] = runner.step('pmd',[java,'-cp',os.pathsep.join(map(str,pmd)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',os.pathsep.join(deps),'--no-cache','--format','xml','--report-file',str(SLOT/'pmd.xml')],SLOT)
    stages['checkstyle'] = runner.step('checkstyle',[java,'-jar',str(static/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(SLOT/'checkstyle.xml'),'@'+str(listing)],SLOT)
    reports = {}
    for name,tag in [('pmd','violation'),('checkstyle','error')]:
        p = SLOT/(name+'.xml'); root = ET.parse(p).getroot()
        findings = [x for x in root.iter() if x.tag.rpartition('}')[2] == tag]
        errors = [x for x in root.iter() if x.tag.rpartition('}')[2] in ['error','configerror']] if name == 'pmd' else []
        reports[name] = dict(findings=len(findings),processingErrors=len(errors),sha256=data.sha(p.read_bytes()))
    assert all(data.sha((data.ROOT/p).read_bytes()) == digest for p,digest in hashes.items())
    assert all(data.sha(Path(p).read_bytes()) == digest for p,digest in {**tools,**deps}.items())
    passed = all(v['actualExit'] == 0 and not v['timedOut'] for v in stages.values()) and all(v['findings'] == v['processingErrors'] == 0 for v in reports.values())
    verify(invocation); OUT.mkdir()
    for name in reports:
        with (OUT/(name+'.xml')).open('xb') as f: f.write((SLOT/(name+'.xml')).read_bytes())
    data.write(OUT/'manifest.json',dict(actualExit=0 if passed else 1,source=None,baseSource=normal['source'],candidateSourceHashes=hashes,
        invocation=invocation,reports=reports,stages=stages,toolAndRuleHashes=tools,productTestsExecuted=0,originalManifestSha256="faa795bf1bc06a56b4a926f48fdda20b60e7b8da7d0672439e0ab479628c598f",tokenInverses=inverses,negativeVectors=negative_vectors,
        candidatePreflightOnly=True,normalCompilationOrRuntimeQualificationInferred=False,newAccepted=0,externalActions=0))
    print(json.dumps(dict(actualExit=0 if passed else 1,reports=reports,manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))
    raise SystemExit(0 if passed else 1)

if __name__ == '__main__': main()
