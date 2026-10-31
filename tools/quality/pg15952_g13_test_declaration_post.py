"""Independent source/class annotation binding and exact existing-case domain split."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg15950_g13_test_declaration_inventory as original

PIN = '0173083ac6c1ed92d23a3fad673afc7d545186d718353366398c1ecd28c6c139'
OUT = data.BASE / 'PG15952-g13-current-test-declaration-post-v1'

def require(ok, message):
    if not ok:
        raise ValueError(message)

def assess(p, declarations, annotated, bound, ambiguous, matched, unmatched, pending, expected, cases):
    require(p['actualExit'] == 0 and p['source'] == original.normal.SOURCE and p['normalManifestSha256'] == original.normal.NORMAL[1] and p['registryManifestSha256'] == original.REGISTRY[1], 'fixed exact current domains')
    require((p['sourceFiles'], p['physicalTestClasses'], p['sourceOrdinaryDeclarations'], p['compiledOrdinaryDeclarations'], p['otherAnnotationDeclarations'], p['exactOrdinaryBindings'], p['ambiguousBindings'], p['existingCaseCount'], p['existingCasesExactlyMatched'], p['existingCasesUnmatched'], p['ordinaryWithoutCurrentCaseReference']) == (856, 1978, 5786, 5786, 1, 5786, 0, 2064, 2058, 6, 3728), 'all declaration/case domains')
    require(len(declarations) == 5786 and len(annotated) == 5787 and bound == expected and not ambiguous, 'all exact ordinary AST/binary bindings')
    index = collections.defaultdict(list)
    for row in bound:
        index[(row['className'], row['method'])].append(row)
    exact = []
    missing = []
    for classname, name in sorted(cases):
        values = index[(classname, name)]
        if len(values) == 1:
            exact.append(dict(classname=classname, name=name, declaration=values[0], executionMeaning='EXISTING_CURRENT2064_REFERENCE_NOT_NEW_EXECUTION'))
        else:
            missing.append(dict(classname=classname, name=name, exactOrdinaryCandidates=len(values), inference='NONE_NO_NAME_NORMALIZATION'))
    require(matched == exact and unmatched == missing and pending == [b for b in bound if (b['className'], b['method']) not in cases], 'all existing case references and ordinary pending')
    for field in ('invocationCountExpanded', 'junitDiscoveryExecuted', 'targetCompiled', 'targetClassesDefinedInitializedOrInvoked', 'otherKindsIgnoredForCompletion', 'formalUpdated', 'wholeG13Accepted', 'whole451Accepted'):
        require(p[field] is False, 'metadata not execution/completion: ' + field)
    for field in ('newProductExecutions', 'newAccepted', 'externalActions'):
        require(type(p[field]) is int and p[field] == 0, 'no new Product result')
    require(p['phaseCompletionPercent'] is p['coverage'] is p['effortPercent'] is None, 'no invented completion/coverage/effort')

def main():
    invocation = capture(__file__)
    require(not OUT.exists(), 'new-only')
    p = data.read_checked(original.OUT / 'manifest.json', PIN)
    values = {name: data.read_checked(original.OUT / name, digest) for name, digest in p['files'].items()}
    declarations, annotated, bound, ambiguous, matched, unmatched, pending, hashes = [values[name] for name in ('ordinary-source-declarations.json', 'compiled-annotated-methods.json', 'exact-ordinary-bindings.json', 'ambiguous-bindings.json', 'existing-case-bindings.json', 'unmatched-existing-cases.json', 'ordinary-without-current-case-reference.json', 'test-source-hashes.json')]
    n = data.read_checked(data.BASE / original.normal.NORMAL[0] / 'manifest.json', original.normal.NORMAL[1])
    require(hashes == {path: h for path, h in n['begin']['inputHashes'].items() if path.startswith('src/') and '/src/test/java/' in path and path.endswith('.java')} and len(hashes) == 856 and all(data.sha((data.ROOT / path).read_bytes()) == digest for path, digest in hashes.items()), 'full current Test source bytes')
    source = {}
    for row in declarations:
        key = (row['className'], row['method'], row['parameterCount'])
        require(key not in source and row['sourceSha256'] == hashes[row['path']] and 0 < row['startLine'] <= row['endLine'], 'unique bounded current AST')
        source[key] = row
    expected = []
    for a in sorted((r for r in annotated if r['annotationKind'] == 'org.junit.jupiter.api.Test'), key=lambda r: (r['className'], r['method'], r['parameterCount'])):
        row = source[(a['className'], a['method'], a['parameterCount'])]
        require(a['path'] == row['path'] and a['sourceSha256'] == row['sourceSha256'], 'independent class/source binding')
        expected.append(dict(**a, sourceStartLine=row['startLine'], sourceEndLine=row['endLine'], binding='SOURCE_AST_AND_CLASS_ANNOTATION_ONLY_NOT_EXECUTED'))
    # Re-read the two separately generated, hash-bound terminal outputs, without invoking either reader again.
    for label, run in zip(('parse-test-source-declarations', 'read-test-annotations'), p['readerRuns']):
        require(run['actualExit'] == 0 and not run['timedOut'], 'genuine reader terminal')
        require(data.sha((original.SLOT / (label + '.stdout')).read_bytes()) == run['stdoutSha256'] and data.sha((original.SLOT / (label + '.stderr')).read_bytes()) == run['stderrSha256'], 'exact reader output hashes')
    ast_lines = (original.SLOT / 'parse-test-source-declarations.stdout').read_text().splitlines()
    require(ast_lines[0] == 'SELFTEST\t7' and len(ast_lines) == 5787, 'whole AST metadata output')
    independent_ast = []
    for line in ast_lines[1:]:
        path, owner, name, parameters, start, end = line.split('\t')
        independent_ast.append(dict(path=path, sourceSha256=hashes[path], className=owner, method=name, parameterCount=int(parameters), startLine=int(start), endLine=int(end)))
    require(independent_ast == declarations, 'all original AST declaration records')
    binary_lines = (original.SLOT / 'read-test-annotations.stdout').read_text().splitlines()
    require(binary_lines[0] == 'SELFTEST\t6', 'binary annotation metadata output')
    class_map = {}
    independent_annotations = []
    physical = original.test_classes(n)
    for line in binary_lines[1:]:
        f = line.split('\t')
        if f[0] == 'CLASS':
            _, role, name, filename, digest = f
            require((role, name) not in class_map and physical[(role, name + '.class')] == digest, 'all current physical Test byte identities')
            path = 'src/schubert-nk-' + role + '/src/test/java/' + name.rsplit('/', 1)[0] + '/' + filename
            class_map[(role, name)] = (path, digest)
        else:
            _, role, name, method, descriptor, parameters, annotation = f
            path, digest = class_map[(role, name)]
            independent_annotations.append(dict(module=role, className=name.replace('/', '.'), method=method, descriptor=descriptor, parameterCount=int(parameters), annotationKind=annotation, path=path, sourceSha256=hashes[path], classSha256=digest))
    require(len(class_map) == 1978 and annotated == independent_annotations, 'all independent binary annotation rows')
    registry = data.read_checked(data.BASE / original.REGISTRY[0] / 'manifest.json', original.REGISTRY[1])
    cases = {(r['classname'], r['name']) for r in registry['cases']}
    assess(p, declarations, annotated, bound, ambiguous, matched, unmatched, pending, expected, cases)
    # Six valid technical cases belong to an explicit quality fixture, not the normal856 Test source domain.
    fixture_post = data.read_checked(data.BASE / 'PG14871-protocol-carrier-boundary-six-post-v2/manifest.json', '87d29dc4e02b03e422270d4f9ebfc5a8b68456804f837c1c338ba1d8b8986696')
    fixture_raw = data.read_checked(data.BASE / 'PG14868-protocol-carrier-boundary-six-pt-v1/manifest.json', fixture_post['originalManifestSha256'])
    fixture_path = data.ROOT / 'tools/quality/architecture/ProtocolCarrierBoundaryTest.java'
    require(fixture_post['actualExit'] == fixture_raw['actualExit'] == 0 and fixture_post['source'] == p['source'] and fixture_post['tests'] == 6, 'existing fixture qualification')
    require(data.sha(fixture_path.read_bytes()) == fixture_raw['begin']['testSourceHashes'][str(fixture_path)] == 'bd1da8b0168836610a5d7a28ec4b3af127dfca86d15c0a7bbabb98282f841003', 'fixed existing public fixture source, not normalTest')
    fixture_cases = {(r['classname'], r['name']) for r in fixture_post['cases']}
    require(fixture_cases == {(r['classname'], r['name']) for r in unmatched} and len(fixture_cases) == 6, 'all six out-of-domain cases, not inferred repeated/inherited cases')
    negatives = []
    for field, value in [('source', '0'*40), ('sourceOrdinaryDeclarations', 5622), ('existingCasesExactlyMatched', 2064), ('existingCasesUnmatched', 0), ('otherAnnotationDeclarations', 0), ('ordinaryWithoutCurrentCaseReference', 0), ('invocationCountExpanded', True), ('junitDiscoveryExecuted', True), ('targetCompiled', True), ('targetClassesDefinedInitializedOrInvoked', True), ('otherKindsIgnoredForCompletion', True), ('newProductExecutions', 2064), ('newAccepted', True), ('phaseCompletionPercent', 100), ('coverage', 100), ('effortPercent', 100)]:
        bad = copy.deepcopy(p)
        bad[field] = value
        try:
            assess(bad, declarations, annotated, bound, ambiguous, matched, unmatched, pending, expected, cases)
        except ValueError:
            negatives.append(field)
        else:
            raise ValueError('unrejected denominator promotion: ' + field)
    for label, mutate in [('drop-binding', lambda b, m, u, q: b.pop()), ('duplicate', lambda b, m, u, q: b.__setitem__(0, b[1])), ('descriptor', lambda b, m, u, q: b[0].update(descriptor='(I)V')), ('source', lambda b, m, u, q: b[0].update(sourceSha256='0'*64)), ('false-case', lambda b, m, u, q: m[0].update(name='invented')), ('drop-fixture-cases', lambda b, m, u, q: u.clear()), ('drop-pending', lambda b, m, u, q: q.pop())]:
        bb, mm, uu, qq = map(copy.deepcopy, (bound, matched, unmatched, pending))
        mutate(bb, mm, uu, qq)
        try:
            assess(p, declarations, annotated, bb, ambiguous, mm, uu, qq, expected, cases)
        except ValueError:
            negatives.append(label)
        else:
            raise ValueError('unrejected binding change: ' + label)
    verify(p['invocation'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'fixture-case-domain.json', dict(existingFixtureSource=str(fixture_path.relative_to(data.ROOT)), sourceSha256='bd1da8b0168836610a5d7a28ec4b3af127dfca86d15c0a7bbabb98282f841003', postManifestSha256='87d29dc4e02b03e422270d4f9ebfc5a8b68456804f837c1c338ba1d8b8986696', cases=unmatched, normalOrdinaryDeclarationCases=False, originalTechnicalCasesRemainValid=True, newExecution=False))
    data.write(OUT / 'manifest.json', dict(actualExit=0, invocation=invocation, source=p['source'], parentManifestSha256=PIN,
        independentNegativeVectors=len(negatives), negativeLabels=negatives, ordinaryDeclarations=5786,
        existingOrdinaryCaseReferences=2058, ordinaryWithoutCurrentCaseReference=3728, existingExternalFixtureCases=6,
        nonordinaryAnnotationDeclarations=1, nonordinaryInvocationsNotQualified=True, phaseCompletionPercent=None, coverage=None, effortPercent=None,
        fixtureCaseDomainSha256=data.sha((OUT / 'fixture-case-domain.json').read_bytes()), newProductExecutions=0, newAccepted=0, formalUpdated=False, wholeG13Accepted=False, whole451Accepted=False, externalActions=0))
    print(data.sha((OUT / 'manifest.json').read_bytes()))
    print(json.dumps(dict(actualExit=0, independentNegativeVectors=len(negatives), ordinary=5786, ordinaryReferences=2058, separateFixtureCases=6)))

if __name__ == '__main__':
    main()
