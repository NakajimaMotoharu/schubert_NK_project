"""Independent import/body/all-byte-scope/current raw finding audit; no Graph execution."""
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from classfile_code_metadata import decode
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes
from pg10690_current_global_static_post import finding_rows

OUT = data.BASE/'PG10702-graph-import-source-post-v1'
IMPORT = r'^import static org\.junit\.jupiter\.api\.Assertions\.(?:\*|assertArrayEquals|assertDoesNotThrow|assertEquals|assertNull|assertSame|assertThrows);\n'


def without_junit_imports(text):
    return canonical(re.sub(IMPORT,'',text,flags=re.M))


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    plan_path = data.BASE/'PG10694-graph-import-only-plan-v1/manifest.json'
    plan = data.read_checked(plan_path,'8dfb0086fc1ec0a4e2b7e7e06815134d96167ecbbf64cf8948a24288f588234c')
    normal_path = data.BASE/'PG10698-graph-import-six-compile-v1/manifest.json'
    normal = data.read_checked(normal_path,'7177fe941af4b6df2f2237112b0f3cc5eb9a82f21f8ef22c34eca6674eec1338')
    old_path = data.BASE/'PG10632-query-semantic-constant-compile-v1/manifest.json'
    old = data.read_checked(old_path,'8f29215a400d24a55ecabee90c74fb72a43525b740f129a12ae6053559701f87')
    static_path = data.BASE/'PG10700-graph-import-static-v1/manifest.json'
    static = data.read_checked(static_path,'d1bfe5019a18274230909ba0a8ddb30779a9284d8ae51d50ecf0a299b60488a1')
    assert old['source'] == plan['baseSource'] == '370fd74f6f170a18bc1bf959aa9fceced0def15a'
    assert normal['source'] == static['source'] == '0a7ff657115228d6cdde3820b5f2ae36ac7f3186'
    assert normal['actualExit'] == normal['testsExecuted'] == 0
    hashes,previous = normal['begin']['inputHashes'],old['begin']['inputHashes']
    changes = {r['path']:r for r in plan['sourceChanges']}
    assert set(hashes) == set(previous) and {p for p in hashes if hashes[p] != previous[p]} == set(changes) and len(changes) == 3
    old_snapshot = Path(old['jars']['api']['path']).parent.parent.parent.parent
    bindings = []
    for path,row in changes.items():
        before = (old_snapshot/path).read_text()
        after = (data.ROOT/path).read_text()
        assert data.sha(before.encode()) == previous[path] == row['beforeSha256']
        assert data.sha(after.encode()) == hashes[path] == row['sha256'] == static['sourceHashes'][path]
        assert len(re.findall(IMPORT,before,re.M)) == 1 and len(re.findall(IMPORT,after,re.M)) == 6
        assert without_junit_imports(before) == without_junit_imports(after)
        damaged = after.replace('assertSame(', 'assertEquals(',1)
        assert damaged != after and without_junit_imports(before) != without_junit_imports(damaged)
        bindings.append(dict(path=path,beforeSha256=previous[path],sha256=hashes[path]))
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    assert jar_classes(old) == jar_classes(normal) and len(jar_classes(normal)) == 1843
    previous_test,current_test = test_classes(old),test_classes(normal)
    assert set(previous_test) == set(current_test) and len(current_test) == 1962
    byte_changes = sorted(k for k in current_test if current_test[k] != previous_test[k])
    allowed = {(p.split('/')[1].removeprefix('schubert-nk-'),p.split('/src/test/java/')[1].removesuffix('.java')) for p in changes}
    for module,entry in byte_changes:
        stem = entry.removesuffix('.class').split('$')[0]
        assert (module,stem) in allowed
        file = Path(normal['jars'][module]['path']).parent/'test-classes'/entry
        assert decode(file.read_bytes(),entry)['sourceFile'] == stem.rpartition('/')[2]+'.java'
    old_global_path = data.BASE/'PG10690-current-global-static-post-v1/manifest.json'
    old_global = data.read_checked(old_global_path,'465c7c64bc75923d275436c72656ddc5b537f2c15982a71a0b4681a19ef03627')
    old_findings = data.read_checked(old_global_path.parent/'findings.json',old_global['findingsSha256'])
    before = [r for r in old_findings if r['path'] in changes and r['scanner'] == 'pmd']
    new_raw = (static_path.parent/'pmd.xml').read_bytes()
    assert data.sha(new_raw) == static['reports']['pmd']['sha256']
    after,_ = finding_rows(new_raw,'pmd',static['sourceHashes'])
    assert len(before) == len(after) == static['reports']['pmd']['findings'] == 4
    for first,last in zip(before,after):
        assert first['path'] == last['path'] and first['rule'] == last['rule']
        expected = dict(first['attributes'])
        for key in ('beginline','endline'):
            expected[key] = str(int(expected[key])+5)
        assert expected == last['attributes']
        message = re.sub(r'first occurrence is on line (\d+)',lambda m:'first occurrence is on line '+str(int(m[1])+5),first['message'])
        assert message == last['message']
    cs_raw = (static_path.parent/'checkstyle.xml').read_bytes()
    assert data.sha(cs_raw) == static['reports']['checkstyle']['sha256']
    cs,_ = finding_rows(cs_raw,'checkstyle',static['sourceHashes'])
    assert not cs and static['reports']['checkstyle']['findings'] == 0
    assert static['actualExit'] == 1 and all(r['processingErrors'] == 0 for r in static['reports'].values())
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=normal['source'],baseSource=old['source'],invocation=invocation,
        sourceChanges=bindings,compileManifestSha256=data.sha(normal_path.read_bytes()),staticManifestSha256=data.sha(static_path.read_bytes()),
        mainClassesUnchanged=1843,totalTestClasses=1962,otherTestClassesUnchanged=1962-len(byte_changes),
        physicalTestClassesChanged=len(byte_changes),changedTestClasses=[dict(module=m,entry=p) for m,p in byte_changes],
        testBodiesUnchanged=True,changedClassInstructionsIndividuallyCompared=False,metadataNegativeVectors=3,
        removedCheckstyleViolations=3,remainingRawPmdFindings=4,rawStaticExit=1,wholeF03Accepted=False,
        productTestsExecuted=0,dynamicStatus='NOT_EXECUTED_HOLD',coverage=None,externalActions=0,
        oldRuntimeReassigned=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
