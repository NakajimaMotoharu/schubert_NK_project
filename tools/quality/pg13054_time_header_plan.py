"""Freeze six genuinely new memory-only boundary oracles; no old held Test extraction."""
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = '7ced2d7078bf508afcb22dbc8e1d82cc15d56573'
OUT = data.BASE/'PG13054-time-header-plan-v1'

def main():
    invocation = capture(__file__); assert not OUT.exists()
    n = data.read_checked(data.BASE/'PG13018-http-route-name-six-compile-v1/manifest.json','66360a6446a271767118ed3ff4d734701f55a010638dc7676490409a0c488351')
    p = data.read_checked(data.BASE/'PG13052-time-header-preflight-v1/manifest.json','c0a176aaf18485b2c7d67694264482de3a15a834d617c66d3e9a1ee9b2b1dd88')
    assert n['source'] == p['baseSource'] == '2f4290e7e511ea30224d087f78d44964d3488919' and n['actualExit'] == n['testsExecuted'] == p['actualExit'] == 0
    assert all(r['findings'] == r['processingErrors'] == 0 for r in p['reports'].values())
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in n['begin']['inputHashes'].items())
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in p['candidateSourceHashes'].items())
    cases = []; whole = {}; mains = {}; paths = list(p['candidateSourceHashes'])
    for suffix in ['QuestionCommandTimeBoundaryTest.java','ContentDispositionBoundaryTest.java']:
        path = next(v for v in paths if v.endswith('/'+suffix)); text = (data.ROOT/path).read_text()
        forbidden = ['@Before','@After','@ExtendWith','@Disabled','@TempDir','java.net.','java.sql.','java.nio.file','ProcessBuilder','System.getenv','System.setProperty','setAccessible','Repository','TemporaryInfrastructureException','WebStartupException','Clock.system','Instant.now(']
        assert not any(v in text for v in forbidden)
        methods = re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',text)
        assert len(methods) == len(set(methods)) == text.count('@Test') == 3
        whole[path] = data.sha(text.encode())
        cases.extend(dict(className=path.split('/java/',1)[1][:-5].replace('/','.'),method=method,path=path,sourceSha256=whole[path]) for method in methods)
    mains = {path:sha for path,sha in p['candidateSourceHashes'].items() if '/src/main/java/' in path}
    assert len(mains) == 6 and len(whole) == 2 and len(cases) == 6
    allowed_imports = {path.split('/java/',1)[1][:-5].replace('/','.') for path in mains}
    for path in [*mains,*whole]:
        text = (data.ROOT/path).read_text()
        imports = re.findall(r'^import (dev\.codex\.schubert\.nk\.[\w.]+);',text,re.M)
        assert set(imports) <= allowed_imports
    changed = subprocess.check_output(['git','diff','--name-only','2f4290e7e511ea30224d087f78d44964d3488919',SOURCE,'--','src'],cwd=data.ROOT,text=True).splitlines()
    assert set(changed) == set(whole)
    verify(invocation); OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,before=n['source'],invocation=invocation,cases=cases,
        wholeTestSourceHashes=whole,eligibilityClosureSourceHashes=mains,supportTestSourceHashes={},originalTests=0,newTests=6,totalTests=6,
        sameExecRequired=True,oldExecUnion=False,totalCorrections=0,scopeStaticFindings=0,
        judgement='Six new memory-only time/header vectors; Main unchanged; old DB whole and old media Test not executed or extracted',
        newAccepted=0,whole451Accepted=False,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__': main()
