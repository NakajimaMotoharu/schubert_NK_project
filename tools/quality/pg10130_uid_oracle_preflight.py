"""One reviewed self-UID method only; preserve every other Test token after literal constant folding."""
import json
from pathlib import Path
import re
import subprocess
import zipfile
import g07_host_class_provenance_inputs as data
from classfile_code_metadata import decode
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX, close

SOURCE = 'd17f122d2026b804be626bf7a3b76912923bd240'
NORMAL = data.ROOT.parent/'pgpt-runs/PG379/pg10128-uid-oracle-six-compile-v1/snapshot'
OUT = data.BASE/'PG10130-uid-oracle-preflight-v1'
TEST = 'src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/LinuxInodeSecurityTest.java'
BINARY = 'dev.codex.schubert.nk.storage.LinuxInodeSecurityTest'
METHOD = 'platformAndSymbolAdmission'


def tokens(text):
    return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]


def original_tokens(text):
    values = tokens(text)
    signature = tokens('void platformAndSymbolAdmission() throws java.io.IOException {')
    matches = [i for i in range(len(values)) if values[i:i+len(signature)] == signature]
    assert len(matches) == 1
    start = matches[0]
    opening = start+len(signature)-1
    ending = close([(v,i) for i,v in enumerate(values)],opening,'{','}')
    body = values[opening+1:ending]
    addition = tokens('long expectedUid = Integer.toUnsignedLong((Integer) Files.getAttribute(root, "unix:uid"));'
        'assertEquals(expectedUid, LinuxInodeSecurity.create().effectiveUid());')
    assert body[:len(addition)] == addition
    body = body[len(addition):]
    assert body.count('expectedUid') == 1
    restored = []
    for token in body:
        restored.extend(tokens('LinuxInodeSecurity.create().effectiveUid()') if token == 'expectedUid' else [token])
    values[start:ending+1] = tokens('void platformAndSymbolAdmission() {')+restored+['}']
    for declaration,name,literal in (
        ('private static final String PUBLIC_ENTRY = "public";','PUBLIC_ENTRY','"public"'),
        ('private static final String LINUX_OS = "Linux";','LINUX_OS','"Linux"'),
        ('private static final String AMD64_ARCH = "amd64";','AMD64_ARCH','"amd64"'),
        ('private static final int ENODATA_ERRNO = 61;','ENODATA_ERRNO','61')):
        pattern = tokens(declaration)
        matches = [i for i in range(len(values)) if values[i:i+len(pattern)] == pattern]
        assert len(matches) == 1
        values[matches[0]:matches[0]+len(pattern)] = []
        values = [part for value in values for part in (tokens(literal) if value == name else [value])]
    return values


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    assert tokens('61') == ['6','1'] and tokens('1000') == ['1','0','0','0']
    assert tokens('"public"') == ['"public"']
    normal_path = data.BASE/'PG10128-uid-oracle-six-compile-v1/manifest.json'
    normal = json.loads(normal_path.read_bytes())
    old = data.read_checked(data.BASE/'PG10100-query-batch-six-compile-v1/manifest.json',
        'a2a8eb62b574693a47e5ce82b830185a7db3fd41f4af61ba4341b598c5f8e3f3')
    assert normal['actualExit'] == normal['testsExecuted'] == 0 and normal['source'] == SOURCE
    hashes = normal['begin']['inputHashes']
    assert set(hashes) == set(old['begin']['inputHashes'])
    assert {p for p in hashes if hashes[p] != old['begin']['inputHashes'][p]} == {TEST}
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((NORMAL/p).read_bytes()) == h for p,h in hashes.items())
    assert not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=data.ROOT)
    text = (data.ROOT/TEST).read_text()
    old_root = Path(old['jars']['storage']['path']).parents[3]
    assert original_tokens(text) == tokens((old_root/TEST).read_text())
    assert not any(x in text for x in ('BeforeAll','BeforeEach','AfterAll','AfterEach','ExtendWith','RegisterExtension'))
    declared = re.findall(r'@Test\s+void\s+(\w+)\s*\(',text)
    assert len(declared) == 9 and declared.count(METHOD) == 1 and '@TempDir Path root;' in text
    assert '--enable-native-access=ALL-UNNAMED' in (NORMAL/'src/schubert-nk-storage/pom.xml').read_text()
    target = NORMAL/'src/schubert-nk-storage/target/test-classes'/(BINARY.replace('.','/')+'.class')
    files = {str(p):data.sha(p.read_bytes()) for p in target.parent.glob('LinuxInodeSecurityTest*.class')}
    for file in files:
        model = decode(Path(file).read_bytes(),str(Path(file).relative_to(NORMAL/'src/schubert-nk-storage/target/test-classes')))
        assert model['sourceFile'] == 'LinuxInodeSecurityTest.java'
    model = decode(target.read_bytes(),BINARY.replace('.','/')+'.class')
    assert len([m for m in model['methods'] if m['name'] == METHOD and m['descriptor'] == '()V' and m['hasCode']]) == 1
    subjects = {'dev/codex/schubert/nk/storage/LinuxInodeSecurity'+suffix+'.class'
        for suffix in ('','$GetXattrCall','$StatvfsCall','$UidCall')}
    jar = Path(normal['jars']['storage']['path'])
    assert data.sha(jar.read_bytes()) == normal['jars']['storage']['sha256']
    with zipfile.ZipFile(jar) as archive:
        physical = {p:data.sha(archive.read(p)) for p in archive.namelist() if p.startswith('dev/codex/schubert/nk/storage/LinuxInodeSecurity') and p.endswith('.class')}
    assert set(physical) == subjects
    cases = [dict(className=BINARY,method=METHOD,path=TEST,sourceSha256=hashes[TEST],
        normalTestClassSha256=data.sha(target.read_bytes()),declarationOriginSource=SOURCE,testId='PT-DB-INBOX-125')]
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'cases.json',cases)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        expectedTests=1,expectedSuites=1,caseCounts={BINARY:1},casesSha256=data.sha((OUT/'cases.json').read_bytes()),
        normalManifestSha256=data.sha(normal_path.read_bytes()),physicalTestFiles=files,physicalMainClasses=physical,
        allCurrentSourceInputHashes=hashes,allDeclaredTestMethods=declared,unselectedTestMethods=sorted(set(declared)-{METHOD}),
        allOtherSourceTokensUnchanged=True,productionGetterRemovedFromExpected=True,literalMetadataVectors=3,
        expectedMechanism='JDK_FILES_UNIX_UID_OF_FRAMEWORK_OWNED_NEW_TEMP_DIRECTORY_UNSIGNED',
        permittedNativeScope='SELF_UID_READ_AND_SYSTEM_SYMBOL_BIND_ONLY',
        forbiddenRuntimeMethods=['accessAcl','readAcl','requireNoFileCapabilities','readOnlyFilesystem','capability','failure'],
        localTemporaryDirectoryOnly=True,permissionOrIdentityChanged=False,externalActions=0,
        productTestsExecuted=0,newTestIds=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,tests=1,suites=1,mainClasses=len(physical),testClasses=len(files),
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
