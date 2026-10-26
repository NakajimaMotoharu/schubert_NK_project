"""Bind19 identical Test constants and context-specific static findings; no original PT run."""
from collections import Counter
from pathlib import Path
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10130_uid_oracle_preflight import tokens
from pg10298_query_test_literal_plan import restored, BASE
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes

SOURCE = '4c975c3eb1d8d5540805fae642b80d0d5e781c12'
OUT = data.BASE/'PG10304-query-test-literal-post-v1'


def check(text,constants,previous):
    if restored(text,constants) != tokens(previous):
        raise ValueError('original Test expression/assertion tokens required')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal_path = data.BASE/'PG10302-query-test-literal-six-compile-v1/manifest.json'
    normal = json.loads(normal_path.read_bytes())
    old = data.read_checked(data.BASE/'PG10284-query-wire-oracle-six-compile-v1/manifest.json',
        '34ab5aef610fb1352732c926c7ca56438fc38b8434d218196d34f693aa6adbf0')
    plan = data.read_checked(data.BASE/'PG10298-query-test-literal-plan-v1/manifest.json',
        '17887da431084a7c24ed4299f83ebe0d948f0d8268d0e44cc62e07b2e6988aa6')
    static = data.read_checked(data.BASE/'PG10300-query-test-literal-static-v1/manifest.json',
        'c82dc0dfd69a1abfe9fafa4d89d05d58c9c2caea7c57ac6c6cc16f909913272f')
    assert normal['actualExit'] == normal['testsExecuted'] == normal['terminal']['actualExit'] == 0
    assert normal['source'] == SOURCE and len(normal['jars']) == 6
    hashes,prior = normal['begin']['inputHashes'],old['begin']['inputHashes']
    assert set(hashes) == set(prior)
    changed = {p for p,h in hashes.items() if prior[p] != h}
    assert changed == set(plan['sourceChanges']) == set(static['sourceHashes']) and len(changed) == 2
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src'],cwd=data.ROOT) == b''
    root,old_root = [Path(n['jars']['api']['path']).parents[3] for n in (normal,old)]
    constants,assertions,negative = 0,{},[]
    for path,item in plan['sourceChanges'].items():
        assert prior[path] == item['beforeSha256'] and hashes[path] == static['sourceHashes'][path]
        text,previous = (root/path).read_text(),(old_root/path).read_text()
        check(text,item['constants'],previous)
        constants += item['constantCount']
        assertions[path] = sum(t.startswith('assert') for t in tokens(text))
        name,literal = next(iter(item['constants'].items()))
        mutations = [text.replace(literal,'"WRONG_LITERAL"',1),text.replace('assertEquals','assertNotEquals',1)]
        for index,mutated in enumerate(mutations):
            assert mutated != text
            try: check(mutated,item['constants'],previous)
            except (ValueError,AssertionError): negative.append(Path(path).stem+':'+str(index))
            else: raise AssertionError('changed expected/actual expression accepted')
    assert constants == 19 and sorted(assertions.values()) == [33,75] and len(negative) == 4
    assert jar_classes(normal) == jar_classes(old) and len(jar_classes(normal)) == 1843
    before,after = test_classes(old),test_classes(normal)
    assert set(before) == set(after)
    changes = {k for k in before if before[k] != after[k]}
    expected_physical = {('api',p.split('/java/',1)[1].removesuffix('.java')+'.class') for p in changed}
    assert changes == expected_physical and len(changes) == 2
    oracle_path = BASE+'QuestionQueryWireOracle.java'
    oracle_class = ('api',oracle_path.split('/java/',1)[1].removesuffix('.java')+'.class')
    assert hashes[oracle_path] == prior[oracle_path] and after[oracle_class] == before[oracle_class]
    assert static['actualExit'] == 1 and static['reports']['pmd']['findings'] == 9
    assert static['reports']['checkstyle']['findings'] == 0 and all(r['processingErrors'] == 0 for r in static['reports'].values())
    counts = Counter(r['rule'] for r in static['reports']['pmd']['details'])
    assert counts == {'UseProperClassLoader':6,'NullAssignment':1,'AvoidCatchingGenericException':1,'AvoidLiteralsInIfCondition':1}
    dispositions = []
    app = next(p for p in changed if p.endswith('/QuestionQueryApplicationServiceTest.java'))
    lines = (root/app).read_text().splitlines()
    for row in static['reports']['pmd']['details']:
        assert row['class'] == 'QuestionQueryApplicationServiceTest'
        line = lines[int(row['beginline'])-1].strip()
        rule = row['rule']
        if rule == 'UseProperClassLoader':
            assert line in {'DataSource.class.getClassLoader(),','Connection.class.getClassLoader(),','java.sql.PreparedStatement.class.getClassLoader(),'}
            reason = 'Standalone Test exact JDBC interface Proxy loader; not a JavaEE container loader.'
        elif rule == 'NullAssignment':
            assert line == 'args[missing] = null;'
            reason = 'Intentional per-parameter constructor null negative fixture, checked by original assertThrows.'
        elif rule == 'AvoidCatchingGenericException':
            assert line == '} catch (Exception e) {'
            reason = 'Test callback adapts metadata checked Exception to AssertionError; no production catch or normal-success conversion.'
        else:
            assert rule == 'AvoidLiteralsInIfCondition' and 'opens.incrementAndGet() == 2' in line
            reason = 'Explicit Test fault fixture second-open ordinal, not a production magic business threshold.'
        dispositions.append(dict(path=app,sourceSha256=hashes[app],rule=rule,line=int(row['beginline']),
            exactSourceLine=line,disposition='NOT_APPLICABLE_TO_THIS_EXACT_TEST_CONTEXT',reason=reason))
    assert len(dispositions) == 9
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**static['dependencyHashes'],**static['toolAndRuleHashes']}.items())
    assert not list((root/'src').glob('*/target/surefire-reports/TEST-*.xml'))
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'pmd-applicability.json',dispositions)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        normalManifestSha256=data.sha(normal_path.read_bytes()),sourceHashes={p:hashes[p] for p in sorted(changed)},
        constants=19,allOriginalTokensRestored=True,allOriginalAssertionsPreserved=True,assertionCounts=assertions,
        metadataNegativeVectors=negative,mainPhysicalClassesUnchanged=1843,changedPreviousTestPhysicalClasses=2,
        unchangedPreviousTestPhysicalClasses=len(before)-2,oracleSourceAndNormalClassUnchanged=True,
        originalOracleMetadataSource=old['source'],originalOracleMetadataReexecuted=False,
        rawStaticExit=1,rawPmdFindings=9,contextuallyApplicablePmdFindings=0,checkstyleFindings=0,
        applicabilitySha256=data.sha((OUT/'pmd-applicability.json').read_bytes()),suppressionsAdded=False,
        originalProductTestsExecuted=0,originalProductPtStatus='NOT_EXECUTED_HOLD',coverageMeasured=False,
        externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None,
        wholeF03Accepted=False,whole451Accepted=False,bug='BUG-1812',ykt='YKT-1563'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
