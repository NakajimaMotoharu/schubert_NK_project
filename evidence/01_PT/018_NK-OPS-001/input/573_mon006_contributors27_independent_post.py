"""Independent, metadata-only verification; no product module imports or execution."""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import datetime
import hashlib
import json
import subprocess

R = Path(__file__).resolve().parents[4]
B = R / 'evidence/01_PT/018_NK-OPS-001'
P = B / 'evidence/PG23904-mon006-contributor27-trace-v1'
O = B / 'evidence/PG23906-mon006-contributor27-independent-v1'
load = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
EXPECTED = {
    'JVM_GC_SYSTEM': 'ApiGcMetricRegistration ApiJvmMetrics ApiSystemMetrics BatchGcMetricRegistration BatchJvmMetrics BatchSystemMetrics WebGcMetricRegistration WebJvmMetrics WebSystemMetrics'.split(),
    'DB_POOL': 'ApiDbPoolMetricBinding DbPoolMetricCollector DbPoolMetricObservation DbPoolMetricRecorder WebDbPoolMetricBinding WebDbPoolMetricCollector WebDbPoolMetricObservation WebDbPoolMetricRecorder TimedDbPoolMonitor'.split(),
    'HEAP': 'HealthUsageRatio JvmHeapHealthMonitor JvmHeapHealthObservation TimedJvmHeapMonitor'.split(),
    'DISK': 'FilesystemHealthMonitor FilesystemHealthObservation'.split(),
    'HTTP_LATENCY': 'HttpMetricRecorder HttpMetricValve WebDurationMetricExporter'.split(),
}
names = {n: cat for cat, values in EXPECTED.items() for n in values}


def validate(rows, remaining, prior, artifacts, requirement):
    assert len(rows) == 27 and len({v['path'] for v in rows}) == 27
    assert {Path(v['path']).stem for v in rows} == set(names)
    assert Counter(v['contributionKind'] for v in rows) == {k: len(v) for k, v in EXPECTED.items()}
    for v in rows:
        n = v['path']
        assert v['contributionKind'] == names[Path(n).stem]
        assert v['requirement'] == 'MON-006' and v['canonicalRequirement'] == requirement
        assert v['sourceSha256'] == prior[n]['sourceSha256'] == artifacts[n]['sha256']
        assert v['declaredResponsibility'] == prior[n]['classDeclaration']
        assert prior[n]['status'] == 'DOCUMENT_OR_OWNER_CONTEXT_ONLY_PRECISE_RD_MAPPING_PENDING'
        assert prior[n]['parsed']['ids'] == [] and v['originalDeclaredReferenceIds'] == []
        assert v['owner'] == artifacts[n]['owner'] and v['costOwner'] == artifacts[n]['costOwner']
        assert v['status'] == 'DERIVED_SUPPORTING_COMPONENT_REFERENCE_ONLY'
        assert v['sourceEvidenceKind'] == 'DERIVED_SUPPORTING_COMPONENT_LINK_NOT_EXPLICIT_CODE_REQUIREMENT_ANNOTATION'
        for flag in ('implementationAccepted', 'actualMeasurementProven', 'ptAccepted',
                     'explicitCodeRequirementAnnotation', 'wholeG13Accepted', 'whole451Accepted'):
            assert v[flag] is False
        assert isinstance(v['reason'], str) and len(v['reason']) > 50
    pending = {n for n, v in prior.items() if v['status'] == 'DOCUMENT_OR_OWNER_CONTEXT_ONLY_PRECISE_RD_MAPPING_PENDING'}
    assert len(pending) == 100 and len(remaining) == len(set(remaining)) == 73
    assert set(remaining) == pending - {v['path'] for v in rows}


