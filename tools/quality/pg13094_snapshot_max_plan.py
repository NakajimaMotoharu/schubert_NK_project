"""Freeze only three new memory snapshot maximum/interior/tail oracles, never old DB-whole cases."""
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = '0a84859838be8826d58886e6d7f27bd849a9ea05'
OUT = data.BASE/'PG13094-snapshot-max-plan-v1'
TEST = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/persistence/ScenarioDetailSnapshotBoundaryTest.java'
MAIN = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/persistence/ScenarioDetailSnapshot.java'

def main():
    invocation = capture(__file__); assert not OUT.exists()
    n = data.read_checked(data.BASE/'PG13076-monitor-test-six-compile-v1/manifest.json','77020a553a53f8c09d498899dbb3e5844121dc67023862901fa7ad82b12c1932')
    p = data.read_checked(data.BASE/'PG13092-snapshot-max-preflight-v1/manifest.json','6183f69df3284a1755331d44b5177b554f8508725dfe87ac6c5c6a5204b5fb91')
    assert n['source'] == p['baseSource'] == '42ae92a74d57a9e1d031613d5b558af3ebe2925c' and n['actualExit'] == n['testsExecuted'] == p['actualExit'] == 0
    assert all(row['findings'] == row['processingErrors'] == 0 for row in p['reports'].values())
    assert set(p['candidateSourceHashes']) == {TEST,MAIN}
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in {**n['begin']['inputHashes'],**p['candidateSourceHashes']}.items())
    text = (data.ROOT/TEST).read_text()
    forbidden = ['@Before','@After','@ExtendWith','@Disabled','@TempDir','java.net.','java.sql.','java.nio.file','ProcessBuilder','System.getenv','System.setProperty','setAccessible','Repository','TemporaryInfrastructureException','WebStartupException','10001','10_001','DeliveryMode.FILE','null','ScenarioDetailDeliveryTest','ScenarioFileRegeneratorTest']
    assert not any(value in text for value in forbidden)
    methods = re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',text)
    assert len(methods) == len(set(methods)) == text.count('@Test') == 3
    for path in [MAIN,TEST]:
        imports = re.findall(r'^import (dev\.codex\.schubert\.nk\.[\w.]+);',(data.ROOT/path).read_text(),re.M)
        assert all(value.startswith('dev.codex.schubert.nk.protocol.') for value in imports)
    changes = subprocess.check_output(['git','diff','--name-only',n['source'],SOURCE,'--','src'],cwd=data.ROOT,text=True).splitlines()
    assert changes == [TEST]
    whole = {TEST:p['candidateSourceHashes'][TEST]}; mains = {MAIN:p['candidateSourceHashes'][MAIN]}
    cases = [dict(className=TEST.split('/java/',1)[1][:-5].replace('/','.'),method=name,path=TEST,sourceSha256=whole[TEST]) for name in methods]
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,before=n['source'],invocation=invocation,cases=cases,
        wholeTestSourceHashes=whole,eligibilityClosureSourceHashes=mains,supportTestSourceHashes={},
        protocolClosure='Existing reviewed standard64 codec/value sources, all old protocol source/jar bytes unchanged; API only this Snapshot and Test',
        originalTests=0,newTests=3,totalTests=3,totalCorrections=0,sameExecRequired=True,oldExecUnion=False,
        judgement='Maximum10000 immutable pre-I/O memory snapshot, interior sequence and tail field validation; no old null/10001/FILE-mode or DB/FS/Root/native cases',
        newAccepted=0,whole451Accepted=False,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__': main()
