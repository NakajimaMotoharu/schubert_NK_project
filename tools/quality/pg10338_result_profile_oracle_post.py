"""Static source/AST domain metadata, not target Test execution or a coverage measurement."""
from collections import Counter
from pathlib import Path
import json
import subprocess
from classfile_code_metadata import decode
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10332_result_profile_oracle_plan import restore, PREDICATE
from pg10130_uid_oracle_preflight import tokens
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes

SOURCE = '2e1ee53459a9cca85a4b821c72901073903a78e3'
OUT = data.BASE/'PG10338-result-profile-oracle-post-v1'


def folded(values):
    result = list(values)
    changed = True
    while changed:
        changed = False
        for i in range(len(result)-2):
            a,op,b = result[i:i+3]
            if a.startswith('"') and b.startswith('"') and op == '+':
                try: value = json.dumps(json.loads(a)+json.loads(b),ensure_ascii=False)
                except json.JSONDecodeError: continue
                result[i:i+3] = [value]
                changed = True
                break
    return result


def check(values,count,previous):
    if folded(restore(values,count)) != folded(tokens(previous)):
        raise ValueError('all non-classifier source tokens must be preserved')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal_path = data.BASE/'PG10336-result-profile-oracle-six-compile-v1/manifest.json'
    normal = json.loads(normal_path.read_bytes())
    old = data.read_checked(data.BASE/'PG10318-user-query-oracle-six-compile-v1/manifest.json',
        '04ac980e0ed4a2b18e83dd41521bfe9adda035251b7ce8ca6f3a90b9fae89942')
    plan = data.read_checked(data.BASE/'PG10332-result-profile-oracle-plan-v1/manifest.json',
        '4912958c280ea4bb7ad9bfb9fb0621b5c361b4ad884fef51f456977697303dd6')
    static = data.read_checked(data.BASE/'PG10334-result-profile-oracle-static-v1/manifest.json',
        '3d4025c20ede027e74fb500830e40bbf457e0aae16ce6d204943df65b8ad0f1a')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == normal['terminal']['actualExit'] == 0
    assert len(normal['jars']) == 6
    hashes,prior = normal['begin']['inputHashes'],old['begin']['inputHashes']
    assert set(hashes) == set(prior)
    paths = {p for p in hashes if hashes[p] != prior[p]}
    assert paths == set(plan['sourceChanges']) == set(static['sourceHashes']) and len(paths) == 5
    root,old_root = [Path(n['jars']['api']['path']).parents[3] for n in (normal,old)]
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((root/p).read_bytes()) == h for p,h in hashes.items())
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src'],cwd=data.ROOT) == b''
    pattern = tokens(PREDICATE)
    assert pattern == ['(','code','==','ResultCode','.','SUCCESS','||','code','==','ResultCode','.','IDEMPOTENT_SUCCESS',')']
    assertions,negatives = {},[]
    for p in sorted(paths):
        text,previous = (root/p).read_text(),(old_root/p).read_text()
        count = plan['sourceChanges'][p]['replacementCount']
        assert prior[p] == plan['sourceChanges'][p]['beforeSha256'] and hashes[p] == static['sourceHashes'][p]
        values = tokens(text)
        check(values,count,previous)
        assert 'usesSuccessProfile(' not in text
        assertions[p] = sum(v.startswith('assert') for v in values)
        assert assertions[p] == sum(v.startswith('assert') for v in tokens(previous))
        first = next(i for i in range(len(values)) if values[i:i+len(pattern)] == pattern)
        for name,index,value in [('logical-and',6,'&&'),('wrong-code',11,'FORBIDDEN'),
            ('not-equal',2,'!='),('wrong-variable',7,'otherCode')]:
            mutated = list(values)
            mutated[first+index] = value
            try: check(mutated,count,previous)
            except (ValueError,AssertionError): negatives.append(dict(path=p,mutation=name))
            else: raise AssertionError('incorrect Test profile predicate accepted')
    assert sum(v['replacementCount'] for v in plan['sourceChanges'].values()) == 12 and len(negatives) == 20
    # Static AST-domain model: names/expected flags come from the independent UI232 table.
    domain = [('SUCCESS','0000',True),('VALIDATION_ERROR','0100',False),('AUTHENTICATION_FAILED','0101',False),
        ('SESSION_INVALID','0102',False),('FORBIDDEN','0103',False),('NOT_FOUND','0104',False),
        ('CONFLICT','0105',False),('LOCKED','0106',False),('NOT_CANCELLABLE','0107',False),
        ('IDEMPOTENT_SUCCESS','0200',True),('TEMPORARY_FAILURE','9000',False),('RESOURCE_LIMIT','9001',False)]
    identities = {pattern[5],pattern[11]}
    assert all((name in identities) == expected for name,_,expected in domain)
    assert jar_classes(normal) == jar_classes(old) and len(jar_classes(normal)) == 1843
    before,after = test_classes(old),test_classes(normal)
    assert set(before) == set(after)
    changed = {k for k in before if before[k] != after[k]}
    source_files = {Path(p).name for p in paths}
    physical = {}
    for module,name in sorted(changed):
        file = Path(normal['jars'][module]['path']).parent/'test-classes'/name
        model = decode(file.read_bytes(),name)
        assert model['sourceFile'] in source_files
        physical[module+':'+name] = dict(sha256=after[(module,name)],sourceFile=model['sourceFile'])
    assert len(changed) >= 5
    assert static['actualExit'] == 1 and static['reports']['pmd']['findings'] == 64
    assert static['reports']['checkstyle']['findings'] == 0 and all(r['processingErrors'] == 0 for r in static['reports'].values())
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**static['dependencyHashes'],**static['toolAndRuleHashes']}.items())
    assert not list((root/'src').glob('*/target/surefire-reports/TEST-*.xml'))
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        normalManifestSha256=data.sha(normal_path.read_bytes()),sourceHashes={p:hashes[p] for p in sorted(paths)},
        originalSource=old['source'],independentPredicates=12,changedSourceCount=5,
        allOriginalNonClassifierTokensPreserved=True,allOriginalAssertionsPreserved=True,assertionCounts=assertions,
        staticAstDomainCases=[dict(enumName=n,wireValue=w,expectedSuccessProfile=b) for n,w,b in domain],
        staticAstDomainCaseCount=12,metadataNegativeVectors=negatives,
        allMainPhysicalClassesUnchanged=1843,changedPreviousTestPhysicalClasses=len(changed),
        unchangedPreviousTestPhysicalClasses=len(before)-len(changed),physicalTestChanges=physical,
        rawStaticExit=1,rawPmdFindings=64,pmdRuleCounts=dict(Counter(r['rule'] for r in static['reports']['pmd']['details'])),
        staticApplicabilityClassificationComplete=False,contextuallyApplicablePmdFindings=None,
        checkstyleFindings=0,suppressionsAdded=False,productionClassifierLoadedOrCalled=False,
        originalProductTestsExecuted=0,originalProductPtStatus='NOT_EXECUTED_HOLD',coverageMeasured=False,
        newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,
        effortPercent=None,externalActions=0,bug='BUG-1817',ykt='YKT-1568'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
