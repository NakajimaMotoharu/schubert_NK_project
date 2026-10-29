"""Current three whole Test sources: actual PMD/Checkstyle findings, no Product execution."""
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import snapshot_program_qualification as cfg
from host_tool_invocation import capture, verify
from f03_all_java_auxiliary import normalize
import pg9666_pagination_static as runner

data = cfg.data
OUT = data.BASE/'PG13814-snapshot-program-test-static-v1'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13814-snapshot-program-test-static-v1'

def main():
    invocation = capture(__file__)
    assert not OUT.exists() and not SLOT.exists()
    n,pin = cfg.normal()
    source_hashes = {cfg.TEST_ROOT+name+'.java':sha for name,sha in cfg.PINS.items()}
    assert all(n['begin']['inputHashes'][p] == sha == data.sha((data.ROOT/p).read_bytes()) for p,sha in source_hashes.items())
    jars = [Path(n['jars'][role]['path']) for role in ['api','batch','bootstrap','protocol','storage','web']]
    roots = [p.parent/'test-classes' for p in jars]
    dependencies = []
    for role in n['jars']:
        dependencies.extend((cfg.NORMAL_SLOT/'snapshot'/('src/schubert-nk-'+role+'/target/pgpt-test-classpath.txt')).read_text().strip().split(os.pathsep))
    aux,external,stale,reused = normalize(list(map(str,jars)),list(map(str,roots)),dependencies)
    library_hashes = {str(p):data.sha(p.read_bytes()) for p in [*jars,*map(Path,external)]}
    static = runner.TC/'static-gates-20261015'
    rules = data.ROOT/'tools/quality/static'
    pmd = [static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))]
    tools = {str(p):data.sha(p.read_bytes()) for p in [*pmd,static/'checkstyle-14.3.0-all.jar',rules/'pmd.xml',rules/'checkstyle.xml']}
    SLOT.mkdir();runner.SLOT = SLOT
    listing = SLOT/'source-list.txt'
    with listing.open('x') as stream:
        stream.write(''.join(str(data.ROOT/p)+chr(10) for p in sorted(source_hashes)))
    java = str(runner.TC/'jdk-25.0.4/bin/java')
    stages = {
        'pmd':runner.step('pmd',[java,'-cp',os.pathsep.join(map(str,pmd)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',os.pathsep.join(aux),'--no-cache','--format','xml','--report-file',str(SLOT/'pmd.xml')],SLOT),
        'checkstyle':runner.step('checkstyle',[java,'-jar',str(static/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(SLOT/'checkstyle.xml'),'@'+str(listing)],SLOT),
    }
    findings = []
    for label in stages:
        root = ET.parse(SLOT/(label+'.xml')).getroot()
        assert not [x for x in root.iter() if x.tag.rpartition('}')[2] in ['configerror','processingerror']]
        if label == 'pmd':
            assert not [x for x in root.iter() if x.tag.rpartition('}')[2] == 'error']
        for file in root:
            if file.tag.rpartition('}')[2] != 'file':
                continue
            path = str(Path(file.get('name')).relative_to(data.ROOT));assert path in source_hashes
            for node in file:
                tag = node.tag.rpartition('}')[2]
                assert tag == ('violation' if label == 'pmd' else 'error')
                findings.append(dict(tool=label,path=path,attributes=dict(node.attrib),message=(node.text or '').strip()))
        expected = 4 if label == 'pmd' and any(r['tool'] == label for r in findings) else 0
        assert stages[label]['actualExit'] == expected and not stages[label]['timedOut']
    assert all(data.sha(Path(p).read_bytes()) == sha for p,sha in {**tools,**library_hashes}.items())
    assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in source_hashes.items())
    verify(invocation);OUT.mkdir()
    for label in stages:
        with (OUT/(label+'.xml')).open('xb') as stream:stream.write((SLOT/(label+'.xml')).read_bytes())
    data.write(OUT/'manifest.json',dict(actualExit=0,source=cfg.SOURCE,invocation=invocation,normalManifestSha256=pin,candidateSourceHashes=source_hashes,
        rawStatic=len(findings),rawStaticGateExit=1 if findings else 0,findings=findings,stages=stages,toolHashes=tools,libraryHashes=library_hashes,
        auxiliaryClasspath=aux,replacedStaleProjectDependencies=stale,alreadyFreshDuplicates=reused,reports={label:data.sha((OUT/(label+'.xml')).read_bytes()) for label in stages},
        productTestsExecuted=0,newAccepted=0,whole451Accepted=False,staticMeasurementNotGlobal=True))
    print(dict(manifestSha256=data.sha((OUT/'manifest.json').read_bytes()),rawStatic=len(findings)))

if __name__ == '__main__':main()
