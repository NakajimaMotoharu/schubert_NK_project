"""Exact Test constants/context binding; assertion invocations are not inferred from token prefixes."""
from collections import Counter
from pathlib import Path
import json
import re
import subprocess
from classfile_code_metadata import decode
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
from pg10342_result_profile_literal_plan import restored
from pg10339_result_profile_oracle_post_v2 import folded
from pg10332_result_profile_oracle_plan import PREDICATE
from pg10130_uid_oracle_preflight import tokens
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes

SOURCE = 'b120eebab4bbe1f8d02c245a06e51e0783a616c5'
OUT = data.BASE/'PG10348-result-profile-literal-post-v1'
INTS = {
    'UserCommandServiceTest.java': {'FIXTURE_UNKNOWN_HASH_MODE':1,'FIXTURE_ARGUMENT_FAILURE_MODE':2},
    'SessionOperationTokenLifecycleTest.java': {'EXPECTED_PENDING_TOKEN_CAPACITY':10}}


def reconstructed(text,constants,ints):
    values = restored(text,constants)
    for name,value in ints.items():
        pattern = tokens('private static final int '+name+' = '+str(value)+';')
        places = [i for i in range(len(values)) if values[i:i+len(pattern)] == pattern]
        if len(places) != 1: raise ValueError('exact independent fixture integer required')
        i, = places
        values[i:i+len(pattern)] = []
        assert values.count(name) == (2 if name == 'EXPECTED_PENDING_TOKEN_CAPACITY' else 1)
        values = [t for token in values for t in (tokens(str(value)) if token == name else [token])]
    return folded(values)


def check(text,constants,ints,previous):
    if reconstructed(text,constants,ints) != folded(tokens(previous)):
        raise ValueError('all original source tokens and independent predicates required')
    if 'code.usesSuccessProfile()' in text:
        raise ValueError('Test expected side must not use production classifier')


def declaration_damage(text,kind,name,literal):
    pattern = re.compile(r'(private\s+static\s+final\s+'+kind+r'\s+'+name+r'\s*=\s*)'+re.escape(literal))
    matches = list(pattern.finditer(text))
    assert len(matches) == 1
    m, = matches
    return text[:m.start()]+m.group(1)+('"WRONG_VALUE"' if kind == 'String' else '999')+text[m.end():]


