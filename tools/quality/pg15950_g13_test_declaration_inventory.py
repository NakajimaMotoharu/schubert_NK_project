"""Current source AST and compiled annotations only: never JUnit discovery or Test execution."""
import collections
import json
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9346_direct_companion_jdk_post as steps
from pg9978_plain_core_quality_post import test_classes
import pg15944_g13_current_main_method_inventory as normal

OUT = data.BASE / 'PG15950-g13-current-test-declaration-inventory-v1'
SLOT = data.ROOT.parent / 'pgpt-runs/PG379/pg15950-g13-current-test-declaration-inventory-v1'
REGISTRY = ('PG15908-current2064-observation-values-registry-v1', 'a2df9a72bc19eca2b725aaff0d5bee234c8da7cdb50e3ec3ce9cf0d5823b3c53')
READERS = [
    ('ExistingTestMethodJdkAudit', 'pg9590-current-test-method-inventory-v1', 'd9552556c572e1f61029829ee72592bfd83f8339a658233b95dd890566c55f23', {
        'ExistingTestMethodJdkAudit$1.class': 'd7f6c6657bb53df952aa1b2aca90e1a297b570e7c692e89467be6a766e2ab711',
        'ExistingTestMethodJdkAudit$2.class': 'f9ae62d2bf23d1f679fe29d4f93039e1e352c0965fcae9b80af34b02b9bf364d',
        'ExistingTestMethodJdkAudit$Method.class': 'a88d92d19c40b35edc3212fc5df4f00cb0c7a72c6bb404f300918ae5eecbd6a9',
        'ExistingTestMethodJdkAudit.class': 'fb0cb8d75401d6f0c06a55fd5ef6833d201d684cf3eebb5c0107f3d62d8d317d'}),
    ('PublicTestMethodMetadataAudit', 'pg9592-current-test-method-post-v1', 'd163f5bd671a7209313aa4dbe654b1c4f6b6e214dfd443e937f199368f526aa6', {
        'PublicTestMethodMetadataAudit$Method.class': 'dd9666be3a69d512fa7fb31e8e14e9823ad53bfa94c309adacd45f7f2edd20de',
        'PublicTestMethodMetadataAudit.class': '43595a47df89586f31c5923e39978b8fc3e6878406d74f9cc34cd4f56b7efc0f'})]

def require(ok, message):
    if not ok:
        raise ValueError(message)

