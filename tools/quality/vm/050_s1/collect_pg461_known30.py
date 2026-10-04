"""Collect ONLY explicitly allowlisted flags; never private NSS/DB/owner payloads."""
import datetime, hashlib, json, pathlib, subprocess
ROOT = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
OUT = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG461-known30-native-v1'
jobs = [
('PAIR461-POST','pg461-tool-test-v3.log','PG461_TIMEOUT_TOOL_PASS independentAssertions=302 productionPt0=true nativeMutation=false'),
('PAIR461-PEERS','pg461-peer-test-v3.log','PG461_PEERS_TOOL_PASS independentAssertions=14 productionPt0=true nativeMutation=false'),
('PAIR461-ISOLATE','pg461-isolation-native-v2.log','PG461_GRAPH_ISOLATED actualParentKnownFailure30=true all8KernelStopped=true sameOriginal291RowsBackupPreserved=true currentStillInvalid=true intentRetired0=true normalExitClaimed=false permitsIssued0=true allOwnedScopesReturnedNormally=true'),
('PAIR461-NATIVE','pg461-pair-recover-v1.log','PG461_KNOWN30_PAIR_RECOVERED actualParentKnownFailure30=true sameEpochInvalid=true typedThreeIntentsRetired=true all291OriginalBackupTransferPreserved=true all9KernelEmpty=true newPermitIssued=false normalExitClaimed=false bothExternalRootsCaptured=true allOwnedScopesReturnedNormally=true'),
('CODE461-NAMES','pg461-code-tool-test-v1.log','PG461_CODE_ONLY_TOOL_PASS independentAssertions=60 productionPt0=true namespaceIntentForeignRejected=true ddlStartsPermitsAbsent=true'),
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
                    'expected': literal, 'oracle': '332 specification and independent literals/typed owner/postconditions',
                    'privateLog': raw.name, 'privateLogSha256': sha(raw),
                    'executionTime': 'not recorded in original log; collection time is not execution time'})
sources = {str(p.relative_to(ROOT)): sha(p) for p in (ROOT / 'tools/quality/vm/050_s1').glob('*461*') if p.is_file()}
classes = {}
for folder in ['pg461-known30-tool-v3','pg461-code-tools-v1']:
    for p in (WORK / folder).glob('*.class'):
        classes[folder + '/' + p.name] = sha(p)
manifest = {
    'id': 'PG461-known30-native-v1', 'collectedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'branch': 'dev-foundation', 'headAtCollection': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
    'toolSourcesDirtyAtCollection': True, 'productionSourceCommit': '8e97eb9138828010926cd47fd10868d8a2d54f11',
    'signedRelease': '0.1.0-PG459', 'signedManifestSha256': '88a6504f93782c65e2328bd719db4133bdc2b3457d0495c9e5887d084fd38311',
    'environment': {'host': 'Linux/JDK25.0.4/Maven3.9.12', 'guest': 'Ubuntu26.04/PostgreSQL18.6/JDK25.0.4', 'passwdPackage': '1:4.17.4-2ubuntu3'},
    'commands': ['javac -Xlint:all -Werror with provided spotbugs-annotations4.10.4 and frozen signedPG459 runtime; independent302+14+60/cohort preflight', 'Pg461OwnedIsolation; Pg461Known30PairRecovery verify; Pg461Known30PairRecovery (no args)'],
    'toolSourcesSha256': sources, 'toolClassesSha256': classes, 'results': results, 'files': files,
    'failedExecutionsPreserved': [{'log':'pg461-tool-compile-v1.log','exitCode':1,'reason':'missing provided annotation classpath'}, {'log':'pg461-isolation-native-v1.log','exitCode':1,'reason':'BUG690 old-watch pin refused before stop/retirement'}],
    'independentAssertions': {'recovery':302,'peer':14,'codeOnly':60,'cohortPins':'independent fixed literals'},
    'bugs':['BUG-690','BUG-691'], 'ykt':['YKT-495'], 'ssc':['SSC-182','SSC-183'], 'qa':['QA-047'],
    'privateCaptureSetSha256':'097c5246b98738659ebfbf525cbeedc99213f3cbf9736767dd2dc4cb18f30299',
    'observerSha256':'89df0f075188e957492d7dd0c0fa2504a43528c52c290c018d306a6a4d3a4c30',
    'productionPtAdded':0, 'formal':False, 'coverage100':False, 'newNativeParentAccepted':False,
    'redaction':'Only exact public flags/source/hash. No NSS contents, gshadow, DB dump, original, credential, token, session/cookie or owner payload.',
    'limitations':['Captured PG460 known30 cohort isolation/typed retirement only; corrected Production source and new candidate native acceptance are separate.', 'Tool assertions do not qualify production coverage; no old BUG544 resolution.']}
(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'id': manifest['id'], 'manifestSha256': sha(OUT / 'manifest.json'), 'formal':False}))
