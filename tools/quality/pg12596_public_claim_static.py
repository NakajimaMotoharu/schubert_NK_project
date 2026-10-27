"""Current three public claim codec Tests PMD/Checkstyle only, no product run."""
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as runner
from frozen_selected_scope import derive_facts

NORMAL_SHA='11866f6596012549a85e43d0ff9a0b9577f446dccb00ff9ecaeadce127d1e305'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg12596-public-claim-static-v1'
OUT = data.BASE/'PG12596-public-claim-static-v1'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    normal_path = data.BASE/'PG12592-public-claim-six-compile-v1/manifest.json'
    normal = data.read_checked(normal_path,NORMAL_SHA)
    previous = data.read_checked(data.BASE/'PG12572-public-unit-six-compile-v1/manifest.json',
        'fe361f6c8fb14008feb760c5b0437f7fc68777a776eb39ca7febc8ec49a27c1a')
    assert normal['source'] == '4749755f2562bd4e51658d8083a61e210ad2c521' and normal['actualExit'] == normal['testsExecuted'] == 0
    assert all(previous['begin']['inputHashes'][p] == h for p,h in normal['begin']['inputHashes'].items() if '/src/main/' in p)
    plan=data.read_checked(data.BASE/'PG12590-public-claim-plan-v1/manifest.json','b2f729a14961d7d0ae65185840764c973ce71fb6ca9b60ee8825abb3fda2a224')
    facts=derive_facts(plan,normal,normal['source']);sources=facts['sources']
    assert set(sources)=={r['path'] for r in plan['sourceChanges']} and facts['modules']==['batch']
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    prepared = data.read_checked(data.BASE/'PG12594-public-claim-host-v1/manifest.json','a0f33528034e6296fa92ff228744a96d039139341a060710adf01ec18c260d00')
    assert prepared['observedTestExecutions']==prepared['begin']['expectedMethods']==20
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
