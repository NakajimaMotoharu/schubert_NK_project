"""Publish only explicit nonsecret diagnostic fields; all raw DB/FD/credentials stay private."""
import datetime
import hashlib
import json
import os
from pathlib import Path
from pg1446_current_cold_stage import W

ROOT = Path(__file__).resolve().parents[2]
SOURCE = '7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e'
SLOTS = ['pg4050-unit-read-profile-v1', 'pg4052-failed-current-capture-v1',
         'pg4054-file-primitive-profile-v1', 'pg4056-file-primitive-profile-v1',
         'pg4058-original-read-profile-v1-compile', 'pg4058-original-read-profile-v1-run',
         'pg4060-original-read-profile-v1-compile', 'pg4060-original-read-profile-v1-run',
         'pg4064-original-read-profile-v1-run']
KEYS = {'actualExit', 'source', 'BOM', 'observedUTC', 'startUTC', 'endUTC', 'profile',
        'sourceSha256', 'javaSha256', 'annotationSha256', 'classHashes', 'parentFailed143',
        'done10NotParentSuccess', 'whole187SignatureVerified', 'sameActorsTwice', 'actorCount',
        'all24ReadTwice', 'all24EqualTwice', 'dbPeerCounts', 'advisoryCounts', 'flockCounts',
        'durableEqualTwice', 'nativeStableDuringCapture', 'nativeExecCount', 'metadataRefsClosed',
        'signalStartStopReloadDbWrites', 'authorityIssued', 'formalAccepted', 'privateSha256',
        'acceptanceOrCoverageClaim', 'sameOrdinaryApiGenerationBeforeAfter', 'rootStartStopDbActions',
        'newGuestEvidenceOnly', 'businessOrProfileIssued', 'newMARDDBTenRefNormalClose',
        'all24OriginalBackupNativeUnitConfigUnchanged', 'ordinaryPoolsFreshSocketMatched',
        'parent143StillFailed', 'beforeSha256', 'afterSha256', 'authorityOrCoverageClaim', 'compileSha256'}


def main():
    out = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4066-failed-root-readonly-diagnostics-v1'
    os.umask(0o022); out.mkdir()
    files = {}
    for slot in SLOTS:
        p = W / slot / 'manifest.safe.json'; raw = p.read_bytes(); value = json.loads(raw)
        if value['source'] != SOURCE: raise ValueError('same diagnostic source required')
        result = value.get('result', {})
        public = {k: value[k] for k in ['actualExit', 'source', 'payloadSha256', 'action', 'formalAccepted'] if k in value}
        public.update(originalManifestSha256=hashlib.sha256(raw).hexdigest(),
                      manifestWriteTimeUTC=datetime.datetime.fromtimestamp(p.stat().st_mtime, datetime.timezone.utc).isoformat(),
                      manifestTimeIsNotExecutionStart=True, result={k: v for k, v in result.items() if k in KEYS})
        target = out / (slot + '.json'); target.write_text(json.dumps(public, ensure_ascii=False, indent=2) + '\n')
        files[target.name] = hashlib.sha256(target.read_bytes()).hexdigest()
    final = json.loads((W / SLOTS[-1] / 'manifest.safe.json').read_bytes())
    manifest = {'source': SOURCE, 'createdUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'files': files, 'originalProfileActualExit': final['actualExit'],
                'BUG1332Closed': False, 'F03Accepted': False, 'formalTests': 1964,
                'formalScopes': 53, 'effortCompletionRate': None, 'QA051Final': 'HELD',
                'productionPtAdded': 0, 'rootOrBusinessReplayed': False, 'privateContentsExported': False}
    target = out / 'manifest.json'; target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'manifestSha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                      'originalProfileActualExit': final['actualExit'], 'exportedManifests': len(files)}))


if __name__ == '__main__': main()
