"""Freeze whole old five plus three new independent NFC byte/scalar cases before execution."""
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg13152_nfc_golden_preflight import MAINS, OLD, NEW

SOURCE = 'b11fe71bd20e244dd10c83bd339f8345a0c1f085'
OUT = data.BASE/'PG13154-nfc-golden-plan-v1'

def main():
    invocation = capture(__file__);assert not OUT.exists()
    n = data.read_checked(data.BASE/'PG13134-main-literal-six-compile-v1/manifest.json','ef0c374ffb76d88402c3a19c70999c9f644bdbdecb0252c747b7f1544521d823')
    p = data.read_checked(data.BASE/'PG13152-nfc-golden-preflight-v1/manifest.json','c7a2ac738655f537cc227ee88b16d89e163ef618c6698ba03ac0d5487f25c34e')
    assert n['source'] == p['baseSource'] == '44afb0a1ecddabfebe577b2037aabdc6fb31d1e3' and n['actualExit'] == n['testsExecuted'] == p['actualExit'] == 0
    assert all(r['findings'] == r['processingErrors'] == 0 for r in p['reports'].values())
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in n['begin']['inputHashes'].items())
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in p['candidateSourceHashes'].items())
    cases = [];whole = {}
    for path,expected in [(OLD,5),(NEW,3)]:
        text = (data.ROOT/path).read_text()
        forbidden = ['@Before','@After','@ExtendWith','@Disabled','@TempDir','java.net.','java.sql.','java.nio.file','ProcessBuilder','System.getenv','System.setProperty','Class.forName','setAccessible','TemporaryInfrastructureException','WebStartupException']
        assert not any(x in text for x in forbidden)
        methods = re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',text)
        assert len(methods) == len(set(methods)) == text.count('@Test') == expected
        whole[path] = data.sha(text.encode())
        cases.extend(dict(className=path.split('/java/',1)[1][:-5].replace('/','.'),method=method,path=path,sourceSha256=whole[path]) for method in methods)
    mains = {path:p['candidateSourceHashes'][path] for path in MAINS}
    for path in MAINS:
        text = (data.ROOT/path).read_text()
        assert not any(x in text for x in ['java.sql','java.net','java.nio.file','java.lang.foreign','ProcessBuilder','catch (NullPointerException'])
    assert len(cases) == 8 and len(whole) == 2 and len(mains) == 3
    assert subprocess.check_output(['git','diff','--name-only',n['source'],SOURCE,'--','src'],cwd=data.ROOT,text=True).splitlines() == [NEW]
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,before=n['source'],invocation=invocation,cases=cases,
        wholeTestSourceHashes=whole,eligibilityClosureSourceHashes=mains,supportTestSourceHashes={},originalTests=5,newTests=3,totalTests=8,
        sameExecRequired=True,oldExecUnion=False,totalCorrections=0,scopeStaticFindings=0,
        judgement='Pure FieldCodec whole old five plus three new Hangul/Angstrom/canonical-order independent scalar/hex vectors; no old method extraction or actual resources',
        newAccepted=0,whole451Accepted=False,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
