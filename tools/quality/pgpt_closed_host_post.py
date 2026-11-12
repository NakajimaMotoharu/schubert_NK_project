"""Independent whole-scope terminal/XML/Git/class-init/CRC/JaCoCo verification.

Only the explicit closed component is qualified. Natural no-Code/zero-branch classes
are reported; misses are retained, never excluded or combined with an earlier exec.
"""
from pathlib import Path
import ast
import hashlib
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

import pgpt_closed_host_profile as policy


def validate_switch_map_shape(text, item):
    """Verify one javac enum switch map, not an arbitrary uncovered synthetic class."""
    require = policy.require
    require(re.search(r'interfaces:\s*0, fields:\s*1, methods:\s*1,', text), 'map has exactly one field and clinit')
    require(re.search(r'flags:.*ACC_SUPER.*ACC_SYNTHETIC', text), 'javac synthetic map class flags')
    field = '$SwitchMap$' + item['enumClass'].replace('.', '$')
    require(text.count('static final int[] ' + field + ';') == 1, 'exact enum map field')
    require(re.search(r'flags:.*ACC_STATIC.*ACC_FINAL.*ACC_SYNTHETIC', text), 'synthetic static final map field flags')
    require(text.count('static {};') == 1 and 'SourceFile: "' + Path(item['sourcePath']).name + '"' in text, 'same source clinit map only')


