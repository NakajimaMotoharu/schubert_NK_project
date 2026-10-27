"""Independent preserved old tokens plus explicit approved SDK additions and new pure Test oracle."""
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions

OUT = data.BASE/'PG12404-batch-runtime-oracle-source-post-v1'
TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/bootstrap/BatchRuntimeDependencyTest.java'
NEW_TEST = 'bat283cApprovedMonitoringSdkCoordinatesRequireVersionCompileAndMainJar'

def raw(text):
    return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]

def inverse(before,after):
    tokens = raw(after)
    for name,literal in [('DEPENDENCY_END_TAG','"</dependency>"'),('COMPILE_SCOPE_NAME','"compile"')]:
        declaration = raw('private static final String '+name+' = '+literal+';')
        matches = [i for i in range(len(tokens)-len(declaration)+1) if tokens[i:i+len(declaration)] == declaration]
        if len(matches) != 1:
            raise ValueError('one exact same-value declaration required')
        i = matches[0];del tokens[i:i+len(declaration)]
        tokens = [literal if token == name else token for token in tokens]
    bodies = {}
    for name,prefix in [(NEW_TEST,['@','Test','void']),('assertMonitoringDependencies',['private','static','void'])]:
        matches = [(a,b) for a,b,n in functions(list(zip(tokens,range(len(tokens))))) if n == name]
        if len(matches) != 1:
            raise ValueError('one complete new pure method required')
        a,b = matches[0]
        if tokens[a-3:a] != prefix:
            raise ValueError('fixed declaration boundary required')
        body = tokens[a:b+1];bodies[name] = body
        required = (
            ['"<version>1.17.1</version>"','"io.micrometer"','"micrometer-core"','"micrometer-registry-prometheus"','"compile"','"jar"','"<classifier>"']
            if name == 'assertMonitoringDependencies' else
            ['"1.17.1"','"1.17.0"','"foreign.group"','"provided"','"system"','"runtime"','"test"','NullPointerException','declared','fixture','wrong','AssertionError']
        )
        if any(value not in body for value in required):
            raise ValueError('approved fixed SDK and all independent negative classes required')
        if name == NEW_TEST:
            for artifact in ('micrometer-core','micrometer-registry-prometheus'):
                fixture = '"<dependency><groupId>io.micrometer</groupId><artifactId>'+artifact+'</artifactId><version>1.17.1</version></dependency>"'
                if fixture not in body:
                    raise ValueError('independent whole literal SDK fixtures required')
        del tokens[a-3:b+1]
    addition = raw('assertMonitoringDependencies(pom);')
    matches = [i for i in range(len(tokens)-len(addition)+1) if tokens[i:i+len(addition)] == addition]
    if len(matches) != 1:
        raise ValueError('new SDK validation in original complete runtime contract required')
    i = matches[0];del tokens[i:i+len(addition)]
    for value in ('io.micrometer:micrometer-core','io.micrometer:micrometer-registry-prometheus'):
        seq = ['"'+value+'"',','];matches = [i for i in range(len(tokens)-1) if tokens[i:i+2] == seq]
        if len(matches) != 1:
            raise ValueError('only independently approved two coordinates required')
        i = matches[0];del tokens[i:i+2]
    if tokens != raw(before):
        raise ValueError('all other original oracles, helper control and assertions must remain')
    return bodies

def main():
    invocation = capture(__file__);assert not OUT.exists()
    proof = data.read_checked(data.BASE/'PG12402-batch-runtime-oracle-discrepancy-v1/manifest.json','a3a5e425e082e01a0a5835ac25a48dd19b4439d725f89e54ecc2f9fe5c044df8')
    normal = data.read_checked(data.BASE/'PG12378-pool-batch-six-compile-v1/manifest.json','27e5dafc18e19fb5e29edd96958a5ba2f05da01611aa12b1ca8208735eb52b75')
    snapshot = Path(normal['jars']['batch']['path']).parent.parent.parent.parent
    before = (snapshot/TEST).read_text();after = (data.ROOT/TEST).read_text()
    assert data.sha(before.encode()) == proof['testSha256'] and all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p != TEST)
    bodies = inverse(before,after)
    old = re.findall(r'@Test\s+void (\w+)\(',before);new = re.findall(r'@Test\s+void (\w+)\(',after)
    assert len(old) == 2 and set(new) == set(old)|{NEW_TEST} and len(new) == 3
    bads = [after.replace('assertEquals(','assertNotEquals(',1),after.replace('"io.micrometer:micrometer-core",','',1),after.replace('assertMonitoringDependencies(pom);','',1),after.replace('"<version>1.17.1</version>"','"<version>1.17.0</version>"',1),after.replace('"foreign.group"','"io.micrometer"',1),after.replace('private static final String DEPENDENCY_END_TAG = "</dependency>";','',1)]
    negatives = 0
    for bad in bads:
        assert bad != after
        try:
            inverse(before,bad)
        except ValueError:
            negatives += 1
        else:
            raise AssertionError('unapproved oracle mutation accepted')
    assert negatives == 6
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,discrepancyManifestSha256='a3a5e425e082e01a0a5835ac25a48dd19b4439d725f89e54ecc2f9fe5c044df8',sourceChanges=[dict(path=TEST,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()))],originalMethods=old,expectedMethods=new,newTestIds=['PT-BAT-283C'],approvedNewMethodTokenSha256={n:data.sha('\0'.join(ts).encode()) for n,ts in bodies.items()},allOtherOriginalTokensRestored=True,allMainAndOtherInputsPreserved=True,metadataNegativeVectors=negatives,productTestsExecuted=0,coverage=None,newAccepted=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    main()
