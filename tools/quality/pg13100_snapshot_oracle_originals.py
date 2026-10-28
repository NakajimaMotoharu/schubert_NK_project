"""Preserve original failed candidate and immutable source/strong exception-layer basis before correction."""
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG13100-snapshot-oracle-originals-v1'
SOURCE = '0a84859838be8826d58886e6d7f27bd849a9ea05'
TEST = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/persistence/ScenarioDetailSnapshotBoundaryTest.java'

def main():
    invocation = capture(__file__); assert not OUT.exists()
    h = data.read_checked(data.BASE/'PG13098-snapshot-max-host-v1/manifest.json','bdc508fa33f1ccb731cd62427bc7b3190a91d4ad28f5d40bf2f31a766b74b27d')
    n = data.read_checked(data.BASE/'PG13096-snapshot-max-six-compile-v1/manifest.json','d4de109ab5b3b31ddedc8bd2fd854fe44cbc95f9cbfb95a08f775326cf3ffad1')
    assert h['source'] == n['source'] == SOURCE and h['actualExit'] == 1 and n['actualExit'] == n['testsExecuted'] == 0 and h['observedTestExecutions'] == 3
    assert sum(not r['nonPass'] for r in h['cases']) == 1 and sum(bool(r['nonPass']) for r in h['cases']) == 2
    raw = (data.ROOT/TEST).read_bytes(); assert raw == subprocess.check_output(['git','show',SOURCE+':'+TEST],cwd=data.ROOT) and data.sha(raw) == n['begin']['inputHashes'][TEST]
    inputs = ['documents/300_SS/320_メッセージング/322_固定長電文codec実装設計.md','src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/codec/FieldCodec.java','src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/PayloadSemanticValidator.java','src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/LayoutValidationException.java','src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/codec/FieldCodecTest.java']
    hashes = {path:data.sha((data.ROOT/path).read_bytes()) for path in inputs}
    verify(invocation); OUT.mkdir();data.write(OUT/'original.json',dict(source=SOURCE,test=TEST,sourceSha256=data.sha(raw),text=raw.decode(),
        failedHostManifestSha256='bdc508fa33f1ccb731cd62427bc7b3190a91d4ad28f5d40bf2f31a766b74b27d',cases=h['cases'],basisHashes=hashes,
        oldActualCauseClassExported=False,expectedCorrections={'snapshotMax002':'LayoutValidationException','snapshotMax003':'FieldEncodingException'},
        primarySpecification='SS322§11 byte overflow and existing immutable layout semantic contract; no Main/spec behavior change'))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,originalSha256=data.sha((OUT/'original.json').read_bytes()),
        oldActualExit=1,oldTests=3,oldSucceeded=1,oldFailed=2,oldActualCauseClassExported=False,productReruns=0,newAccepted=0,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__': main()
