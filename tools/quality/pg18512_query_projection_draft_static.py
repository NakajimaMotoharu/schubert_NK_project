"""Compile the held V draft only; never execute JUnit, Product, DB or any held probe."""
import hashlib
import json
import os
from pathlib import Path

import pg9666_pagination_static as shared
from host_tool_invocation import capture, verify

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT.parent / 'pgpt-runs/PG379'
NORMAL = WORK / 'pg14216-typed-marker-guard-six-compile-v1'
NORMAL_SHA = '1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
SOURCE = '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
SLOT = WORK / 'pg18512-query-projection-draft-static-v1'
OUT = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18512-query-projection-draft-static-v1'
TEST = ROOT / 'tools/quality/architecture/QuestionProjectionFailureContractTest.java'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    invocation = capture(__file__)
    assert not SLOT.exists() and not OUT.exists()
    manifest = NORMAL / 'manifest.safe.json'
    assert sha(manifest) == NORMAL_SHA
    normal = json.loads(manifest.read_bytes())
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    assert set(normal['jars']) == {'protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'}
    jars = [Path(row['path']) for row in normal['jars'].values()]
    assert all(sha(Path(row['path'])) == row['sha256'] for row in normal['jars'].values())
    cpfile = NORMAL / 'snapshot/src/schubert-nk-api/target/pgpt-test-classpath.txt'
    deps = [Path(p) for p in cpfile.read_text().strip().split(os.pathsep)
            if '/dev/codex/schubert/' not in p and not p.startswith(str(NORMAL / 'snapshot/src') + '/')]
    assert deps and all(str(p).startswith(str(ROOT.parent / 'toolchain/m2/repository') + '/') and p.is_file() for p in deps)
    declaration = json.loads((ROOT / 'documents/400_PGPT/470_PMO/500_SV計画整備_20261104/534_API二十一の保留交差・十五metadata再発防止.json').read_bytes())
    assert declaration['source'] == SOURCE and declaration['draft']['sha256'] == sha(TEST)
    assert declaration['draft']['executed'] is False and declaration['knownDirectHolds'] == 6
    os.umask(0o077)
    SLOT.mkdir()
    classes = SLOT / 'compiled-draft'
    classes.mkdir()
    shared.SLOT = SLOT
    jdk = ROOT.parent / 'toolchain/jdk-25.0.4/bin'
    command = [str(jdk / 'javac'), '--release', '25', '-proc:none', '-Xlint:all', '-Werror',
               '-cp', os.pathsep.join(map(str, [*jars, *deps])), '-d', str(classes), str(TEST)]
    begin = dict(source=SOURCE, invocation=invocation, testSourceSha256=sha(TEST),
                 normalCompileSha256=NORMAL_SHA, classpathFileSha256=sha(cpfile),
                 dependencyHashes={str(p): sha(p) for p in [*jars, *deps]},
                 sourceScope='EXACT_NEW_TEST_PLUS_EXISTING_SIX_MAIN_JAR_BYTES_NOT_ALL_NORMAL_TEST_SOURCES',
                 heldRootFailedSourcesAccessed=False, heldTwoToolsAccessed=False,
                 productTestsPlanned=0, annotationProcessing=False)
    shared.data.write(SLOT / 'begin.safe.json', begin)
    stage = shared.step('draft-javac', command, SLOT)
    verify(invocation)
    result = dict(actualExit=stage['actualExit'], source=SOURCE, begin=begin, stages=[stage],
                  testSourceUnchanged=sha(TEST) == begin['testSourceSha256'],
                  compiledClasses={str(p.relative_to(classes)): sha(p) for p in sorted(classes.rglob('*.class'))},
                  productTestsExecuted=0, junitInvoked=False, productInitialized=False,
                  databaseOperations=0, vmOperations=0, networkOperations=0, serviceOperations=0,
                  actualCoverage=None, newAcceptedCriteria=0, formalUpdated=False,
                  VAccepted=False, dynamicHoldMaintained=True,
                  toolResultIsNotPtPass=True)
    OUT.mkdir()
    shared.data.write(SLOT / 'manifest.safe.json', result)
    shared.data.write(OUT / 'manifest.json', result)
    print(json.dumps(dict(actualExit=result['actualExit'], productTestsExecuted=0,
                          testSourceUnchanged=result['testSourceUnchanged'],
                          manifestSha256=sha(OUT / 'manifest.json'))))
    raise SystemExit(stage['actualExit'])


if __name__ == '__main__':
    main()
