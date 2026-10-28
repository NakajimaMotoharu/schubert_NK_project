"""Current two whole-Test static scope; reuse immutable same-source six-SB evidence explicitly."""
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as runner

SOURCE='0124b5938a50f4ceea542486c336ba12146cb1b4'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg12840-exact-registry-caller-static-v1'
OUT=data.BASE/'PG12840-exact-registry-caller-static-v1'


def main():
    invocation=capture(__file__);assert not SLOT.exists() and not OUT.exists()
    normal=data.read_checked(data.BASE/'PG12819-exact-registry-six-compile-v2/manifest.json','8a5081b03b988d4370df0c3fa45c69eeeda6d5296543a38f1e2239b0ae088f89')
    host=data.read_checked(data.BASE/'PG12839-exact-registry-caller-host-v2/manifest.json','70426a057be6c8f8b53e7b52ea98f2a3e2e9269039864c73da0d6a81ad562291')
    plan=data.read_checked(data.BASE/'PG12837-exact-registry-caller-plan-v1/manifest.json','b7dddb9dfdce042bc9076a45d0983f29f22a00777e8d3882c915034458bb3a01')
    prior=data.read_checked(data.BASE/'PG12820-exact-registry-static-v1/manifest.json','90c12edb90d3380de96ab28d71ac28d3445500890a49627be852eee106dd136b')
    assert normal['source']==host['source']==plan['source']==prior['source']==SOURCE
    assert normal['actualExit']==normal['testsExecuted']==host['actualExit']==0 and prior['actualExit']==1 and host['observedTestExecutions']==19
    assert prior['normalManifestSha256']==host['begin']['normalManifestSha256']=='8a5081b03b988d4370df0c3fa45c69eeeda6d5296543a38f1e2239b0ae088f89'
    assert prior['spotbugsSixExit']==prior['stages']['spotbugs-six']['actualExit']==0 and not prior['stages']['spotbugs-six']['timedOut']
    assert host['begin']['normalSnapshot']==str(Path(normal['jars']['api']['path']).parent.parent.parent.parent)
    hashes=normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/path).read_bytes())==digest for path,digest in hashes.items())
    assert all(data.sha(Path(path).read_bytes())==digest for path,digest in {**prior['dependencyHashes'],**prior['toolAndRuleHashes'],**host['begin']['physicalTestFiles']}.items())
    # SB analyzed target/classes in this exact immutable normal snapshot; compare all six to jars.
    import zipfile
    for value in normal['jars'].values():
        jarpath=Path(value['path']);classes=jarpath.parent/'classes'
        with zipfile.ZipFile(jarpath) as jar:
            names=[name for name in jar.namelist() if name.endswith('.class')]
            assert {str(path.relative_to(classes)) for path in classes.rglob('*.class')}==set(names)
            assert all((classes/name).read_bytes()==jar.read(name) for name in names)
    sources={**plan['wholeTestSourceHashes'],**{p:h for p,h in plan['eligibilityClosureSourceHashes'].items() if p.endswith('/ExactDurationMeterRegistry.java')}};assert len(sources)==3
    static=runner.TC/'static-gates-20261015';rules=data.ROOT/'tools/quality/static'
    pmd=[static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))]
    tools={str(path):data.sha(path.read_bytes()) for path in [*pmd,static/'checkstyle-14.3.0-all.jar',rules/'pmd.xml',rules/'checkstyle.xml']}
    assert tools==prior['toolAndRuleHashes']
    SLOT.mkdir();runner.SLOT=SLOT;listing=SLOT/'source-list.txt'
    with listing.open('x') as stream:
        stream.write(''.join(str(data.ROOT/path)+'\n' for path in sorted(sources)))
    java=str(runner.TC/'jdk-25.0.4/bin/java');deps=host['begin']['dependencyHashes'];stages={}
    stages['pmd']=runner.step('pmd',[java,'-cp',os.pathsep.join(map(str,pmd)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',os.pathsep.join(deps),'--no-cache','--format','xml','--report-file',str(SLOT/'pmd.xml')],SLOT)
    stages['checkstyle']=runner.step('checkstyle',[java,'-jar',str(static/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(SLOT/'checkstyle.xml'),'@'+str(listing)],SLOT)
    reports={};OUT.mkdir()
    for label,tag in [('pmd','violation'),('checkstyle','error')]:
        content=(SLOT/(label+'.xml')).read_bytes();root=ET.fromstring(content)
        findings=[node for node in root.iter() if node.tag.rpartition('}')[2]==tag]
        errors=[node for node in root.iter() if node.tag.rpartition('}')[2] in ['error','configerror']] if label=='pmd' else []
        reports[label]=dict(findings=len(findings),processingErrors=len(errors),sha256=data.sha(content))
        with (OUT/(label+'.xml')).open('xb') as stream:
            stream.write(content)
    assert all(data.sha((data.ROOT/path).read_bytes())==digest for path,digest in sources.items())
    verify(invocation)
    passed=all(row['actualExit']==0 and not row['timedOut'] for row in stages.values()) and all(row['findings']==row['processingErrors']==0 for row in reports.values())
    value=dict(actualExit=0 if passed else 1,source=SOURCE,invocation=invocation,sourceHashes=sources,normalManifestSha256='8a5081b03b988d4370df0c3fa45c69eeeda6d5296543a38f1e2239b0ae088f89',hostManifestSha256='70426a057be6c8f8b53e7b52ea98f2a3e2e9269039864c73da0d6a81ad562291',dependencyHashes=deps,toolAndRuleHashes=tools,stages=stages,reports=reports,spotbugsSixExit=0,spotbugsSixExecutedByThisStage=False,reusedSameSourceSpotbugsManifestSha256='90c12edb90d3380de96ab28d71ac28d3445500890a49627be852eee106dd136b',allSixTargetClassesMatchImmutableNormalJars=True,normalRecompiled=False,oldExecUnion=False,productTestsExecuted=0,newAccepted=0,coverage=None,wholeF03Accepted=False)
    data.write(OUT/'manifest.json',value)
    print(dict(actualExit=value['actualExit'],reports=reports,spotbugsSixReused=True,manifestSha256=data.sha((OUT/'manifest.json').read_bytes())))
    raise SystemExit(value['actualExit'])


if __name__=='__main__':
    main()
