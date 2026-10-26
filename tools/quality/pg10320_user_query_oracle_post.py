"""Preserve original Test tokens except declared independent profile selection; metadata only."""
from collections import Counter
from pathlib import Path
import json
import re
import subprocess
from classfile_code_metadata import decode
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10130_uid_oracle_preflight import tokens
from public_java_digest_provenance import close
from pg10313_user_query_literal_plan_v2 import restored
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes

SOURCE = '8788668513552ce50862797cb700d2b7a4162ac1'
BASE = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/'
APP,REPLAY,ORACLE = [BASE+'UserQuery'+s+'.java' for s in ('ApplicationServiceTest','ReplayServiceTest','WireOracle')]
OUT = data.BASE/'PG10320-user-query-oracle-post-v1'


def position(values,pattern):
    matches = [i for i in range(len(values)) if values[i:i+len(pattern)] == pattern]
    assert len(matches) == 1
    return matches[0]


def source_preserved(old_app,app,old_replay,replay,oracle,constants):
    mark = '  static byte[] expected('
    start,stop = app.index(mark),app.index('    put(expected, 113,',app.index(mark))
    first,last = old_app.index(mark),old_app.index('    put(expected, 113,',old_app.index(mark))
    assert tokens(app[:start]+old_app[first:last]+app[stop:]) == tokens(old_app)
    assert 'UserQueryRequest.decode' not in app[start:stop]
    assert 'UserQueryWireOracle.wire' in app[start:stop] and 'message.header().layoutId().value()' in app[start:stop]
    values,original = restored(replay,constants),tokens(old_replay)
    begin,end = tokens('static byte[] wire('),tokens('static String time(Instant instant)')
    start,stop = position(values,begin),position(values,end)
    first,last = position(original,begin),position(original,end)
    values[start:stop] = original[first:last]
    replacements = [
        ('wire("USRREQ01", MESSAGE,',3),('wire("UDTREQ01", MESSAGE,',4),
        ('wire(detail ? "UDTREQ01" : "USRREQ01", MESSAGE,',5),
        ('wire(n % 2 == 0 ? "UDTREQ01" : "USRREQ01", new UUID(100, n),',2)]
    counts = []
    for text,expected in replacements:
        pattern = tokens(text)
        matches = [i for i in range(len(values)) if values[i:i+len(pattern)] == pattern]
        assert len(matches) == expected
        counts.append(expected)
        for i in reversed(matches): values[i:i+len(pattern)] = tokens('wire(request,')
    new_head = tokens('for(boolean detail:List.of(false,true)){var request = detail ? detail(3,MESSAGE):list(null,null,null,1,MESSAGE);')
    old_head = tokens('for(var request:List.of(list(null,null,null,1,MESSAGE),detail(3,MESSAGE))){')
    start = position(values,new_head)
    opening = start+new_head.index('{')
    ending = close([(v,i) for i,v in enumerate(values)],opening,'{','}')
    body = values[start+len(new_head):ending]
    assert body.count('detail') == 7
    body = [part for value in body for part in (tokens('request.detailRequest()') if value == 'detail' else [value])]
    values[start:ending+1] = old_head+body+['}']
    assert values == original and sum(counts) == 14
    assert 'request.detailRequest()' not in replay
    old_wire = old_replay[old_replay.index('  static byte[] wire('):old_replay.index('  static String time(Instant instant)')]
    before = old_wire[old_wire.index('    byte[] bytes ='):old_wire.index('    return bytes;')]
    after = oracle[oracle.index('    byte[] bytes ='):oracle.index('    return bytes;')]
    before = before.replace('request.header().messageId().toString()','request.toString()').replace('time(NOW)','time(rowAt)')
    assert tokens(before) == tokens(after)
    assert not any(p in oracle for p in ('import dev.codex.','UserQueryRequest','java.sql','javax.crypto'))
    for old,new in ((old_app,app),(old_replay,replay)):
        assert re.findall(r'@Test\s+void\s+(\w+)\s*\(',old) == re.findall(r'@Test\s+void\s+(\w+)\s*\(',new)
        assert sum(t.startswith('assert') for t in tokens(old)) == sum(t.startswith('assert') for t in tokens(new))
    return dict(internalCallerCount=14,independentFixtureConditions=7,
        allOriginalAssertionsPreserved=True,allOriginalNonProfileTokensPreserved=True,originalBytePlacementPreserved=True)


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal_path = data.BASE/'PG10318-user-query-oracle-six-compile-v1/manifest.json'
    normal = json.loads(normal_path.read_bytes())
    old = data.read_checked(data.BASE/'PG10302-query-test-literal-six-compile-v1/manifest.json',
        'f71fc6274ba7f881e0a11d84190edce8bf71e14cbd0936a4d92a471acdd86eaf')
    metadata = data.read_checked(data.BASE/'PG10316-user-query-oracle-metadata-v1/manifest.json',
        'd45fd41a41e7daa58149c568dba1a7411f114e7b4d84a1b309ad0f1e1d32c7bf')
    static = data.read_checked(data.BASE/'PG10314-user-query-oracle-static-v2/manifest.json',
        '58b872c710117d6d22c4fbca689f933af8c6657cba8a0b34d4c287ccf34111ba')
    plan = data.read_checked(data.BASE/'PG10313-user-query-literal-plan-v2/manifest.json',
        '5a4797dd4e394e2dd0d4e9b2be72b58fb1e8112fc12b11ff65033f0654db4d92')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == normal['terminal']['actualExit'] == 0
    assert len(normal['jars']) == 6
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src'],cwd=data.ROOT) == b''
    hashes,prior = normal['begin']['inputHashes'],old['begin']['inputHashes']
    assert set(hashes)-set(prior) == {ORACLE} and not set(prior)-set(hashes)
    assert {p for p in prior if hashes[p] != prior[p]} == {APP,REPLAY}
    root,old_root = [Path(n['jars']['api']['path']).parents[3] for n in (normal,old)]
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((root/p).read_bytes()) == h for p,h in hashes.items())
    result = source_preserved((old_root/APP).read_text(),(root/APP).read_text(),
        (old_root/REPLAY).read_text(),(root/REPLAY).read_text(),(root/ORACLE).read_text(),plan['sourceChanges'][REPLAY]['constants'])
    assert metadata['actualExit'] == 0 and metadata['metadataVectors'] == 27 and metadata['metadataNegativeVectors'] == 3
    assert not metadata['productionClassesAvailable'] and metadata['originalProductTestsExecuted'] == 0
    assert metadata['sourceHashes'][ORACLE] == hashes[ORACLE]
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in metadata['sourceHashes'].items())
    assert jar_classes(normal) == jar_classes(old) and len(jar_classes(normal)) == 1843
    before,after = test_classes(old),test_classes(normal)
    assert set(before) <= set(after)
    changes,added = {k for k in before if before[k] != after[k]},set(after)-set(before)
    assert added == {('api',ORACLE.split('/java/',1)[1].removesuffix('.java')+'.class')}
    physical = {}
    for module,name in changes|added:
        assert module == 'api'
        file = Path(normal['jars'][module]['path']).parent/'test-classes'/name
        model = decode(file.read_bytes(),name)
        assert model['sourceFile'] in {Path(p).name for p in (APP,REPLAY,ORACLE)}
        physical[name] = dict(sha256=after[(module,name)],sourceFile=model['sourceFile'],added=(module,name) in added)
    assert static['sourceHashes'] == {p:hashes[p] for p in (APP,REPLAY,ORACLE)}
    assert static['actualExit'] == 1 and static['reports']['pmd']['findings'] == 14
    assert static['reports']['checkstyle']['findings'] == 0 and all(r['processingErrors'] == 0 for r in static['reports'].values())
    assert not any(r['class'] == 'UserQueryWireOracle' for r in static['reports']['pmd']['details'])
    rules = Counter(r['rule'] for r in static['reports']['pmd']['details'])
    assert rules == dict(NullAssignment=5,AvoidCatchingGenericException=1,DoNotUseThreads=6,CloseResource=1,UseProperClassLoader=1)
    dispositions = []
    app_text = (root/APP).read_text()
    assert 'var receiver = factory.createContext(jakarta.jms.JMSContext.SESSION_TRANSACTED);' in app_text
    assert 'return UserApplicationFixture.invoke(receiver, m, a);' in app_text
    for row in static['reports']['pmd']['details']:
        path = BASE+row['class']+'.java'
        line = (root/path).read_text().splitlines()[int(row['beginline'])-1].strip()
        rule = row['rule']
        if rule == 'NullAssignment':
            assert line == 'f.sqlFault = null;'
            reason = 'Reset optional Test fault fixture after an explicitly checked fault; not a production null invariant.'
        elif rule == 'AvoidCatchingGenericException':
            assert line == '} catch (Exception failure) {'
            reason = 'Checked metadata failure becomes AssertionError in Test callback, not production success.'
        elif rule == 'DoNotUseThreads':
            assert 'Executors.newFixedThreadPool(10)' in line or line == 'pool.submit('
            reason = 'Standalone bounded Test executor, lexically owned try-with, not JavaEE webapp thread creation.'
        elif rule == 'UseProperClassLoader':
            assert line == 'jakarta.jms.JMSContext.class.getClassLoader(),'
            reason = 'Standalone Test Proxy exact interface loader, not JavaEE container context loading.'
        else:
            assert rule == 'CloseResource' and line == 'var failing ='
            reason = 'Test Proxy borrows receiver owned by outer try-with JMSContext; independently closing proxy would close borrowed owner.'
        dispositions.append(dict(path=path,sourceSha256=hashes[path],line=int(row['beginline']),exactSourceLine=line,
            rule=rule,disposition='NOT_APPLICABLE_TO_THIS_EXACT_TEST_CONTEXT',reason=reason))
    assert len(dispositions) == 14
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in {**static['dependencyHashes'],**static['toolAndRuleHashes']}.items())
    assert not list((root/'src').glob('*/target/surefire-reports/TEST-*.xml'))
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'pmd-applicability.json',dispositions)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,**result,
        normalManifestSha256=data.sha(normal_path.read_bytes()),sourceHashes={p:hashes[p] for p in (APP,REPLAY,ORACLE)},
        metadataVectors=27,metadataNegativeVectors=3,metadataProductionClasspathAbsent=True,
        allMainPhysicalClassesUnchanged=1843,changedPreviousTestPhysicalClasses=len(changes),
        unchangedPreviousTestPhysicalClasses=len(before)-len(changes),addedTestPhysicalClasses=len(added),physicalTestChanges=physical,
        rawStaticExit=1,rawPmdFindings=14,contextuallyApplicablePmdFindings=0,checkstyleFindings=0,
        applicabilitySha256=data.sha((OUT/'pmd-applicability.json').read_bytes()),suppressionsAdded=False,
        originalProductTestsExecuted=0,originalProductPtStatus='NOT_EXECUTED_HOLD',coverageMeasured=False,
        newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None,
        externalActions=0,bugs=['BUG-1814','BUG-1815','BUG-1816'],ykts=['YKT-1565','YKT-1566','YKT-1567']))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