def main():
    invocation = capture(__file__)
    require(not OUT.exists() and not SLOT.exists(), 'new-only')
    n = data.read_checked(data.BASE / normal.NORMAL[0] / 'manifest.json', normal.NORMAL[1])
    r = data.read_checked(data.BASE / REGISTRY[0] / 'manifest.json', REGISTRY[1])
    require(n['actualExit'] == r['actualExit'] == 0 and n['source'] == r['source'] == normal.SOURCE and len(r['cases']) == 2064, 'fixed current source/normal/registry')
    hashes = {p: h for p, h in n['begin']['inputHashes'].items() if p.startswith('src/') and '/src/test/java/' in p and p.endswith('.java')}
    require(len(hashes) == 856 and all(data.sha((data.ROOT / p).read_bytes()) == h for p, h in hashes.items()), 'all current856 Test bytes')
    physical = test_classes(n)
    require(len(physical) == 1978, 'all normal Test physical classes')
    snapshots = {Path(v['path']).parents[3] for v in n['jars'].values()}
    require(len(snapshots) == 1, 'one fixed normal snapshot')
    snapshot = snapshots.pop()
    class_paths = {(role, entry): snapshot / ('src/schubert-nk-' + role) / 'target/test-classes' / entry for role, entry in physical}
    require(all(data.sha(path.read_bytes()) == physical[key] for key, path in class_paths.items()), 'all compiled Test bytes fixed')
    reader_paths = []
    for name, slot, digest, classes in READERS:
        require(data.sha((data.ROOT / 'tools/quality/architecture' / (name + '.java')).read_bytes()) == digest, 'fixed parse-only helper source')
        directory = data.ROOT.parent / 'pgpt-runs/PG379' / slot / 'reader'
        require({p.name for p in directory.glob('*.class')} == set(classes) and all(data.sha((directory / f).read_bytes()) == h for f, h in classes.items()), 'fixed helper-only classpath')
        reader_paths.append(directory)
    SLOT.mkdir()
    source_catalog = SLOT / 'test-sources.txt'
    source_catalog.write_text('\n'.join(sorted(hashes)) + '\n')
    class_catalog = SLOT / 'test-classes.tsv'
    class_catalog.write_text(''.join(role + '\t' + str(path) + '\n' for (role, entry), path in sorted(class_paths.items())))
    steps.SLOT = SLOT
    runs = [steps.step('parse-test-source-declarations', [str(steps.TC / 'jdk-25.0.4/bin/java'), '-cp', str(reader_paths[0]), READERS[0][0], str(data.ROOT), str(source_catalog)])]
    require(runs[-1]['actualExit'] == 0 and not runs[-1]['timedOut'], 'source parse genuine terminal')
    runs.append(steps.step('read-test-annotations', [str(steps.TC / 'jdk-25.0.4/bin/java'), '-cp', str(reader_paths[1]), READERS[1][0], str(snapshot), str(class_catalog)]))
    require(runs[-1]['actualExit'] == 0 and not runs[-1]['timedOut'], 'binary annotation genuine terminal')
    source_lines = (SLOT / 'parse-test-source-declarations.stdout').read_text().splitlines()
    binary_lines = (SLOT / 'read-test-annotations.stdout').read_text().splitlines()
    require(source_lines[0] == 'SELFTEST\t7' and binary_lines[0] == 'SELFTEST\t6', 'own reader metadata vectors, not Product PT')
    declarations = []
    for line in source_lines[1:]:
        path, owner, method, parameters, start, end = line.split('\t')
        require(path in hashes and 0 < int(start) <= int(end), 'exact bounded source declaration')
        declarations.append(dict(path=path, sourceSha256=hashes[path], className=owner, method=method, parameterCount=int(parameters), startLine=int(start), endLine=int(end)))
    classes = {}
    annotated = []
    for line in binary_lines[1:]:
        fields = line.split('\t')
        if fields[0] == 'CLASS':
            _, role, name, filename, digest = fields
            require((role, name + '.class') in physical and physical[(role, name + '.class')] == digest and (role, name) not in classes, 'exact unique class')
            path = 'src/schubert-nk-' + role + '/src/test/java/' + name.rsplit('/', 1)[0] + '/' + filename
            require(path in hashes, 'SourceFile exact current Test source')
            classes[(role, name)] = dict(path=path, classSha256=digest)
        else:
            require(fields[0] == 'TEST' and len(fields) == 7, 'annotation record')
            _, role, name, method, descriptor, parameters, annotation = fields
            c = classes[(role, name)]
            annotated.append(dict(module=role, className=name.replace('/', '.'), method=method, descriptor=descriptor, parameterCount=int(parameters), annotationKind=annotation, path=c['path'], sourceSha256=hashes[c['path']], classSha256=c['classSha256']))
    require(len(classes) == 1978, 'all physical Test classes read as data')
    ast = collections.defaultdict(list)
    binary = collections.defaultdict(list)
    for d in declarations:
        ast[(d['className'], d['method'], d['parameterCount'])].append(d)
    ordinary = [a for a in annotated if a['annotationKind'] == 'org.junit.jupiter.api.Test']
    other = [a for a in annotated if a['annotationKind'] != 'org.junit.jupiter.api.Test']
    for a in ordinary:
        binary[(a['className'], a['method'], a['parameterCount'])].append(a)
    bound = []
    ambiguous = []
    for key in sorted(set(ast) | set(binary)):
        if len(ast[key]) != 1 or len(binary[key]) != 1 or ast[key][0]['path'] != binary[key][0]['path']:
            ambiguous.append(dict(className=key[0], method=key[1], parameterCount=key[2], sourceDeclarations=len(ast[key]), compiledDeclarations=len(binary[key]), inference='NONE'))
            continue
        bound.append(dict(**binary[key][0], sourceStartLine=ast[key][0]['startLine'], sourceEndLine=ast[key][0]['endLine'], binding='SOURCE_AST_AND_CLASS_ANNOTATION_ONLY_NOT_EXECUTED'))
    case_keys = {(c['classname'], c['name']) for c in r['cases']}
    require(len(case_keys) == 2064, 'unique existing executed cases, not invented')
    methods_by_case = collections.defaultdict(list)
    for b in bound:
        methods_by_case[(b['className'], b['method'])].append(b)
    matched_cases = []
    unmatched_cases = []
    for classname, name in sorted(case_keys):
        values = methods_by_case[(classname, name)]
        if len(values) == 1:
            matched_cases.append(dict(classname=classname, name=name, declaration=values[0], executionMeaning='EXISTING_CURRENT2064_REFERENCE_NOT_NEW_EXECUTION'))
        else:
            unmatched_cases.append(dict(classname=classname, name=name, exactOrdinaryCandidates=len(values), inference='NONE_NO_NAME_NORMALIZATION'))
    not_matched = [b for b in bound if (b['className'], b['method']) not in case_keys]
    require(all(data.sha((data.ROOT / p).read_bytes()) == h for p, h in hashes.items()) and test_classes(n) == physical, 'all original inputs unchanged')
    verify(invocation)
    OUT.mkdir()
    outputs = {'ordinary-source-declarations.json': declarations, 'compiled-annotated-methods.json': annotated, 'exact-ordinary-bindings.json': bound, 'ambiguous-bindings.json': ambiguous, 'existing-case-bindings.json': matched_cases, 'unmatched-existing-cases.json': unmatched_cases, 'ordinary-without-current-case-reference.json': not_matched, 'test-source-hashes.json': hashes}
    for filename, value in outputs.items():
        data.write(OUT / filename, value)
    data.write(OUT / 'manifest.json', dict(actualExit=0, source=normal.SOURCE, invocation=invocation, normalManifestSha256=normal.NORMAL[1], registryManifestSha256=REGISTRY[1], readerRuns=runs,
        sourceFiles=856, physicalTestClasses=1978, sourceOrdinaryDeclarations=len(declarations), compiledOrdinaryDeclarations=len(ordinary), otherAnnotationDeclarations=len(other), exactOrdinaryBindings=len(bound), ambiguousBindings=len(ambiguous),
        existingCaseCount=2064, existingCasesExactlyMatched=len(matched_cases), existingCasesUnmatched=len(unmatched_cases), ordinaryWithoutCurrentCaseReference=len(not_matched),
        files={filename: data.sha((OUT / filename).read_bytes()) for filename in outputs},
        invocationCountExpanded=False, junitDiscoveryExecuted=False, targetCompiled=False, targetClassesDefinedInitializedOrInvoked=False,
        otherKindsIgnoredForCompletion=False, newProductExecutions=0, newAccepted=0, formalUpdated=False, effortPercent=None,
        phaseCompletionPercent=None, coverage=None, wholeG13Accepted=False, whole451Accepted=False, externalActions=0))
    print(data.sha((OUT / 'manifest.json').read_bytes()))
    print(json.dumps(dict(actualExit=0, sourceOrdinary=len(declarations), binaryOrdinary=len(ordinary), bound=len(bound), ambiguity=len(ambiguous), otherAnnotations=len(other), matchedExistingCases=len(matched_cases), unmatchedExistingCases=len(unmatched_cases), noCurrentCaseReference=len(not_matched))))

if __name__ == '__main__':
    main()
