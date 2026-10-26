"""Verify six literal mappings and exact source preservation; never load held target Tests."""
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
from classfile_code_metadata import decode
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical
from pg10406_result_code_literal_plan import transformed, CODES
from pg10410_result_code_literal_plan import restored
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes

SOURCE = 'b8234ad5a1403e944acaf8e13f1e5f07a22309bd'
OUT = data.BASE/'PG10416-result-code-literal-post-v1'


def check(text,previous,constants):
    plain = ' '.join(restored(text,constants)) if constants else text
    if canonical(plain) != canonical(transformed(previous)):
        raise ValueError('only independent result mapping and same-value constants allowed')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    plan = data.read_checked(data.BASE/'PG10406-result-code-literal-plan-v1/manifest.json',
        'f247320941366dd0700ab3cbf8eb6601e00b6732cb2234c72b8526bc9ce4991f')
    literals = data.read_checked(data.BASE/'PG10410-result-code-literal-plan-v1/manifest.json',
        '55d6a1a5f6bc7c127c5838c4b130b4e6bcc5ec94aa9dd99833ff83ef07439301')
    static = data.read_checked(data.BASE/'PG10412-result-code-final-static-v1/manifest.json',
        '73c9f0237b0e32e2c8a006c700b4d95af35c4892519003ea77b192a22bd841c0')
    normal = data.read_checked(data.BASE/'PG10414-result-code-six-compile-v1/manifest.json',
        '83e2904ee2a0ee50ef0efab4916f73f53aaa0660cd8b3a2555b2eec21477da35')
    old = data.read_checked(data.BASE/'PG10396-role-literal-six-compile-v1/manifest.json',
        '42e446d87c251b819592758cbadeee1d5ba4e785d91269edfb6ac873f71b8b5c')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == normal['terminal']['actualExit'] == 0
    hashes,previous_hashes = normal['begin']['inputHashes'],old['begin']['inputHashes']
    assert set(hashes) == set(previous_hashes) and len(normal['jars']) == 6
    changed = {p for p,h in hashes.items() if previous_hashes[p] != h}
    assert changed == set(plan['sourceChanges']) == set(static['sourceHashes']) and len(changed) == 6
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src'],cwd=data.ROOT) == b''
    approved = subprocess.check_output(['git','show','origin/main:'+plan['approvedUi']],cwd=data.ROOT)
    assert data.sha(approved) == plan['approvedUiSha256'] and all('| `'+v+'` |' in approved.decode() for v in CODES.values())
    negatives,mappings = [],{}
    for p,row in plan['sourceChanges'].items():
        text = (data.ROOT/p).read_text()
        before = subprocess.check_output(['git','show',plan['source']+':'+p],cwd=data.ROOT).decode()
        assert data.sha(before.encode()) == previous_hashes[p] == row['beforeSha256']
        assert static['sourceHashes'][p] == hashes[p]
        constants = literals['sourceChanges'].get(p,{}).get('constants',{})
        check(text,before,constants)
        start = text.rfind('private static String oracleResultCode(ResultCode code)')
        assert start > 0
        helper = text[start:]
        matches = list(re.finditer(r'case\s+(\w+)\s*->\s*([^;]+);',helper))
        observed = {}
        for match in matches:
            expression = match[2].strip()
            value = json.loads(constants.get(expression,expression))
            assert match[1] not in observed
            observed[match[1]] = value
            damaged = text[:start+match.start(2)]+'"9999"'+text[start+match.end(2):]
            try: check(damaged,before,constants)
            except (ValueError,AssertionError): negatives.append(dict(path=p,mutation='result-'+match[1]))
            else: raise AssertionError('incorrect result literal accepted')
        assert observed == CODES and len(observed) == 12
        mappings[p] = observed
        coupled = text[:start]+'private static String oracleResultCode(ResultCode code) { return code.wireValue(); }\n}\n'
        try: check(coupled,before,constants)
        except (ValueError,AssertionError): negatives.append(dict(path=p,mutation='production-encoder-reintroduced'))
        else: raise AssertionError('production encoder dependency accepted')
        for name,literal in constants.items():
            pattern = r'(private\s+static\s+final\s+String\s+'+name+r'\s*=\s*)'+re.escape(literal)
            damaged,count = re.subn(pattern,lambda m:m[1]+'"WRONG_LITERAL"',text)
            assert count == 1
            try: check(damaged,before,constants)
            except (ValueError,AssertionError): negatives.append(dict(path=p,mutation=name))
            else: raise AssertionError('changed fixture constant accepted')
    assert len(negatives) == 87
    assert jar_classes(old) == jar_classes(normal) and len(jar_classes(normal)) == 1843
    before_test,after_test = test_classes(old),test_classes(normal)
    physical = {}
    for module,name in set(before_test)|set(after_test):
        if before_test.get((module,name)) == after_test.get((module,name)): continue
        source_normal = normal if (module,name) in after_test else old
        file = Path(source_normal['jars'][module]['path']).parent/'test-classes'/name
        model = decode(file.read_bytes(),name)
        assert model['sourceFile'] in {Path(p).name for p in changed}
        physical[module+':'+name] = dict(sourceFile=model['sourceFile'],beforeSha256=before_test.get((module,name)),sha256=after_test.get((module,name)))
    assert static['actualExit'] == 1 and static['reports']['checkstyle']['findings'] == 0
    assert all(v['processingErrors'] == 0 for v in static['reports'].values())
    rules = Counter(r['rule'] for r in static['reports']['pmd']['details'])
    assert rules == dict(DoNotUseThreads=8,NullAssignment=3,UseProperClassLoader=3,CloseResource=2,CompareObjectsWithEquals=1)
    applicability = []
    for row in static['reports']['pmd']['details']:
        p, = [p for p in changed if Path(p).stem == row['class']]
        text = (data.ROOT/p).read_text()
        line = text.splitlines()[int(row['beginline'])-1].strip()
        rule = row['rule']
        if rule == 'DoNotUseThreads':
            assert any(v in line for v in ('Executors.newFixedThreadPool(','.submit('))
            reason = 'Standalone JUnit executor fixture, not Production JavaEE thread creation; no liveness or original Test execution certified.'
        elif rule == 'NullAssignment':
            assert line == 'args[i] = null;'
            reason = 'Deliberate null-parameter negative Test fixture, not nullable Production state introduced.'
        elif rule == 'UseProperClassLoader':
            assert line in {'Connection.class.getClassLoader(),','PreparedStatement.class.getClassLoader(),','ResultSet.class.getClassLoader(),'}
            reason = 'Standalone fixed JDBC interface Proxy loader, not JavaEE container class loading; no actual connection invoked.'
        elif rule == 'CompareObjectsWithEquals':
            assert line == 'current == original ? CONTEXT : NEW_CONTEXT,'
            reason = 'Test input object identity chooses the associated fixed context; value equality is not the intended property.'
        elif p.endswith('UserMutationReplayServiceTest.java'):
            assert line == 'for (var current : List.of(original, retry)) {'
            assert 'try (var original = request(' in text and 'var retry = request(' in text
            reason = 'Borrowed aliases original/retry are lexically owned by enclosing try-with; do not separately close aliases.'
        else:
            assert p.endswith('LoginReplayServiceTest.java') and row['variable'] == 'closed'
            assert 'closed.close();' in text and text.index('closed.close();') > text.index(line)
            reason = 'Explicitly closed Test codec intentionally retained for closed-resource negative assertions; no key-erasure/lifetime runtime witness executed.'
        applicability.append(dict(path=p,sha256=hashes[p],line=int(row['beginline']),sourceLine=line,rule=rule,
            disposition='NOT_APPLICABLE_IN_EXACT_TEST_CONTEXT',reason=reason))
    role = data.read_checked(data.BASE/'PG10402-role-view-post-v1/manifest.json',
        '08802be2aec7b9a6794526549d9cf9a19bbde0a0c979d253ec9908cc6ad40d93')
    assert all(hashes[p] == h for p,h in role['sourceHashes'].items())
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'pmd-applicability.json',applicability)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        sourceHashes={p:hashes[p] for p in changed},normalManifestSha256='83e2904ee2a0ee50ef0efab4916f73f53aaa0660cd8b3a2555b2eec21477da35',
        approvedUiSha256=plan['approvedUiSha256'],literalCodeMappings=mappings,mappingEntries=72,
        metadataNegativeVectors=negatives,metadataNegativeCount=87,independentResultCalls=15,sameValueStringConstants=9,
        allOriginalAssertionsAndOtherTokensPreserved=True,actualAssertionInvocationCounts=None,
        mainClassesUnchanged=1843,physicalTestChanges=physical,
        otherTestClassesUnchanged=sum(before_test.get(k) == h for k,h in after_test.items()),
        testClassesBefore=len(before_test),testClassesAfter=len(after_test),
        rawStaticExit=1,rawPmdFindings=17,contextuallyApplicableFindings=0,checkstyleFindings=0,suppressionsAdded=False,
        applicabilitySha256=data.sha((OUT/'pmd-applicability.json').read_bytes()),
        priorRoleRuntimeReference=dict(source=role['source'],manifest='PG10402-role-view-post-v1/manifest.json',
            sha256='08802be2aec7b9a6794526549d9cf9a19bbde0a0c979d253ec9908cc6ad40d93',
            roleSourcesAndMainBytesUnchanged=True,runtimeReassignedToNewGlobalSource=False),
        productTestsExecuted=0,originalProductPtStatus='NOT_EXECUTED_HOLD',coverageMeasured=False,
        wholeF03Accepted=False,wholeG03Accepted=False,whole451Accepted=False,externalActions=0,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
