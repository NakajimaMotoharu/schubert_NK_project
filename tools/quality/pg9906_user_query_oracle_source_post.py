"""Independent source/byte metadata post for explicit expected layout; never runs business Tests."""
import json
from pathlib import Path
import re
import subprocess
import zipfile

import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX

ROOT = data.ROOT
SOURCE = '5f18a4e3d3f35fe58e2fdb381735200824a727d3'
OUT = data.BASE/'PG9906-user-query-oracle-source-post-v1'
MAIN = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/admin/UserQueryRequest.java'
BASE = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/'
TEST = BASE+'UserQueryRequestTest.java'
CALLER = BASE+'UserQueryApplicationServiceTest.java'


def compact(text):
    return ''.join(m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*')))


def oracle(text, caller):
    code = compact(text)
    helper = code[code.index('staticbyte[]check('):]
    if helper.count('request.detailRequest()') != 1 or 'assertEquals(expectedDetail,request.detailRequest());' not in helper:
        raise ValueError('SUT branch may only be the actual side of an independent assertion')
    required = (
        'StringexpectedLayout,List<String>expected)',
        'booleanexpectedDetail=expectedLayout.equals("UDTREQ01");',
        'Stringlayout=expectedLayout;',
        'varnames=expectedDetail?List.of("userId"):List.of("usernamePrefix","role","state","page","pageSize");',
        'Stringtype=expectedDetail||i>=3?"N1":"X1";',
        'out.writeInt(-1);',
        'out.write("SCHUBERT-NK-OP1".getBytes(StandardCharsets.US_ASCII));')
    if any(item not in helper for item in required):
        raise ValueError('approved independent field/frame selector changed')
    calls = ('check(request,ADMIN,"USRREQ01",','check(request,ADMIN,"UDTREQ01",')
    if any(code.count(item) != 1 for item in calls) or code.count('check(request,actor,expectedLayout,expected);') != 2:
        raise ValueError('all four internal callers must supply independent fixture layout')
    if 'StringexpectedLayout=n%2==0?"UDTREQ01":"USRREQ01";' not in code:
        raise ValueError('parallel fixture selector must come from n, not request result')
    if 'UserQueryRequestTest.check(UserQueryRequest.decode(message),UserQueryRequestTest.ADMIN,detail?"UDTREQ01":"USRREQ01",' not in compact(caller):
        raise ValueError('external caller fixture selector missing or reversed')
    if tuple(re.findall(r'@Test\s+void\s+(\w+)\s*\(',text)) != (
        'adm040DecodeAndCanonicalKeepAllOriginalQueryFields','adm041RealReadOnlyQueriesUseTheSameDecodedValues',
        'adm042NullMalformedAndResponseMismatchNeverPass','adm043ConcurrentRequestsOwnIndependentCanonicalBuffers'):
        raise ValueError('original four test declarations must remain unchanged')


def negatives(text, caller):
    mutations = [
        (text.replace('String layout = expectedLayout;', 'String layout = request.detailRequest() ? "UDTREQ01" : "USRREQ01";'),caller),
        (text.replace('var names =\n          expectedDetail', 'var names =\n          request.detailRequest()'),caller),
        (text.replace('String type = expectedDetail || i >= 3', 'String type = request.detailRequest() || i >= 3'),caller),
        (text.replace('String expectedLayout = n % 2 == 0 ? "UDTREQ01" : "USRREQ01";', 'String expectedLayout = n % 2 == 0 ? "USRREQ01" : "UDTREQ01";'),caller),
        (text.replace('out.writeInt(-1);','out.writeInt(0);'),caller),
        (text,caller.replace('detail ? "UDTREQ01" : "USRREQ01",','detail ? "USRREQ01" : "UDTREQ01",')),
        (text.replace('"pageSize"','"size"'),caller)]
    for changed, other in mutations:
        assert (changed,other) != (text,caller)
        try:
            oracle(changed,other)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid oracle source metadata accepted')
    return len(mutations)


def jar_classes(normal):
    rows = {}
    for module,item in normal['jars'].items():
        path = Path(item['path'])
        assert data.sha(path.read_bytes()) == item['sha256']
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                if name.endswith('.class'):
                    assert (module,name) not in rows
                    rows[(module,name)] = data.sha(archive.read(name))
    return rows


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal_path = data.BASE/'PG9904-user-query-oracle-six-compile-v1/manifest.json'
    normal = json.loads(normal_path.read_bytes())
    prior = data.read_checked(data.BASE/'PG9866-snapshot-nonce-six-compile-v1/manifest.json',
        '2b00918c64ac9dfc7e9b4d648c93ef8ef0bee293ae1faa65cc280c3dd21ab535')
    assert normal['actualExit'] == 0 and normal['source'] == SOURCE and normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in hashes.items())
    changed = {p for p in hashes if hashes[p] != prior['begin']['inputHashes'].get(p)}
    assert set(hashes) == set(prior['begin']['inputHashes']) and changed == {TEST,CALLER}
    assert not list(Path(normal['jars']['api']['path']).parent.parent.glob('target/surefire-reports/TEST-*.xml'))
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT) == b''
    text, caller = (ROOT/TEST).read_text(), (ROOT/CALLER).read_text()
    oracle(text,caller)
    negative_count = negatives(text,caller)
    before, after = jar_classes(prior),jar_classes(normal)
    assert len(before) == len(after) == 1843 and before == after
    old_tests, new_tests = {},{}
    for witness, target in ((prior,old_tests),(normal,new_tests)):
        for item in witness['jars'].values():
            root = Path(item['path']).parent/'test-classes'
            for path in root.rglob('*.class'):
                target[(root.parent.parent.name,path.relative_to(root).as_posix())] = data.sha(path.read_bytes())
    assert set(old_tests) == set(new_tests) and len(new_tests) == 1918
    changes = sorted(k for k in new_tests if new_tests[k] != old_tests[k])
    assert changes and all(k[0] == 'schubert-nk-api' and
        (k[1].startswith('dev/codex/schubert/nk/api/application/admin/UserQueryRequestTest') or
         k[1].startswith('dev/codex/schubert/nk/api/application/admin/UserQueryApplicationServiceTest')) for k in changes)
    external_callers = subprocess.check_output(['rg','-l','UserQueryRequestTest\\.check|import static .*UserQueryRequestTest\\.check',
        'src','-g','*.java'],cwd=ROOT,text=True).splitlines()
    assert external_callers == [CALLER]
    verify(invocation)
    OUT.mkdir()
    value = dict(actualExit=0,source=SOURCE,invocation=invocation,normalManifestSha256=data.sha(normal_path.read_bytes()),
        previousCompileManifestSha256='2b00918c64ac9dfc7e9b4d648c93ef8ef0bee293ae1faa65cc280c3dd21ab535',
        changedSourceHashes={p:hashes[p] for p in sorted(changed)},mainSourceHash=hashes[MAIN],mainSourceChanged=False,
        mainClasses=1843,allMainClassBytesUnchanged=True,physicalTestClasses=1918,changedTestClasses=changes,
        testDeclarationsPreserved=4,internalCallSites=4,externalCallSites=1,negativeSourceMetadataVectors=negative_count,
        originalFailedCompile=dict(run='PG9900',actualExit=1,manifestSha256='bae93b8a78229288a39519fb9e12a742e0aaa4dc665146faeb9518aee90ea65d'),
        bugs=['BUG1777','BUG1778'],horizontal=['YKT1528','YKT1529'],productTestsExecuted=0,
        dynamicTestStatus='NOT_EXECUTED_DB_DEPENDENCY_HOLD',coverage=None,oldDynamicSuccessTransferred=False,
        externalActions=0,heldValidationRetried=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    data.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,mainUnchanged=1843,changedTestClasses=len(changes),
        metadataNegatives=negative_count,productTests=0,manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
