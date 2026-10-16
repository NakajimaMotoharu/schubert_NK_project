"""Publish only hashes/qualifications, never retained data or raw journal/credential."""
import hashlib
import json
from pg4420_shared_manager_full import W, ROOT, SOURCE


def main():
    names = {
        'signed-candidate.json': W / 'pg4432-candidate-build-v1.safe.json',
        'fresh-current.json': W / 'pg4434-current-candidate-admission-read-v1/manifest.safe.json',
        'canonical-original-failure.json': W / 'pg4438-failed-current-canonical-view-v1/manifest.safe.json',
        'canonical-diagnosis.json': W / 'pg4440-failed-full-image-diagnosis-v1/manifest.safe.json',
        'canonical-qualified.json': W / 'pg4442-failed-current-view-qualified-v1/manifest.safe.json'}
    out = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4436-signed-failed-baseline-v1'; out.mkdir()
    hashes = {}
    for name, path in names.items():
        value = json.loads(path.read_bytes())
        expected = 1 if name == 'canonical-original-failure.json' else 0
        if value['actualExit'] != expected: raise ValueError('preserve genuine original result')
        encoded = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()
        (out / name).write_bytes(encoded); hashes[name] = hashlib.sha256(encoded).hexdigest()
    value = {'candidateSource': SOURCE, 'release': 'PG4432', 'candidateBom': '93807abdd4db24ad300b93d95d844ea21e64487dc5cf24b815c15db34305d3de',
        'deployedSource': '7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e', 'candidateDeployed': False,
        'whole': {'tests':3721,'suites':545,'physicalMain':1644}, 'signatureVerified':True, 'signedArtifacts':187,
        'freshCurrentAll24AndOriginalBackupKeysNative58Startup37':True, 'newScopesNormal':True,
        'oldParentNormal':False, 'oldUnknownNormalized':False, 'dataOnlyCurrentViewAccepted':True,
        'normalReceiptOrRuntimeAuthorityIssued':False, 'nativeCandidateCredit':False, 'formalAccepted':False,
        'formalTests':1964,'formalScopes':53,'effortCompletion':None,'QA051final':'HELD','BUG':[1358], 'YKT':[1124],
        'rawRetainedPrivately':True,'rawOrCredentialsExported':False,'vmActions':0,'files':hashes}
    path = out / 'manifest.json'; path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'actualExit':0,'manifestSha256':hashlib.sha256(path.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