def main():
    assert not O.exists()
    manifest = load(P / 'manifest.json')
    assert manifest['actualExit'] == 0 and manifest['supportingSourceReferences'] == 27
    assert manifest['productTestsExecuted'] == 0 and manifest['actualMeasurementProven'] is False
    for name, digest in manifest['files'].items():
        assert sha(P / name) == digest
    config = load(R / manifest['config']['path'])
    assert sha(R / manifest['config']['path']) == manifest['config']['sha256']
    prior_ref = config['priorDeclaredRows']
    assert sha(R / prior_ref['path']) == prior_ref['sha256']
    prior = {v['path']: v for v in load(R / prior_ref['path'])}
    wb_path = R / manifest['wbsAfter']['path']
    assert sha(wb_path) == manifest['wbsAfter']['sha256']
    before = json.loads(subprocess.check_output(['git', 'show', 'HEAD:' + manifest['wbsBefore']['path']], cwd=R))
    before_bytes = subprocess.check_output(['git', 'show', 'HEAD:' + manifest['wbsBefore']['path']], cwd=R)
    assert hashlib.sha256(before_bytes).hexdigest() == manifest['wbsBefore']['sha256']
    wb = load(wb_path)
    inverse = deepcopy(wb)
    overlay = inverse.pop('currentMonitoringMon006Contributor27Trace20261108')
    assert inverse == before
    assert overlay['sourcePrograms'] == 27 and overlay['remainingPreciseMapping'] == 73
    assert overlay['original12Declared84LinksUnchanged'] is True
    assert overlay['implementedRequirementsInferred'] is False and overlay['effortRate'] is None
    assert overlay['newProductTests'] == overlay['newAcceptance'] == 0
    requirement = next(v for v in wb['requirements'] if v['id'] == 'MON-006')
    for term in ('JVM', 'heap', 'GC', 'DB connection pool', 'ディスク残量', 'HTTP応答時間'):
        assert term in requirement['requirement']
    for ref in config['authority']:
        p = R / ref['path']
        assert sha(p) == ref['sha256']
        assert p.read_bytes() == subprocess.check_output(['git', 'show', 'origin/main:' + ref['path']], cwd=R)
    rows = load(P / 'contributor-links.json')
    remaining = load(P / 'remaining-precise-mapping.json')
    artifacts = {v['path']: v for v in wb['artifacts']}
    validate(rows, remaining, prior, artifacts, requirement)
    negatives = []
    for field, value in [('requirement', 'MON-005'), ('contributionKind', 'DISK'),
                         ('implementationAccepted', True), ('actualMeasurementProven', True),
                         ('ptAccepted', True), ('explicitCodeRequirementAnnotation', True),
                         ('sourceSha256', '0' * 64), ('whole451Accepted', True)]:
        mutated = deepcopy(rows)
        mutated[0][field] = value
        try:
            validate(mutated, remaining, prior, artifacts, requirement)
        except AssertionError:
            negatives.append(field)
        else:
            raise AssertionError('accepted mutated field: ' + field)
    for label, mutated, rem in [('missing', rows[:-1], remaining), ('duplicate', rows[:-1] + [rows[0]], remaining),
                                 ('missing-pending', rows, remaining[:-1])]:
        try:
            validate(mutated, rem, prior, artifacts, requirement)
        except AssertionError:
            negatives.append(label)
        else:
            raise AssertionError('accepted mutation: ' + label)
    O.mkdir()
    out = dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(),
               source=manifest['source'], producerManifest=dict(path=str((P / 'manifest.json').relative_to(R)), sha256=sha(P / 'manifest.json')),
               supportingSourceReferences=27, requirement='MON-006', categoryCounts={k: len(v) for k, v in EXPECTED.items()},
               preciseMappingPendingBefore=100, preciseMappingPendingAfter=73, original12Declared84LinksUnchanged=True,
               unchangedWbsExceptNewOverlay=True, authorityMatchesOriginMain=True, negativeMetadataChecks=negatives,
               actualMeasurementProven=False, productTestsExecuted=0, compilerOrJvmExecuted=False,
               actualBackendActions=0, sourceMutation=False, newAcceptance=0, formalUpdated=False,
               effortRate=None, wholeG13Accepted=False, whole451Accepted=False,
               tool=dict(path=str(Path(__file__).relative_to(R)), sha256=sha(Path(__file__))))
    (O / 'manifest.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(actualExit=0, manifestSha256=sha(O / 'manifest.json'), negativeMetadataChecks=len(negatives))))


if __name__ == '__main__':
    main()
