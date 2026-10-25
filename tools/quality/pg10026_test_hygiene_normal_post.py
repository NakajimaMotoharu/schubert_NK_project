"""Bind committed normal source, unchanged Main bytes and complete Test debug-only structure."""
import json
import os
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes
import pg9346_direct_companion_jdk_post as steps

SOURCE = '5012c53265d8d8d789ea2a3edf0b63fa45853a6a'
WORK = data.ROOT.parent/'pgpt-runs/PG379'
OLD = WORK/'pg9992-query-pair-six-compile-v1/snapshot'
NORMAL = WORK/'pg10024-test-hygiene-six-compile-v1/snapshot'
SLOT = WORK/'pg10026-test-hygiene-normal-post-v1'
OUT = data.BASE/'PG10026-test-hygiene-normal-post-v1'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    normal = data.read_checked(data.BASE/'PG10024-test-hygiene-six-compile-v1/manifest.json',
        '5888cf524ecdc64fcb510d01ea800c6018222f1db790ad057466dae4b89072bf')
    previous = data.read_checked(data.BASE/'PG9992-query-pair-six-compile-v1/manifest.json',
        '33f7f2f8d1676bcc53f03252733530a33042a8dc910a36e2624ad1f54206c284')
    candidate = data.read_checked(data.BASE/'PG10016-test-hygiene-candidate-v2/manifest.json',
        'a1ae4f5fd15881b039f59648867fa6a1c24fd6143b02cd5d5b1a38f24ad2d2f0')
    applied = data.read_checked(data.BASE/'PG10022-test-hygiene-applied-post-v1/manifest.json',
        'ff6a93074d2a3973e0b05b72151e170b22954fe3f63fdebbe1ff9aa0ab69c32b')
    assert normal['actualExit'] == previous['actualExit'] == applied['actualExit'] == 0
    assert normal['source'] == SOURCE and normal['testsExecuted'] == 0 and applied['source'] is None
    hashes,old_hashes = normal['begin']['inputHashes'],previous['begin']['inputHashes']
    assert set(hashes) == set(old_hashes)
    changes = {p:h for p,h in hashes.items() if h != old_hashes[p]}
    assert changes == applied['changedSourceHashes'] and len(changes) == 641
    assert all(hashes[p] == h for p,h in candidate['heldSourceHashes'].items())
    assert all(data.sha((data.ROOT/p).read_bytes()) == data.sha((NORMAL/p).read_bytes()) == h for p,h in hashes.items())
    old_main,new_main = jar_classes(previous),jar_classes(normal)
    assert old_main == new_main and len(new_main) == 1843
    before,after = test_classes(previous),test_classes(normal)
    assert set(before) == set(after) and len(before) == 1922
    tc = data.ROOT.parent/'toolchain'
    helper = data.ROOT/'tools/quality/architecture/TestClassDebugOnlyMeasure.java'
    asm = tc/'m2/repository/org/ow2/asm/asm/9.10.1/asm-9.10.1.jar'
    inputs = {str(p):data.sha(p.read_bytes()) for p in (helper,asm)}
    SLOT.mkdir(mode=0o700)
    (SLOT/'reader').mkdir()
    steps.SLOT = SLOT
    stages = [steps.step('compile-measure',[str(tc/'jdk-25.0.4/bin/javac'),'-proc:none','-Xlint:all','-Werror',
        '-cp',str(asm),'-d',str(SLOT/'reader'),str(helper)])]
    assert stages[0]['actualExit'] == 0 and not stages[0]['timedOut']
    stages.append(steps.step('measure-test-structure',[str(tc/'jdk-25.0.4/bin/java'),'-cp',
        str(SLOT/'reader')+os.pathsep+str(asm),helper.stem,str(OLD),str(NORMAL)]))
    text = (SLOT/'measure-test-structure.stdout').read_text()
    lines = text.splitlines()
    assert lines[0] == 'METADATA_VECTORS\t5'
    summary = lines[-1].split('\t')
    assert len(summary) == 4 and summary[0] == 'SUMMARY'
    identical,debug,different = map(int,summary[1:])
    rows = [line.split('\t') for line in lines[1:-1]]
    assert len(rows) == 1922 and all(len(r) == 6 and r[0] == 'CLASS' for r in rows)
    old_keys = {module+'/'+name:digest for (module,name),digest in before.items()}
    new_keys = {module+'/'+name:digest for (module,name),digest in after.items()}
    assert {r[1] for r in rows} == set(old_keys) and len({r[1] for r in rows}) == 1922
    assert all(r[3] == old_keys[r[1]] and r[4] == new_keys[r[1]] for r in rows)
    assert sum(r[2] == 'BYTE_IDENTICAL' for r in rows) == identical
    assert sum(r[2] == 'DEBUG_ONLY' for r in rows) == debug
    assert sum(r[2] == 'NON_DEBUG_DIFFERENCE' for r in rows) == different
    assert identical+debug+different == 1922
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in inputs.items())
    verify(invocation)
    OUT.mkdir()
    (OUT/'test-class-structure.tsv').write_text(text)
    passed = stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut'] and different == 0
    value = dict(actualExit=0 if passed else 1,source=SOURCE,invocation=invocation,stages=stages,
        normalManifestSha256='5888cf524ecdc64fcb510d01ea800c6018222f1db790ad057466dae4b89072bf',
        candidateManifestSha256='a1ae4f5fd15881b039f59648867fa6a1c24fd6143b02cd5d5b1a38f24ad2d2f0',
        changedSourceHashes=changes,heldSourceFilesUnchanged=3,changedTestSources=641,
        mainClassesUnchanged=1843,testClasses=1922,byteIdenticalTestClasses=identical,debugOnlyTestClasses=debug,
        nonDebugTestClassDifferences=different,metadataVectors=5,metadataVectorsAreNotProductPt=True,
        structureTsvSha256=data.sha((OUT/'test-class-structure.tsv').read_bytes()),helperAndLibraryHashes=inputs,
        allCandidateStaticSourceHashesBoundToCurrentNormal=True,candidateCheckstyleFindings=0,
        currentJavaPaths=1800,currentMainPaths=965,currentTestPaths=835,
        productTestsExecuted=0,oldSuccessReassigned=False,oldExecUnion=False,coverage=None,
        wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None)
    data.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=value['actualExit'],mainUnchanged=1843,testClasses=1922,
        identical=identical,debugOnly=debug,nonDebugDifferent=different,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))
    raise SystemExit(value['actualExit'])


if __name__ == '__main__':
    main()
