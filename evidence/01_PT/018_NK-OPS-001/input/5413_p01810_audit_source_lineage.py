"""Distinguish exact audit-vector lineage from changed and held inputs."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess


OPS = Path('evidence/01_PT/018_NK-OPS-001/evidence')
PLAN = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def read(ref):
    path = Path(ref['path'])
    assert pin(path) == ref
    return json.loads(path.read_bytes())


def git(source, path):
    return subprocess.check_output(['git', 'show', f'{source}:{path}'])


def verify_inputs(inputs, source_hint, core, code):
    comparable = {}
    for path, value in inputs.items():
        if not path.startswith('src/') and path != 'pom.xml':
            continue
        digest = value['sha256'] if isinstance(value, dict) else value
        source = code if '/src/test/' in path else core
        assert sha(git(source_hint, path)) == digest
        comparable[path] = sha(git(source, path)) == digest
    return comparable


def main():
    start = json.loads(next(PLAN.glob('1045_P01810*')).read_bytes())['values']
    refs = start['oracleReferences']
    previous, catalog, security, media, trace, parser = map(read, refs)
    core, source = start['productionCoreMain'], start['source']
    assert previous['productionCoreMain'] == core
    entries = {row['boundaryId']: row for row in catalog}
    assert len(entries) == len(catalog) == 8
    assert security['actualExit'] == security['stages']['unit']['actualExit'] == 0
    assert len(security['cases']) == 6 and all(not row['nonPass'] for row in security['cases'])
    bounded_security = verify_inputs(security['begin']['inputHashes'], security['source'], core, source)
    bounded_media = verify_inputs(media['inputHashes'], media['source'], core, source)
    assert len(bounded_security) == 9 and all(bounded_security.values())
    assert len(bounded_media) == 20 and all(bounded_media.values())
    rules = {path: value for path, value in media['inputHashes'].items() if path.startswith('tools/')}
    assert set(rules) == {'tools/quality/static/checkstyle.xml', 'tools/quality/static/pmd.xml'}
    for path, value in rules.items():
        digest = value['sha256'] if isinstance(value, dict) else value
        assert sha(git(media['source'], path)) == sha(git(source, path)) == digest
    assert media['actualExit'] == 0 and media['tests'] == media['productTestsExecuted'] == 9
    assert media['completeSourceComponentFour100'] is True

    route = entries['WEB-ROUTE-METADATA']
    old_hashes = trace['inputHashes']
    assert all(old_hashes[row['path']] == row['sha256'] == sha(git(
        source if '/src/test/' in row['path'] else core, row['path']))
               for row in (route['main'], route['testSource']))
    differing_route_dependencies = []
    old_source = trace['source']
    for path in old_hashes:
        if not path.startswith('src/') and path != 'pom.xml':
            continue
        test_only = '/src/test/' in path
        target = source if test_only else core
        origin = old_source if test_only else trace['productionCoreMain']
        delta = subprocess.check_output(['git', 'diff', '--name-only', origin, target, '--', path])
        if delta:
            differing_route_dependencies.append(path)
    assert differing_route_dependencies

    newer_parser = read(parser['starts'][1])
    assert parser['actualExit'] == newer_parser['actualExit'] == 0
    assert parser['productionCore'] == newer_parser['productionCore'] and parser['productTests'] == 1
    admitted_parser = entries['API-DETAILS-ALLOWLIST']['main']['path']
    assert git(parser['productionCore'], admitted_parser) == git(core, admitted_parser)
    assert newer_parser['testSourceSha256'] == sha(git(source, entries['API-DETAILS-ALLOWLIST']['testSource']['path']))
    rows = [
        dict(boundaryId='WEB-SECURITY-LOCAL', status='EXACT_SOURCE_INPUT_LINEAGE',
             checkedSourceInputs=len(bounded_security), retainedCases=6, historicalReceipt=refs[2],
             remaining='Actual sink, runtime scope and 451 are separate.'),
        dict(boundaryId='WEB-MEDIA-LOCAL', status='EXACT_SOURCE_INPUT_LINEAGE',
             checkedSourceInputs=len(bounded_media), checkedRules=len(rules), retainedCases=9, historicalReceipt=refs[3],
             remaining='Actual sink and HTTP environment remain distinct.'),
        dict(boundaryId='WEB-ROUTE-METADATA', status='REFERENCE_WITH_DIFF', historicalReceipt=refs[4],
             targetMainAndOriginalTestExact=True, dependencyDelta=differing_route_dependencies),
        dict(boundaryId='API-DETAILS-ALLOWLIST', status='ONE_SCALAR_METHOD_WITH_MAIN_TEST_LINEAGE',
             retainedCases=1, historicalReceipt=refs[5],
             remaining='Current whole parser suite and actual producer/consumer independent results.'),
    ]
    for name in ('WEB-REQUEST-LOCAL', 'API-LOG-INGEST', 'WEB-FATAL-BOUNDARY', 'BATCH-VALUE-DIAGNOSTIC'):
        rows.append(dict(boundaryId=name, status='DEPENDENCY_REMAINS', remaining=entries[name]['unresolved']))
    assert {row['boundaryId'] for row in rows} == set(entries)
    out = OPS/start['run']
    out.mkdir()
    proof = out/'manifest.json'
    with proof.open('x') as stream:
        json.dump(dict(actualExit=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                       productionCore=core, source=source, originalCatalog=refs[1],
                       boundariesReviewed=8, exactComponentLineage=2, exactScalarMethods=1,
                       rows=rows, newProductTestExecutions=0, oldCoverageCombined=False,
                       oldReceiptRelabelled=False, heldClassfilesRead=0, actualSinksStarted=0,
                       whole451=False, formalDelta=0), stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(pin(proof))


if __name__ == '__main__':
    main()
