"""Three import-only Test source static checks; unchanged Main type bytes, no Graph PT."""
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as runner
from pg10694_graph_import_only_plan import TESTS

SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg10700-graph-import-static-v1'
OUT = data.BASE/'PG10700-graph-import-static-v1'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    normal_path = data.BASE/'PG10698-graph-import-six-compile-v1/manifest.json'
    normal = json.loads(normal_path.read_bytes())
    assert normal['source'] == '0a7ff657115228d6cdde3820b5f2ae36ac7f3186' and normal['actualExit'] == normal['testsExecuted'] == 0
    previous_path = data.BASE/'PG10688-current-global-static-v1/manifest.json'
    previous = data.read_checked(previous_path,'d91104d420967cd34c0d313919b86c7f1745577a1e1fe31d9343927d53dfe636')
    previous_inputs = data.read_checked(previous_path.parent/'inputs.json',previous['inputsSha256'])
    assert all(normal['begin']['inputHashes'][p] == h for p,h in previous_inputs.items() if p not in TESTS)
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    deps,tools = previous['dependencyHashes'],previous['toolAndRuleHashes']
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**deps,**tools}.items())
    static = runner.TC/'static-gates-20261015'
    rules = data.ROOT/'tools/quality/static'
    pmd = [static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))]
    SLOT.mkdir()
    runner.SLOT = SLOT
    listing = SLOT/'source-list.txt'
    with listing.open('x') as stream:
        stream.write(''.join(str(data.ROOT/p)+'\n' for p in TESTS))
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
    assert all(data.sha((data.ROOT/p).read_bytes()) == normal['begin']['inputHashes'][p] for p in TESTS)
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**deps,**tools}.items())
    verify(invocation)
    passed = all(r['actualExit'] == 0 and not r['timedOut'] for r in results.values()) and all(r['findings'] == r['processingErrors'] == 0 for r in reports.values())
    data.write(OUT/'manifest.json',dict(actualExit=0 if passed else 1,source=normal['source'],invocation=invocation,
        sourceHashes={p:normal['begin']['inputHashes'][p] for p in TESTS},normalManifestSha256=data.sha(normal_path.read_bytes()),
        unchangedMainTypeSource=previous['source'],previousGlobalManifestSha256=data.sha(previous_path.read_bytes()),
        dependencyHashes=deps,toolAndRuleHashes=tools,stages=results,reports=reports,productTestsExecuted=0,
        graphNineDynamicHoldMaintained=True,coverage=None,externalActions=0,wholeF03Accepted=False,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0 if passed else 1,reports=reports,manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
