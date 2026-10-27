"""Current four supplied-pool/capacity Tests PMD/Checkstyle only, no product run."""
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as runner
from frozen_selected_scope import derive_facts

NORMAL_SHA='5b954538ef967b5ced149c9f0b4f3b11a15e88676e07c2ea56c22215e9a1e0b0'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg12356-pool-capacity-static-v1'
OUT = data.BASE/'PG12356-pool-capacity-static-v1'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    normal_path = data.BASE/'PG12352-pool-capacity-six-compile-v1/manifest.json'
    normal = data.read_checked(normal_path,NORMAL_SHA)
    previous = data.read_checked(data.BASE/'PG10736-protocol-uppercase-six-compile-v1/manifest.json',
        '5bfb5e23af7295e2d163f7b8de21d2290c14ffb6eba8339e654ff4c56ae86492')
    assert normal['source'] == 'e2a04c5d5775b8629ce3c4f17259d8378b2bb5f9' and normal['actualExit'] == normal['testsExecuted'] == 0
    assert all(previous['begin']['inputHashes'][p] == h for p,h in normal['begin']['inputHashes'].items() if '/src/main/' in p)
    plan=data.read_checked(data.BASE/'PG12348-pool-capacity-plan-v1/manifest.json','c9358f2f5f8478dd2d16004c2231c9ca558f3a219505aed28232b1096842b4e1')
    facts=derive_facts(plan,normal,normal['source']);sources=facts['sources']
    assert set(sources)==set(['src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/DbPoolMetricObservationTest.java', 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/WebDbPoolMetricObservationTest.java', 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/OperationMismatchMetricRecorderTest.java', 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/storage/TransferCapacityTest.java']) and facts['modules']==['api','web']
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    prepared = data.read_checked(data.BASE/'PG12354-pool-capacity-host-v1/manifest.json','4ff7ea2da45aeae1e1e91d69c8f9b30cd5f943905b126231426908398ac706aa')
    assert prepared['observedTestExecutions']==prepared['begin']['expectedMethods']==29
    assert all(r['actualExit']==0 and not r['timedOut'] for r in prepared['stages'])
    assert prepared['actualExit'] == 0 and prepared['source'] == normal['source']
    deps = prepared['begin']['dependencyHashes']
    static = runner.TC/'static-gates-20261015'
    rules = data.ROOT/'tools/quality/static'
    pmd = [static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))]
    tools = {str(p):data.sha(p.read_bytes()) for p in [*pmd,static/'checkstyle-14.3.0-all.jar',rules/'pmd.xml',rules/'checkstyle.xml']}
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**deps,**tools}.items())
    SLOT.mkdir()
    runner.SLOT = SLOT
    listing = SLOT/'source-list.txt'
    with listing.open('x') as stream:
        stream.write(''.join(str(data.ROOT/p)+'\n' for p in sorted(sources)))
    java = str(runner.TC/'jdk-25.0.4/bin/java')
    results = {}
    results['pmd'] = runner.step('pmd',[java,'-cp',os.pathsep.join(map(str,pmd)),
        'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),
        '--use-version','java-25','--minimum-priority','5','--aux-classpath',os.pathsep.join(deps),
        '--no-cache','--format','xml','--report-file',str(SLOT/'pmd.xml')],SLOT)
    results['checkstyle'] = runner.step('checkstyle',[java,'-jar',str(static/'checkstyle-14.3.0-all.jar'),
        '-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(SLOT/'checkstyle.xml'),'@'+str(listing)],SLOT)
    reports = {}
    OUT.mkdir()
    for label,tag in [('pmd','violation'),('checkstyle','error')]:
        raw = (SLOT/(label+'.xml')).read_bytes()
        root = ET.fromstring(raw)
        nodes = [n for n in root.iter() if n.tag.rpartition('}')[2] == tag]
        errors = [n for n in root.iter() if n.tag.rpartition('}')[2] in ('error','configerror')] if label == 'pmd' else []
        reports[label] = dict(findings=len(nodes),processingErrors=len(errors),sha256=data.sha(raw))
        with (OUT/(label+'.xml')).open('xb') as stream:
            stream.write(raw)
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**deps,**tools}.items())
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in sources.items())
    verify(invocation)
    passed = all(r['actualExit'] == 0 and not r['timedOut'] for r in results.values()) and all(r['findings'] == r['processingErrors'] == 0 for r in reports.values())
    data.write(OUT/'manifest.json',dict(actualExit=0 if passed else 1,source=normal['source'],invocation=invocation,
        sourceHashes=sources,normalManifestSha256=data.sha(normal_path.read_bytes()),
        dependencyHashes=deps,toolAndRuleHashes=tools,stages=results,reports=reports,productTestsExecuted=0,
        suppressionsAdded=False,coverage=None,externalActions=0,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(__import__('json').dumps(dict(actualExit=0 if passed else 1,reports=reports,manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