def predicate_span(text):
    matches = [m for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
    values = [m.group() for m in matches]
    pattern = tokens(PREDICATE)
    i = next(i for i in range(len(values)) if values[i:i+len(pattern)] == pattern)
    return matches[i].start(),matches[i+len(pattern)-1].end()


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal_path = data.BASE/'PG10346-result-profile-literal-six-compile-v1/manifest.json'
    normal = json.loads(normal_path.read_bytes())
    old = data.read_checked(data.BASE/'PG10336-result-profile-oracle-six-compile-v1/manifest.json',
        '2e5714ab3e64348997a1ca1de9a8e8519e096f91bb9bfa366b58ec4158a9f34e')
    plan = data.read_checked(data.BASE/'PG10342-result-profile-literal-plan-v1/manifest.json',
        'bf587753ddfecfb6be27de953441b7ce156fb2ba08d19ce911fa70b4b7ecc988')
    static = data.read_checked(data.BASE/'PG10345-result-profile-literal-static-v2/manifest.json',
        'b77aec448705426e0aaddb887721a24bdebd571fa5bbd127896783b9a8ca1045')
    correction = data.read_checked(data.BASE/'PG10349-assert-prefix-metric-correction-v1/manifest.json',
        'a9546154434952712380f83b4752af700ca0d62895bcfc9b5537ba9d8527e811')
    assert correction['actualExit'] == 0 and correction['actualAssertionInvocationCounts'] is None
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == normal['terminal']['actualExit'] == 0
    assert len(normal['jars']) == 6
    hashes,prior = normal['begin']['inputHashes'],old['begin']['inputHashes']
    assert set(hashes) == set(prior)
    changed = {p for p,h in hashes.items() if prior[p] != h}
    assert changed == set(plan['sourceChanges']) == set(static['sourceHashes']) and len(changed) == 5
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src'],cwd=data.ROOT) == b''
    root,old_root = [Path(n['jars']['api']['path']).parents[3] for n in (normal,old)]
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((root/p).read_bytes()) == h for p,h in hashes.items())
    prefixes,negatives,independent_predicates = {},[],0
    for p,row in plan['sourceChanges'].items():
        assert prior[p] == row['beforeSha256'] and hashes[p] == static['sourceHashes'][p]
        text,previous = (root/p).read_text(),(old_root/p).read_text()
        ints = INTS.get(Path(p).name,{})
        check(text,row['constants'],ints,previous)
        prefixes[p] = sum(t.startswith('assert') for t in tokens(text))
        assert prefixes[p] == sum(t.startswith('assert') for t in tokens(previous))
        values,pattern = tokens(text),tokens(PREDICATE)
        independent_predicates += sum(values[i:i+len(pattern)] == pattern for i in range(len(values)))
        name,literal = next(iter(row['constants'].items()))
        low,high = predicate_span(text)
        mutations = [
            ('constant-value',declaration_damage(text,'String',name,literal)),
            ('assert-method',text.replace('assertEquals','assertNotEquals',1)),
            ('profile-identity',text[:low]+text[low:high].replace('IDEMPOTENT_SUCCESS','FORBIDDEN')+text[high:]),
            ('production-classifier',text[:low]+'code.usesSuccessProfile()'+text[high:])]
        mutations += [('int-'+n,declaration_damage(text,'int',n,str(value))) for n,value in ints.items()]
        for label,mutated in mutations:
            assert mutated != text
            try: check(mutated,row['constants'],ints,previous)
            except (ValueError,AssertionError): negatives.append(dict(path=p,mutation=label))
            else: raise AssertionError('incorrect fixture or expected classifier accepted')
    assert len(negatives) == 23 and independent_predicates == 12
    assert jar_classes(normal) == jar_classes(old) and len(jar_classes(normal)) == 1843
    before,after = test_classes(old),test_classes(normal)
    assert set(before) == set(after)
    differences = {k for k in before if before[k] != after[k]}
    physical = {}
    for module,name in sorted(differences):
        file = Path(normal['jars'][module]['path']).parent/'test-classes'/name
        model = decode(file.read_bytes(),name)
        assert model['sourceFile'] in {Path(p).name for p in changed}
        physical[module+':'+name] = dict(sha256=after[(module,name)],sourceFile=model['sourceFile'])
    assert len(differences) == 5
    assert static['actualExit'] == 1 and static['reports']['pmd']['findings'] == 26
    assert static['reports']['checkstyle']['findings'] == 0 and all(r['processingErrors'] == 0 for r in static['reports'].values())
    rules = Counter(r['rule'] for r in static['reports']['pmd']['details'])
    assert rules == dict(DoNotUseThreads=17,NullAssignment=5,UseProperClassLoader=2,CloseResource=1,CompareObjectsWithEquals=1)
    borrowed = next(p for p in changed if p.endswith('/UserMutationReplayServiceTest.java'))
    borrowed_text = (root/borrowed).read_text()
    assert 'try (var original = request(layout, target, expected, flag, SOURCE, CONTEXT);' in borrowed_text
    assert 'var retry = request(layout, target, expected, flag, RETRY, NEW_CONTEXT)) {' in borrowed_text
    dispositions = []
    for row in static['reports']['pmd']['details']:
        p, = [p for p in changed if Path(p).stem == row['class']]
        text = (root/p).read_text()
        line = text.splitlines()[int(row['beginline'])-1].strip()
        rule = row['rule']
        if rule == 'DoNotUseThreads':
            assert 'import org.junit.jupiter.api.Test;' in text
            assert any(s in line for s in ('Executors.newFixedThreadPool(','.submit(','.invokeAll('))
            reason = 'Standalone JUnit concurrency fixture, not Production JavaEE application thread creation; no runtime/liveness certification.'
        elif rule == 'NullAssignment':
            assert line in {'args[i] = null;','f.clock.value = null;'}
            reason = 'Deliberate constructor/null-clock negative Test fixture, not Production nullable state introduced by this change.'
        elif rule == 'UseProperClassLoader':
            assert line == 'DataSource.class.getClassLoader(),'
            reason = 'Standalone Test exact interface Proxy loader, not JavaEE container loading.'
        elif rule == 'CloseResource':
            assert p == borrowed and line == 'for (var current : List.of(original, retry)) {'
            reason = 'Borrowed aliases of original/retry both lexically owned by enclosing try-with; do not close the aliases independently.'
        else:
            assert rule == 'CompareObjectsWithEquals' and p == borrowed and line == 'current == original ? CONTEXT : NEW_CONTEXT,'
            reason = 'Intentional Test input identity selects original vs retry context, not value equality.'
        dispositions.append(dict(path=p,sourceSha256=hashes[p],line=int(row['beginline']),exactSourceLine=line,
            rule=rule,disposition='NOT_APPLICABLE_TO_THIS_EXACT_TEST_CONTEXT',reason=reason))
    assert len(dispositions) == 26
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**static['dependencyHashes'],**static['toolAndRuleHashes']}.items())
    assert not list((root/'src').glob('*/target/surefire-reports/TEST-*.xml'))
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'pmd-applicability.json',dispositions)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        normalManifestSha256=data.sha(normal_path.read_bytes()),sourceHashes={p:hashes[p] for p in sorted(changed)},
        stringConstants=35,integerConstants=3,allOriginalTokensRestored=True,allOriginalAssertionsPreserved=True,
        assertPrefixTokenOccurrences=prefixes,actualAssertionInvocationCounts=None,
        assertionMetricMeaning='ASSERT_PREFIX_TOKEN_OCCURRENCES_NOT_ASSERTION_INVOCATIONS',
        independentSuccessPredicatesUnchanged=12,metadataNegativeVectors=negatives,
        allMainPhysicalClassesUnchanged=1843,changedPreviousTestPhysicalClasses=5,
        unchangedPreviousTestPhysicalClasses=len(before)-5,physicalTestChanges=physical,
        rawStaticExit=1,rawPmdFindings=26,contextuallyApplicablePmdFindings=0,checkstyleFindings=0,
        applicabilitySha256=data.sha((OUT/'pmd-applicability.json').read_bytes()),suppressionsAdded=False,
        originalProductTestsExecuted=0,originalProductPtStatus='NOT_EXECUTED_HOLD',coverageMeasured=False,
        newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,
        effortPercent=None,externalActions=0,bugs=['BUG-1819','BUG-1820','BUG-1821']))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
