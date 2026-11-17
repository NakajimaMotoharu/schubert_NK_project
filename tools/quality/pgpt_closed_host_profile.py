"""SS311/351/451: explicit closed host profiles, never an authority or HOLD override.

Whole source closure and independent business oracles must be reviewed before a profile is
created. No application JAR, implicit source tree, database, native access, selected method,
automatic retry, suppression or coverage exclusion is supported by this bounded runner.
The independent post verifier is a separate program. Tool validation is not product PT.
"""
from pathlib import Path, PurePosixPath
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

import pg9666_pagination_static as steps

DENIED = frozenset({
    'TemporaryInfrastructureException', 'FingerprintKeyRing', 'ResponseSnapshotCodec',
    'WebStartupException', 'RootFailedStartRecoveryTest', 'RootFailedStartPairRecoveryTest',
    'SnapshotKeyCloseWitness', 'pg9892_snapshot_key_close_witness',
    'NotificationListViewModel', 'NotificationDetailViewModel',
    'QuestionListViewModel', 'QuestionDetailViewModel',
})
R = Path(__file__).resolve().parents[2]
TC = R.parent / 'toolchain'
RUNS = R.parent / 'pgpt-runs/PG379'
ANN = TC / 'm2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar'
CONSOLE = TC / 'junit-platform-console-standalone-1.13.4.jar'
JAVA = TC / 'jdk-25.0.4/bin/java'
JAVAC = JAVA.with_name('javac')
MAVEN = TC / 'm2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'
QUALITY_INPUTS = ['tools/quality/static/pmd.xml', 'tools/quality/static/checkstyle.xml']
PMD_POLICY_SOURCE = '1634e3884a7b645f50b3552642ed4a1844736ab5'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text())


