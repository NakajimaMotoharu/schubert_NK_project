"""Five exact pure codec/Main Test sources, strict golden authorship, no Product PT."""
import json
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9666_pagination_static as runner

SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13152-nfc-golden-preflight-v1'
OUT = data.BASE/'PG13152-nfc-golden-preflight-v1'
PREFIX = 'src/schubert-nk-protocol/src/'
PACKAGE = 'dev/codex/schubert/nk/protocol/codec/'
MAINS = [PREFIX+'main/java/'+PACKAGE+name+'.java' for name in ['FieldCodec','FieldEncodingException','PermanentProtocolException']]
OLD = PREFIX+'test/java/'+PACKAGE+'FieldCodecTest.java'
NEW = PREFIX+'test/java/'+PACKAGE+'FieldCodecNfcGoldenTest.java'

def main():
    invocation = capture(__file__);assert not SLOT.exists() and not OUT.exists()
    n = data.read_checked(data.BASE/'PG13134-main-literal-six-compile-v1/manifest.json','ef0c374ffb76d88402c3a19c70999c9f644bdbdecb0252c747b7f1544521d823')
    assert n['source'] == '44afb0a1ecddabfebe577b2037aabdc6fb31d1e3' and n['actualExit'] == n['testsExecuted'] == 0
    assert NEW not in n['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in n['begin']['inputHashes'].items())
    paths = [*MAINS,OLD,NEW];hashes = {p:data.sha((data.ROOT/p).read_bytes()) for p in paths}
    text = (data.ROOT/NEW).read_text()
    assert len(re.findall(r'@Test\s+void\s+(\w+)\s*\(',text)) == text.count('@Test') == 3
    assert not any(x in text for x in ['Normalizer','@Before','@After','@Disabled','@ExtendWith','@TempDir','java.net','java.sql','java.nio.file','ProcessBuilder','System.getenv','Class.forName','setAccessible'])
    old_text = (data.ROOT/OLD).read_text();assert len(re.findall(r'@Test\s+void\s+(\w+)\s*\(',old_text)) == old_text.count('@Test') == 5
    static = runner.TC/'static-gates-20261015';rules = data.ROOT/'tools/quality/static'
    pmd = [static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))]
    tools = {str(p):data.sha(p.read_bytes()) for p in [*pmd,static/'checkstyle-14.3.0-all.jar',rules/'pmd.xml',rules/'checkstyle.xml']}
    snapshot = Path(n['jars']['protocol']['path']).parents[3]
    cp = (snapshot/'src/schubert-nk-protocol/target/pgpt-test-classpath.txt').read_text().strip()
    deps = {p:data.sha(Path(p).read_bytes()) for p in cp.split(os.pathsep) if Path(p).is_file()}
    assert deps
    SLOT.mkdir();runner.SLOT = SLOT;listing = SLOT/'source-list.txt'
    with listing.open('x') as f:f.write(''.join(str(data.ROOT/p)+'\n' for p in paths))
    java = str(runner.TC/'jdk-25.0.4/bin/java')
    stages = {
        'pmd':runner.step('pmd',[java,'-cp',os.pathsep.join(map(str,pmd)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',cp,'--no-cache','--format','xml','--report-file',str(SLOT/'pmd.xml')],SLOT),
        'checkstyle':runner.step('checkstyle',[java,'-jar',str(static/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(SLOT/'checkstyle.xml'),'@'+str(listing)],SLOT),
    }
    reports = {}
    for name,tag in [('pmd','violation'),('checkstyle','error')]:
        p = SLOT/(name+'.xml');root = ET.parse(p).getroot()
        reports[name] = dict(findings=sum(x.tag.rpartition('}')[2] == tag for x in root.iter()),
            processingErrors=sum(x.tag.rpartition('}')[2] in ['error','configerror'] for x in root.iter()) if name == 'pmd' else 0,sha256=data.sha(p.read_bytes()))
    assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in hashes.items())
    assert all(data.sha(Path(p).read_bytes()) == sha for p,sha in {**tools,**deps}.items())
    passed = all(x['actualExit'] == 0 and not x['timedOut'] for x in stages.values()) and all(x['findings'] == x['processingErrors'] == 0 for x in reports.values())
    verify(invocation);OUT.mkdir()
    for name in reports:
        with (OUT/(name+'.xml')).open('xb') as f:f.write((SLOT/(name+'.xml')).read_bytes())
    data.write(OUT/'manifest.json',dict(actualExit=0 if passed else 1,source=None,baseSource=n['source'],invocation=invocation,candidateSourceHashes=hashes,
        originalRelatedTests=5,newTests=3,reports=reports,stages=stages,toolAndRuleHashes=tools,productTestsExecuted=0,newAccepted=0,whole451Accepted=False))
    print(json.dumps(dict(actualExit=0 if passed else 1,reports=reports,manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))
    raise SystemExit(0 if passed else 1)

if __name__ == '__main__':main()
