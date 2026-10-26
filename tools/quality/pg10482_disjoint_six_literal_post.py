"""Reversible six-source changes, nested static completeness and immutable Main bytes."""
from collections import Counter
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
from classfile_code_metadata import decode
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical
from pg10477_disjoint_six_literal_plan_v2 import restored
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes

SOURCE = 'a82c44a678cce0ded7fda59cf84a2276ded51e30'
OUT = data.BASE/'PG10482-disjoint-six-literal-post-v1'
EXPECTED_RULES = dict(AvoidDuplicateLiterals=50,AvoidLiteralsInIfCondition=4,DoNotUseThreads=16,AvoidUsingVolatile=10)


def check(text,previous,constants):
    if canonical(' '.join(restored(text,constants))) != canonical(previous):
        raise ValueError('exact same-value constants and formatting only')


def rule_contract(value):
    if value != EXPECTED_RULES or sum(value.values()) != 80:
        raise ValueError('all file-level nested class findings required')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    plan = data.read_checked(data.BASE/'PG10477-disjoint-six-literal-plan-v2-v1/manifest.json',
        'c5fecebd4b814e14e8f0d487e36ce062340da72f333085168f1f132e101fb5f5')
    static = data.read_checked(data.BASE/'PG10478-disjoint-six-literal-static-v1/manifest.json',
        '1cae3c256e3442adace66f78b521f981b119754d1edfeaef03ac0c2a4f73e4bc')
    normal = data.read_checked(data.BASE/'PG10480-disjoint-six-literal-compile-v1/manifest.json',
        '11ca97be3c74142b3acfcac9c2612c0dd9230be17a4d91c5140a2abc28fbb179')
    old = data.read_checked(data.BASE/'PG10462-topbar-contract-six-compile-v1/manifest.json',
        '1b73c7462722d9a221a56daad3cb9d9efcbbee6a4385926d0ea9c379bec7d15b')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    hashes,old_hashes = normal['begin']['inputHashes'],old['begin']['inputHashes']
    changed = {p for p,h in hashes.items() if old_hashes[p] != h}
    assert changed == set(plan['sourceChanges']) == set(static['sourceHashes']) and len(changed) == 6
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src'],cwd=data.ROOT) == b''
    negatives = []
    for p,row in plan['sourceChanges'].items():
        previous = subprocess.check_output(['git','show',plan['baseSource']+':'+p],cwd=data.ROOT).decode()
        assert data.sha(previous.encode()) == row['beforeSha256'] == old_hashes[p]
        text = (data.ROOT/p).read_text()
        assert hashes[p] == static['sourceHashes'][p]
        check(text,previous,row['constants'])
        for name,constant in row['constants'].items():
            pattern = r'(private\s+static\s+final\s+'+constant['type']+r'\s+'+name+r'\s*=\s*)'+re.escape(constant['literal'])
            wrong = '"WRONG_LITERAL"' if constant['type'] == 'String' else '9999'
            damaged,count = re.subn(pattern,lambda m:m[1]+wrong,text)
            assert count == 1
            try:
                check(damaged,previous,row['constants'])
            except ValueError:
                negatives.append(dict(path=p,constant=name))
            else:
                raise AssertionError('changed original Test literal accepted')
    assert len(negatives) == 54
    original = ET.parse(data.BASE/'PG10394-role-literal-static-v1/pmd.xml').getroot()
    original_rows = []
    for file in original:
        path = str(Path(file.get('name','')).relative_to(data.ROOT)) if file.get('name') else None
        if path in changed:
            original_rows.extend(dict(path=path,**dict(n.attrib)) for n in file)
    rules = dict(Counter(r['rule'] for r in original_rows))
    rule_contract(rules)
    assert len([r for r in original_rows if '.' in r['class']]) == 11
    count_negatives = []
    for label,mutated in [
        ('nested-literal-missing',dict(rules,AvoidDuplicateLiterals=49)),
        ('nested-volatile-missing',dict(rules,AvoidUsingVolatile=0)),
        ('outer-only69',dict(AvoidDuplicateLiterals=49,AvoidLiteralsInIfCondition=4,DoNotUseThreads=16)),
        ('thread-incomplete',dict(rules,DoNotUseThreads=14))]:
        try:
            rule_contract(mutated)
        except ValueError:
            count_negatives.append(label)
        else:
            raise AssertionError('incomplete file-level findings accepted')
    assert static['actualExit'] == 1 and static['reports']['pmd']['findings'] == 26
    assert dict(Counter(r['rule'] for r in static['reports']['pmd']['details'])) == dict(DoNotUseThreads=16,AvoidUsingVolatile=10)
    assert static['reports']['checkstyle']['findings'] == 0 and all(r['processingErrors']==0 for r in static['reports'].values())
    applicability = []
    for row in static['reports']['pmd']['details']:
        p, = [p for p in changed if Path(p).stem == row['class'].split('.')[0]]
        text = (data.ROOT/p).read_text()
        line = text.splitlines()[int(row['beginline'])-1].strip()
        if row['rule'] == 'DoNotUseThreads':
            assert any(part in line for part in ('Executors.newFixedThreadPool(','.submit('))
            assert 'TimeUnit.SECONDS' in text
            status = 'NOT_APPLICABLE_IN_EXACT_STANDALONE_TEST_CONTEXT'
            reason = 'Owned standalone JUnit executor/submit, not JavaEE Production thread creation; dynamic qualification is separate.'
        else:
            assert row['class'].endswith('.Fixture') and line.startswith('volatile ')
            assert row['variable'] in {'count','code','responder','failureStage'}
            status = 'NEEDS_FIXTURE_PUBLICATION_REVIEW_DYNAMIC_UNQUALIFIED'
            reason = 'Shared synthetic Fixture controls are unchanged; do not remove volatile or assert multi-field visibility/coherence without dedicated contextual evidence.'
        applicability.append(dict(path=p,sha256=hashes[p],line=int(row['beginline']),sourceLine=line,rule=row['rule'],disposition=status,reason=reason))
    assert jar_classes(old) == jar_classes(normal) and len(jar_classes(normal)) == 1843
    before,after = test_classes(old),test_classes(normal)
    physical = {}
    for module,name in set(before)|set(after):
        if before.get((module,name)) == after.get((module,name)):
            continue
        current = normal if (module,name) in after else old
        path = Path(current['jars'][module]['path']).parent/'test-classes'/name
        model = decode(path.read_bytes(),name)
        assert model['sourceFile'] in {Path(p).name for p in changed}
        physical[module+':'+name] = dict(sourceFile=model['sourceFile'],beforeSha256=before.get((module,name)),sha256=after.get((module,name)))
    runtime = data.read_checked(data.BASE/'PG10468-topbar-contract-post-v1/manifest.json',
        '42666d58ce7585680f23b890a27056b38605721b61b4211397a8db6237217154')
    assert all(hashes[p] == old_hashes[p] == h for p,h in runtime['sourceHashes'].items())
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'pmd-applicability.json',applicability)
    data.write(OUT/'original-file-findings.json',original_rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        sourceHashes={p:hashes[p] for p in changed},sourceChanges=6,stringConstants=50,intConstants=4,
        allOriginalAssertionsAndOtherTokensPreserved=True,actualAssertionInvocationCounts=None,
        metadataNegativeVectors=negatives,metadataNegativeCount=54,fileCountNegatives=count_negatives,
        baselineFileFindings=80,originalNestedFindings=11,rawPmdFindings=26,rawStaticExit=1,
        contextualNonApplicable=16,pendingApplicability=10,contextuallyApplicableFindings=None,
        pmdApplicabilityComplete=False,checkstyleFindings=0,suppressionsAdded=False,
        applicabilitySha256=data.sha((OUT/'pmd-applicability.json').read_bytes()),
        normalManifestSha256='11ca97be3c74142b3acfcac9c2612c0dd9230be17a4d91c5140a2abc28fbb179',
        mainClassesUnchanged=1843,physicalTestChanges=physical,
        otherTestClassesUnchanged=sum(before.get(k)==h for k,h in after.items()),testClassesBefore=len(before),testClassesAfter=len(after),
        previousPureViewRuntimeReference=dict(source=runtime['source'],sha256='42666d58ce7585680f23b890a27056b38605721b61b4211397a8db6237217154',
            mainAndThreeTestSourceBytesUnchanged=True,runtimeReassignedToNewGlobalSource=False),
        productTestsExecuted=0,originalDynamicPtStatus='NOT_EXECUTED_HOLD_PENDING_INDEPENDENCE_ASSESSMENT',
        wholeF03Accepted=False,wholeG03Accepted=False,whole451Accepted=False,externalActions=0,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
