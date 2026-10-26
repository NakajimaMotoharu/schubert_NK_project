"""Freeze one ordinary header method; preserve all old tokens except eight equivalent constants."""
from pathlib import Path
import json
import re
import zipfile
import g07_host_class_provenance_inputs as data
from classfile_code_metadata import decode
from host_tool_invocation import capture, verify
from pg10130_uid_oracle_preflight import tokens
from pg10170_cancel_wire_preflight import remove

SOURCE='ddde23ca0304654d59608b434c647c87d58ae3b6'
NORMAL=data.ROOT.parent/'pgpt-runs/PG379/pg10226-header-profile-six-compile-v1/snapshot'
OUT=data.BASE/'PG10228-header-profile-preflight-v1'
TEST='src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/codec/MessageCodecTest.java'
BINARY='dev.codex.schubert.nk.protocol.codec.MessageCodecTest'
METHOD='responseAndEventHeadersRoundTripWithoutLeakingContext'
CONSTANTS=dict(PROTOCOL_MAGIC='"SCHBNK01"',LAYOUT_VERSION='"001"',GAME_RESPONSE='"GAMRSP01"',
    SYNC_REPLY_ADDRESS='"nk.sync.reply.web"',SYNC_REQUEST_ADDRESS='"nk.sync.request"',
    JMS_FIXTURE_ID='"ID:1"',REPLY_ADDRESS='"reply"',DESTINATION_ADDRESS='"destination"')


def restore(text):
    start=text.index('    String literalIdsAndJst =')
    end=text.index('    assertEquals(event, HeaderCodec.standard().peek(eventGolden));',start)
    end+=len('    assertEquals(event, HeaderCodec.standard().peek(eventGolden));')
    block=text[start:end]
    assert all(fragment in block for fragment in ('"SCHBNK01001GAMRSP01001SS"',
        '"SCHBNK01001WLGEVT01001EI"','"02560000090002720000010000005370000"',
        '"0256002080000000000000000002336"','"20260902123456789"',
        'assertArrayEquals(responseGolden, HeaderCodec.standard().encode(response))',
        'assertArrayEquals(eventGolden, HeaderCodec.standard().encode(event))',
        'assertEquals(response, HeaderCodec.standard().peek(responseGolden))'))
    values=tokens(text[:start]+text[end:])
    for name,literal in CONSTANTS.items():
        remove(values,tokens('private static final String '+name+' = '+literal+';'))
        values=[t for v in values for t in (tokens(literal) if v==name else [v])]
    return values,block


def main():
    invocation=capture(Path(__file__))
    assert not OUT.exists()
    path=data.BASE/'PG10226-header-profile-six-compile-v1/manifest.json'
    normal=json.loads(path.read_bytes())
    old=data.read_checked(data.BASE/'PG10202-pre-sql-boundary-six-compile-v1/manifest.json',
        'a050b88ec51ec64a18d0abd5adf5ea2bf64304a496735acb40f4da8091dfa8f2')
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    hashes=normal['begin']['inputHashes']
    assert set(hashes)==set(old['begin']['inputHashes'])
    assert {p for p,h in hashes.items() if h!=old['begin']['inputHashes'][p]}=={TEST}
    assert all(data.sha((data.ROOT/p).read_bytes())==data.sha((NORMAL/p).read_bytes())==h for p,h in hashes.items())
    old_root=Path(old['jars']['protocol']['path']).parents[3]
    text=(data.ROOT/TEST).read_text()
    restored,block=restore(text)
    assert restored==tokens((old_root/TEST).read_text())
    methods=re.findall(r'@Test\s+void\s+(\w+)\s*\(',text)
    assert len(methods)==7 and methods.count(METHOD)==1
    assert not any(v in text for v in ('@Before','@After','@ExtendWith','@TempDir','Files.',
        'System.getenv','ProcessBuilder','java.lang.foreign','DriverManager'))
    jar=Path(normal['jars']['protocol']['path'])
    prefix='dev/codex/schubert/nk/protocol/codec/HeaderCodec'
    with zipfile.ZipFile(jar) as archive:
        physical={p:data.sha(archive.read(p)) for p in archive.namelist() if p.startswith(prefix) and p.endswith('.class')}
    assert set(physical)=={prefix+'.class'}
    target=NORMAL/'src/schubert-nk-protocol/target/test-classes'/(BINARY.replace('.','/')+'.class')
    assert decode(target.read_bytes(),BINARY.replace('.','/')+'.class')['sourceFile']=='MessageCodecTest.java'
    ids=b'123e4567-e89b-12d3-a456-426614174000223e4567-e89b-12d3-a456-42661417400020260902123456789'
    vectors=dict(response=b'SCHBNK01001GAMRSP01001SS'+ids+b'a'*64+b'02560000090002720000010000005370000'+b' '*44,
        event=b'SCHBNK01001WLGEVT01001EI'+ids+b' '*64+b'0256002080000000000000000002336'+b' '*48)
    assert all(len(v)==256 and v[212:]==b' '*44 for v in vectors.values())
    assert vectors['response'][199:212]==b'0000005370000' and vectors['event'][199:212]==b'000002336    '
    assert vectors['response'][113:177]==b'a'*64 and vectors['event'][113:177]==b' '*64
    cases=[dict(className=BINARY,method=METHOD,path=TEST,testIds=['PT-PRO-002-H01'])]
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'cases.json',cases)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        expectedTests=1,expectedSuites=1,caseCounts={BINARY:1},casesSha256=data.sha((OUT/'cases.json').read_bytes()),
        normalManifestSha256=data.sha(path.read_bytes()),physicalTestFiles={str(target):data.sha(target.read_bytes())},
        physicalMainClasses=physical,allCurrentSourceInputHashes=hashes,allDeclaredTestMethods=methods,
        allOriginalSourceTokensPreserved=True,addedBlockSha256=data.sha(block.encode()),
        newGoldenVectorHashes={k:data.sha(v) for k,v in vectors.items()},newTestIds=0,
        targetCodeExecuted=False,productTestsExecuted=0,externalActions=0,newAccepted=0,formalUpdated=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__': main()
