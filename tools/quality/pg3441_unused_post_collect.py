"""Publish bounded completed unused/post receipts; never reissue an operation."""
import hashlib
import json
from pathlib import Path

import pg3434_current_outbox_candidate_sources as role


def main():
    names = ['pg3438-stage-v1.safe.json', 'pg3438-stage-v2.safe.json',
             'pg3438-place-v1.safe.json',
             'pg3440-current-outbox-unused-independent-post-v1/manifest.safe.json']
    records = {}
    for name in names:
        path = role.W / name
        value = json.loads(path.read_bytes())
        expected = 1 if name == names[0] else 0
        assert value['actualExit'] == expected
        if 'privateLogSha256' in value:
            log = role.W / name.replace('.safe.json', '.private.log')
            assert hashlib.sha256(log.read_bytes()).hexdigest() == value['privateLogSha256']
        records[name] = {'manifestSha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                         'result': value}
    post = records[names[-1]]['result']['guest']
    assert post['candidateSource'] == role.SOURCE and post['candidateManifestSha256'] == role.BOM
    for key in ['all24And32And187Unchanged', 'allTenKernelEmpty', 'allClientAdvisoryFlock0',
                'allOriginalBackupAndNativeUnchanged', 'currentEpochApprovalUnchanged',
                'unusedCandidate187Verified', 'signatureVerified', 'signals0']:
        assert post[key] is True
    assert post['candidateNativeCredit'] is False
    frozen = json.loads((role.W / 'pg3436-frozen-v1.safe.json').read_bytes())
    for name, raw in role.sources().items():
        data = (role.W / role.TOOLS / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == frozen['fileHashes'][name]
        if name in ['pg3434_native_refs.py', 'pg3434_input_preflight.py']:
            data = data.split(b'\n', 1)[1]
        assert data == raw.encode(), name
    result = {'actualExit': 0, 'candidateSource': role.SOURCE, 'candidateBomSha256': role.BOM,
              'currentSourceUnchanged': role.CURRENT, 'records': records,
              'all18GeneratedFilesByteUnchangedAfterBinderCorrection': True,
              'wholeCompileStagePlaceReplay': False, 'candidateUnusedPlaced': True,
              'candidateReadOnly': False, 'candidatePublished': False,
              'candidateNativeQualified': False, 'formalUpdated': False,
              'formal': '1964PT/53scope', 'individual': '17/190', 'effortCompletionRate': None,
              'qa051Final': 'HELD', 'pgptAllComplete': False}
    out = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3441-unused-independent-post'
    out.mkdir()
    path = out / 'manifest.json'
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'manifestSha256': hashlib.sha256(path.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
