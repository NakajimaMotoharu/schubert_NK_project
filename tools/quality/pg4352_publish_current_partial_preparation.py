"""Publish only sanitized current read/qualification receipts, never raw pair/DB values."""
import datetime
import hashlib
import json
from pathlib import Path
from pg1446_current_cold_stage import W


def main():
    out = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4352-current-partial-preparation-v1'
    out.mkdir()
    hashes = {}
    for slot in ['pg4336-current-unknown-read-v1', 'pg4346-current-partial-tools-v1-stage',
                 'pg4346-current-partial-tools-v1-proof', 'pg4350-current-partial-qualification-v1']:
        raw = (W / slot / 'manifest.safe.json').read_bytes()
        value = json.loads(raw)
        value['originalManifestSha256'] = hashlib.sha256(raw).hexdigest()
        target = out / (slot + '.json')
        target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
        hashes[target.name] = hashlib.sha256(target.read_bytes()).hexdigest()
    log = out / 'host-tests.log'
    log.write_bytes((W / 'pg4350-current-partial-qualification-v1/host-tests.log').read_bytes())
    hashes[log.name] = hashlib.sha256(log.read_bytes()).hexdigest()
    value = {'source': '7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e',
             'createdUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'designMain': 'f9600af73555fb002fc98ddd0af0dea4c0e686b6', 'designPR': 138,
             'files': hashes, 'rawExported': False, 'recoveryAccepted': False,
             'originalUnknownNormal': False, 'formalAccepted': False, 'productionPtAdded': 0}
    target = out / 'manifest.json'
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'manifestSha256': hashlib.sha256(target.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
