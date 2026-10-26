"""Independent raw source and class-byte post; no fault Test invocation."""
import difflib
import json
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes

SOURCE = '095720ee2766cd9f0bd441ee4bc019833fde8184'
OUT = data.BASE/'PG10600-fixed-error-oracle-post-v1'
BASE = 'c91916e8fe1d46768b4ffcd8607164e973aa1bde'
PREFIX = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/'
ROWS = [
    (PREFIX+'log/LogQueryApplicationServiceTest.java','TemporaryInfrastructureException','request transaction is unavailable','error'),
    (PREFIX+'admin/UserQueryApplicationServiceTest.java','TemporaryInfrastructureException','request transaction is unavailable','error'),
    (PREFIX+'admin/UserQueryReplayServiceTest.java','TemporaryInfrastructureException','request transaction is unavailable','e'),
    ('src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/CleanupStepRepositoryTest.java','BatchRepositoryException','batch repository operation failed','e'),
]


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    old = data.read_checked(data.BASE/'PG10558-trace-context-final-compile-v1/manifest.json',
        'e4f64a5711e95d5b5a6362bcec7adb3fe641f878d2edb2809c7dcbc8770f5e49')
    current_path = data.BASE/'PG10598-fixed-error-oracle-compile-v1/manifest.json'
    current = json.loads(current_path.read_bytes())
    plan = data.read_checked(data.BASE/'PG10594-fixed-error-oracle-plan-v2/manifest.json',
        '5c535c7af7bd6b68eb70094ff6bfed55d83eb5ea6afdf85191b42689313b0b97')
    static = data.read_checked(data.BASE/'PG10596-fixed-error-oracle-static-v1/manifest.json',
        'e23b29ba95ba12a85c33230b406eb88e25e00216d4671b714374a5ae0c1062f6')
    assert current['source'] == SOURCE and old['source'] == BASE
    assert current['actualExit'] == old['actualExit'] == current['testsExecuted'] == old['testsExecuted'] == plan['actualExit'] == 0
    hashes, prior = current['begin']['inputHashes'], old['begin']['inputHashes']
    assert set(hashes) == set(prior)
    changed = {p for p in hashes if hashes[p] != prior[p]}
    assert changed == {r[0] for r in ROWS}
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    bindings = []
    for path,kind,message,actual in ROWS:
        before = subprocess.check_output(['git','show',BASE+':'+path],cwd=data.ROOT).decode().splitlines(keepends=True)
        after = (data.ROOT/path).read_text().splitlines(keepends=True)
        edits = [s for s in difflib.ndiff(before,after) if s.startswith(('- ','+ '))]
        assert edits == ['-     assertEquals(new '+kind+'().getMessage(), '+actual+'.getMessage());\n',
                         '+     assertEquals("'+message+'", '+actual+'.getMessage());\n']
        assert hashes[path] == static['sourceHashes'][path]
        bindings.append(dict(path=path,beforeSha256=prior[path],sha256=hashes[path],changedLines=1))
    before_main, after_main = jar_classes(old), jar_classes(current)
    assert len(after_main) == 1843 and before_main == after_main
    before_test, after_test = test_classes(old), test_classes(current)
    assert set(before_test) == set(after_test) and len(after_test) == 1962
    byte_changes = {key for key in after_test if after_test[key] != before_test[key]}
    expected = {(p.split('/')[1].removeprefix('schubert-nk-'),p.split('/src/test/java/')[1].removesuffix('.java')+'.class') for p in changed}
    assert byte_changes == expected and len(byte_changes) == 4
    assert static['actualExit'] == 1 and static['reports']['pmd']['findings'] == 50
    assert static['reports']['checkstyle']['findings'] == 0 and all(r['processingErrors'] == 0 for r in static['reports'].values())
    changed_lines = {Path(p).stem: next(i+1 for i,s in enumerate((data.ROOT/p).read_text().splitlines()) if 'assertEquals("'+m+'", '+a+'.getMessage());' in s) for p,_,m,a in ROWS}
    assert all(not (int(r['beginline']) <= changed_lines[r['class']] <= int(r['endline'])) for r in static['reports']['pmd']['details'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,baseSource=BASE,invocation=invocation,
        compileManifestSha256=data.sha(current_path.read_bytes()),planManifestSha256=data.sha((data.BASE/'PG10594-fixed-error-oracle-plan-v2/manifest.json').read_bytes()),
        staticManifestSha256=data.sha((data.BASE/'PG10596-fixed-error-oracle-static-v1/manifest.json').read_bytes()),
        sourceChanges=bindings,mainClassesUnchanged=1843,otherTestClassesUnchanged=1958,
        physicalTestClassesChanged=4,totalTestClasses=1962,allOtherInputHashesUnchanged=True,
        staticRawFindings=50,staticFindingsAtChangedLines=0,staticApplicability='PENDING_NOT_WHOLE_F03_ACCEPTED',
        productTestsExecuted=0,dynamicStatus='NOT_EXECUTED_HOLD',coverage=None,externalActions=0,
        oldRuntimeReassigned=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
