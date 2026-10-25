"""Independently bind corrected Main, new test, current selected result/static and unaffected Web."""
import json
from pathlib import Path
import subprocess
import zipfile
import g07_host_class_provenance_inputs as data
from coverage_session_schema import selftest
from host_tool_invocation import capture, verify

ROOT = data.ROOT
SOURCE = 'e598a81bb4200b4e4930278b31479ff927aa025f'
OUT = data.BASE / 'PG9762-outbox-quality-source-post-v1'
MAIN = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxDispatchReport.java'
TEST = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxDispatchReportBoundaryTest.java'
WEB = 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebLogDispatcher.java'


def classes(jars):
    result = {}
    for module,row in jars.items():
        path = Path(row['path'])
        assert data.sha(path.read_bytes()) == row['sha256']
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                if name.endswith('.class'):
                    assert name not in result
                    result[name] = dict(module=module,sha256=data.sha(archive.read(name)))
    return result


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    before = data.read_checked(data.BASE / 'PG9694-semantic-direct-fixed-six-compile-v1/manifest.json',
        '7d2e18f86d2bc9e5c61473da8b8924aa7c6668bf8903541d5502902d2dac1d7a')
    normal = data.read_checked(data.BASE / 'PG9750-outbox-report-six-compile-v1/manifest.json',
        '7b1c2b2e67dab622cc3e905e1c04ac5819a587f90992c404cf6cab3f0ceebb96')
    hashes = normal['begin']['inputHashes']
    assert before['source'] == 'fd3d04df5710ca28f0e34f919cbc103e569a607b'
    assert before['actualExit'] == normal['actualExit'] == 0 and normal['source'] == SOURCE
    assert not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)
    assert all(data.sha((ROOT / p).read_bytes()) == h for p,h in hashes.items())
    changed = {p for p,h in hashes.items() if before['begin']['inputHashes'].get(p) != h}
    assert changed == {MAIN,TEST} and set(before['begin']['inputHashes']) | {TEST} == set(hashes)
    old_main = subprocess.check_output(['git','show',before['source'] + ':' + MAIN],cwd=ROOT)
    assert old_main.count(b'claimed != sent + failed + leaseLost') == 1
    assert old_main.replace(b'claimed != sent + failed + leaseLost',b'claimed != (long) sent + failed + leaseLost') == (ROOT / MAIN).read_bytes()
    old_classes, current_classes = classes(before['jars']), classes(normal['jars'])
    assert len(old_classes) == len(current_classes) == 1843 and set(old_classes) == set(current_classes)
    changed_classes = {p for p in old_classes if old_classes[p] != current_classes[p]}
    assert changed_classes == {'dev/codex/schubert/nk/api/messaging/outbound/OutboxDispatchReport.class'}
    current_snapshot = Path(normal['jars']['api']['path']).parents[3]
    previous_snapshot = Path(before['jars']['api']['path']).parents[3]
    old_tests = {p.relative_to(previous_snapshot).as_posix():data.sha(p.read_bytes()) for p in previous_snapshot.glob('src/*/target/test-classes/**/*.class')}
    new_tests = {p.relative_to(current_snapshot).as_posix():data.sha(p.read_bytes()) for p in current_snapshot.glob('src/*/target/test-classes/**/*.class')}
    assert len(old_tests) == 1912 and len(new_tests) == 1913 and all(new_tests.get(p) == h for p,h in old_tests.items())
    added_classes = set(new_tests) - set(old_tests)
    assert added_classes == {'src/schubert-nk-api/target/test-classes/dev/codex/schubert/nk/api/messaging/outbound/OutboxDispatchReportBoundaryTest.class'}
    pins = {
        'PG9754-outbox-value-host-v2':'affbf2ef4c901e34206b99fa6610cf839c6c89037d7c4e6bc7b4e0a22ddc91e4',
        'PG9756-outbox-value-post-v3':'ad294102220a887c95846df3ce33188d130bee2a3a89babe188e9d7d9e012600',
        'PG9758-outbox-api-static-v1':'2c8439ae72535023ee5a22bc5311d90e46bd634bc4f1f7df50c889b791ada34f',
        'PG9760-outbox-changed-source-static-v1':'adc1062211e62be7464d1388a86e3f23c863b67b60db216cddd4d2c7e8bc8d26'}
    proofs = {name:data.read_checked(data.BASE / name / 'manifest.json',digest) for name,digest in pins.items()}
    assert all(p['actualExit'] == 0 and p['source'] == SOURCE for p in proofs.values())
    report = proofs['PG9756-outbox-value-post-v3']
    assert report['actualTests'] == 13 and report['suites'] == 4 and report['four100ExecutableClassCount'] == 8 and report['selectedSourceUnitFour100']
    static = proofs['PG9758-outbox-api-static-v1']
    assert set(static['results']) == {'api'}
    assert all(v['findings'] == v['processingErrors'] == 0 for v in static['results'].values())
    assert all(v['findings'] == v['processingErrors'] == 0 for v in proofs['PG9760-outbox-changed-source-static-v1']['reports'].values())
    web = (ROOT / WEB).read_text()
    assert hashes[WEB] == before['begin']['inputHashes'][WEB]
    assert '|| (long) sent + failed + leaseLost != claimed' in web and '|| claimed > 100' in web
    web_test = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/WebLogDispatcherTest.java'
    assert hashes[web_test] == before['begin']['inputHashes'][web_test]
    assert '{1, Integer.MAX_VALUE, Integer.MAX_VALUE, 3}' in (ROOT / web_test).read_text()
    assert selftest() == 7
    failures = []
    for name,reason in [
        ('pg9752_outbox_value_preflight.py','path copied from storage; rows0, no job'),
        ('pg9752_outbox_value_preflight_v2.py','API Jar compared to storage hash; no job'),
        ('pg9754_outbox_value_host.py','current normal internal classpath guard; no slot/job'),
        ('pg9756_outbox_value_post.py','session[4] instead of end column; report success retained'),
        ('pg9756_outbox_value_post_v2.py','literal backslash-t separator; schema rejection, no JVM')]:
        path = ROOT / 'tools/quality' / name
        failures.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=data.sha(path.read_bytes()),observedCommandExit=1,reason=reason,notProductPtFailure=True))
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,proofManifestHashes=pins,
        currentSourceHashes={p:hashes[p] for p in changed},allMainClasses=1843,changedMainClassNames=sorted(changed_classes),unchangedMainClassCount=1842,
        previousTestClasses=1912,currentTestClasses=1913,previousTestClassBytesUnchanged=True,newTestClassNames=sorted(added_classes),
        oldWholeDynamicResultsTransferred=False,oldPureStaticBytesEquivalenceOnly=True,webReportNotAffectedByIntSum=True,
        webSourceSha256=hashes[WEB],webTestSourceSha256=hashes[web_test],webActualDbJmsTestsExecuted=False,
        sessionSchemaVectors=7,toolFailureObservations=failures,actualSelectedTests=13,newTestIds=3,
        completeSelectedSourceUnits=8,selectedCoverage=report['selectedSourceUnitCounters'],apiStaticMainClasses=static['allInputMainClasses'],
        bugs=['BUG-1760','BUG-1761','BUG-1762'],horizontal=['YKT-1511','YKT-1512','YKT-1513'],
        productTestsExecutedByPost=0,actualExternalActions=0,whole451Accepted=False,wholeApiOutboxAccepted=False,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,mainClasses=1843,changedMainClasses=1,newTestClasses=1,qualifiedSelectedTests=13,
        manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
