"""Publish explicit nonsecret measurement/results only; no private command/owner/DB export."""
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
W = ROOT.parent / 'pgpt-runs/PG379'
SLOTS = ['pg4392-proc-metadata-cost-v1', 'pg4394-root-read-cost-v1',
         'pg4396-binding-regex-cost-v1', 'pg4400-exact-native-adapter-cost-v1',
         'pg4402-child-unit-read-cost-v1', 'pg4404-shared-manager-candidate-cost-v1',
         'pg4406-verified-shared-manager-cost-v1', 'pg4408-canonical-shared-manager-cost-v1']


def main():
    out = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4410-root-cost-components-v1'
    out.mkdir(); files = {}
    for name in SLOTS:
        path = W / name / 'manifest.safe.json'; raw = path.read_bytes(); value = json.loads(raw)
        if value['source'] != '7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e': raise ValueError('fixed deployed measurement source')
        expected = 1 if name.startswith('pg4406-') else 0
        if value['actualExit'] != expected: raise ValueError('preserve exact actual result, no success inference')
        result = value.get('result', {})
        if result and result.get('operationsIssued') != 0: raise ValueError('measurement-only operation0')
        public = {'actualExit': value['actualExit'], 'source': value['source'],
                  'payloadSha256': value['payloadSha256'], 'originalManifestSha256': hashlib.sha256(raw).hexdigest(),
                  'result': result, 'measurementOnly': True, 'formalAccepted': False}
        target = out / (name + '.json'); target.write_text(json.dumps(public, ensure_ascii=False, indent=2) + '\n')
        files[target.name] = hashlib.sha256(target.read_bytes()).hexdigest()
    value = {'createdUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'files': files,
             'deployedSource': '7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e',
             'candidateSource': '964e96e45bb588e7e75798b5adf425cbd9985427', 'SSC': 'SSC295',
             'rootRemainsTimeout143': True, 'BUG1332Closed': False,
             'old4406ToolExit': 1, 'BUG1354New4408Exit': 0, 'sharedFullRequired': True,
             'formalTests': 1964, 'formalScopes': 53, 'effortCompletionRate': None, 'QA051Final': 'HELD',
             'productionPtAddedByTheseMeasurements': 0, 'acceptedLeafDelta': 0,
             'rawExported': False, 'formalSecretScanClaim': False, 'formalAccepted': False}
    target = out / 'manifest.json'; target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'manifestSha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'measurements': len(files)}))


if __name__ == '__main__':
    main()
