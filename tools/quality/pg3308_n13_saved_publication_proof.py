"""Rebind saved successful a9 publication proof, not reexecute or accept N13.

Source042 qualifies preserved originals; newCurrentSource a9 qualifies the
published result. Never substitute either source or grant current live authority.
"""
import collections
import copy
import json
from pathlib import Path
import subprocess

from pg3274_header_group_full_six import ROOT, SOURCE, W
from pg3282_wbs_current_source_apply import replace_public, rewrite_root
import wbs_progress_audit as audit

OLD = '04207efc3ad78bca75942153a90c70985064c988'
BOOT = '79a3260a-e16d-42bf-942a-b914ed144c28'
PUBLIC = Path('evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3308-N13-saved-publication')
STAGES = [
    ('unused', 'pg2838-network-cold-unused-owned-place-v1', 'e8eab3eb35bb79924ca6588320ffd1afe6727977a8dd65237a18bcda3aed8a54', 'pg2840-network-cold-unused-independent-post-v1', 'ec2f61dc636d03e48d5d3caf8a7a1ec126510c6b3652828b5584551e8de4733d', '6f7367fd3fa5aa46aae17a65964c2f93d0b3c6e1e95448dbcbc090dc0e8a122a'),
    ('readonly', 'pg2848-network-cold-ro-owned-prepare-v1', '2101bd1fda8d870e396d437b706274d64f658c6df948763258580799fbb407e1', 'pg2850-network-cold-ro-independent-post-v1', 'add92a0687cc760755abcc18f4724b9c36a24dde041185bb923d9e032c8fbfb5', 'b9a4eb1dcf71e4e514f689734ca54bf1471c19b4aa4f2e7b8d27b471c3ae06ee'),
    ('publication', 'pg2858-network-cold-publication-owned-activate-v1', 'fffb21b0ab499e588d719f2d846a760630aa51a296fa236305ee525055a8414b', 'pg2860-network-cold-publication-independent-post-v1', '3dfc9a4125415cbd1a6c36f442d7fba406df78e07e421e0bf9b3445b7ae57efa', '51bfda383bbb7a57e8cadc2e213d253fcaba31bef07a1451a1b0b9cf018cf916')]
COMMON_FLAGS = ('candidateFull187Verified', 'fullCurrentDbOriginalBackupSignatureTwice',
                'metadataScopesClosedNormally', 'oldDoneUnchanged', 'parentBackendAdvisoryFlocksGone',
                'releaseReadonly', 'tenCold18Full32', 'twelveRolesEmptyCorrectIdsModesAcl')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_records(records):
    require(set(records) == {'unused', 'readonly', 'publication'}, 'all three stages required')
    result = []
    for label, own_name, _, post_name, _, prepared_sha in STAGES:
        own, post = records[label]; guest = post['guest']
        require(type(own['actualExit']) is int and type(post['actualExit']) is int
                and type(guest['actualExit']) is int and own['actualExit'] == post['actualExit'] == guest['actualExit'] == 0, 'actual independent success0 required')
        require(own['productionSource'] == guest['source'] == OLD
                and guest['candidateSource'] == SOURCE and guest['boot'] == BOOT,
                'old-original/new-candidate source and same measured boot must remain distinct')
        require(own['run'].lower() == own_name and guest['run'].lower() == post_name,
                'exact matching historical owned/post pair required')
        require(guest['prepareAfterSha256'] == prepared_sha and all(guest[f] is True for f in COMMON_FLAGS), 'all original/current DB24/config32/artifact187/resources scope required')
        require(type(guest['businessWrites']) is int and guest['businessWrites'] == 0
                and guest['permissionIssued'] is False and guest['formalAccepted'] is False, 'no business write/permission/formal claim')
        require(guest['candidateNotActivated'] is (label != 'publication'), 'phase must not imply early activation')
        if label in ('readonly', 'publication'):
            require(guest['candidateImmutableIndependentPost'] is True, 'independent candidate immutable scope required')
        if label == 'publication':
            require(guest['newCurrentSource'] == SOURCE and all(guest[f] is True for f in (
                'coldPublicationSevenPhasesVerified', 'linkedOldCurrentPreserved', 'newCanonicalInvalidNoPermission')),
                'all seven finite phases/new current/retained original/no authority required')
        else:
            require(guest['afterSha256'] == 'c9aa34a32b6d2c411c23489016e1c365f12fc27653d16c7d5aa69028a7c6130a', 'original current unchanged until publication')
        result.append({'stage': label, 'ownedRun': own['run'], 'postRun': guest['run'],
                       'actualExit': 0, 'originalQualifiedSource': OLD, 'candidateSource': SOURCE,
                       'prepareAfterSha256': prepared_sha, 'postAfterSha256': guest['afterSha256'],
                       'allRequiredScopeFlags': True, 'permissionIssued': False})
    return result


