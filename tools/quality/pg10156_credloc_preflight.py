"""Exact five pure Map/Path methods; no credential/file/native operation."""
from pathlib import Path
import json
import re
import zipfile
import g07_host_class_provenance_inputs as data
from classfile_code_metadata import decode
from host_tool_invocation import capture, verify

SOURCE = '904ff094b89f457edb53a168f8495a0ad2e28ff9'
NORMAL = data.ROOT.parent/'pgpt-runs/PG379/pg10154-credloc-six-compile-v1/snapshot'
OUT = data.BASE/'PG10156-credloc-preflight-v1'
TEST = 'src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/ServiceCredentialLocationTest.java'
BINARY = 'dev.codex.schubert.nk.storage.ServiceCredentialLocationTest'
METHODS = [
    'opsCredloc001AcceptsPrivateAbsoluteLocationWithoutOtherEnvironmentRetention',
    'opsCredloc002RejectsMissingEmptyRelativeAndRoot',
    'opsCredloc003RejectsAliasTraversalAndControlBytes',
    'opsCredloc004BoundsAndNullContracts',
    'opsCredloc005ConcurrentFreshMapsDoNotChangeSnapshot']


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal_path = data.BASE/'PG10154-credloc-six-compile-v1/manifest.json'
    normal = json.loads(normal_path.read_bytes())
    old = data.read_checked(data.BASE/'PG10128-uid-oracle-six-compile-v1/manifest.json',
        '7738e9ba61b5166e1ca9ed2223f6c7ce494051c9837526df1b2f549a0b7a92be')
    assert normal['actualExit'] == normal['testsExecuted'] == 0 and normal['source'] == SOURCE
    hashes = normal['begin']['inputHashes']
    assert set(hashes) == set(old['begin']['inputHashes'])
    assert {p for p,h in hashes.items() if h != old['begin']['inputHashes'][p]} == {TEST}
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((NORMAL/p).read_bytes()) == h for p,h in hashes.items())
    text = (data.ROOT/TEST).read_text()
    assert re.findall(r'@Test\s+void\s+(\w+)\s*\(',text) == METHODS
    assert text.count('Path expected = Path.of(ROOT);') == text.count('assertEquals(expected, task.get());') == 1
    restored = text.replace('Path expected = Path.of(ROOT);','var value = ServiceCredentialLocation.read(Map.of(KEY, ROOT));').replace('assertEquals(expected, task.get());','assertEquals(value.directory(), task.get());')
    assert data.sha(restored.encode()) == old['begin']['inputHashes'][TEST]
    assert not any(v in text for v in ('BeforeEach','BeforeAll','ExtendWith','RegisterExtension','Files.','System.getenv','java.lang.foreign','ProcessBuilder'))
    subject = 'dev/codex/schubert/nk/storage/ServiceCredentialLocation.class'
    main_path = 'src/schubert-nk-storage/src/main/java/'+subject.replace('.class','.java')
    main = (NORMAL/main_path).read_text()
    assert not any(v in main for v in ('Files.','System.getenv','java.lang.foreign','ProcessBuilder','Class.forName','setAccessible'))
    jar = Path(normal['jars']['storage']['path'])
    assert data.sha(jar.read_bytes()) == normal['jars']['storage']['sha256']
    with zipfile.ZipFile(jar) as archive:
        physical = {n:data.sha(archive.read(n)) for n in archive.namelist() if n.startswith(subject.removesuffix('.class')) and n.endswith('.class')}
    assert set(physical) == {subject}
    target = NORMAL/'src/schubert-nk-storage/target/test-classes'/(BINARY.replace('.','/')+'.class')
    model = decode(target.read_bytes(),BINARY.replace('.','/')+'.class')
    assert model['sourceFile'] == 'ServiceCredentialLocationTest.java'
    assert {m['name'] for m in model['methods'] if m['name'] in METHODS and m['hasCode']} == set(METHODS)
    cases = [dict(className=BINARY,method=m,path=TEST,testId='PT-OPS-CREDLOC-'+str(i).zfill(3)) for i,m in enumerate(METHODS,1)]
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'cases.json',cases)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,expectedTests=5,expectedSuites=1,
        caseCounts={BINARY:5},casesSha256=data.sha((OUT/'cases.json').read_bytes()),normalManifestSha256=data.sha(normal_path.read_bytes()),
        physicalTestFiles={str(target):data.sha(target.read_bytes())},physicalMainClasses=physical,
        allCurrentSourceInputHashes=hashes,originalOtherSourceBytesPreserved=True,
        mainClosure='PURE_MAP_PATH_NON_SECRET_LOCATION_NO_FILE_ENV_NATIVE_IO',productTestsExecuted=0,
        externalActions=0,newTestIds=0,newAccepted=0,formalUpdated=False))
    print(json.dumps(dict(actualExit=0,tests=5,suites=1,manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
