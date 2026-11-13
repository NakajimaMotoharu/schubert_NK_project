"""One reviewed memory-process Test. No command, Root or cached application authority."""
from pathlib import Path
import hashlib
import json
import re
import zipfile
import copy
import xml.etree.ElementTree as ET

R = Path(__file__).resolve().parents[2]
RUNS = R.parent / 'pgpt-runs/PG379'
BASE = 'dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle'
ENUM = BASE + '$Outcome'
SOURCE = 'src/schubert-nk-batch/src/main/java/' + BASE + '.java'
SOURCE_SHA = 'd2686fed8d6c620411de1b92ed4a7bf19507e9f37f18d65b753208b3631de68a'
CLASS_SHA = {
    BASE: 'dbf0c01bee5c1955ce41b11858d6d855c0ab8d7bf503814951fd8a11ee9216d9',
    ENUM: '86ccc00797c876ed4688bf412cc38c1dbdeba5c9813c495f8fe2ea2fd87dd50a',
}
WITNESS = 'evidence/01_PT/018_NK-OPS-001/evidence/PG28782-real-outcome-static-byte-witness-v1/manifest.json'
WITNESS_SHA = 'b6ab59cc3fcc8d88ae3174af9bc430d257c4cbb076fd0f8667e7f9c1af37aa31'
CACHE = RUNS / 'pg28782-real-outcome-static-byte-witness-v1/compile-signatures'
PLATFORM = 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/'
STORAGE = 'src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/'
MAINS = {PLATFORM + n + '.java' for n in [
    'MaintenanceUnitStopPolicy', 'MaintenanceUnit', 'InspectorUnitProbe', 'InspectorUnitSnapshot',
    'SystemctlStateSource', 'ProcessResourceScope', 'StopGateException', 'StopGateFailure',
    'ApplicationStopGate', 'ApplicationUnit', 'UnitStateParser',
]} | {STORAGE + n + '.java' for n in ['ResourceScope', 'StorageIoException']}
TESTDIR = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/'
TEST = TESTDIR + 'MaintenanceUnitStopPolicyTest.java'
HELPER = TESTDIR + 'InspectorUnitProbeFixture.java'
FACTORY = PLATFORM + 'SystemctlStateSource.java'
FORBIDDEN_INIT = {BASE, ENUM, 'dev/codex/schubert/nk/batch/platform/InspectorUnitSnapshot',
                  'dev/codex/schubert/nk/batch/platform/SystemctlStateSource$NativeProcess'}
ANNOTATION = 'com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar'


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def syntax(c):
    option = c.get('reviewedUnstartedProcess')
    if option is None:
        return
    require(isinstance(option, dict) and set(option) == {'sourceWitness', 'typeWitness'},
            'exact unstarted process source/type witnesses')
    for pin in option.values():
        require(isinstance(pin, dict) and set(pin) == {'path', 'sha256'} and
                isinstance(pin['sha256'], str) and re.fullmatch('[0-9a-f]{64}', pin['sha256']) and
                pin['path'].startswith('evidence/01_PT/018_NK-OPS-001/evidence/') and
                '..' not in Path(pin['path']).parts and pin['path'].endswith('/manifest.json') and
                pin in c.get('closureProofs', []), 'pinned public source/type witness')
    require(option['typeWitness'] == dict(path=WITNESS, sha256=WITNESS_SHA),
            'exact real normal Outcome bytes, no alternative cache')
    require(set(c['mainSources']) == MAINS and len(c['mainSources']) == 13,
            'exact thirteen reviewed fresh Main sources')
    paths = {t['path']: t['tests'] for t in c['testSources']}
    require(len(c['testSources']) == 2 and set(paths) == {TEST, HELPER} and
            paths[TEST] in [7, 8] and paths[HELPER] == 0, 'whole MPOL Test and whole original helper')
    require(set(c.get('sdkJars', [])) <= {ANNOTATION} and not c.get('systemProperties') and
            not c.get('reviewedReflection') and c.get('reviewedGuardSignature') is None and
            c.get('reviewedAnalysisOnlyContext') is None and c.get('reviewedArtemisSdk') is None,
            'no implicit reflection, backend, Root or other symbol capabilities')
    physical = c['physicalClasses']
    require(ENUM + '.class' in physical and
            not any(n.startswith(BASE) and n != ENUM + '.class' for n in physical),
            'Outcome enum only in runtime/report, parent compile-only')
    require(FORBIDDEN_INIT <= set(c.get('forbiddenInitializedClasses', [])),
            'factory, snapshot and both parent/enum initialization forbidden')


