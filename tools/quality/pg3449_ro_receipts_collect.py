"""Bounded completed host ABI/RO/independent post receipts only, no VM operation."""
import hashlib
import json
from pathlib import Path
from pg1446_current_cold_stage import W


def main():
    records = {}
    for name in ['pg3444-frozen-v1.safe.json', 'pg3445-ro-current-preflight-v1/manifest.safe.json',
                 'pg3446-stage-v1.safe.json', 'pg3446-prepare-ro-v1.safe.json',
                 'pg3448-current-outbox-ro-independent-post-v1/manifest.safe.json']:
        p = W / name
        v = json.loads(p.read_bytes())
        assert type(v['actualExit']) is int and v['actualExit'] == 0
        if 'privateLogSha256' in v:
            log = W / name.replace('.safe.json', '.private.log')
            assert hashlib.sha256(log.read_bytes()).hexdigest() == v['privateLogSha256']
        records[name] = {'manifestSha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'result': v}
    g = v['guest']
    assert g['candidateSource'] == '4856b3fcaeb4cae983d77757a38dc0bf56a693e2'
    assert g['candidateHostReadonlyVerified'] is True and g['candidateNativeCredit'] is False
    value = {'actualExit': 0, 'records': records, 'candidateRoIndependentlyVerified': True,
             'currentSourceUnchanged': 'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25',
             'candidatePublished': False, 'candidateNativeQualified': False,
             'formal': '1964PT/53scope', 'individual': '17/190', 'effortCompletionRate': None,
             'qa051Final': 'HELD', 'formalUpdated': False, 'pgptAllComplete': False}
    out = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3449-candidate-ro-post'
    out.mkdir()
    p = out / 'manifest.json'
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'manifestSha256': hashlib.sha256(p.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