def verify(c, config, source):
    root = policy.R
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    load = lambda p: json.loads(p.read_text())
    require = policy.require
    policy.validate_syntax(c)
    unit = policy.RUNS / c['privateDirs']['unit']
    work = policy.RUNS / c['privateDirs']['prepare']
    artifact = root / c['slots']['unit']
    m = load(artifact / 'manifest.json'); b = m['begin']
    require((m['actualExit'], m['tests'], m['failures'], m['errors'], m['skipped']) == (0, c['expectedTests'], 0, 0, 0), 'true whole-run terminal success required')
    require(b['source'] == source and b['config'] == policy.ref(config) and b['productionCoreMain'] == c['productionCoreMain'], 'same source/config/run')
    require(not b['oldExecUnion'] and not b['coverageExclusions'], 'no old exec or exclusions')
    for name, value in b['metadataPins'].items():
        require(sha(root / name) == value == hashlib.sha256(subprocess.check_output(['git', 'show', source + ':' + name], cwd=root)).hexdigest(), 'fixed Git input/metadata bytes')
    for name, value in b['dependencies'].items(): require(sha(Path(name)) == value, 'same SDK bytes')
    for label, stage in m['stages'].items():
        require(stage['actualExit'] == 0 and not stage['timedOut'] and stage == load(artifact / (label + '-exit.safe.json')), 'actual stage terminal')
        for stream in ['stdout', 'stderr']: require(sha(artifact / (label + '.' + stream)) == stage[stream + 'Sha256'], 'unit stream hash')
    pf = root / b['preflight']['path']; p = load(pf)
    require(sha(pf) == b['preflight']['sha256'] and p['inputHashes'] == b['inputHashes'] and all(p[k] == 0 for k in ['staticApplicable', 'unclassified', 'processingErrors', 'checkstyle', 'spotbugs']), 'independent preflight')
    prep = load(root / b['prepare']['path'])
    require(sha(root / b['prepare']['path']) == b['prepare']['sha256'], 'prepare hash')
    expected = set()
    for test in c['testSources']:
        text = (root / test['path']).read_text()
        package = re.search(r'^package\s+([\w.]+);', text, re.M).group(1)
        names = [x.group(1) + '()' for x in re.finditer(r'@Test\s*(?:@Timeout\([^\n]*\)\s*)?void\s+(\w+)\s*\(', text)]
        require(len(names) == test['tests'], 'independent whole Test count')
        expected.update((package + '.' + Path(test['path']).stem, name) for name in names)
    selected = sorted({x[0] for x in expected}); cmd = m['stages']['unit']['command']
    require(b['selectedClasses'] == selected and cmd.count('--select-class') == len(selected), 'whole class selectors')
    require(not any(x in str(cmd) for x in ['--select-method', '--scan-classpath', 'excludes=', 'append=true', 'enable-native-access']), 'no selective or native override')
    require(m['stages']['unit']['cwd'] == str(unit), 'owned run cwd')
    actual = []; env = {}
    for xml in (unit / 'xml').glob('TEST-*.xml'):
        tree = ET.parse(xml).getroot()
        require(not any(tree.findall('.//' + tag) for tag in ['failure', 'error', 'skipped']), 'XML F/E/S')
        actual.extend((x.get('classname'), x.get('name')) for x in tree.findall('testcase'))
        env.update({x.get('name'): x.get('value') for x in tree.findall('./properties/property') if x.get('name') in ['os.name', 'os.arch', 'java.version', 'file.encoding', 'user.timezone']})
    require(len(expected) == len(actual) == c['expectedTests'] and set(actual) == expected, 'XML unique expected full set')
    transcript = (artifact / 'unit.stdout').read_text()
    for text in [f'{c["expectedTests"]} tests found', f'{c["expectedTests"]} tests started', f'{c["expectedTests"]} tests successful', '0 tests failed', '0 tests skipped', '0 tests aborted', '0 containers aborted']: require(text in transcript, 'JUnit terminal summary')
    physical = {str(x.relative_to(work / 'component')): sha(x) for x in (work / 'component').rglob('*.class')}
    require(physical == b['physicalClassHashes'] == prep['physicalClassHashes'] and set(physical) == set(c['physicalClasses']), 'complete physical universe')
    require({str(x.relative_to(work / 'target/classes')): sha(x) for x in (work / 'target/classes').rglob('*.class')} == physical, 'no different report Main bytes')
    require({str(x.relative_to(work / 'test-classes')): sha(x) for x in (work / 'test-classes').rglob('*.class')} == b['testClassHashes'], 'exact whole Test bytes')
    for resource in c.get('resources', []):
        name = resource['path']
        copied = work / 'test-classes' / name.split('/src/test/resources/')[1] if resource['placement'] == 'TEST_CLASSPATH' else work / 'public-repository' / name
        require(sha(copied) == b['inputHashes'][name], 'immutable public resource copy')
    # Reuse pure classfile readers only; never execute an earlier product producer or class.
    helper = root / 'evidence/01_PT/018_NK-OPS-001/input/1415_manifest_current_independent_post.py'
    nodes = [n for n in ast.parse(helper.read_text()).body if isinstance(n, ast.FunctionDef) and n.name in ['crc64', 'code_count']]
    require(len(nodes) == 2, 'explicit pure classfile reader functions')
    import struct
    namespace = dict(struct=struct)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(helper), 'exec'), namespace)
    ids = {n[:-6]: namespace['crc64']((work / 'component' / n).read_bytes()) for n in physical}
    method_counts = {n[:-6]: namespace['code_count']((work / 'component' / n).read_bytes()) for n in physical}
    signature = b.get('guardSignature')
    if c.get('reviewedGuardSignature') is not None:
        # Independent byte/ZIP/command checks; do not call the producer's cache reader.
        import zipfile
        outer_name = 'dev/codex/schubert/nk/bootstrap/MaintenanceOwnerFrame'
        guard_name = outer_name + '$Guard'
        expected_hashes = {
            outer_name: 'cf12980ffcb4982da0b9cd5425730825a5cd8762bfdcdc581aa3cf6ab18b46ea',
            guard_name: '53f2b39f586ec6ee172b0e3009d46638a60ca8f1ce8ad442f497affa6cbd869b',
        }
        require(signature == prep.get('guardSignature') and isinstance(signature, dict), 'same signature receipt')
        carrier = work / 'guard-compile-signatures.jar'
        require(signature['compileCarrier'] == dict(path=str(carrier), sha256=sha(carrier)), 'own exact compiler carrier')
        with zipfile.ZipFile(carrier) as archive:
            require(len(archive.namelist()) == 2 and set(archive.namelist()) == {n + '.class' for n in expected_hashes}, 'two compiler symbols only')
            require(all(hashlib.sha256(archive.read(n + '.class')).hexdigest() == value for n, value in expected_hashes.items()), 'compiler symbol bytes')
        require(physical[guard_name + '.class'] == expected_hashes[guard_name] and outer_name + '.class' not in physical, 'runtime/report interface only')
        require(ids[guard_name] == 'b5b153f7fd9d91fa', 'real Guard positive witness CRC')
        runtime_paths = cmd[cmd.index('--class-path') + 1].split(':')
        require(runtime_paths == [str(work / 'target/classes'), str(work / 'test-classes'), *b['dependencies']] and
                str(carrier) not in runtime_paths, 'exact runtime paths, compiler carrier absent')
        required_forbidden = {outer_name, 'dev/codex/schubert/nk/bootstrap/ChildStartupContext', 'dev/codex/schubert/nk/storage/LinuxMonotonicClock'}
        require(required_forbidden <= set(c.get('forbiddenInitializedClasses', [])), 'no outer/native initialization permission')
    else:
        require(signature is None, 'no implicit signature component')
    no_code = {n for n, value in method_counts.items() if value == 0}
    info = {name: dict(crc=crc, instructions=int(inst)) for inst, branch, line, method, complexity, crc, name in re.findall(r'^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+class 0x([0-9a-f]{16}) (\S+)$', (artifact / 'classinfo.stdout').read_text(), re.M)}
    analyzed = {n for n, x in info.items() if x['instructions'] > 0}
    maps = {x['className']: x for x in c.get('standardCompilerSwitchMaps', [])}
    map_evidence = {}
    for name, item in maps.items():
        require(name in info and method_counts[name] == 1 and info[name]['instructions'] == 0, 'standard analyzer map zero, physical clinit retained')
        cmd = [str(policy.JAVA.with_name('javap')), '-p', '-v', str(work / 'component' / (name + '.class'))]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=False)
        require(result.returncode == 0 and not result.stderr, 'owned compiler map disassembly terminal')
        validate_switch_map_shape(result.stdout, item)
        map_evidence[name] = dict(command=cmd, actualExit=result.returncode, disassembly=result.stdout, enumClass=item['enumClass'], physicalCrc=ids[name], codeMethods=1, analyzerInstructions=0, customFilter=False)
    require(analyzed == set(ids) - no_code - set(maps), 'unexpected compiler artifact/analysis gap; no exclusion')
    missing = set(ids) - set(info)
    require(all(n.endswith('/package-info') and n in no_code for n in missing), 'unexpected omitted physical class')
    require(all(ids[n] == x['crc'] for n, x in info.items()), 'classinfo actual CRC')
    require(set(info) - analyzed == (no_code - missing) | set(maps), 'only proven default-filtered maps or natural no-Code')
    ex = (artifact / 'execinfo.stdout').read_text()
    require(ex.count('Session "') == 1 and 'Session "' + c['id'] + '"' in ex, 'one exact exec session')
    probes = {n: (crc, int(hit), int(total)) for crc, hit, total, n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$', ex, re.M)}
    test_names = {n[:-6] for n in b['testClassHashes']}
    observed = {n for n in probes if n.startswith('dev/codex/schubert/nk/') and n not in test_names}
    if signature is not None:
        require(guard_name in observed, 'fresh real Guard execution required')
    require(observed <= analyzed | set(maps) and all(probes[n][0] == ids[n] and probes[n][1] > 0 for n in observed), 'positive same-Main CRC only')
    init = {n for n in re.findall(r"Initializing '([^']+)'", (unit / 'class-init.log').read_text()) if n.startswith('dev/codex/schubert/nk/') and not any(n == t or n.startswith(t + '$') for t in test_names)}
    require(not any(n.rpartition('/')[2].split('$')[0] in policy.DENIED for n in init), 'held class initialized')
    require(not set(c.get('forbiddenInitializedClasses', [])) & init, 'source-reviewed compile-only JDBC parent initialized')
    real = init & set(ids)
    require(real - observed <= no_code and observed <= real, 'class init and exec membership')
    bindings = {}
    for n in init - set(ids):
        match = re.fullmatch(r'(dev/codex/schubert/nk/[^+]+)\$\$Lambda\+0x[0-9a-f]+', n)
        require(match is not None and match.group(1) in ids, 'unknown initialized application adapter')
        bindings[n] = match.group(1)
    tree = ET.parse(unit / 'coverage.xml').getroot(); classes = {x.get('name'): x for x in tree.findall('.//class')}
    require(set(classes) == set(info), 'coverage full analyzer universe')
    counters = lambda el: {x.get('type'): dict(covered=int(x.get('covered')), missed=int(x.get('missed'))) for x in el.findall('counter')}
    coverage = counters(tree)
    for key, row in coverage.items():
        for field in ['covered', 'missed']: require(sum(counters(el).get(key, {}).get(field, 0) for el in classes.values()) == row[field], 'independent full counter sum')
    uncovered = {n: {k: row['missed'] for k, row in counters(el).items() if row['missed'] > 0} for n, el in classes.items() if any(row['missed'] > 0 for row in counters(el).values())}
    targets = {n: counters(classes[n]) for n in c['targetClasses']}
    component = {key: dict(covered=sum(v.get(key, {}).get('covered', 0) for v in targets.values()), missed=sum(v.get(key, {}).get('missed', 0) for v in targets.values())) for key in set().union(*(set(v) for v in targets.values()))}
    component100 = all(component.get(k, {}).get('covered', 0) > 0 and component[k]['missed'] == 0 for k in ['LINE', 'METHOD', 'CLASS', 'BRANCH'])
    out = policy.environment(c, 'post'); files = {}
    for i, (name, value) in enumerate(map_evidence.items()):
        filename = f'standard-switch-map-{i:03d}.txt'
        (out / filename).write_text(value.pop('disassembly'))
        files[filename] = sha(out / filename)
        value['disassemblyFile'] = filename
    for base, prefix in [(artifact, 'unit-'), (unit, 'original-')]:
        candidates = [x for x in base.iterdir() if x.is_file()] + list((base / 'xml').glob('TEST-*.xml'))
        for path in candidates:
            require(path.suffix != '.class', 'no product binaries in public evidence')
            name = 'jacoco.exec' if path.name == 'jacoco.exec' else prefix + ('class-init.stdout' if path.name == 'class-init.log' else path.name)
            require(name not in files, 'unique copied evidence name')
            shutil.copyfile(path, out / name); files[name] = sha(out / name)
    result = dict(actualExit=0, source=source, productionCoreMain=b['productionCoreMain'], config=policy.ref(config), run=c['id'], tests=len(actual), newTestDefinitions=c.get('newTestDefinitions', 0), physicalClasses=len(physical), positiveMainCrc=len(observed), coverage=coverage, targetCounters=targets, completeSourceComponentCounters=component, completeSourceComponentFour100=component100, wholeScopeFour100=not uncovered, uncoveredFullSourceClasses=uncovered, naturalNoCodeClasses=sorted(no_code), naturalNoBranchClasses=sorted(n for n, row in targets.items() if 'BRANCH' not in row), classIds=ids, actualJvmCodeMethodCounts=method_counts, hiddenJvmAdapters=bindings, manualCoverageExclusions=[], oldExecCombined=False, preflight=policy.ref(pf), inputHashes=b['inputHashes'], dependencies=b['dependencies'], environment=env, productTestsExecuted=len(actual), actualBackendNativeFsRootOrHeldClassActions=0, formalUpdated=False, whole451Accepted=False, newAcceptance=0, effortRate=None, files=files, verifier=policy.ref(Path(__file__).resolve()))
    result.update(defaultStandardFilteredSwitchMaps=map_evidence, forbiddenInitializedClasses=c.get('forbiddenInitializedClasses', []), forbiddenInitializedClassesObserved=[], reviewedReflection=c.get('reviewedReflection', []))
    result['guardSignature'] = signature
    policy.write_json(out / 'manifest.json', result)
    return result


if __name__ == '__main__':
    policy.require(len(sys.argv) == 3, 'config fixed-source')
    config = Path(sys.argv[1]).resolve()
    result = verify(policy.read_json(config), config, sys.argv[2])
    print(json.dumps({k: result[k] for k in ['actualExit', 'tests', 'physicalClasses', 'positiveMainCrc', 'completeSourceComponentFour100', 'wholeScopeFour100']}))
