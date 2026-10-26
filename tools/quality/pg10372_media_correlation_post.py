"""Exact UUID-only oracle source change; metadata negatives, no target execution."""
from collections import Counter
from pathlib import Path
import subprocess
from classfile_code_metadata import decode
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10130_uid_oracle_preflight import tokens
from pg10339_result_profile_oracle_post_v2 import folded
from pg10366_media_oracle_plan import PATHS, original, transformed
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes

SOURCE = '0867302e7c5eb95163213cb6340ac86f6898e137'
OUT = data.BASE/'PG10372-media-correlation-post-v1'


def check(path,text):
    if folded(tokens(text)) != folded(tokens(transformed(path,original(path)))):
        raise ValueError('only declared correlation plumbing and constant string formatting allowed')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    old = data.read_checked(data.BASE/'PG10346-result-profile-literal-six-compile-v1/manifest.json',
        'c7119960eb3cbf1514d58454c9f56e07780757339f4294d49ae82181acf24965')
    normal = data.read_checked(data.BASE/'PG10370-media-correlation-six-compile-v1/manifest.json',
        '83a5412fbceda6c07949301eef954a478b4a7b0ed7a53c453d8939dde39a4168')
    static = data.read_checked(data.BASE/'PG10368-media-correlation-static-v1/manifest.json',
        '2716a22b7190801d5e39fce691a91415a64d4ea77a35381fdff1cb4bc0bdf994')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == normal['terminal']['actualExit'] == 0
    hashes,prior = normal['begin']['inputHashes'],old['begin']['inputHashes']
    assert set(hashes) == set(prior) and len(normal['jars']) == 6
    changed = {p for p in hashes if hashes[p] != prior[p]}
    assert changed == set(PATHS) == set(static['sourceHashes'])
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src'],cwd=data.ROOT) == b''
    negatives = []
    replacements = {
        'MediaReplayFixture.java':('put(body, 60, correlation.toString());','put(body, 60, response.toString());'),
        'MediaStageFixture.java':('request.header().messageId(),','MediaRequest.decode(request),'),
        'MediaReplayServiceTest.java':('request.header().messageId(),','NEXT,')}
    for path in PATHS:
        text = (data.ROOT/path).read_text()
        check(path,text)
        a,b = replacements[Path(path).name]
        assert a in text
        corrupted = text.replace(a,b,1)
        try: check(path,corrupted)
        except ValueError: negatives.append(dict(path=path,mutation='wrong-or-coupled-correlation'))
        else: raise AssertionError('incorrect correlation source accepted')
        assert static['sourceHashes'][path] == hashes[path]
    production = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/media/MediaRequest.java'
    code = (data.ROOT/production).read_text()
    assert 'this.retainedHeader = header;' in code and 'return new MediaRequest(kind, request.header(), values);' in code
    assert 'public CommonHeader header() {\n    return retainedHeader;\n  }' in code
    before_main,after_main = jar_classes(old),jar_classes(normal)
    assert before_main == after_main and len(after_main) == 1843
    before_test,after_test = test_classes(old),test_classes(normal)
    assert set(before_test) == set(after_test)
    differences = {k for k in before_test if before_test[k] != after_test[k]}
    physical = {}
    for module,name in sorted(differences):
        path = Path(normal['jars'][module]['path']).parent/'test-classes'/name
        model = decode(path.read_bytes(),name)
        assert model['sourceFile'] in {Path(p).name for p in PATHS}
        physical[module+':'+name] = dict(sourceFile=model['sourceFile'],sha256=after_test[(module,name)])
    assert differences
    assert static['actualExit'] == 1 and static['reports']['checkstyle']['findings'] == 0
    assert all(r['processingErrors'] == 0 for r in static['reports'].values())
    raw = Counter(r['rule'] for r in static['reports']['pmd']['details'])
    assert raw == dict(AvoidDuplicateLiterals=17,DoNotUseThreads=2,UseProperClassLoader=2)
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        sourceHashes={p:hashes[p] for p in PATHS},normalManifestSha256='83a5412fbceda6c07949301eef954a478b4a7b0ed7a53c453d8939dde39a4168',
        originalSource='b120eebab4bbe1f8d02c245a06e51e0783a616c5',allNonCorrelationTokensPreserved=True,
        compileTimeStringJoiningOnly=True,allOriginalAssertionsPreserved=True,actualAssertionInvocationCounts=None,
        replayWireCallers=10,replayCallerOriginalCurrentInputs=dict(request=9,current=1),stageDecoderRemoved=True,
        independentCorrelationMetadataNegatives=negatives,mainClassesUnchanged=len(after_main),
        allOtherTestClassesUnchanged=len(after_test)-len(differences),physicalTestChanges=physical,
        rawPmdFindings=21,rawPmdRules=dict(raw),rawStaticExit=1,checkstyleFindings=0,
        pmdApplicabilityComplete=False,wholeF03Accepted=False,wholeG03Accepted=False,
        bug='BUG-1822',ykt='YKT-1573',originalProductTestsExecuted=0,originalProductPtStatus='NOT_EXECUTED_HOLD',
        coverageMeasured=False,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