def load_records():
    records = {}; hashes = {}
    for label, own_name, own_sha, post_name, post_sha, _ in STAGES:
        own_path = W / own_name; post_path = W / post_name
        require(audit.digest(own_path / 'manifest.safe.json') == own_sha
                and audit.digest(post_path / 'manifest.safe.json') == post_sha, 'six frozen original receipt hashes required')
        own = audit.read_json(own_path / 'manifest.safe.json'); post = audit.read_json(post_path / 'manifest.safe.json')
        require(audit.digest(own_path / 'observer.private.log') == own['logSha256'], 'actual original owned log hash required')
        require(audit.digest(post_path / 'payload.private.py') == post['payloadSha256']
                and json.loads((post_path / 'observer.private.log').read_bytes()) == post['guest'], 'independent original payload/log proof required')
        records[label] = (own, post); hashes[label] = {'ownedReceiptSha256': own_sha, 'postReceiptSha256': post_sha}
    return records, hashes


def main():
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT), 'fixed clean evidence binding tool required')
    before = audit.verify(); records, hashes = load_records(); stages = check_records(records)
    snapshot_path = audit.PMO / '486_WBS現行実績.json'; snapshot = audit.read_json(snapshot_path)
    row = next(r for r in snapshot['rows'] if r['id'] == 'WBS-N13')
    require(snapshot['source'] == SOURCE and row['measurementStatus'] == 'HISTORICAL_VM_SUCCESS_RECHECK'
            and row['acceptance']['status'] != 'ACCEPTED', 'only unbound historical N13 measurement, not acceptance')
    out = W / 'pg3308-n13-saved-proof-rebind-v1'; out.mkdir(mode=0o700)
    with (out / 'before-snapshot.json').open('xb') as stream:
        stream.write(snapshot_path.read_bytes())
    value = {'actualExit': 0, 'productionSource': SOURCE, 'run': 'PG3308-N13-saved-proof-rebind',
             'measuredBoot': BOOT, 'stages': stages, 'originalReceiptHashes': hashes,
             'newCurrentSource': SOURCE, 'originalQualifiedSource': OLD,
             'allSevenPublicationPhasesPreviouslyVerified': True, 'all24Tables32Config187ArtifactsPreserved': True,
             'allOwnedResourcesClosed': True, 'metadataScopesReturnedNormally': True,
             'historicalMeasuredProofOnly': True, 'currentLiveAuthority': False,
             'newRuntimeOrVmActions': 0, 'newPtCredit': 0, 'newNativeCredit': 0,
             'acceptedLeafDelta': 0, 'formalAccepted': False, 'effortPercent': None}
    target = ROOT / PUBLIC; target.mkdir(parents=True, exist_ok=False)
    with (target / 'manifest.json').open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2); stream.write('\n')
    row.setdefault('historicalRuntimeBindings', []).append(copy.deepcopy({k: row[k] for k in row if k != 'acceptance'}))
    row.update(measurementStatus='VM_STEP_VERIFIED', measurementSource=SOURCE,
               currentLiveAuthority=False, measurementStageRun=value['run'],
               currentStageProof={'path': str(PUBLIC / 'manifest.json'), 'sha256': audit.digest(target / 'manifest.json')})
    row['evidence'].append(str(PUBLIC / 'manifest.json'))
    text = rewrite_root(snapshot_path.read_text(), {'rows': snapshot['rows'], 'counts': dict(collections.Counter(r['measurementStatus'] for r in snapshot['rows']))})
    candidate = out / 'candidate-snapshot.json'; candidate.write_text(text)
    qualified = audit.verify(snapshot_path=candidate)
    require(qualified['acceptedTasks'] == before['acceptedTasks'], 'acceptance unchanged')
    replace_public(snapshot_path, text.encode()); after = audit.verify()
    require(after['acceptedTasks'] == before['acceptedTasks'], 'no acceptance granted')
    with (out / 'manifest.safe.json').open('x') as stream:
        json.dump({'actualExit': 0, 'productionSource': SOURCE, 'before': before, 'after': after,
                   'publicManifestSha256': audit.digest(target / 'manifest.json')}, stream)
    print(json.dumps({'actualExit': 0, 'runtimeVerified': after['currentMeasurementCounts']['VM_STEP_VERIFIED'],
                      'runtimeHistorical': after['currentMeasurementCounts']['HISTORICAL_VM_SUCCESS_RECHECK'],
                      'acceptedTasks': after['acceptedTasks'], 'runtimeOperationsReissued': 0}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
