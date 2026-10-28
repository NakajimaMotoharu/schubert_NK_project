"""One appended pure numeric method; preserve original five and unchanged NFC whole three."""
import os
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg13152_nfc_golden_preflight import MAINS, OLD, NEW
from pg13171_numeric_ceiling_inverse import inverse, negatives, numeric_fixture
import pg9666_pagination_static as runner

SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13172-numeric-ceiling-preflight-v1'
OUT = data.BASE/'PG13172-numeric-ceiling-preflight-v1'

def main():
    invocation = capture(__file__);assert not SLOT.exists() and not OUT.exists()
    n = data.read_checked(data.BASE/'PG13156-nfc-golden-six-compile-v1/manifest.json','4c1f5352b5d048cda761851d3482fd74983b3ec885ed839d91f987bca60be0d9')
    assert n['source'] == 'b11fe71bd20e244dd10c83bd339f8345a0c1f085' and n['actualExit'] == n['testsExecuted'] == 0
    assert {p for p,sha in n['begin']['inputHashes'].items() if data.sha((data.ROOT/p).read_bytes()) != sha} == {OLD}
    original = subprocess.check_output(['git','show',n['source']+':'+OLD],cwd=data.ROOT)
    assert data.sha(original) == n['begin']['inputHashes'][OLD]
    current = (data.ROOT/OLD).read_text();changes = inverse(original.decode(),current);vectors = negatives(original.decode(),current);fixtures = numeric_fixture()
    paths = [*MAINS,OLD,NEW];hashes = {p:data.sha((data.ROOT/p).read_bytes()) for p in paths}
    assert len(re.findall(r'@Test\s+void\s+(\w+)\s*\(',current)) == current.count('@Test') == 6
    assert (data.ROOT/NEW).read_text().count('@Test') == 3
    assert not any(x in current for x in ['@Before','@After','@ExtendWith','@Disabled','@TempDir','java.net.','java.sql.','java.nio.file','ProcessBuilder','System.getenv','Class.forName','setAccessible'])
    static = runner.TC/'static-gates-20261015';rules = data.ROOT/'tools/quality/static'
    pmd = [static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))]
    tools = {str(p):data.sha(p.read_bytes()) for p in [*pmd,static/'checkstyle-14.3.0-all.jar',rules/'pmd.xml',rules/'checkstyle.xml']}
    snapshot = Path(n['jars']['protocol']['path']).parents[3];cp = (snapshot/'src/schubert-nk-protocol/target/pgpt-test-classpath.txt').read_text().strip()
    deps = {p:data.sha(Path(p).read_bytes()) for p in cp.split(os.pathsep)}
    SLOT.mkdir();runner.SLOT = SLOT;listing = SLOT/'source-list.txt'
    with listing.open('x') as f:f.write(''.join(str(data.ROOT/p)+'\n' for p in paths))
    java = str(runner.TC/'jdk-25.0.4/bin/java')
    stages = {
        'pmd':runner.step('pmd',[java,'-cp',os.pathsep.join(map(str,pmd)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',cp,'--no-cache','--format','xml','--report-file',str(SLOT/'pmd.xml')],SLOT),
        'checkstyle':runner.step('checkstyle',[java,'-jar',str(static/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(SLOT/'checkstyle.xml'),'@'+str(listing)],SLOT),
    }
    reports = {}
    for name,tag in [('pmd','violation'),('checkstyle','error')]:
        p = SLOT/(name+'.xml');root = ET.parse(p).getroot();reports[name] = dict(findings=sum(x.tag.rpartition('}')[2] == tag for x in root.iter()),
            processingErrors=sum(x.tag.rpartition('}')[2] in ['error','configerror'] for x in root.iter()) if name == 'pmd' else 0,sha256=data.sha(p.read_bytes()))
    assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in hashes.items()) and all(data.sha(Path(p).read_bytes()) == sha for p,sha in {**tools,**deps}.items())
    passed = all(x['actualExit'] == 0 and not x['timedOut'] for x in stages.values()) and all(x['findings'] == x['processingErrors'] == 0 for x in reports.values())
    verify(invocation);OUT.mkdir();data.write(OUT/'original.json',dict(source=n['source'],path=OLD,sha256=data.sha(original),text=original.decode()))
    for name in reports:
        with (OUT/(name+'.xml')).open('xb') as f:f.write((SLOT/(name+'.xml')).read_bytes())
    data.write(OUT/'manifest.json',dict(actualExit=0 if passed else 1,source=None,baseSource=n['source'],invocation=invocation,candidateSourceHashes=hashes,
        appendedMethodInverse=changes,negativeVectors=vectors,independentNumericFixture=fixtures,originalSourceSha256=data.sha((OUT/'original.json').read_bytes()),
        originalRelatedTests=8,newTests=1,totalTests=9,reports=reports,stages=stages,toolAndRuleHashes=tools,productTestsExecuted=0,newAccepted=0,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()));raise SystemExit(0 if passed else 1)

if __name__ == '__main__':main()