def validate_type_witness(c, w, pre, parent_sha):
    syntax(c)
    require(w.get('actualExit') == 0 and w.get('productClassesLoadedOrInitialized') is False and
            w.get('productTestsExecuted') == w.get('appJarOrActualFourOrRootProtectedClassAccess') ==
            w.get('otherUnknownCachedClassAccess') == 0 and
            w.get('priorPositiveExecutionClaimed') is False and
            w.get('allUnexecutedCountersPreserved') is True and
            w.get('outcomeRuntimeInitializationPermission') is False,
            'static type provenance only, no execution or authority')
    require(w.get('sourceFrame') == dict(path=SOURCE, sha256=SOURCE_SHA) and
            parent_sha == SOURCE_SHA, 'unchanged exact real parent source')
    require(pre.get('normalCompileExit') == 0 and
            pre.get('normalCompileSource') == 'd8ff9efb16a7da1b073bdf9770487e3e6415b636' and
            pre.get('allThreeSourceBytesSameCurrentNormalPassive') is True and
            pre.get('cachedClassActionsBeforeThisReceipt') == 0 and
            pre.get('independentStaticClassCrc') == {BASE: '41384012e52c40ed', ENUM: '9bca5185cf2ba25e'},
            'normal compiler/current source/static CRC before original class access')
    require(set(w.get('classes', {})) == set(CLASS_SHA), 'exact two compiler symbols')
    for n, expected in CLASS_SHA.items():
        row = w['classes'][n]
        purpose = 'COMPILE_SYMBOL_ONLY_FORBIDDEN_RUNTIME_INITIALIZATION' if n == BASE else 'REAL_ENUM_TYPE_ONLY_ALL_MISSES_FORBIDDEN_INITIALIZATION'
        require(row.get('sha256') == expected and row.get('ownedCopy') == str(CACHE / (n + '.class')) and
                row.get('purpose') == purpose, 'exact immutable witnessed class bytes/path/purpose')


def checked(c):
    if c.get('reviewedUnstartedProcess') is None:
        return None
    syntax(c)
    option = c['reviewedUnstartedProcess']; tp = R / WITNESS
    require(digest(tp) == WITNESS_SHA, 'original type witness hash')
    w = json.loads(tp.read_text()); pp = R / w['preconditions']['path']
    require(digest(pp) == w['preconditions']['sha256'], 'original precondition hash')
    validate_type_witness(c, w, json.loads(pp.read_text()), digest(R / SOURCE))
    sp = R / option['sourceWitness']['path']
    require(digest(sp) == option['sourceWitness']['sha256'], 'whole current source witness hash')
    proof = json.loads(sp.read_text())
    require(proof.get('schema') == 'PGPT_UNSTARTED_PROCESS_SOURCE_V1' and proof.get('actualExit') == 0 and
            proof.get('wholeTestAndHelperReviewed') is True and
            proof.get('noActualCommandInvocation') is True and
            proof.get('defaultFactoryConstructionOnly') is True and proof.get('noRootOrOtherAuthority') is True,
            'reviewed memory-process source is not startup/stop authority')
    require(proof.get('mainInputHashes') == {n: digest(R / n) for n in c['mainSources']} and
            proof.get('testInputHashes') == {t['path']: digest(R / t['path']) for t in c['testSources']} and
            proof.get('wholeTestCount') == c['expectedTests'], 'all whole source bytes and Test count fixed')
    golden = proof.get('goldenLiteralSource', {})
    golden_path = TESTDIR + 'InspectorUnitSnapshotTest.java'
    require(golden.get('path') == golden_path and golden.get('sha256') == digest(R / golden_path) and
            golden.get('wholeTestModifiedOrReplayed') is False and
            proof.get('literalFixtureFieldExactOriginalValue') is True, 'unchanged independent golden source, never selected Test')
    source_literal = re.search(r'  static final String GOLDEN =\n      ("(?:[^"\\]|\\.)*");', (R / golden_path).read_text())
    helper_literal = re.search(r'  private static final String GOLDEN =\n      ("(?:[^"\\]|\\.)*");', (R / HELPER).read_text())
    require(source_literal is not None and helper_literal is not None and
            source_literal.group(1) == helper_literal.group(1) and
            hashlib.sha256(json.loads(source_literal.group(1)).encode('ascii')).hexdigest() == golden.get('valueSha256'),
            'literal oracle bytes identical, no Production-derived expected value')
    for n in [TEST, HELPER]:
        text = (R / n).read_text()
        require(not re.search(r'ProcessBuilder|Runtime\.getRuntime|ProcessHandle|\.exec\s*\(|'
                              r'\.start\s*\(|executeStreaming|RootStartupContext|MaintenanceOwnerFrame|'
                              r'Class\.forName|getDeclared|java\.net\.|java\.nio\.file\.', text),
                'no real command, Root/Guard fixture, reflection, network or file port')
    require('InspectorUnitSnapshotTest' not in (R / HELPER).read_text(),
            'literal helper must not compile or execute an unselected Test class')
    require('invokeAll(tasks, 5, TimeUnit.SECONDS)' in (R / TEST).read_text() and
            'pool.shutdownNow();' in (R / TEST).read_text() and
            'pool.awaitTermination(5, TimeUnit.SECONDS)' in (R / TEST).read_text(),
            'whole memory Test workers are bounded and terminated')
    for n in c['mainSources']:
        text = (R / n).read_text()
        if 'ProcessBuilder' in text:
            require(allow_builder(c, n, text), 'only exact uncalled native factory source')
    return w


