"""Exact Test-only source/normal-byte binding. No original business PT or graph/key execution."""
from collections import Counter
from pathlib import Path
import json
import re
import subprocess
from classfile_code_metadata import decode
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10130_uid_oracle_preflight import tokens
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes

SOURCE = '21228608b9defca3eb6fac7e0485f28a56925246'
BASE = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/question/'
APP,REPLAY,ORACLE = [BASE+'QuestionQuery'+s+'.java' for s in ('ApplicationServiceTest','ReplayServiceTest','WireOracle')]
OUT = data.BASE/'PG10286-query-wire-oracle-source-post-v1'


def normalized(text):
    values = tokens(text)
    changed = True
    while changed:
        changed = False
        for i in range(len(values)-2):
            if values[i].startswith('"') and values[i+1] == '+' and values[i+2].startswith('"'):
                values[i:i+3] = [json.dumps(json.loads(values[i])+json.loads(values[i+2]),ensure_ascii=False)]
                changed = True
                break
    return values


def preserved(old_app,app,old_replay,replay,oracle):
    marker = '  static byte[] expected('
    start,stop = app.index(marker),app.index('    if (!success) return b;',app.index(marker))
    first,last = old_app.index(marker),old_app.index('    if (!success) return b;',old_app.index(marker))
    assert normalized(app[:start]+old_app[first:last]+app[stop:]) == normalized(old_app)
    assert 'QuestionQueryRequest.decode' not in app[start:stop]
    assert 'QuestionQueryWireOracle.wire' in app[start:stop] and 'layout,' in app[start:stop]
    current = replay.replace('wire(layout,','wire(request,')
    assert replay.count('wire(layout,') == 7
    current = current.replace('wire("QSDREQ01", REPLY, LATER, "0200", 0)','wire(request, REPLY, LATER, "0200", 0)')
    current = current.replace('wire("NTDREQ01", RESPONSE, COMPLETED, "0000", 0)','wire(request, RESPONSE, COMPLETED, "0000", 0)')
    start,stop = current.index('  static byte[] wire('),current.index('  static String time(Instant at)')
    first,last = old_replay.index('  static byte[] wire('),old_replay.index('  static String time(Instant at)')
    assert normalized(current[:start]+old_replay[first:last]+current[stop:]) == normalized(old_replay)
    # The entire old byte placement block is unchanged after explicitly named substitutions.
    original = old_replay[old_replay.index('    byte[] b =',first):old_replay.index('    return b;',first)]
    moved = oracle[oracle.index('    byte[] b ='):oracle.index('    return b;')]
    original = original.replace('request.responseLayoutId().value()','reply').replace('MESSAGE.toString()','request.toString()').replace('time(NOW)','time(rowAt)')
    moved = moved.replace('QUESTION_TEXT','"question"')
    assert normalized(original) == normalized(moved)
    assert 'import dev.codex.' not in oracle and 'QuestionQueryRequest' not in oracle
    assert re.findall(r'@Test\s+void\s+(\w+)\s*\(',app) == re.findall(r'@Test\s+void\s+(\w+)\s*\(',old_app)
    assert re.findall(r'@Test\s+void\s+(\w+)\s*\(',replay) == re.findall(r'@Test\s+void\s+(\w+)\s*\(',old_replay)
    return {p:sum(t.startswith('assert') for t in tokens(s)) for p,s in ((APP,app),(REPLAY,replay))}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal_path = data.BASE/'PG10284-query-wire-oracle-six-compile-v1/manifest.json'
    normal = json.loads(normal_path.read_bytes())
    old = data.read_checked(data.BASE/'PG10263-scenario-media-six-compile-v2/manifest.json',
        '52622b296c357e6dabb76957c15978a1430b4d928887b0785f41d18ece977558')
    metadata = data.read_checked(data.BASE/'PG10282-query-wire-oracle-metadata-v2/manifest.json',
        'c0e532154eb45e90684a425696ec52630e4e8ef5eb6de4a8089e4d30092f4d4b')
    static = data.read_checked(data.BASE/'PG10281-query-wire-oracle-static-v2/manifest.json',
        '8e68da33c559ef0de554823e6db8e0a03724dffa85619616a7e5e5be8188d626')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    assert normal['terminal']['actualExit'] == 0 and len(normal['jars']) == 6
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src'],cwd=data.ROOT) == b''
    hashes,prior = normal['begin']['inputHashes'],old['begin']['inputHashes']
    assert set(hashes)-set(prior) == {ORACLE} and not set(prior)-set(hashes)
    assert {p for p in prior if hashes[p] != prior[p]} == {APP,REPLAY}
    root = Path(normal['jars']['api']['path']).parents[3]
    old_root = Path(old['jars']['api']['path']).parents[3]
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((root/p).read_bytes()) == h for p,h in hashes.items())
    asserts = preserved((old_root/APP).read_text(),(root/APP).read_text(),
        (old_root/REPLAY).read_text(),(root/REPLAY).read_text(),(root/ORACLE).read_text())
    assert jar_classes(normal) == jar_classes(old) and len(jar_classes(normal)) == 1843
    before,after = test_classes(old),test_classes(normal)
    assert set(before) <= set(after)
    changed = {p for p in before if before[p] != after[p]}
    added = set(after)-set(before)
    physical = {}
    for key in sorted(changed|added):
        module,name = key
        assert module == 'api'
        file = Path(normal['jars'][module]['path']).parent/'test-classes'/name
        model = decode(file.read_bytes(),name)
        assert model['sourceFile'] in {Path(p).name for p in (APP,REPLAY,ORACLE)}
        physical[name] = dict(sha256=after[key],sourceFile=model['sourceFile'],added=key in added)
    assert added == {('api','dev/codex/schubert/nk/api/application/question/QuestionQueryWireOracle.class')}
    assert static['actualExit'] == 1 and static['reports']['pmd']['findings'] == 28
    assert static['reports']['checkstyle']['findings'] == 0 and all(r['processingErrors'] == 0 for r in static['reports'].values())
    assert static['sourceHashes'] == {p:hashes[p] for p in (APP,REPLAY,ORACLE)}
    assert not any(r['class'] == 'QuestionQueryWireOracle' for r in static['reports']['pmd']['details'])
    rule_counts = Counter(r['rule'] for r in static['reports']['pmd']['details'])
    assert rule_counts == {'AvoidDuplicateLiterals':19,'UseProperClassLoader':6,'NullAssignment':1,
        'AvoidCatchingGenericException':1,'AvoidLiteralsInIfCondition':1}
    assert metadata['actualExit'] == 0 and metadata['metadataVectors'] == 24
    assert metadata['originalProductTestsExecuted'] == 0 and not metadata['productionClassesAvailable']
    assert metadata['sourceHashes'][ORACLE] == hashes[ORACLE]
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in metadata['sourceHashes'].items())
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**static['dependencyHashes'],**static['toolAndRuleHashes']}.items())
    assert not list((root/'src').glob('*/target/surefire-reports/TEST-*.xml'))
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        normalManifestSha256=data.sha(normal_path.read_bytes()),originalNormalSource=old['source'],
        sourceHashes={p:hashes[p] for p in (APP,REPLAY,ORACLE)},allMainPhysicalClassesUnchanged=1843,
        changedPreviousTestPhysicalClasses=len(changed),unchangedPreviousTestPhysicalClasses=len(before)-len(changed),
        addedTestPhysicalClasses=len(added),physicalTestChanges=physical,
        allOriginalAssertionsPreserved=True,originalAssertionCounts=asserts,originalBytePlacementPreserved=True,
        testOnlyOracleMetadataVectors=24,metadataNegativeVectors=5,metadataProductClasspathAbsent=True,
        metadataManifestSha256='c0e532154eb45e90684a425696ec52630e4e8ef5eb6de4a8089e4d30092f4d4b',
        rawPmdFindings=28,rawCheckstyleFindings=0,pmdRuleCounts=dict(rule_counts),
        existingDuplicateLiteralFindingsUnresolved=19,otherContextReviewFindings=9,
        newHelperPmdFindings=0,wholeF03Accepted=False,whole451Accepted=False,
        originalProductTestsExecuted=0,originalProductPtStatus='NOT_EXECUTED_HOLD',coverageMeasured=False,
        newAccepted=0,formalUpdated=False,effortPercent=None,externalActions=0,
        bug='BUG-1811',ykt='YKT-1562',staticBug='BUG-1812',staticYkt='YKT-1563'))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
