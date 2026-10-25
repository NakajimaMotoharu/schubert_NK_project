"""Reusable bounded static row/source/spec binder, explicitly not an executing PT gate."""
from collections import Counter
import datetime as dt
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify


def run(library, output, spec, review, oracles, class_counts, main_paths, extra):
    invocation = capture(library)
    assert not output.exists()
    spec_path, spec_sha = spec
    review_path, review_sha = review
    assert data.sha(spec_path.read_bytes()) == spec_sha and data.sha(review_path.read_bytes()) == review_sha
    normal = data.read_checked(data.BASE / data.PINS['normal'][0] / 'manifest.json', data.PINS['normal'][1])
    mm = data.read_checked(data.BASE / 'PG9592-current-test-method-post-v1/manifest.json',
        'd73ffe203a58ca9fab7f19f0b4baa7b2588fb25ad7e13c75c0c6411f5a719a18')
    methods = data.read_checked(data.BASE / 'PG9592-current-test-method-post-v1/method-declaration-bindings.json', mm['bindingsSha256'])
    texts = {}
    for prefix, (path, digest) in oracles.items():
        raw = (data.ROOT / path).read_bytes()
        assert data.sha(raw) == digest
        texts[prefix] = raw.decode().splitlines()
    records = []
    hashes = {}
    for number, line in enumerate(review_path.read_text().splitlines(), 1):
        if not any(line.startswith('| ' + kind + ' |') for kind in class_counts):
            continue
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        assert len(cells) == 5
        kind, method_name, ids, basis, limits = cells
        found = [m for m in methods if m['className'].rpartition('.')[2] == kind and m['method'] == method_name]
        assert len(found) == 1 and found[0]['compiledDescriptor'] == '()V'
        method = found[0]
        identifiers = ids.split(', ')
        assert len(identifiers) == len(set(identifiers))
        refs = []
        for identifier in identifiers:
            prefixes = [prefix for prefix in oracles if identifier.startswith(prefix)]
            assert len(prefixes) == 1
            prefix = prefixes[0]
            hits = [(i, row) for i, row in enumerate(texts[prefix], 1)
                if row.startswith('| ' + identifier + ' |') or row.startswith(identifier + '（') or row.startswith(identifier + '：')]
            assert len(hits) == 1
            at, row = hits[0]
            path, digest = oracles[prefix]
            refs.append(dict(testId=identifier, path=path, sha256=digest, line=at, rowSha256=data.sha(row.encode())))
        hashes[method['path']] = method['sourceSha256']
        records.append(dict(method=method, reviewLine=number, reviewRowSha256=data.sha(line.encode()),
            oracleReferences=refs, independentBasis=basis, limits=limits, productExecuted=False, oldDynamicTransferred=False))
    assert len(records) == len({row['method']['methodDeclarationKey'] for row in records}) == sum(class_counts.values())
    assert Counter(row['method']['className'].rpartition('.')[2] for row in records) == Counter(class_counts)
    assert len(main_paths) == len(set(main_paths))
    for path in main_paths:
        assert '/src/main/java/' in path and path.endswith('.java')
        hashes[path] = normal['begin']['inputHashes'][path]
    for path, digest in hashes.items():
        assert normal['begin']['inputHashes'][path] == data.sha((data.ROOT / path).read_bytes()) == data.sha((data.NORMAL / path).read_bytes()) == digest
    additional = extra()
    assert subprocess.check_output(['git', 'diff', '--name-only', data.SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw'], cwd=data.ROOT) == b''
    verify(invocation)
    output.mkdir()
    data.write(output / 'method-oracle-review.json', records)
    value = dict(actualExit=0, source=data.SOURCE, timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
        invocation=invocation, specPath=str(spec_path.relative_to(data.ROOT)), specSha256=spec_sha,
        reviewPath=str(review_path.relative_to(data.ROOT)), reviewSha256=review_sha, sourceHashes=hashes,
        methodOracleReviewSha256=data.sha((output / 'method-oracle-review.json').read_bytes()),
        methods=len(records), existingFamilies=len({ref['testId'] for row in records for ref in row['oracleReferences']}),
        methodFamilyRelations=sum(len(row['oracleReferences']) for row in records), reviewedMainSourceFiles=len(main_paths),
        parentSemanticReviewOnly=True, productTestsExecuted=0, newTestIds=0, newMain=0, coverage=None,
        newAccepted=0, formalUpdated=False, effortPercent=None, wholeG13Accepted=False, whole451Accepted=False,
        additionalStaticEvidence=additional)
    data.write(output / 'manifest.json', value)
    return value, data.sha((output / 'manifest.json').read_bytes())
