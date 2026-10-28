"""Before source freeze: exact pure Snapshot and new maximum-list Test sources only, Product PT0."""
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as runner
from pg13101_snapshot_oracle_inverse import inverse, negative

SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13102-snapshot-oracle-preflight-v1'
OUT = data.BASE/'PG13102-snapshot-oracle-preflight-v1'

def main():
    invocation = capture(__file__); assert not SLOT.exists() and not OUT.exists()
    normal = data.read_checked(data.BASE/'PG13096-snapshot-max-six-compile-v1/manifest.json','d4de109ab5b3b31ddedc8bd2fd854fe44cbc95f9cbfb95a08f775326cf3ffad1')
    h = data.read_checked(data.BASE/'PG13098-snapshot-max-host-v1/manifest.json','bdc508fa33f1ccb731cd62427bc7b3190a91d4ad28f5d40bf2f31a766b74b27d')
    assert normal['source'] == h['source'] == '0a84859838be8826d58886e6d7f27bd849a9ea05'
    assert normal['actualExit'] == 0 and h['actualExit'] == 1
    assert all(data.sha((data.ROOT/p).read_bytes()) == digest for p,digest in normal['begin']['inputHashes'].items() if not p.endswith('/ScenarioDetailSnapshotBoundaryTest.java'))
    paths = ['src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/persistence/ScenarioDetailSnapshot.java', 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/persistence/ScenarioDetailSnapshotBoundaryTest.java']
    hashes = {p:data.sha((data.ROOT/p).read_bytes()) for p in paths}
    preserved = data.read_checked(data.BASE/'PG13100-snapshot-oracle-originals-v1/manifest.json','4c9db4bb5ddf53982ac6778a801a57a12ec84ce1ce55d37765ec1328f733a861')
    original = data.read_checked(data.BASE/'PG13100-snapshot-oracle-originals-v1/original.json',preserved['originalSha256'])
    current = (data.ROOT/original['test']).read_text()
    changes = inverse(original['text'],current); negative_vectors = negative(original['text'],current)
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
        invocation=invocation,reports=reports,stages=stages,toolAndRuleHashes=tools,productTestsExecuted=0,oracleCorrectionInverse=changes,oracleCorrectionNegativeVectors=negative_vectors,
        candidatePreflightOnly=True,normalCompilationOrRuntimeQualificationInferred=False,newAccepted=0,externalActions=0))
    print(json.dumps(dict(actualExit=0 if passed else 1,reports=reports,manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))
    raise SystemExit(0 if passed else 1)

if __name__ == '__main__': main()