def write_json(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def ref(path):
    return dict(path=str(path.relative_to(R)), sha256=digest(path))


def relative_name(value):
    require(isinstance(value, str) and value and '\\' not in value, 'relative name')
    p = PurePosixPath(value)
    require(not p.is_absolute() and '..' not in p.parts and str(p) == value, 'canonical relative name')
    require(p.stem.split('$')[0] not in DENIED, 'HOLD name, before stat/read/compile')
    return value


def validate_syntax(c):
    require(isinstance(c, dict) and c.get('schema') == 'PGPT_CLOSED_HOST_PROFILE_V1', 'profile schema')
    require(isinstance(c.get('id'), str) and re.fullmatch(r'PG[0-9]+-[A-Z0-9]+(?:-[A-Z0-9]+)*', c['id']), 'profile id')
    require(c.get('costWbsLeafIds') == ['WBS-F03'] and c.get('costBoundary') == 'ADDITIONAL_QUALIFICATION_NO_ORIGINAL_COST_REASSIGNMENT', 'explicit qualification cost owner')
    require(c.get('productOwnerByMainPath') and c.get('oracleSpecs') and c.get('closureProofs'), 'explicit owner/oracle/closure, no defaults')
    require(c.get('qualityExceptions') == [] and c.get('coverageExclusions') == [], 'no quality override')
    require(isinstance(c.get('productionCoreMain'), str) and re.fullmatch(r'[0-9a-f]{40}', c['productionCoreMain']), 'explicit Main identity')
    main = c.get('mainSources'); tests = c.get('testSources')
    require(isinstance(main, list) and main and isinstance(tests, list) and tests, 'explicit sources')
    test_paths = []
    for item in tests:
        require(set(item) == {'path', 'tests'} and type(item['tests']) is int and item['tests'] >= 0, 'whole Test or unchanged helper count')
        test_paths.append(item['path'])
    paths = main + test_paths
    require(len(paths) == len(set(paths)), 'unique Main/Test paths')
    for path in main:
        relative_name(path)
        require(path.startswith('src/') and '/src/main/java/' in path and path.endswith('.java'), 'Main source boundary')
    for path in test_paths:
        relative_name(path)
        require(path.endswith('.java') and (('/src/test/java/' in path and path.startswith('src/')) or path.startswith('tools/quality/architecture/')), 'whole Test boundary')
    require(set(c['productOwnerByMainPath']) == set(main) and all(re.fullmatch(r'WBS-[A-Z0-9]+(?:-[A-Z0-9]+)*', v) for v in c['productOwnerByMainPath'].values()), 'explicit artifact owner, no cloned business label')
    require(sum(t['tests'] for t in tests) == c.get('expectedTests') and c['expectedTests'] > 0, 'whole expected Test count')
    for item in c.get('resources', []):
        require(set(item) == {'path', 'placement'} and item['placement'] in ['TEST_CLASSPATH', 'PUBLIC_REPOSITORY'], 'resource schema')
        path = relative_name(item['path'])
        require(('/src/test/resources/' in path and path.startswith('src/')) if item['placement'] == 'TEST_CLASSPATH' else (path.startswith('src/deployment/config/') and path.endswith('.template')), 'public literal resource boundary')
    for p in c.get('sdkJars', []):
        relative_name(p)
        import pgpt_artemis_sdk as mq_sdk
        reviewed_sdk = c.get('reviewedArtemisSdk') is not None and p in mq_sdk.SDK_PATHS
        require(reviewed_sdk or p.endswith('.jar') and 'schubert' not in p.lower() and not any(x in p.lower() for x in ['postgres', 'artemis', 'hikari', 'jna', 'jnr']), 'prepared SDK only, no app/backend/native JAR')
    dependencies = c.get('preparedDependencyHashes')
    expected_dependencies = {str(p) for p in [ANN, CONSOLE, *[TC / 'm2/repository' / x for x in c.get('sdkJars', [])]]}
    require(isinstance(dependencies, dict) and set(dependencies) == expected_dependencies and all(isinstance(v, str) and re.fullmatch(r'[0-9a-f]{64}', v) for v in dependencies.values()), 'explicit complete approved SDK hash set')
    physical = c.get('physicalClasses')
    require(isinstance(physical, list) and physical and len(physical) == len(set(physical)), 'explicit full physical universe')
    for p in physical:
        relative_name(p)
        require(p.startswith('dev/codex/schubert/nk/') and p.endswith('.class'), 'physical namespace')
    targets = c.get('targetClasses')
    require(isinstance(targets, list) and targets and len(targets) == len(set(targets)) and all(n + '.class' in physical for n in targets), 'explicit executable targets')
    for n in c.get('pomInputs', []):
        relative_name(n)
        require(n == 'pom.xml' or n.startswith('src/') and n.endswith('/pom.xml'), 'POM input')
    require('pom.xml' in c.get('pomInputs', []), 'Root compiler source required')
    for name, value in c.get('systemProperties', {}).items():
        require((name, value) in [('spring.security.strategy', 'MODE_THREADLOCAL'), ('nk.pt.repository', 'OWNED_PUBLIC_REPOSITORY')], 'bounded child JVM property')
    for item in c['oracleSpecs'] + c['closureProofs']:
        require(set(item) == {'path', 'sha256'} and re.fullmatch(r'[0-9a-f]{64}', item['sha256']), 'proof hash schema')
        path = relative_name(item['path'])
        require(path.startswith('evidence/') and Path(path).suffix in ['.md', '.json'] and '/private' not in path.lower(), 'public proof only')
    import pgpt_artemis_sdk
    pgpt_artemis_sdk.syntax(c)
    import pgpt_unstarted_process
    pgpt_unstarted_process.syntax(c)
    validate_optional_capabilities(c)
    import pgpt_guard_signature
    pgpt_guard_signature.syntax(c)
    import pgpt_analysis_symbols
    pgpt_analysis_symbols.syntax(c)
    require(set(c.get('slots', {})) == {'prestyle', 'prepare', 'static', 'preflight', 'unit', 'post'}, 'six explicit immutable evidence slots')
    require(len(set(c['slots'].values())) == 6, 'distinct evidence slots')
    for p in c['slots'].values():
        relative_name(p)
        require(re.fullmatch(r'evidence/01_PT/018_NK-OPS-001/evidence/PG[0-9]+-[a-z0-9-]+', p), 'owned public output boundary')
    require(set(c.get('privateDirs', {})) == {'prepare', 'unit'}, 'explicit private owned dirs')
    require(len(set(c['privateDirs'].values())) == 2 and all(re.fullmatch(r'pg[0-9]+-[a-z0-9-]+', v) for v in c['privateDirs'].values()), 'fresh private run names')
    return c


def validate_optional_capabilities(c):
    import pgpt_protocol_public_oracle
    pgpt_protocol_public_oracle.syntax(c)
    """Explicit reviewed source capabilities; never infer permission from a matching name."""
    reflection = c.get('reviewedReflection', [])
    require(isinstance(reflection, list) and len(reflection) <= 1, 'one reviewed immutable History reflection only')
    for item in reflection:
        require(set(item) == {'testPath', 'targetClass', 'sourceAnchor', 'targetSource', 'closureProof'}, 'reflection schema')
        require(item['testPath'] in [t['path'] for t in c['testSources']], 'reflection whole Test')
        target = 'dev.codex.schubert.nk.batch.repository.BatchRunRepository$History'
        require(item['targetClass'] == target, 'only source-reviewed immutable History, no Root/authority reflection')
        require(item['sourceAnchor'] == 'var type = Class.forName("' + target + '");', 'one exact reflection anchor')
        require(item['targetSource'] in c['mainSources'] and item['targetSource'].endswith('/BatchRunRepository.java'), 'whole reviewed parent source')
        require(target.replace('.', '/') + '.class' in c['physicalClasses'], 'full History physical class')
        require(item['closureProof'] in c['closureProofs'], 'explicit reflection closure proof')
    forbidden = c.get('forbiddenInitializedClasses', [])
    require(isinstance(forbidden, list) and len(forbidden) == len(set(forbidden)), 'unique forbidden initialization set')
    for name in forbidden:
        relative_name(name)
        import pgpt_guard_signature as guard
        signature_fence = c.get('reviewedGuardSignature') is not None and name in guard.FORBIDDEN_INIT
        import pgpt_analysis_symbols as analysis
        analysis_fence = c.get('reviewedAnalysisOnlyContext') is not None and name in analysis.NAMES
        import pgpt_unstarted_process as process
        process_fence = c.get('reviewedUnstartedProcess') is not None and name in process.FORBIDDEN_INIT
        require(name + '.class' in c['physicalClasses'] or signature_fence or analysis_fence or process_fence, 'forbidden initialization in full physical scope or exact signature/analysis fence')
    for item in reflection:
        require(item['targetClass'].split('$')[0].replace('.', '/') in forbidden, 'JDBC parent must not initialize')
    maps = c.get('standardCompilerSwitchMaps', [])
    require(isinstance(maps, list) and len(maps) == len({x.get('className') for x in maps}), 'unique compiler maps')
    for item in maps:
        require(set(item) == {'className', 'enumClass', 'sourcePath'}, 'compiler map schema')
        name = relative_name(item['className'])
        require(name.endswith('$1') and name + '.class' in c['physicalClasses'], 'explicit physical compiler map')
        require(name not in c['targetClasses'], 'compiler map is not a claimed executable target')
        require(item['sourcePath'] in c['mainSources'] and name.split('$')[0].endswith('/' + Path(item['sourcePath']).stem), 'same-source compiler map owner')
        enum = item['enumClass']
        require(isinstance(enum, str) and re.fullmatch(r'dev\.codex\.schubert\.nk\.[A-Za-z0-9_.$]+', enum) and enum.replace('.', '/') + '.class' in c['physicalClasses'], 'explicit same-component enum')


def input_paths(c):
    import pgpt_guard_signature as guard
    import pgpt_analysis_symbols as analysis
    import pgpt_unstarted_process as process
    return c['mainSources'] + [t['path'] for t in c['testSources']] + [r['path'] for r in c.get('resources', [])] + c['pomInputs'] + QUALITY_INPUTS + ([guard.SOURCE] if c.get('reviewedGuardSignature') is not None else []) + (analysis.SOURCE_PATHS if c.get('reviewedAnalysisOnlyContext') is not None else []) + ([process.SOURCE, process.TESTDIR + 'InspectorUnitSnapshotTest.java'] if c.get('reviewedUnstartedProcess') is not None else [])


def validate_owners(c, owners):
    require(all(owners.get(p) == owner for p, owner in c['productOwnerByMainPath'].items()), 'artifact owner mismatch')


def tool_hashes():
    paths = ['tools/quality/' + n + '.py' for n in ['pgpt_closed_host_profile', 'pgpt_closed_host_stages', 'pgpt_closed_host_post', 'pgpt_guard_signature', 'pgpt_analysis_symbols', 'pgpt_artemis_sdk', 'pgpt_unstarted_process', 'pgpt_public_unit_xml', 'pgpt_protocol_public_oracle']]
    return {p: digest(R / p) for p in paths}


def checked_inputs(c):
    # Name/HOLD rejection precedes every product path stat/read.
    validate_syntax(c)
    paths = input_paths(c)
    require(len(paths) == len(set(paths)), 'unique frozen inputs')
    inventory = read_json(R / 'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json')
    validate_owners(c, {x['path']: x['owner'] for x in inventory['artifacts']})
    for p in paths:
        require(not (R / p).is_symlink() and (R / p).is_file(), 'regular public input')
    hashes = {p: digest(R / p) for p in paths}
    require(hashes[QUALITY_INPUTS[0]] == hashlib.sha256(subprocess.check_output(['git', 'show', PMD_POLICY_SOURCE + ':' + QUALITY_INPUTS[0]], cwd=R)).hexdigest(), 'full approved Root PMD policy unchanged')
    for item in c['oracleSpecs'] + c['closureProofs']:
        require(digest(R / item['path']) == item['sha256'], 'independent proof changed')
    for item in c.get('reviewedReflection', []):
        proof = read_json(R / item['closureProof']['path'])
        reviewed = proof.get('reflection', {})
        require(proof.get('actualExit') == 0 and proof.get('privateRootOrHeldClassActions') == 0, 'reviewed immutable source closure')
        require(all(reviewed.get(k) == item[k] for k in ['testPath', 'targetClass', 'sourceAnchor', 'targetSource']), 'exact original reflection proof')
        require(proof.get('inputHashes', {}).get(item['targetSource']) == hashes[item['targetSource']], 'whole parent source unchanged since closure')
        require(proof.get('forbiddenInitializedClasses') == c.get('forbiddenInitializedClasses'), 'all JDBC parents remain runtime-forbidden')
        source = (R / item['testPath']).read_text()
        require(source.count(item['sourceAnchor']) == source.count('Class.forName') == 1, 'no additional reflection call')
    import pgpt_unstarted_process as process
    process.checked(c)
    import pgpt_protocol_public_oracle
    pgpt_protocol_public_oracle.checked(c)
    for path in c['mainSources'] + [t['path'] for t in c['testSources']]:
        text = pgpt_protocol_public_oracle.reviewed_text(c, path, (R / path).read_text())
        for item in c.get('reviewedReflection', []):
            if path == item['testPath']:
                text = text.replace(item['sourceAnchor'], '', 1)
        require(not any(x in text for x in [*DENIED, '@BeforeAll', '@TestFactory', '@ParameterizedTest', 'DriverManager', 'DataSource', 'Class.forName', 'java.lang.foreign', 'java.net.Socket']), 'outside closed ordinary host scope')
        require('ProcessBuilder' not in text or process.allow_builder(c, path, text), 'outside closed ordinary host ProcessBuilder scope')
    import pgpt_guard_signature
    pgpt_guard_signature.checked(c)
    import pgpt_analysis_symbols
    pgpt_analysis_symbols.checked(c)
    import pgpt_artemis_sdk
    pgpt_artemis_sdk.checked(c)
    return hashes


def expected_cases(c):
    cases = []
    for item in c['testSources']:
        text = (R / item['path']).read_text()
        methods = re.findall(r'@Test[ \t]*(?://[^\r\n]*)?\s*(?:@Timeout\([^\n]+\)\s*)?void (\w+)\s*\(', text)
        require(len(methods) == item['tests'], 'whole Test method count changed')
        package = re.search(r'package ([A-Za-z0-9_.]+);', text).group(1)
        cases.extend(dict(classname=package + '.' + Path(item['path']).stem, name=n + '()') for n in methods)
    require(len(cases) == c['expectedTests'], 'expected cases')
    return cases


def compiler_element():
    ns = 'http://maven.apache.org/POM/4.0.0'
    ET.register_namespace('', ns)
    tag = lambda n: '{' + ns + '}' + n
    root = ET.parse(R / 'pom.xml').getroot()
    compiler = next(p for p in root.findall('.//' + tag('plugin')) if p.findtext(tag('artifactId')) == 'maven-compiler-plugin')
    body = ET.tostring(compiler).decode()
    require('-Xep:NullAway:ERROR' in body and '-Werror' in body and 'JSpecifyMode' in body, 'unchanged Root NullAway policy')
    return compiler, tag


def class_hashes(folder):
    return {str(p.relative_to(folder)): digest(p) for p in folder.rglob('*.class')}


def environment(c, slot):
    out = R / c['slots'][slot]
    require(not out.exists(), 'immutable evidence already exists; recover original stage, do not retry')
    out.mkdir()
    steps.SLOT = out
    os.environ['JAVA_HOME'] = str(TC / 'jdk-25.0.4')
    return out


def prestyle(c, config):
    hashes = checked_inputs(c)
    out = environment(c, 'prestyle')
    paths = c['mainSources'] + [t['path'] for t in c['testSources']]
    listing = out / 'sources.txt'
    listing.write_text(''.join(str(R / p) + '\n' for p in paths))
    sg = TC / 'static-gates-20261015'
    rules = out / 'preliminary-two-style-rules.xml'
    rules.write_text('<ruleset name="Preliminary only" xmlns="http://pmd.sourceforge.net/ruleset/2.0.0"><description>Full Root rules remain mandatory.</description><rule ref="category/java/errorprone.xml/AvoidDuplicateLiterals"/><rule ref="category/java/errorprone.xml/AvoidFieldNameMatchingMethodName"/></ruleset>\n')
    libs = [sg / 'record-fix-v1/pmd-record-1298.jar', *sorted((sg / 'pmd-bin-7.28.0/lib').glob('*.jar'))]
    stages = {'style-pmd': steps.step('style-pmd', [str(JAVA), '-cp', ':'.join(map(str, libs)), 'net.sourceforge.pmd.cli.PmdCli', 'check', '--file-list', str(listing), '--rulesets', str(rules), '--use-version', 'java-25', '--no-cache', '--format', 'xml', '--report-file', str(out / 'pmd.xml')], R)}
    # One invocation checks exactly the same finite path list and original formatter flags.
    # Each file is still checked; this avoids one JVM startup per source (204 for SSC451).
    stages['format-batch'] = steps.step('format-batch', [str(JAVA), '-jar', str(TC / 'google-java-format-1.36.1-all-deps.jar'), '--skip-reflowing-long-strings', '--dry-run', '--set-exit-if-changed', *[str(R / p) for p in paths]], R)
    stages['checkstyle'] = steps.step('checkstyle', [str(JAVA), '-jar', str(sg / 'checkstyle-14.3.0-all.jar'), '-c', str(R / 'tools/quality/static/checkstyle.xml'), '-f', 'xml', '-o', str(out / 'checkstyle.xml'), '@' + str(listing)], R)
    issues = [x for x in ET.parse(out / 'pmd.xml').iter() if x.tag.rpartition('}')[2] in ['violation', 'error', 'configerror']]
    okay = not issues and not ET.parse(out / 'checkstyle.xml').findall('.//error') and all(x['actualExit'] == 0 and not x['timedOut'] for x in stages.values())
    m = dict(actualExit=0 if okay else 1, config=ref(config), inputHashes=hashes, preliminaryOnly=True, fullQualityGateSatisfied=False, stages=stages, productTestsExecuted=0, verifier=ref(Path(__file__).resolve()))
    write_json(out / 'manifest.json', m)
    require(okay, 'prestyle failed; ticket before correction, preserve original evidence')
    return m


def prepare(c, config):
    hashes = checked_inputs(c)
    pre = R / c['slots']['prestyle'] / 'manifest.json'
    pm = read_json(pre)
    require(pm['actualExit'] == 0 and pm['inputHashes'] == hashes and pm['config'] == ref(config), 'same-input prestyle required')
    dependency_paths = [ANN, CONSOLE, *[TC / 'm2/repository' / p for p in c.get('sdkJars', [])]]
    require(all(not p.is_symlink() and p.is_file() for p in dependency_paths), 'regular prepared SDK files')
    deps = {str(p): digest(p) for p in dependency_paths}
    require(deps == c.get('preparedDependencyHashes'), 'explicit approved SDK hashes, no implicit replacement')
    cases = expected_cases(c)
    work = RUNS / c['privateDirs']['prepare']
    require(not work.exists(), 'fresh prepare only')
    out = environment(c, 'prepare'); work.mkdir(); (work / 'test-classes').mkdir()
    import pgpt_guard_signature as guard
    signature = guard.create_compile_carrier(c, work)
    import pgpt_unstarted_process as process
    type_signature = process.create_compile_carrier(c, work)
    for p in c['mainSources']:
        to = work / 'src/main/java' / p.split('/src/main/java/')[1]
        to.parent.mkdir(parents=True, exist_ok=True); to.write_bytes((R / p).read_bytes())
    for item in c.get('resources', []):
        p = item['path']
        to = work / 'test-classes' / p.split('/src/test/resources/')[1] if item['placement'] == 'TEST_CLASSPATH' else work / 'public-repository' / p
        to.parent.mkdir(parents=True, exist_ok=True); to.write_bytes((R / p).read_bytes())
        require(digest(to) == hashes[p], 'resource copy')
    compiler, tag = compiler_element()
    root = ET.Element(tag('project'))
    def add(parent, name, value=None):
        el = ET.SubElement(parent, tag(name)); el.text = value; return el
    for n, v in [('modelVersion', '4.0.0'), ('groupId', 'dev.codex.schubert.quality'), ('artifactId', c['id'].lower()), ('version', '0.1.0-SNAPSHOT')]: add(root, n, v)
    props = add(root, 'properties')
    for n, v in [('maven.compiler.release', '25'), ('project.build.sourceEncoding', 'UTF-8'), ('error-prone.version', '2.50.0'), ('nullaway.version', '0.14.1')]: add(props, n, v)
    ds = add(root, 'dependencies'); d = add(ds, 'dependency')
    for n, v in [('groupId', 'org.jspecify'), ('artifactId', 'jspecify'), ('version', '1.0.1')]: add(d, n, v)
    for i, jar in enumerate(c.get('sdkJars', [])):
        d = add(ds, 'dependency')
        for n, v in [('groupId', 'dev.codex.schubert.quality'), ('artifactId', f'closed-sdk-{i}'), ('version', '1'), ('scope', 'system'), ('systemPath', str(TC / 'm2/repository' / jar))]: add(d, n, v)
    if signature is not None:
        d = add(ds, 'dependency')
        for n, v in [('groupId', 'dev.codex.schubert.quality'), ('artifactId', 'real-guard-compile-symbols'), ('version', '1'), ('scope', 'system'), ('systemPath', signature['compileCarrier']['path'])]: add(d, n, v)
    if type_signature is not None:
        d = add(ds, 'dependency')
        for n, v in [('groupId', 'dev.codex.schubert.quality'), ('artifactId', 'real-outcome-compile-symbols'), ('version', '1'), ('scope', 'system'), ('systemPath', type_signature['compileCarrier']['path'])]: add(d, n, v)
    add(add(root, 'build'), 'plugins').append(copy.deepcopy(compiler))
    ET.ElementTree(root).write(work / 'pom.xml', encoding='unicode', xml_declaration=True)
    stages = {'nullaway-compile': steps.step('nullaway-compile', [str(MAVEN), '-o', '--no-transfer-progress', '-Dmaven.repo.local=' + str(TC / 'm2/repository'), '-Dmaven.test.skip=true', 'compile'], work)}
    require(stages['nullaway-compile']['actualExit'] == 0 and not stages['nullaway-compile']['timedOut'], 'Main compile failed; no retry')
    guard.copy_runtime_interface(signature, work)
    process.copy_runtime_enum(type_signature, work)
    process.create_analysis_pom(type_signature, work)
    compile_only = [signature['compileCarrier']['path']] if signature is not None else []
    if type_signature is not None: compile_only.append(type_signature['compileCarrier']['path'])
    stages['test-compile'] = steps.step('test-compile', [str(JAVAC), '--release', '25', '-g', '-proc:none', '-implicit:none', '-encoding', 'UTF-8', '-Xlint:all', '-Werror', '-cp', str(work / 'target/classes') + ':' + ':'.join([*deps, *compile_only]), '-d', str(work / 'test-classes'), *[str(R / t['path']) for t in c['testSources']]], R)
    require(stages['test-compile']['actualExit'] == 0 and not stages['test-compile']['timedOut'], 'whole Test compile failed; no retry')
    physical = class_hashes(work / 'target/classes')
    require(set(physical) == set(c['physicalClasses']), 'full physical class universe differs')
    import shutil
    shutil.copytree(work / 'target/classes', work / 'component')
    import pgpt_analysis_symbols as analysis
    analysis_context = analysis.create_owned_context(c, work) if c.get('reviewedAnalysisOnlyContext') is not None else None
    m = dict(actualExit=0, config=ref(config), inputHashes=hashes, dependencies=deps, toolHashes=tool_hashes(), physicalClassHashes=physical, testClassHashes=class_hashes(work / 'test-classes'), expectedCases=cases, selectedClasses=sorted({x['classname'] for x in cases}), stages=stages, preliminaryStyle=ref(pre), rootCompilerSha256=hashlib.sha256(ET.tostring(compiler)).hexdigest(), subsetPomSha256=digest(work / 'pom.xml'), productTestsExecuted=0, MainCompiled=True, wholeProjectMainRebuilt=False, verifier=ref(Path(__file__).resolve()))
    m.update(unstartedProcess=type_signature, analysisOnlyContext=analysis_context, guardSignature=signature, freshMainSourceCount=len(c['mainSources']), reusedRuntimeSignatureClassCount=1 if signature is not None else 0)
    write_json(out / 'manifest.json', m)
    return m


def main():
    require(len(sys.argv) >= 3, 'phase config [fixed-source]')
    phase = sys.argv[1]; config = Path(sys.argv[2]).resolve()
    require(config.is_relative_to(R / 'evidence'), 'public configuration boundary')
    c = validate_syntax(read_json(config))
    require(phase in ['prestyle', 'prepare', 'static', 'preflight', 'run'], 'supported phase')
    if phase == 'prestyle': result = prestyle(c, config)
    elif phase == 'prepare': result = prepare(c, config)
    else:
        from pgpt_closed_host_stages import static, preflight, run
        result = {'static': static, 'preflight': preflight, 'run': run}[phase](c, config, sys.argv[3:])
    print(json.dumps(dict(actualExit=result['actualExit'], phase=phase, profile=c['id'], productTestsExecuted=result.get('productTestsExecuted', 0))))
    if result['actualExit'] != 0:
        raise SystemExit(result['actualExit'])


if __name__ == '__main__':
    main()
