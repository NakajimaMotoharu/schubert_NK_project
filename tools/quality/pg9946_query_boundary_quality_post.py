"""Bind precommit static bytes to committed compilation; retain source-specific four-PT history."""
from collections import Counter
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
from pg9906_user_query_oracle_source_post import jar_classes

ROOT = data.ROOT
SOURCE = '35b059820f010ddca25cba5b6d496a65a99e8887'
RUNTIME_SOURCE = '7cdcf0029cf111d63498ba4de383bbbf494f91a1'
OUT = data.BASE/'PG9946-query-boundary-quality-post-v1'
PREFIX = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/'
USER = PREFIX+'admin/UserQueryRequestTest.java'
NEW = PREFIX+'admin/UserQueryResponseBoundaryTest.java'
LOG = PREFIX+'log/LogRequestTest.java'


def tokens(text):
    body = ''.join(m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*')))
    return body[body.index('classLogRequestTest{'):]


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal_path = data.BASE/'PG9944-log-style-six-compile-v1/manifest.json'
    normal = data.read_checked(normal_path,'9bd924d4baa1720b896451c96eee53c42f885afa213b8bca618ea4c4f9cd262d')
    previous = data.read_checked(data.BASE/'PG9932-user-query-response-six-compile-v1/manifest.json',
        '8fab1c6ae6fe984af5886d984a722ce6db13f958c83dcae6fe4ff058c2eaa27f')
    static_path = data.BASE/'PG9942-log-style-precommit-static-v1/manifest.json'
    static = data.read_checked(static_path,'cdc232bf07d5666d0f05e5763409d0ff6ec1dcdf33af7a8457e2c48caacf0fe5')
    pt = data.read_checked(data.BASE/'PG9938-user-query-response-post-v1/manifest.json',
        'bfc77cc75a8f7764ad4c64a7955481f3e1cd7f10031c508b6f3e1902271062c3')
    assert normal['actualExit'] == previous['actualExit'] == pt['actualExit'] == 0
    assert normal['source'] == SOURCE and previous['source'] == pt['source'] == RUNTIME_SOURCE
    assert normal['testsExecuted'] == 0 and static['source'] is None and static['baseSource'] == RUNTIME_SOURCE
    assert static['qualification'] == 'DECLARED_WORKTREE_HASHES_STATIC_ONLY'
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in hashes.items())
    assert set(hashes) == set(previous['begin']['inputHashes'])
    assert {p for p,h in hashes.items() if h != previous['begin']['inputHashes'][p]} == {LOG}
    assert all(hashes[p] == h for p,h in static['sourceHashes'].items())
    assert static['sourceHashes'][LOG] == '283303adafd8fd708a2a82c1223ba6554aec62bb10b48af3d5efa7532e71c1fd'
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**static['dependencyHashes'],**static['toolAndRuleHashes']}.items())
    before,after = jar_classes(previous),jar_classes(normal)
    assert before == after and len(after) == 1843
    old_classes,new_classes = {},{}
    for witness,target in ((previous,old_classes),(normal,new_classes)):
        for module,item in witness['jars'].items():
            root = Path(item['path']).parent/'test-classes'
            for file in root.rglob('*.class'):
                target[(module,file.relative_to(root).as_posix())] = data.sha(file.read_bytes())
    assert set(old_classes) == set(new_classes) and len(new_classes) == 1919
    differences = [key for key in old_classes if old_classes[key] != new_classes[key]]
    assert differences == [('api','dev/codex/schubert/nk/api/application/log/LogRequestTest.class')]
    assert hashes[NEW] == previous['begin']['inputHashes'][NEW]
    old = subprocess.check_output(['git','show',RUNTIME_SOURCE+':'+LOG],cwd=ROOT).decode()
    text = (ROOT/LOG).read_text()
    declaration = 'private static final String SEARCH_LAYOUT = "LGSREQ01";'
    assert text.count(declaration) == 1
    expanded = LEX.sub(lambda m:'"LGSREQ01"' if m.group() == 'SEARCH_LAYOUT' else m.group(),text.replace(declaration,''))
    assert tokens(old) == tokens(expanded)
    xml = data.BASE/'PG9942-log-style-precommit-static-v1/pmd.xml'
    assert data.sha(xml.read_bytes()) == static['reports']['pmd']['sha256']
    by_name = {Path(p).name:p for p in (USER,LOG,NEW)}
    applicability = []
    counts = Counter()
    for file in ET.parse(xml).getroot().iter():
        if file.tag.rpartition('}')[2] != 'file':
            continue
        path = by_name[Path(file.attrib['name']).name]
        for node in file:
            if node.tag.rpartition('}')[2] != 'violation':
                continue
            rule,line = node.attrib['rule'],int(node.attrib['beginline'])
            source_line = (ROOT/path).read_text().splitlines()[line-1]
            assert path != NEW
            if rule == 'DoNotUseThreads':
                assert 'Executors.' in source_line or 'pool.submit(' in source_line
                reason = 'Exact standalone host JUnit fixture, not a managed J2EE component. Existing owned pool/future lifecycle assertions unchanged; no worker invoked in this post.'
            else:
                assert rule == 'CloseResource' and path == USER and 'var actual = canonical.fields().get(i);' in source_line
                assert 'try (var canonical = request.canonical(actor);' in (ROOT/USER).read_text()
                reason = 'Borrowed canonical field is released by the enclosing try-with CanonicalRequest; do not separately consume the borrowed value.'
            counts[rule] += 1
            applicability.append(dict(path=path,sourceSha256=hashes[path],line=line,rule=rule,
                status='NOT_APPLICABLE_TO_THIS_EXACT_TEST_STATEMENT',reason=reason))
    assert dict(counts) == {'DoNotUseThreads':4,'CloseResource':1}
    assert static['actualExit'] == 1 and static['reports']['pmd']['findings'] == 5 and static['reports']['checkstyle']['findings'] == 0
    assert all(r['processingErrors'] == 0 for r in static['reports'].values())
    assert not any('assertThrows(RuntimeException.class' in (ROOT/p).read_text() for p in (USER,LOG,NEW))
    java_paths = {p for p in hashes if '/java/' in p and p.endswith('.java')}
    assert len(java_paths) == 1797 and len([p for p in java_paths if '/src/main/java/' in p]) == 965
    assert pt['tests'] == 4 and pt['suites'] == 1 and not pt['targetUnitFour100']
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'pmd-applicability.json',applicability)
    value = dict(actualExit=0,source=SOURCE,invocation=invocation,normalManifestSha256=data.sha(normal_path.read_bytes()),
        precommitStaticManifestSha256=data.sha(static_path.read_bytes()),precommitStaticSourceWasNull=True,
        staticSourceHashesExactlyMatchCommittedCompilation=True,normalTestExecutionCount=0,
        mainClassesUnchanged=1843,testClasses=1919,changedTestClasses=differences,
        newPureTestSourceAndClassUnchanged=True,logBodyTokensEquivalent=True,unicodeLiteralsReinterpreted=False,
        rawStaticExit=1,rawPmdFindings=5,pmdApplicableFindings=0,checkstyleFindings=0,suppressionsAdded=False,
        applicabilitySha256=data.sha((OUT/'pmd-applicability.json').read_bytes()),
        historicalFourPtSource=RUNTIME_SOURCE,historicalFourPtManifestSha256='bfc77cc75a8f7764ad4c64a7955481f3e1cd7f10031c508b6f3e1902271062c3',
        historicalFourPtReexecuted=False,historicalFourPtReassignedToCurrentSource=False,
        sourceSpecificRuntimeResult=dict(source=RUNTIME_SOURCE,tests=4,suites=1,counters=pt['counters'],methodCounters=pt['methodCounters']),
        currentSourceProductTestsExecuted=0,databaseBackedUserAndLogTests='NOT_EXECUTED_HOLD',
        currentJavaPaths=1797,currentMainPaths=965,currentTestPaths=832,
        wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None,
        bugs=['BUG1781','BUG1782'],horizontal=['YKT1532','YKT1533'])
    data.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,mainUnchanged=1843,logStyleClassOnlyChanged=True,rawPmd=5,applicablePmd=0,cs=0,
        currentSourcePt=0,sourceSpecificFourPt=4,manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
