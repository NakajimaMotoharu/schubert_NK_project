"""Current-source quality, byte delta, eight RNG scopes and explicit legacy metadata correction."""
from collections import Counter
import json
from pathlib import Path
import re
import zipfile
import g07_host_class_provenance_inputs as data
import pg9346_direct_companion_jdk_post as steps
from public_java_digest_provenance import LEX, close
from host_tool_invocation import capture, verify

ROOT = data.ROOT
BASE = data.BASE
SOURCE = '21d7c30425e7aa9ce435e808035a94fa4d75c93b'
SLOT = ROOT.parent/'pgpt-runs/PG379/pg9876-snapshot-nonce-quality-source-post-v1'
OUT = BASE/'PG9876-snapshot-nonce-quality-source-post-v1'
MAIN = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec.java'
TEST = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/idempotency/ResponseSnapshotNonceFailureTest.java'
RNG_PATHS = ('api/idempotency/ResponseSnapshotCodec','api/security/AuthContextCodec','api/security/AuthSessionService',
    'web/logging/WebLogPayloadCodec','web/revocation/RevocationPayloadCodec','web/session/SessionPayloadCodec',
    'web/session/WebSessionId','web/security/WebCsrfToken')


def buffer_scope(text):
    matches = list(re.finditer(r'\b(?:secureRandom|random)\.nextBytes\((\w+)\)',text))
    if len(matches) != 1:
        raise ValueError('one exact provider call per source')
    call = matches[0]
    tokens = [(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
    for i,(value,offset) in enumerate(tokens):
        if value != 'try':
            continue
        start = i+1
        if tokens[start][0] == '(':
            start = close(tokens,start,'(',')')+1
        if tokens[start][0] != '{':
            raise ValueError('lexical try body')
        end = close(tokens,start,'{','}')
        cursor = end+1
        while cursor < len(tokens) and tokens[cursor][0] == 'catch':
            cursor = close(tokens,cursor+1,'(',')')+1
            cursor = close(tokens,cursor,'{','}')+1
        if cursor >= len(tokens) or tokens[cursor][0] != 'finally':
            continue
        first = cursor+1
        last = close(tokens,first,'{','}')
        body = text[tokens[first][1]:tokens[last][1]+1]
        if tokens[start][1] < call.start() < tokens[end][1] and re.search(
            r'Arrays\.fill\(\s*'+re.escape(call.group(1))+r'\s*,\s*\(byte\)\s*0\s*\)',body):
            return dict(callLine=text.count('\n',0,call.start())+1,buffer=call.group(1),
                tryLine=text.count('\n',0,offset)+1,finallyLine=text.count('\n',0,tokens[cursor][1])+1,
                providerWithinErasingFinally=True)
    raise ValueError('provider is outside its owned buffer erasing finally')


def counts(expected, begin, actual_tests, actual_suites):
    values = [expected['expectedTests'],expected['expectedSuites'],begin['expectedTests'],begin['expectedSuites'],actual_tests,actual_suites]
    if any(type(v) is not int for v in values) or values != [9,2,9,2,9,2]:
        raise ValueError('method and suite dimensions must agree exactly at every boundary')


def method_body(text,name):
    match = re.search(r'(?m)^  (?:public|private|protected) [^\n]*\b'+re.escape(name)+r'\([^\n]*\);\s*$',text)
    if match is None:
        raise ValueError('exact original JVM method header')
    following = re.search(r'(?m)^  (?:public|private|protected|static) ',text[match.end():])
    return text[match.end():match.end()+following.start()] if following else text[match.end():]


def entries(item):
    path = Path(item['path'])
    assert data.sha(path.read_bytes()) == item['sha256']
    with zipfile.ZipFile(path) as jar:
        return {n:data.sha(jar.read(n)) for n in jar.namelist() if not n.endswith('/')}


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    pins = {
        'normal':('PG9866-snapshot-nonce-six-compile-v1','2b00918c64ac9dfc7e9b4d648c93ef8ef0bee293ae1faa65cc280c3dd21ab535'),
        'prepared':('PG9867-snapshot-nonce-preflight-v2','be7c2e31d2dc9074dd35eb50d59b27ffe694ef8c3f28418e27258cfc889e630e'),
        'host':('PG9868-snapshot-nonce-host-v1','5bdde82ac463edabe892c872e0081344cdc176738decca475f51bf7b39d8b0e6'),
        'coverage':('PG9870-snapshot-nonce-post-v1','12f63783cc61bdf8e0605c2644da90e860d26bcf867e7a3add9882e8f559e23f'),
        'spotbugs':('PG9872-snapshot-codec-static-v1','f2d3fcafd1525f8f8a75c9421cc221918982f670eba47d9af45919425770e8ae'),
        'pmdCs':('PG9874-snapshot-changed-source-static-v1','a97e2167ec9e923dc3de12e84ae4f32f43bbe195f5379d8a9017ded1a1a41723')}
    m = {k:data.read_checked(BASE/n/'manifest.json',h) for k,(n,h) in pins.items()}
    assert all(v['source'] == SOURCE for v in m.values())
    assert all(v['actualExit'] == 0 for k,v in m.items() if k != 'pmdCs') and m['pmdCs']['actualExit'] == 1
    counts(m['prepared'],m['host']['begin'],m['coverage']['tests'],m['coverage']['suites'])
    assert m['coverage']['targetUnitFour100'] and m['spotbugs']['allInputMainClasses'] == 1
    report = m['pmdCs']['reports']
    assert report['pmd']['findings'] == 3 and report['pmd']['processingErrors'] == 0 and report['checkstyle']['findings'] == 0
    assert Counter(v['rule'] for v in report['pmd']['details']) == Counter(HardCodedCryptoKey=1,CloseResource=2)
    old = data.read_checked(BASE/'PG9812-cleanup-values-six-compile-v1/manifest.json',
        'e074d972cbaf56b94ba4d25a77e7368b4f53ccd91489be0fbc27f07ef3975c95')
    normal = m['normal']
    changed_classes = []
    unchanged_modules = []
    current_main = {}
    for module,item in normal['jars'].items():
        previous,current = entries(old['jars'][module]),entries(item)
        if module != 'api':
            assert current == previous
            unchanged_modules.append(module)
        else:
            assert set(current) == set(previous)
            assert {k for k in current if current[k] != previous[k]} == {'dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec.class'}
        for name,digest in current.items():
            if name.endswith('.class'):
                current_main[module+':'+name] = digest
                if digest != previous[name]:
                    changed_classes.append(module+':'+name)
    assert len(current_main) == 1843 and len(changed_classes) == 1
    old_snapshot = Path(old['jars']['api']['path']).parents[3]
    snapshot = Path(normal['jars']['api']['path']).parents[3]
    assert old_snapshot.name == snapshot.name == 'snapshot'
    old_source = (old_snapshot/MAIN).read_text()
    current_source = (snapshot/MAIN).read_text()
    assert old_source.replace('    secureRandom.nextBytes(nonce);\n    try {\n',
        '    try {\n      // The provider can fail before Cipher acquisition; owned buffers still need erasure.\n      secureRandom.nextBytes(nonce);\n') == current_source
    old_tests = {str(p.relative_to(old_snapshot)):data.sha(p.read_bytes()) for p in old_snapshot.glob('src/*/target/test-classes/**/*.class')}
    new_tests = {str(p.relative_to(snapshot)):data.sha(p.read_bytes()) for p in snapshot.glob('src/*/target/test-classes/**/*.class')}
    assert len(old_tests) == 1916 and all(new_tests[k] == v for k,v in old_tests.items())
    added = {k:v for k,v in new_tests.items() if k not in old_tests}
    assert len(added) == 2 and all('ResponseSnapshotNonceFailureTest' in k for k in added)
    scopes = []
    for suffix in RNG_PATHS:
        module = suffix.split('/',1)[0]
        path = 'src/schubert-nk-'+module+'/src/main/java/dev/codex/schubert/nk/'+suffix+'.java'
        text = (ROOT/path).read_text()
        assert data.sha(text.encode()) == normal['begin']['inputHashes'][path]
        scopes.append(dict(path=path,sha256=data.sha(text.encode()),changed=path==MAIN,**buffer_scope(text)))
    assert len(scopes) == 8 and sum(r['changed'] for r in scopes) == 1
    SLOT.mkdir(mode=0o700)
    steps.SLOT = SLOT
    jdk = ROOT.parent/'toolchain/jdk-25.0.4/bin/javap'
    stages = [steps.step('current-codec-bytecode',[str(jdk),'-c','-p','-classpath',normal['jars']['api']['path'],
        'dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec']),
        steps.step('jdk-zip-close-end',[str(jdk),'-c','-p','java.util.zip.Deflater','java.util.zip.Inflater'])]
    assert all(s['actualExit'] == 0 and not s['timedOut'] for s in stages)
    bytecode = (SLOT/'current-codec-bytecode.stdout').read_text()
    encrypt = method_body(bytecode,'encrypt')
    pc = [int(x.group(1)) for x in re.finditer(r'^\s+(\d+):.*// Method java/security/SecureRandom\.nextBytes:\(\[B\)V',encrypt,re.MULTILINE)]
    handlers = [tuple(map(int,x)) for x in re.findall(r'^\s+(\d+)\s+(\d+)\s+(\d+)\s+any\s*$',encrypt,re.MULTILINE)]
    assert len(pc) == 1
    protecting = [h for h in handlers if h[0] <= pc[0] < h[1]]
    assert protecting and all('Arrays.fill('+n+', (byte) 0)' in current_source for n in ('compressed','nonce','aad'))
    for name,type_name in (('compress','Deflater'),('decompress','Inflater')):
        code = method_body(bytecode,name)
        allocation = [int(x.group(1)) for x in re.finditer(r'^\s+(\d+):\s+newarray\s+byte\b',code,re.MULTILINE)]
        acquisition = [int(x.group(1)) for x in re.finditer(r'^\s+(\d+):.*// Method java/util/zip/'+type_name+r'\."<init>":',code,re.MULTILINE)]
        assert len(allocation) == len(acquisition) == 1 and allocation[0] < acquisition[0]
        assert code.count('java/util/zip/'+type_name+'.end:()V') == 2
    zip_code = (SLOT/'jdk-zip-close-end.stdout').read_text()
    assert len(re.findall(r'public void close\(\);',zip_code)) == 2 and zip_code.count('// Method end:()V') == 2
    assert 'this.currentKey = validateKey(currentKey, "currentKey");' in current_source and 'return key.clone();' in current_source
    classifications = [{**row,'classification':'FALSE_POSITIVE_RUNTIME_INPUT_LABEL_NOT_KEY_MATERIAL' if row['rule']=='HardCodedCryptoKey'
        else 'FALSE_POSITIVE_EXPLICIT_END_FINALLY_NO_SCRATCH_ACQUISITION_GAP','rawFindingRetained':True} for row in report['pmd']['details']]
    rejected = []
    for label,values in (('old-cleanup', [4,1,4,1,4,1]),('stale-batch',[20,4,20,4,20,4]),
        ('wrong-suite',[9,1,9,1,9,1]),('notrun',[9,2,9,2,8,2]),('bool',[True,2,9,2,9,2]),('string',[9,'2',9,2,9,2])):
        try:
            counts(dict(expectedTests=values[0],expectedSuites=values[1]),dict(expectedTests=values[2],expectedSuites=values[3]),*values[4:])
        except ValueError:
            rejected.append(label)
        else:
            raise AssertionError('cross-boundary metadata false count accepted')
    old_host = data.read_checked(BASE/'PG9814-cleanup-values-host-v2/manifest.json',
        '3aba49441d549d8bc492dc4b063b230ab464772bb8554eedc83ff0cafa6a1944')
    assert (old_host['begin']['expectedTests'],old_host['begin']['expectedSuites']) == (20,4)
    assert len(old_host['cases']) == 4 and len(old_host['xmlHashes']) == 1
    correction = dict(originalManifestSha256='3aba49441d549d8bc492dc4b063b230ab464772bb8554eedc83ff0cafa6a1944',
        originalSource=old_host['source'],originalBegin=dict(expectedTests=20,expectedSuites=4),
        correctedBegin=dict(expectedTests=4,expectedSuites=1),actualResultUnchanged=True,oldArtifactRewritten=False,
        originalSuccessfulProductRunReplayed=False,bug='BUG1772',status='APPEND_ONLY_METADATA_CORRECTION_NOT_NEW_TEST_RESULT')
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'rng-scope-review.json',scopes)
    data.write(OUT/'pmd-three-applicability.json',classifications)
    data.write(OUT/'legacy-cleanup-begin-correction.json',correction)
    (OUT/'current-codec-bytecode.txt').write_text(bytecode)
    (OUT/'jdk-zip-close-end.txt').write_text(zip_code)
    result = dict(actualExit=0,source=SOURCE,invocation=invocation,inputPins=pins,stages=stages,
        currentMainClasses=1843,changedMainClasses=changed_classes,unchangedMainClasses=1842,
        allUncompressedEntriesUnchangedOutsideCodec=True,unchangedModules=sorted(unchanged_modules),
        previousTestClasses=1916,currentTestClasses=len(new_tests),addedTestClasses=added,oldTestClassesUnchanged=True,
        currentJavaPaths=1796,mainJavaPaths=965,testJavaPaths=831,scopeReviewed=8,changedRngCallScopes=1,nonAffectedRngCallScopes=7,
        selectedTests=9,selectedSuites=2,targetUnitFour100=True,spotbugsFindings=0,rawPmdFindings=3,
        pmdApplicabilityClassifiedFalsePositive=3,pmdUnclassifiedInChangedScope=0,checkstyleFindings=0,
        newTestPmdFindings=0,newTestCheckstyleFindings=0,pmdOriginalActualExit=1,rawStaticZeroClaim=False,
        erasingFinallyProtectsNextBytesPc=pc[0],originalAnyHandlersProtectingCall=protecting,
        countGuardNegativeVectors=rejected,legacyCleanupBeginCorrectionSha256=data.sha((OUT/'legacy-cleanup-begin-correction.json').read_bytes()),
        rngScopeReviewSha256=data.sha((OUT/'rng-scope-review.json').read_bytes()),
        pmdApplicabilitySha256=data.sha((OUT/'pmd-three-applicability.json').read_bytes()),
        productTestsExecutedByPost=0,actualExternalOperations=0,historicalSuccessTransferred=False,
        wholeF03Accepted=False,wholeG13Accepted=False,whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    data.write(OUT/'manifest.json',result)
    print(json.dumps(dict(actualExit=0,tests=9,suites=2,changedMain=1,rngScopes=8,rawPmd=3,applicabilityFalsePositive=3,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
