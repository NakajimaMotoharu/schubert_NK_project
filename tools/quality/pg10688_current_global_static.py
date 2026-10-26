"""One exact-source full Java PMD/Checkstyle measurement; no Product or Test execution."""
from collections import Counter
import json
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as runner

SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg10688-current-global-static-v1'
OUT = data.BASE/'PG10688-current-global-static-v1'
SOURCE = '370fd74f6f170a18bc1bf959aa9fceced0def15a'
JAVA_SOURCE = r'src/schubert-nk-(api|web|batch|bootstrap|protocol|storage)/src/(main|test)/java/(?:[A-Za-z_$][A-Za-z0-9_$]*/)*(?:[A-Za-z_$][A-Za-z0-9_$]*|package-info)\.java'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    normal_path = data.BASE/'PG10632-query-semantic-constant-compile-v1/manifest.json'
    normal = data.read_checked(normal_path,'8f29215a400d24a55ecabee90c74fb72a43525b740f129a12ae6053559701f87')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    inputs = {p:h for p,h in normal['begin']['inputHashes'].items() if re.fullmatch(JAVA_SOURCE,p)}
    assert set(inputs) == {p for p in normal['begin']['inputHashes'] if p.startswith('src/schubert-nk-') and '/src/' in p and p.endswith('.java')}
    assert sum(p.endswith('/package-info.java') for p in inputs) == 37
    for path in ('tools/quality/architecture/SnapshotKeyCloseWitness.java','private/x.java','src/schubert-nk-api/src/main/java/X.java.raw'):
        assert not re.fullmatch(JAVA_SOURCE,path)
    assert len(inputs) == 1810 and Counter('MAIN' if '/src/main/' in p else 'TEST' for p in inputs) == {'MAIN':965,'TEST':845}
    snapshot = Path(normal['jars']['api']['path']).parent.parent.parent.parent
    for p,h in inputs.items():
        assert data.sha((data.ROOT/p).read_bytes()) == data.sha((snapshot/p).read_bytes()) == h
    deps = {v['path']:v['sha256'] for v in normal['jars'].values()}
    for module in ('api','web','batch','bootstrap','protocol','storage'):
        cp = snapshot/('src/schubert-nk-'+module+'/target/pgpt-test-classpath.txt')
        for value in cp.read_text().strip().split(os.pathsep):
            if '/dev/codex/schubert/' in value or Path(value).is_relative_to(snapshot/'src'):
                continue
            path = Path(value)
            assert path.is_relative_to(runner.TC/'m2/repository') and path.is_file() and not path.is_symlink()
            digest = data.sha(path.read_bytes())
            assert str(path) not in deps or deps[str(path)] == digest
            deps[str(path)] = digest
    assert len(deps) > 6 and all(data.sha(Path(p).read_bytes()) == h for p,h in deps.items())
    static = runner.TC/'static-gates-20261015'
    rules = data.ROOT/'tools/quality/static'
    pmd = [static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))]
    tools = {str(p):data.sha(p.read_bytes()) for p in [*pmd,static/'checkstyle-14.3.0-all.jar',rules/'pmd.xml',rules/'checkstyle.xml']}
    os.umask(0o077)
    SLOT.mkdir()
    runner.SLOT = SLOT
    listing = SLOT/'source-list.txt'
    with listing.open('x') as stream:
        stream.write(''.join(str(data.ROOT/p)+'\n' for p in sorted(inputs)))
    java = str(runner.TC/'jdk-25.0.4/bin/java')
    results = {}
    results['pmd'] = runner.step('pmd',[java,'-cp',os.pathsep.join(map(str,pmd)),
        'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),
        '--use-version','java-25','--minimum-priority','5','--aux-classpath',os.pathsep.join(deps),
        '--no-cache','--format','xml','--report-file',str(SLOT/'pmd.xml')],SLOT,timeout=1200)
    results['checkstyle'] = runner.step('checkstyle',[java,'-jar',str(static/'checkstyle-14.3.0-all.jar'),
        '-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(SLOT/'checkstyle.xml'),'@'+str(listing)],SLOT,timeout=1200)
    reports = {}
    OUT.mkdir()
    for label,tag in [('pmd','violation'),('checkstyle','error')]:
        raw = (SLOT/(label+'.xml')).read_bytes()
        document = ET.fromstring(raw)
        nodes = [n for n in document.iter() if n.tag.rpartition('}')[2] == tag]
        errors = [n for n in document.iter() if n.tag.rpartition('}')[2] in ('error','configerror')] if label == 'pmd' else []
        reports[label] = dict(findings=len(nodes),processingErrors=len(errors),sha256=data.sha(raw))
        with (OUT/(label+'.xml')).open('xb') as stream:
            stream.write(raw)
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((snapshot/p).read_bytes()) == h for p,h in inputs.items())
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**deps,**tools}.items())
    verify(invocation)
    passed = all(r['actualExit'] == 0 and not r['timedOut'] for r in results.values()) and all(r['findings'] == r['processingErrors'] == 0 for r in reports.values())
    data.write(OUT/'inputs.json',inputs)
    data.write(OUT/'manifest.json',dict(actualExit=0 if passed else 1,measurementCompleted=True,source=SOURCE,
        invocation=invocation,normalManifestSha256=data.sha(normal_path.read_bytes()),sourceCount=len(inputs),mainSourceCount=965,testSourceCount=845,
        inputsSha256=data.sha((OUT/'inputs.json').read_bytes()),snapshot=str(snapshot),sourceListSha256=data.sha(listing.read_bytes()),
        dependencyHashes=deps,toolAndRuleHashes=tools,stages=results,reports=reports,suppressionsAdded=False,rulesChanged=False,
        productTestsExecuted=0,productCodeExecuted=False,coverage=None,externalActions=0,wholeF03Accepted=False,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0 if passed else 1,source=SOURCE,reports=reports,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
