"""PG461 allowlisted code-only evidence. No private payload is copied."""
import datetime, hashlib, json, pathlib, subprocess
ROOT = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
OUT = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG461-code-only-v1'
SOURCE = '00785cf0698aecf1ace1e60b87e8849639e85b97'
DIGEST = '1b7688de234ad15e39ffe578060019ff61fc21efd3c8e0c5aa62c39c95959b3c'
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
jobs = [
    ('CODE461-STAGE', 'pg461-stage-v1.log', 'PG461_STAGE exactSource=true signedCandidateBytes=true rootToolAndStableObserver=true wrapperExecutableMetadata=true previousCurrentUnchanged=true ddl0=true starts0=true permits0=true'),
    ('CODE461-VERIFY', 'pg461-code-verify-v1.log', 'PG461_CODE_ONLY_VERIFIED signed027=true all291Full14AndBusinessOriginalBackupTransferPreserved=true all9KernelEmpty=true ddl0=true permits0=true starts0=true ownedClosed=true'),
    ('CODE461-ACTIVATE', 'pg461-code-activate-v1.log', 'PG461_CODE_ONLY_ACTIVATED signed027=true all291Full14AndBusinessOriginalBackupTransferPreserved=true all9KernelEmpty=true ddl0=true permits0=true starts0=true ownedClosed=true'),
]
full = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG461-caddy-policy-full/manifest.json'
f = json.loads(full.read_bytes())
assert f['sourceCommit'] == SOURCE and f['tests'] == 3260 and f['totalSuites'] == 481 and f['actualRunnerExitCode'] == 0
release = WORK / 'pg461-release-v1'
assert sha(release / 'RELEASE-MANIFEST.json') == DIGEST
assert not OUT.exists()
for _, name, literal in jobs:
    assert (WORK / name).read_text().splitlines().count(literal) == 1
OUT.mkdir(mode=0o750)
results, files = [], []
for test_id, name, literal in jobs:
    path = OUT / (test_id + '.txt')
    path.write_text(literal + '\n')
    files.append({'path': path.name, 'sha256': sha(path)})
    results.append({'testId': test_id, 'exitCode': 0, 'actual': literal,
        'expected': '332 specification: signed027, same source; full291x14/business/original/Backup/Transfer and old16 preserved, all9 empty, no DDL/start/permit, all owned scopes normal return',
        'privateLog': name, 'privateLogSha256': sha(WORK / name),
        'executionTime': 'Original command did not persist timestamp; collection time is not execution time'})
manifest = {
    'id': 'PG461-code-only-v1', 'collectedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'headAtCollection': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
    'branch': 'dev-foundation', 'productionSourceCommit': SOURCE, 'previousSource': '8e97eb9138828010926cd47fd10868d8a2d54f11',
    'signedRelease': '0.1.0-PG461', 'schema': '027', 'manifestSha256': DIGEST,
    'nativeToolClassSha256': sha(WORK / 'pg461-code-tools-v1/Pg461CodeOnlyDeployment.class'),
    'hostFullManifestSha256': sha(full), 'hostFullTests': 3260, 'hostFullSuites': 481,
    'assembly': {'artifacts': 185, 'sql': 27, 'signatureVerified': True, 'allSixTargetsFrozenByteEqual': True},
    'environment': {'host': 'Linux/JDK25.0.4/Maven3.9.12/Node24.19.0', 'guest': 'Ubuntu26.04/PostgreSQL18.6/JDK25.0.4/Artemis2.56.0'},
    'commands': ['AssembleReleaseFixture repo pg461-release-v1 source00785 0.1.0-PG461 approved-effective-profile public-recipient; independent185BOM/27SQL/frozen6/Ed25519 verification',
        'pg461_stage_v1.py manifestDigest sourceCommit', 'Pg461CodeOnlyDeployment sourceCommit manifestDigest verify', 'Pg461CodeOnlyDeployment sourceCommit manifestDigest activate'],
    'results': results, 'files': files, 'productionPtAdded': 0, 'formal': False, 'coverage100': False, 'nativeParentAccepted': False,
    'bugs': ['BUG-691'], 'ykt': ['YKT-495'], 'ssc': ['SSC-182','SSC-183'],
    'limitations': ['Code-only provisioning is not parent, CHR, native coverage100 or formal acceptance; external parent is separately observed.', 'Private keys/originals/DB/authority records remain outside Git.'],
    'redaction': 'Only fixed public flags, source and hashes; no token/session/cookie/password/key/DB dump or owner payload.',
}
(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'id': manifest['id'], 'manifestSha256': sha(OUT / 'manifest.json'), 'formal': False}))
