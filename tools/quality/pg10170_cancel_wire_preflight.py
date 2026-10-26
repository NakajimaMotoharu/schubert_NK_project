"""One pure codec method; preserve all old source tokens and independently fixed UI236 vectors."""
from pathlib import Path
import json
import re
import zipfile
import g07_host_class_provenance_inputs as data
from classfile_code_metadata import decode
from host_tool_invocation import capture, verify
from pg10130_uid_oracle_preflight import tokens

SOURCE = '5e8255bcf8f309d05fb091cee2e9ad810b276c87'
NORMAL = data.ROOT.parent/'pgpt-runs/PG379/pg10169-cancel-six-compile-v2/snapshot'
OUT = data.BASE/'PG10170-cancel-wire-preflight-v1'
TEST = 'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/codec/PayloadCodecTest.java'
BINARY = 'dev.codex.schubert.nk.protocol.codec.PayloadCodecTest'
METHOD = 'resultCodeProfilePreservesOnlyTheApprovedCancellationConflictState'
CONSTANTS = dict(UPDATED_STATE='"更新後状態"',USERNAME_FIELD='"Username"',LOOPBACK_ADDRESS='"127.0.0.1"',
    LOGIN_REQUEST='"LGNREQ01"',GAME_RESPONSE='"GAMRSP01"',LOGOUT_REQUEST='"LOGREQ01"',SAFE_FIELD='"safeName"')
CONFLICT = '''byte[] conflictGolden = new byte[32];
Arrays.fill(conflictGolden, (byte) ' ');
byte[] stateBytes = state.getBytes(StandardCharsets.US_ASCII);
System.arraycopy(stateBytes, 0, conflictGolden, 0, stateBytes.length);
assertArrayEquals(conflictGolden, statePayload.copyData());
assertEquals(stateValue, codec.decode(layoutId, conflictGolden, List.of(), ResultCode.NOT_CANCELLABLE));'''
SUCCESS = '''byte[] cancelledGolden = "CANCELLED   20260902123456789   ".getBytes(StandardCharsets.US_ASCII);
for (ResultCode code : List.of(ResultCode.SUCCESS, ResultCode.IDEMPOTENT_SUCCESS)) {
assertArrayEquals(cancelledGolden, codec.encode(success, code).copyData());
assertEquals(success, codec.decode(layoutId, cancelledGolden, List.of(), code)); }'''


def remove(values, pattern):
    matches = [i for i in range(len(values)) if values[i:i+len(pattern)] == pattern]
    assert len(matches) == 1
    i = matches[0]
    values[i:i+len(pattern)] = []


def restored_tokens(text):
    values = tokens(text)
    for name,literal in CONSTANTS.items():
        remove(values,tokens('private static final String '+name+' = '+literal+';'))
        values = [t for v in values for t in (tokens(literal) if v == name else [v])]
    for block in (CONFLICT,SUCCESS): remove(values,tokens(block))
    return values


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    path = data.BASE/'PG10169-cancel-six-compile-v2/manifest.json'
    normal = json.loads(path.read_bytes())
    old = data.read_checked(data.BASE/'PG10154-credloc-six-compile-v1/manifest.json',
        '683c715df260cde5a46f76888ad3e60159ddeae5e303e35992edc1edd9d0bf6e')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert set(hashes) == set(old['begin']['inputHashes'])
    assert {p for p,h in hashes.items() if h != old['begin']['inputHashes'][p]} == {TEST}
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((NORMAL/p).read_bytes()) == h for p,h in hashes.items())
    old_root = Path(old['jars']['protocol']['path']).parents[3]
    text = (data.ROOT/TEST).read_text()
    assert restored_tokens(text) == tokens((old_root/TEST).read_text())
    methods = re.findall(r'@Test\s+void\s+(\w+)\s*\(',text)
    assert len(methods) == 8 and methods.count(METHOD) == 1
    assert not any(v in text for v in ('TempDir','BeforeEach','BeforeAll','ExtendWith','RegisterExtension','Files.','System.getenv','ProcessBuilder','java.lang.foreign'))
    jar = Path(normal['jars']['protocol']['path'])
    assert data.sha(jar.read_bytes()) == normal['jars']['protocol']['sha256']
    prefix = 'dev/codex/schubert/nk/protocol/codec/PayloadCodec'
    with zipfile.ZipFile(jar) as archive:
        physical = {p:data.sha(archive.read(p)) for p in archive.namelist() if p.startswith(prefix) and p.endswith('.class')}
    assert set(physical) == {prefix+'.class',prefix+'$1.class'}
    target = NORMAL/'src/schubert-nk-protocol/target/test-classes'/(BINARY.replace('.','/')+'.class')
    assert decode(target.read_bytes(),BINARY.replace('.','/')+'.class')['sourceFile'] == 'PayloadCodecTest.java'
    vectors = {'0107-COMPLETED':b'COMPLETED'+b' '*23,'0107-ERROR':b'ERROR'+b' '*27,
        '0000-CANCELLED':b'CANCELLED   20260902123456789   ','0200-CANCELLED':b'CANCELLED   20260902123456789   '}
    assert all(len(v) == 32 and v[29:] == b' '*3 for v in vectors.values())
    assert all(v[12:29] == b' '*17 for k,v in vectors.items() if k.startswith('0107'))
    cases = [dict(className=BINARY,method=METHOD,path=TEST,testIds=['PT-PRO-002-E01','PT-PRO-002-E02','PT-PRO-002-P02'])]
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'cases.json',cases)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        expectedTests=1,expectedSuites=1,caseCounts={BINARY:1},casesSha256=data.sha((OUT/'cases.json').read_bytes()),
        normalManifestSha256=data.sha(path.read_bytes()),physicalTestFiles={str(target):data.sha(target.read_bytes())},
        physicalMainClasses=physical,allCurrentSourceInputHashes=hashes,allDeclaredTestMethods=methods,
        allOriginalSourceTokensPreserved=True,newGoldenVectorHashes={k:data.sha(v) for k,v in vectors.items()},
        vectorSource='UI236_section10.2_offsets1_13_30_lengths12_17_3',newTestIds=0,
        targetCodeExecuted=False,productTestsExecuted=0,externalActions=0,newAccepted=0,formalUpdated=False))
    print(json.dumps(dict(actualExit=0,tests=1,suites=1,manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
