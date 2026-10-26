"""Same-value fixture constants and exact Test applicability; no target execution."""
from collections import Counter
from pathlib import Path
import json
import re
import subprocess
from classfile_code_metadata import decode
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10130_uid_oracle_preflight import tokens
from pg10339_result_profile_oracle_post_v2 import folded
from pg10375_media_literal_plan_v2 import restored, class_marker
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes

SOURCE = '3d9f1d9fd395e8cb9456b0a540e1f29bcb87876e'
OUT = data.BASE/'PG10380-media-literal-post-v1'


def check(text,constants,previous):
    if folded(restored(text,constants)) != folded(tokens(previous)):
        raise ValueError('original oracle plumbing, assertions and all fixture tokens required')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    old = data.read_checked(data.BASE/'PG10370-media-correlation-six-compile-v1/manifest.json',
        '83a5412fbceda6c07949301eef954a478b4a7b0ed7a53c453d8939dde39a4168')
    prior_proof = data.read_checked(data.BASE/'PG10372-media-correlation-post-v1/manifest.json',
        'fc7ccf630a34447ef4cf81dd9036f585b74cf808a0cbe51124816bb30a6671c7')
    plan = data.read_checked(data.BASE/'PG10375-media-literal-plan-v2/manifest.json',
        '3f5904257384e70fea53871f8ed3f181b2625a40290c5e0bb975ed4aa1e8ef7b')
    static = data.read_checked(data.BASE/'PG10376-media-literal-static-v1/manifest.json',
        '8d8cc72c4f178f6e69dc1bc1e7b9b55fcbc926353dfffb9883b787a545728554')
    normal_path = data.BASE/'PG10378-media-literal-six-compile-v1/manifest.json'
    normal = json.loads(normal_path.read_bytes())
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == normal['terminal']['actualExit'] == 0
    assert prior_proof['actualExit'] == 0 and old['source'] == plan['source'] == prior_proof['source']
    hashes,previous = normal['begin']['inputHashes'],old['begin']['inputHashes']
    assert set(hashes) == set(previous) and len(normal['jars']) == 6
    changed = {p for p in hashes if hashes[p] != previous[p]}
    assert changed == set(plan['sourceChanges']) == set(static['sourceHashes']) and len(changed) == 3
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src'],cwd=data.ROOT) == b''
    negatives = []
    for p,row in plan['sourceChanges'].items():
        assert row['beforeSha256'] == previous[p] == prior_proof['sourceHashes'][p]
        assert hashes[p] == static['sourceHashes'][p]
        text = (data.ROOT/p).read_text()
        before = subprocess.check_output(['git','show',old['source']+':'+p],cwd=data.ROOT).decode()
        check(text,row['constants'],before)
        for name,literal in row['constants'].items():
            pattern = r'(private\s+static\s+final\s+String\s+'+name+r'\s*=\s*)'+re.escape(literal)
            broken,count = re.subn(pattern,lambda m:m[1]+'"WRONG_LITERAL"',text)
            assert count == 1
            try: check(broken,row['constants'],before)
            except (ValueError,AssertionError): negatives.append(dict(path=p,mutation=name))
            else: raise AssertionError('changed fixture value accepted')
    assert len(negatives) == 17
    for declaration in ('class Synthetic {','final class Synthetic {','final class Synthetic implements AutoCloseable {'):
        assert class_marker(declaration,'Synthetic') == declaration
    marker_negatives = 0
    for text in ('class Other {','class Synthetic {\nclass Synthetic {'):
        try: class_marker(text,'Synthetic')
        except AssertionError: marker_negatives += 1
        else: raise AssertionError('ambiguous declaration accepted')
    assert jar_classes(old) == jar_classes(normal) and len(jar_classes(normal)) == 1843
    before_test,after_test = test_classes(old),test_classes(normal)
    assert set(before_test) == set(after_test)
    differences = {k for k in before_test if before_test[k] != after_test[k]}
    physical = {}
    for module,name in sorted(differences):
        path = Path(normal['jars'][module]['path']).parent/'test-classes'/name
        model = decode(path.read_bytes(),name)
        assert model['sourceFile'] in {Path(p).name for p in changed}
        physical[module+':'+name] = dict(sourceFile=model['sourceFile'],sha256=after_test[(module,name)])
    assert differences
    assert static['actualExit'] == 1 and static['reports']['checkstyle']['findings'] == 0
    assert all(r['processingErrors'] == 0 for r in static['reports'].values())
    rules = Counter(r['rule'] for r in static['reports']['pmd']['details'])
    assert rules == dict(DoNotUseThreads=2,UseProperClassLoader=2)
    applicability = []
    for row in static['reports']['pmd']['details']:
        p, = [p for p in changed if Path(p).stem == row['class']]
        text = (data.ROOT/p).read_text()
        line = text.splitlines()[int(row['beginline'])-1].strip()
        if row['rule'] == 'DoNotUseThreads':
            assert p.endswith('MediaReplayServiceTest.java')
            assert any(v in line for v in ('Executors.newFixedThreadPool(','.invokeAll('))
            assert 'var pool = Executors.newFixedThreadPool(10)' in text and 'try (var codec = codec();' in text
            reason = 'Standalone JUnit worker fixture, lexically try-with owned, not a JavaEE application thread; no runtime ownership qualification.'
        else:
            assert p.endswith('MediaStageFixture.java') and line in {'DataSource.class.getClassLoader(),','Connection.class.getClassLoader(),'}
            assert 'Proxy.newProxyInstance(' in text
            reason = 'Standalone Test fixed JDBC interface Proxy loader, not JavaEE container class loading; no DB/fixture execution.'
        applicability.append(dict(path=p,sha256=hashes[p],line=int(row['beginline']),sourceLine=line,
            rule=row['rule'],disposition='NOT_APPLICABLE_IN_EXACT_TEST_CONTEXT',reason=reason))
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'pmd-applicability.json',applicability)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        sourceHashes={p:hashes[p] for p in changed},normalManifestSha256=data.sha(normal_path.read_bytes()),
        originalOracleSourceProof=dict(source=old['source'],manifest='PG10372-media-correlation-post-v1/manifest.json',
            sha256='fc7ccf630a34447ef4cf81dd9036f585b74cf808a0cbe51124816bb30a6671c7'),
        originalAssertionsAndAllTokensPreserved=True,actualAssertionInvocationCounts=None,
        sameValueStringConstants=17,wrongLiteralMetadataNegatives=negatives,
        classDeclarationMetadataVectors=3,classDeclarationMetadataNegatives=marker_negatives,
        originalFailedPlanToolSha256=data.sha((data.ROOT/'tools/quality/pg10374_media_literal_plan.py').read_bytes()),
        mainClassesUnchanged=1843,allOtherTestClassesUnchanged=len(after_test)-len(differences),physicalTestChanges=physical,
        rawStaticExit=1,rawPmdFindings=4,pmdContextuallyApplicableFindings=0,checkstyleFindings=0,suppressionsAdded=False,
        applicabilitySha256=data.sha((OUT/'pmd-applicability.json').read_bytes()),wholeF03Accepted=False,wholeG03Accepted=False,
        originalProductTestsExecuted=0,originalProductPtStatus='NOT_EXECUTED_HOLD',coverageMeasured=False,
        externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
