"""Declared worktree Test-only static preflight using unchanged normal Main type bytes; no Test execution."""
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET

import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as stage

ROOT = data.ROOT
SOURCE = '3d9f1d9fd395e8cb9456b0a540e1f29bcb87876e'
SLOT = ROOT.parent/'pgpt-runs/PG379/pg10394-role-literal-static-v1'
OUT = data.BASE/'PG10394-role-literal-static-v1'
TESTS = sorted(json.loads((data.BASE/'PG10392-role-literal-plan-v1/manifest.json').read_bytes())['sourceChanges'])


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    normal_path = data.BASE/'PG10378-media-literal-six-compile-v1/manifest.json'
    normal = json.loads(normal_path.read_bytes())
    assert normal['source'] == SOURCE and normal['actualExit'] == 0 and normal['testsExecuted'] == 0
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p not in TESTS)
    assert set(TESTS) <= set(normal['begin']['inputHashes'])
    current_hashes = {p:data.sha((ROOT/p).read_bytes()) for p in TESTS}
    assert len(current_hashes) == 13
    snapshot = Path(normal['jars']['api']['path']).parent.parent.parent.parent
    deps = {v['path']:v['sha256'] for v in normal['jars'].values()}
    for module in ('api','web'):
        cp = snapshot/('src/schubert-nk-'+module+'/target/pgpt-test-classpath.txt')
        for text in cp.read_text().strip().split(os.pathsep):
            if '/dev/codex/schubert/' in text or Path(text).is_relative_to(snapshot/'src'):
                continue
            path = Path(text)
            assert path.is_relative_to(stage.TC/'m2/repository') and path.is_file() and not path.is_symlink()
            digest = data.sha(path.read_bytes())
            assert str(path) not in deps or deps[str(path)] == digest
            deps[str(path)] = digest
    assert len(deps) > 6 and all(data.sha(Path(p).read_bytes()) == h for p,h in deps.items())
    static = stage.TC/'static-gates-20261015'
    rules = ROOT/'tools/quality/static'
    pmd = [static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))]
    tools = {str(p):data.sha(p.read_bytes()) for p in [*pmd,static/'checkstyle-14.3.0-all.jar',rules/'pmd.xml',rules/'checkstyle.xml']}
    SLOT.mkdir()
    stage.SLOT = SLOT
    listing = SLOT/'source-list.txt'
    with listing.open('x') as stream:
        stream.write(''.join(str(ROOT/p)+'\n' for p in TESTS))
    java = str(stage.TC/'jdk-25.0.4/bin/java')
    results = {}
    results['pmd'] = stage.step('pmd',[java,'-cp',os.pathsep.join(map(str,pmd)),
        'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),
        '--use-version','java-25','--minimum-priority','5','--aux-classpath',os.pathsep.join(deps),
        '--no-cache','--format','xml','--report-file',str(SLOT/'pmd.xml')],SLOT)
    results['checkstyle'] = stage.step('checkstyle',[java,'-jar',str(static/'checkstyle-14.3.0-all.jar'),
        '-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(SLOT/'checkstyle.xml'),'@'+str(listing)],SLOT)
    reports = {}
    OUT.mkdir()
    for label,tag in [('pmd','violation'),('checkstyle','error')]:
        path = SLOT/(label+'.xml')
        document = ET.parse(path).getroot()
        nodes = [n for n in document.iter() if n.tag.rpartition('}')[2] == tag]
        errors = [n for n in document.iter() if n.tag.rpartition('}')[2] in ('error','configerror')] if label == 'pmd' else []
        reports[label] = dict(findings=len(nodes),processingErrors=len(errors),sha256=data.sha(path.read_bytes()),
            details=[dict(n.attrib,message=' '.join(''.join(n.itertext()).split())) for n in nodes])
        with (OUT/(label+'.xml')).open('xb') as stream:
            stream.write(path.read_bytes())
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**deps,**tools}.items())
    verify(invocation)
    passed = all(r['actualExit'] == 0 and not r['timedOut'] for r in results.values()) and all(r['findings'] == r['processingErrors'] == 0 for r in reports.values())
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in current_hashes.items())
    result = dict(actualExit=0 if passed else 1,source=None,baseSource=SOURCE,qualification='DECLARED_WORKTREE_HASHES_STATIC_ONLY',
        unchangedNormalMainTypesUsed=True,normalTypeSource=SOURCE,invocation=invocation,normalManifestSha256=data.sha(normal_path.read_bytes()),
        sourceHashes=current_hashes,toolAndRuleHashes=tools,dependencyHashes=deps,
        stages=results,reports=reports,productTestsExecuted=0,externalActions=0,suppressionsAdded=False,
        wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    data.write(OUT/'manifest.json',result)
    print(json.dumps(dict(actualExit=result['actualExit'],reports={k:{f:v[f] for f in ('findings','processingErrors')} for k,v in reports.items()},
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))
    raise SystemExit(result['actualExit'])


if __name__ == '__main__':
    main()