def allow_builder(c, name, text):
    if c.get('reviewedUnstartedProcess') is None or name != FACTORY:
        return False
    syntax(c)
    marker = '  static final class NativeProcess {'
    return text.count(marker) == 1 and 'ProcessBuilder' not in text.split(marker)[0] and \
        text.count('new ProcessBuilder(command)') == 1 and \
        'static ProcessBuilder builder(List<String> command)' in text


def create_compile_carrier(c, work):
    w = checked(c)
    if w is None:
        return None
    carrier = work / 'outcome-compile-symbols.jar'
    with zipfile.ZipFile(carrier, 'x', compression=zipfile.ZIP_STORED) as archive:
        for n, value in CLASS_SHA.items():
            path = CACHE / (n + '.class')
            require(path.is_file() and not path.is_symlink(), 'exact witnessed owned class')
            data = path.read_bytes()
            require(hashlib.sha256(data).hexdigest() == value, 'witnessed normal class bytes unchanged')
            archive.writestr(zipfile.ZipInfo(n + '.class', (1980, 1, 1, 0, 0, 0)), data)
    return dict(typeWitness=c['reviewedUnstartedProcess']['typeWitness'],
                sourceWitness=c['reviewedUnstartedProcess']['sourceWitness'],
                sourceFrame=dict(path=SOURCE, sha256=SOURCE_SHA), compileClassHashes=dict(CLASS_SHA),
                compileCarrier=dict(path=str(carrier), sha256=digest(carrier)),
                runtimeClass=ENUM, runtimeClassSha256=CLASS_SHA[ENUM],
                runtimeInitializationPermitted=False)


def copy_runtime_enum(signature, work):
    if signature is None:
        return
    value = (CACHE / (ENUM + '.class')).read_bytes()
    require(hashlib.sha256(value).hexdigest() == CLASS_SHA[ENUM], 'real witnessed enum bytes')
    p = work / 'target/classes' / (ENUM + '.class')
    require(not p.exists(), 'compiler must not create a replacement enum')
    p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(value)


def analysis_root(root):
    """Drop only the compiler-only Outer carrier; the real enum is in the component."""
    result = copy.deepcopy(root)
    ns = result.tag.split('}')[0] + '}' if '}' in result.tag else ''
    deps = result.find(ns + 'dependencies')
    require(deps is not None, 'explicit compiler dependencies')
    rows = [d for d in deps if d.findtext(ns + 'artifactId') == 'real-outcome-compile-symbols']
    require(len(rows) == 1, 'exact compiler-only dependency')
    deps.remove(rows[0])
    return result


def create_analysis_pom(signature, work):
    if signature is None:
        return
    p = work / 'spotbugs-no-outer.pom.xml'
    require(not p.exists(), 'fresh exact analyzer POM')
    ET.ElementTree(analysis_root(ET.parse(work / 'pom.xml').getroot())).write(p, encoding='unicode', xml_declaration=True)
    signature['analyzerPom'] = dict(path=str(p), sha256=digest(p))


def validate_prepared(c, m, work):
    signature = m.get('unstartedProcess')
    if c.get('reviewedUnstartedProcess') is None:
        require(signature is None, 'no implicit process/type capability')
        return
    checked(c)
    require(isinstance(signature, dict) and
            signature['typeWitness'] == c['reviewedUnstartedProcess']['typeWitness'] and
            signature['sourceWitness'] == c['reviewedUnstartedProcess']['sourceWitness'] and
            signature['compileClassHashes'] == CLASS_SHA and
            signature['runtimeClass'] == ENUM and signature['runtimeClassSha256'] == CLASS_SHA[ENUM] and
            signature['runtimeInitializationPermitted'] is False, 'exact prepared static-only type receipt')
    path = work / 'outcome-compile-symbols.jar'
    require(signature['compileCarrier'] == dict(path=str(path), sha256=digest(path)) and
            str(path) not in m['dependencies'], 'own compile-only carrier never runtime dependency')
    with zipfile.ZipFile(path) as archive:
        require(len(archive.namelist()) == 2 and set(archive.namelist()) == {n + '.class' for n in CLASS_SHA},
                'exact two named real compiler symbols')
        require(all(hashlib.sha256(archive.read(n + '.class')).hexdigest() == h for n, h in CLASS_SHA.items()),
                'exact immutable carrier bytes')
    require(m['physicalClassHashes'].get(ENUM + '.class') == CLASS_SHA[ENUM] and
            BASE + '.class' not in m['physicalClassHashes'], 'only real unexecuted enum in component')
    analyzer = work / 'spotbugs-no-outer.pom.xml'
    require(signature.get('analyzerPom') == dict(path=str(analyzer), sha256=digest(analyzer)) and
            ET.tostring(ET.parse(analyzer).getroot()) == ET.tostring(analysis_root(ET.parse(work / 'pom.xml').getroot())),
            'analysis drops only compiler-only Outer, no missing-class suppression or new symbols')
