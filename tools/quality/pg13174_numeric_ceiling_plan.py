"""Freeze one new semantic boundary and eight necessary related methods in whole two Tests."""
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg13152_nfc_golden_preflight import MAINS, OLD, NEW
from pg13171_numeric_ceiling_inverse import NAME

SOURCE = '80ba5f783432c84b6facd83bcd3a80774f4e4665'
OUT = data.BASE/'PG13174-numeric-ceiling-plan-v1'

def main():
    invocation = capture(__file__);assert not OUT.exists()
    n = data.read_checked(data.BASE/'PG13156-nfc-golden-six-compile-v1/manifest.json','4c1f5352b5d048cda761851d3482fd74983b3ec885ed839d91f987bca60be0d9')
    p = data.read_checked(data.BASE/'PG13172-numeric-ceiling-preflight-v1/manifest.json','7559e9d9529f5415b0a000ece97bd92be6f6cc8b75139942aa22b6fbaeb71d24')
    assert n['source'] == p['baseSource'] == 'b11fe71bd20e244dd10c83bd339f8345a0c1f085' and n['actualExit'] == n['testsExecuted'] == p['actualExit'] == 0
    assert all(r['findings'] == r['processingErrors'] == 0 for r in p['reports'].values())
    assert {path for path,sha in n['begin']['inputHashes'].items() if data.sha((data.ROOT/path).read_bytes()) != sha} == {OLD}
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in p['candidateSourceHashes'].items())
    cases = [];whole = {}
    for path,expected in [(OLD,6),(NEW,3)]:
        text = (data.ROOT/path).read_text()
        forbidden = ['@Before','@After','@ExtendWith','@Disabled','@TempDir','java.net.','java.sql.','java.nio.file','ProcessBuilder','System.getenv','System.setProperty','Class.forName','setAccessible','TemporaryInfrastructureException','WebStartupException']
        assert not any(x in text for x in forbidden)
        methods = re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',text)
        assert len(methods) == len(set(methods)) == text.count('@Test') == expected
        whole[path] = data.sha(text.encode())
        cases.extend(dict(className=path.split('/java/',1)[1][:-5].replace('/','.'),method=method,path=path,sourceSha256=whole[path]) for method in methods)
    mains = {path:p['candidateSourceHashes'][path] for path in MAINS}
    assert len(cases) == 9 and len(whole) == 2 and len(mains) == 3 and sum(r['method'] == NAME for r in cases) == 1
    assert subprocess.check_output(['git','diff','--name-only',n['source'],SOURCE,'--','src'],cwd=data.ROOT,text=True).splitlines() == [OLD]
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,before=n['source'],invocation=invocation,cases=cases,
        wholeTestSourceHashes=whole,eligibilityClosureSourceHashes=mains,supportTestSourceHashes={},originalTests=8,newTests=1,totalTests=9,
        newMethodIds=[r['className']+'#'+r['method'] for r in cases if r['method'] == NAME],modifiedTestPaths=[OLD],newTestPaths=[],
        appendedMethodInverse=p['appendedMethodInverse'],inverseNegativeVectors=p['negativeVectors'],sameExecRequired=True,oldExecUnion=False,totalCorrections=0,scopeStaticFindings=0,
        judgement='Pure FieldCodec whole six plus unchanged NFC three; one new semantic ceiling method, original eight assertions preserved, no actual resources or old exec union',
        newAccepted=0,whole451Accepted=False,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
