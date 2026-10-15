"""Persist genuine finite publication completion, never replay or infer Root success."""
import hashlib
import json
from pathlib import Path
from pg1446_current_cold_stage import W


def main():
    records = {}
    for name in ['pg3452-frozen-v1.safe.json', 'pg3454-stage-v1.safe.json',
                 'pg3454-activate-v1.safe.json',
                 'pg3458-current-outbox-publication-independent-post-v1/manifest.safe.json']:
        p = W / name
        v = json.loads(p.read_bytes())
        assert type(v['actualExit']) is int and v['actualExit'] == 0
        if 'privateLogSha256' in v:
            assert hashlib.sha256((W / name.replace('.safe.json', '.private.log')).read_bytes()).hexdigest() == v['privateLogSha256']
        records[name] = {'manifestSha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'result': v}
    g = v['guest']
    assert g['productionSource'] == '4856b3fcaeb4cae983d77757a38dc0bf56a693e2'
    for key in ['sevenFinitePhasesVerified', 'all24And32Unchanged', 'whole187SignedArtifactBytesVerified',
                'allTenKernelEmpty', 'allClientAdvisoryFlock0', 'originalBackupNativePreserved',
                'canonicalInvalidEpochApprovalCurrentAndOldLinkVerified', 'unitBytesInodesConfigurationUnchanged',
                'newSourceParentNotStarted', 'oldNativeNotAppliedToNewSource']:
        assert g[key] is True
    assert g['unitExchangeAndReload'] is False
    value = {'actualExit': 0, 'records': records, 'candidatePublishedIndependentlyVerified': True,
             'productionSource': g['productionSource'], 'release': 'PG3420',
             'candidateBomSha256': g['candidateManifestSha256'], 'newParentStarted': False,
             'candidateNativeQualified': False, 'formal': '1964PT/53scope', 'individual': '17/190',
             'effortCompletionRate': None, 'qa051Final': 'HELD', 'formalUpdated': False,
             'pgptAllComplete': False, 'wholeOrLifecycleReplayed': False}
    out = Path(__file__).resolve().parents[2] / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3459-finite-publication-post'
    out.mkdir()
    p = out / 'manifest.json'
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'manifestSha256': hashlib.sha256(p.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
