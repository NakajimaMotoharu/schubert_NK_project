"""Collect ONLY explicitly allowlisted flags; never private NSS/DB/owner payloads."""
import datetime, hashlib, json, pathlib, subprocess
ROOT = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
OUT = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG460-nss-pair-v1'
jobs = [
    ('PAIR460-POST', 'pg460-tool-test-v1.log', 'PG460_TIMEOUT_TOOL_PASS independentAssertions=278 productionPt0=true nativeMutation=false'),
    ('PAIR460-PEERS', 'pg460-peer-test-v1.log', 'PG460_PEERS_TOOL_PASS independentAssertions=14 productionPt0=true nativeMutation=false'),
    ('PAIR460-NATIVE', 'pg460-pair-recover-v2.log', 'PG460_KNOWN30_PAIR_RECOVERED actualParentKnownFailure30=true sameEpochInvalid=true typedThreeIntentsRetired=true all281OriginalBackupTransferPreserved=true all9KernelEmpty=true newPermitIssued=false normalExitClaimed=false bothExternalRootsCaptured=true allOwnedScopesReturnedNormally=true'),
    ('NSS460-LITERAL', 'pg460-nss-host-test-v3.log', 'PG460_NSS_TOOL_PASS independentAssertions=25 productionPt0=true'),
    ('NSS460-FIXTURE', 'pg460-nss-native-fixture-v3.log', 'PG460_NSS_NATIVE_FIXTURE_PASS literalGroupShadowOtherMemberBackupPreserved=true actualCaddyNssUnchanged=true fixtureRetainedPrivate=true productionPt0=true'),
    ('NSS460-NATIVE', 'pg460-nss-native-v3.log', 'PG460_NSS_PREPARED primaryOnly978=true onlyKnownWwwDataMemberRemoved=true all281BusinessOriginalBackupStartupPreserved=true all9KernelEmpty=true allOwnedScopesReturnedNormally=true startsPermitsDdl0=true privateBeforeImagesPreserved=true'),
]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
checked = []
for test_id, name, literal in jobs:
    raw = WORK / name
    assert raw.read_text().splitlines().count(literal) == 1, test_id
    checked.append((test_id, raw, literal))
assert not OUT.exists()
OUT.mkdir(mode=0o750)
files = []; results = []
for test_id, raw, literal in checked:
    safe = OUT / (test_id + '.txt')
    safe.write_text(literal + '\n')
    files.append({'path': safe.name, 'sha256': sha(safe)})
    results.append({'testId': test_id, 'exitCode': 0, 'actual': literal,
                    'expected': literal, 'oracle': '330 specification and independent literals/typed owner/postconditions',
                    'privateLog': raw.name, 'privateLogSha256': sha(raw),
                    'executionTime': 'not recorded in original log; collection time is not execution time'})
sources = {str(p.relative_to(ROOT)): sha(p) for p in (ROOT / 'tools/quality/vm/050_s1').glob('*460*') if p.is_file()}
classes = {}
for folder in ['pg460-known30-tool-v1', 'pg460-nss-tool-v3']:
    for p in (WORK / folder).glob('*.class'):
        classes[folder + '/' + p.name] = sha(p)
manifest = {
    'id': 'PG460-nss-pair-v1', 'collectedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'branch': 'dev-foundation', 'headAtCollection': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
    'toolSourcesDirtyAtCollection': True, 'productionSourceCommit': '8e97eb9138828010926cd47fd10868d8a2d54f11',
    'signedRelease': '0.1.0-PG459', 'signedManifestSha256': '88a6504f93782c65e2328bd719db4133bdc2b3457d0495c9e5887d084fd38311',
    'environment': {'host': 'Linux/JDK25.0.4/Maven3.9.12', 'guest': 'Ubuntu26.04/PostgreSQL18.6/JDK25.0.4', 'passwdPackage': '1:4.17.4-2ubuntu3'},
    'commands': ['javac -Xlint:all -Werror; independent Tool Tests', 'Pg460OwnedIsolation; Pg460Known30PairRecovery verify; Pg460Known30PairRecovery (no args)', 'Pg460CaddyNssPreparationTest native-fixture: gpasswd --root <private fixture> -d caddy www-data', 'Pg460CaddyNssPreparation: genuine M/A/DB; gpasswd -d caddy www-data'],
    'toolSourcesSha256': sources, 'toolClassesSha256': classes, 'results': results, 'files': files,
    'failedExecutionsPreserved': [{'log':'pg460-pair-recover-v1.log','exitCode':1,'reason':'unsupported recover argument, no mutation'}, {'log':'pg460-nss-native-fixture-v1.log','exitCode':1,'reason':'BUG687 wrong -R flag; no actual NSS mutation'}],
    'independentAssertions': {'recovery':278,'peer':14,'nssHost':25,'nssNativeFixture':32,'nssFixtureIncludesHost25':True},
    'bugs':['BUG-685','BUG-686','BUG-687'], 'ykt':['YKT-490','YKT-491','YKT-492'], 'ssc':['SSC-181'],
    'productionPtAdded':0, 'formal':False, 'coverage100':False, 'newNativeParentAccepted':False,
    'redaction':'Only exact public flags/source/hash. No NSS contents, gshadow, DB dump, original, credential, token, session/cookie or owner payload.',
    'limitations':['NSS administrative and old-cohort pair retirement proof only; new parent/CHR/native coverage are separate.', 'Tool assertions do not qualify production coverage; no old BUG544 resolution.']}
(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'id': manifest['id'], 'manifestSha256': sha(OUT / 'manifest.json'), 'formal':False}))
