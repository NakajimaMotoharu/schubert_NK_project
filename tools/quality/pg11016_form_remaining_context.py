"""Twelve current source-local static contexts: delegated form ownership and finite ordinary JUnit workers."""
from collections import Counter
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10910_current_f03_web_metric_delta import attrs

SOURCE = '9c37bc73a20bab2028413db2c08f6bbdf28c76a6'
OUT = data.BASE/'PG11016-form-remaining-context-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG11008-form-close-assert-six-compile-v1/manifest.json',
        '5150b4e1aceb6ac51c8a38d253108f6729307cd7df77253b8a37f2c44426ea63')
    proof = data.read_checked(data.BASE/'PG11014-form-close-assert-post-v1/manifest.json',
        'c5272833fa8e1597c93ee20fd5b2bc8fa382ddc9a82e1649108298e78d1caeaa')
    static_path = data.BASE/'PG11012-form-close-assert-static-v1/manifest.json'
    static = data.read_checked(static_path,'d642c529b96c8cac73372108e5ea6423cf829e5ea8923badae39fffe04be5df0')
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
        '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    assert normal['actualExit'] == proof['actualExit'] == 0 and normal['source'] == proof['source'] == static['source'] == SOURCE
    assert static['actualExit'] == 1 and proof['originalObservedTestExecutions'] == 40 and proof['selectedFormFourCounters100']
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    raw = (static_path.parent/'pmd.xml').read_bytes()
    assert data.sha(raw) == static['reports']['pmd']['sha256']
    rows = []
    for file in ET.fromstring(raw):
        if file.tag.rpartition('}')[2] != 'file':
            continue
        path = str(Path(file.get('name')).relative_to(data.ROOT))
        text = (data.ROOT/path).read_text()
        assert hashes[path] == static['sourceHashes'][path]
        compact = re.sub(r'\s+','',text)
        for node in file:
            if node.tag.rpartition('}')[2] != 'violation':
                continue
            rule = node.get('rule')
            matches = [r for r in original if r['path'] == path and r['rule'] == rule and
                attrs(r['attributes']) == attrs(node.attrib) and ' '.join(r['message'].split()) == ' '.join((node.text or '').split())]
            assert len(matches) == 1
            old = matches[0]
            if rule == 'CloseResource':
                assert Path(path).stem == 'UserMutationFormTest' and node.get('method') == 'bind'
                factory = next(n for n in ('UserStatusForm','UserRoleForm','PasswordResetForm','UserUnlockForm') if n+' object' in (node.text or ''))
                assert 'varf='+factory+'.bind(' in compact
                assert compact.count('yieldnewForm(f,f::close,f::isValid,f::getIssues,f::displayValues,f::toRequest);') == 4
                assert 'implementsAutoCloseable{@Overridepublicvoidclose(){closer.run();}}' in compact
                assert 'try(varf=bind(' in compact and 'finally{f.close();}' in compact
                main = 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/form/'+factory+'.java'
                source = (data.ROOT/main).read_text()
                assert 'input.close();' in source and hashes[main] == data.sha(source.encode())
                basis = dict(kind='OWNERSHIP_TRANSFER_TO_TEST_AUTOCLOSEABLE_RECORD',factory=factory,
                    mainSourceSha256=hashes[main],ownership='factory f captured by Form.closer=f::close; Form.close invokes closer; callers TWR or finally',
                    scope='Four exact returned wrappers; no actual DB/socket/key/resource acquired by these forms')
            else:
                assert rule == 'DoNotUseThreads' and node.get('method') in (
                    'qstForm008ConcurrentIndependentBodiesAndTokens','target008OneHundredParallelBindHasNoSharedMutableState',
                    'create007OneHundredConcurrentIndependentRequests','change015OneHundredIndependentParallelOperations')
                assert 'try(varexecutor=Executors.newFixedThreadPool(8))' in compact
                assert '100' in compact and re.search(r'\.get\((5|10|30),TimeUnit\.SECONDS\)',compact)
                assert not any(s in text for s in ('java.net.','getConnection(','ProcessBuilder','@ExtendWith','@Before','@After'))
                basis = dict(kind='FINITE_ORDINARY_JUNIT_NOT_J2EE_APPLICATION_RUNTIME',workers=8,tasks=100,
                    ownership='TWR-owned executor, finite pure form/codec tasks, Future5/10/30s, enclosing dedicated JVM240s',
                    scope='Exact Test worker sites only; not an exemption for Main threads or other rules')
            rows.append(dict(id=old['id'],path=path,source=SOURCE,sourceSha256=hashes[path],rule=rule,attributes=dict(node.attrib),
                originalRowSha256=old['rowSha256'],basis=basis,status='CONTEXT_REVIEWED_CURRENT_WHOLE_PENDING',
                currentSelectedProofSha256='c5272833fa8e1597c93ee20fd5b2bc8fa382ddc9a82e1649108298e78d1caeaa',
                currentWholeCaseRefs=[],rawWarningRetained=True,oldRuntimeReassigned=False,
                productTestsExecuted=0,coverage=None,ptExecutionExempt=False))
    assert len(rows) == len({r['id'] for r in rows}) == 12 and Counter(r['rule'] for r in rows) == Counter(CloseResource=4,DoNotUseThreads=8)
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'contexts.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,contextsSha256=data.sha((OUT/'contexts.json').read_bytes()),
        staticManifestSha256=data.sha(static_path.read_bytes()),selectedProofSha256='c5272833fa8e1597c93ee20fd5b2bc8fa382ddc9a82e1649108298e78d1caeaa',
        rawWarnings=12,sourceLocalContexts=12,wholeF03Accepted=False,whole451Accepted=False,productTestsExecuted=0,
        coverage=None,externalActions=0,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
