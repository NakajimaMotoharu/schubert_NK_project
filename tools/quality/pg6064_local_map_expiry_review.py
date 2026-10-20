"""25 individually source-locked PG reviews; selected PT and static-only context kept separate."""
import json
import os
from collections import Counter
from pathlib import Path
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6054_expiry_read_qualification import SOURCE, MAIN
from pg6046_jdbc_ownership_facts import validate_scope
from pg6048_current_jdbc24_review import alias_binding
from pg5958_private_lock_reason_review import fragment

MAP_LINES = {'BackupArtifactVerifier': {185, 186, 489, 490},
             'MaintenanceRunFiles': {1039, 1040, 1041, 1042, 1128, 1129, 1130}}
EXPIRY_LINES = {'CloseResource': {261, 267}, 'AvoidCatchingGenericException': {292, 299, 303, 310, 448, 451},
               'DoNotThrowExceptionInFinally': {295, 306}}


def map_premise(name, text, token):
    if name not in MAP_LINES or 'new HashMap<>()' not in token or '=' not in token:
        raise ValueError('one explicitly reviewed local Map declaration')
    if name == 'BackupArtifactVerifier':
        required = ('files = Map.copyOf(files);', 'contents = Map.copyOf(contents);',
                    'return new PendingDigests(', 'return new BundleSnapshot(', 'child.atExistingEntryHandle(')
        reason = ('1271 individual PG review: this map is local to one observePending/retained capture invocation; '
                  'only the serial loop and inline OwnedTransferDirectory callback access it. PendingDigests returns three values, '
                  'not a map; BundleSnapshot copies both maps with Map.copyOf before publication. No mutable map/closure is '
                  'stored or submitted to another thread. The existing Thread.currentThread interrupt check does not imply '
                  'cross-thread ownership. ConcurrentHashMap would not protect whole snapshot consistency and is not applicable.')
    else:
        required = ('runs = Map.copyOf(runs);', 'begins = Map.copyOf(begins);', 'done = Map.copyOf(done);',
                    'plans = Map.copyOf(plans);', 'Map.copyOf(runs),', 'Map.copyOf(begins),', 'Map.copyOf(done),')
        reason = ('1271 individual PG review: this inventory/scan map is built by sequential local loops and reads, '
                  'never published as the mutable object. Inventory copies all four maps and graph copies its three maps '
                  'with Map.copyOf before returning; enclosing owner serialization remains unchanged. ConcurrentHashMap '
                  'is not required for a thread-confined builder. This premise proves neither live namespace consistency '
                  'nor OS/DB ownership; those remain separate runtime criteria.')
    if any(s not in text for s in required):
        raise ValueError('reviewed immutable publication/callback boundaries must stay exact')
    return reason


def main():
    qp = BASE/'PG6054-expiry-read-qualification-v1/manifest.json'
    if sha(qp) != '9f1269de6b66c0be2467aab5de164e82553f03d33dc79f5212e410ff4f1daee9':
        raise ValueError('actual sourcec4 selected148/static1305 qualification')
    q = json.loads(qp.read_bytes()); folder = W/'pg6054-expiry-read-qualification-v1'
    for name, key in (('manifest.safe.json', 'privateManifestSha256'), ('cases.safe.json', 'casesSha256'), ('findings.safe.json', 'findingsSha256')):
        if sha(folder/name) != q[key]:
            raise ValueError('actual original physical/148/canonical raw reports immutable')
    physical = json.loads((folder/'manifest.safe.json').read_bytes()); raw = json.loads((folder/'findings.safe.json').read_bytes())
    cases = json.loads((folder/'cases.safe.json').read_bytes())
    selected = [r for r in cases if r['className'].rsplit('.', 1)[-1] in ('ExpiryAuditResourceFailureTest', 'ExpiryAuditRepositoryTest', 'ExpirySuccessfulScopeTest')]
    if len(selected) != 35 or any(r['source'] != SOURCE or r['result'] != 'PASS_ORIGINAL_XML' for r in selected):
        raise ValueError('all35 actual sourcec4 Expiry independent cases,not fabricated or historical')
    fp = W/'pg6062-expiry-read-facts-v1/manifest.safe.json'
    if sha(fp) != 'e700803c7538325a66e022575a8b501ee82708d2146be91a86135e441aa278e2':
        raise ValueError('actual two parsed read scopes')
    facts = json.loads(fp.read_bytes()); source = (ROOT/MAIN).read_text()
    if facts['source'] != SOURCE or facts['phaseExits'] != [0, 0] or len(facts['scopes']) != 2:
        raise ValueError('actual same-source parse facts,not Production invocation')
    aliases = {}
    for scope in facts['scopes']:
        validate_scope(scope)
        if scope['sourceSha256'] != sha(ROOT/MAIN) or scope['method'] != 'read':
            raise ValueError('exact two owned resources of read only')
        alias = alias_binding(source, scope, 'presentRead'); aliases[alias['firstLine']] = alias
    result = []
    for row in raw:
        name = Path(row['sourcePath']).stem; line = int(row['beginline']); rule = row['rule']
        map_scope = name in MAP_LINES and rule == 'UseConcurrentHashMap' and line in MAP_LINES[name]
        expiry_scope = row['sourcePath'] == MAIN and rule in EXPIRY_LINES and line in EXPIRY_LINES[rule]
        if not map_scope and not expiry_scope:
            continue
        path = ROOT/row['sourcePath']; text = path.read_text()
        if sha(path) != row['sourceSha256'] or physical['allSourceHashes'][row['sourcePath']] != sha(path):
            raise ValueError('each reviewed diagnostic exact current source bytes')
        token = fragment(text, row).strip()
        value = dict(row, source=SOURCE, rawWarningRetained=True, implementationReviewedNoChangeRequired=True,
                     reviewSpec='018/1271', currentWholeJoinPending=True, formalAccepted=False, ptAlternativeCompleted=0)
        if map_scope:
            value.update(status='CONTEXT_NOT_APPLICABLE', reason=map_premise(name, text, token),
                         staticContextPremiseOnly=True, currentSelectedCaseRefs=[])
        else:
            status = 'FALSE_POSITIVE' if rule == 'CloseResource' else 'REQUIRED_CONTRACT'
            if rule == 'CloseResource':
                alias = aliases.get(line)
                if alias is None or token != alias['alias']:
                    raise ValueError('each warning is exactly the protected identity alias,not a second acquired resource')
                value['aliasProof'] = alias
            reason = ('SS332SSC310/063199: each read resource enters immediate typed primary protection and closes once '
                      'with SQL-versus-unknown precedence; null acquisition is checked inside that protection. '
                      'The actual primary is recorded and rethrown unchanged, unknown cleanup replaces only a known SQL primary, '
                      'and a retained unknown primary receives only a new fixed secondary. The two identity aliases allocate '
                      'no new resource. SS343SSC304 usingJdbc catch Throwable instead preserves the separate exact JavaTWR '
                      'primary/secondary/self-suppression contract, including declared SQL/IO. Each of these catches/finally '
                      'has nontrivial contract work; it is not the previously withdrawn pure Error rethrow rationale. '
                      'Independent current35 cases include68 table subcases and24 exactTWR tests; actual program four counters '
                      'have no misses. Stage/finish broad Runtime catches are expressly not classified by this review.')
            value.update(status=status, reason=reason, staticContextPremiseOnly=False, currentSelectedCaseRefs=selected,
                         sourceScopeFactsSha256=sha(fp), selectedQualificationSha256=sha(qp))
        result.append(value)
    if (len(result) != 25 or Counter(r['status'] for r in result) != Counter(CONTEXT_NOT_APPLICABLE=11, FALSE_POSITIVE=2, REQUIRED_CONTRACT=12)
            or {r['beginline'] for r in result if r['sourcePath'] == MAIN and r['rule'] == 'CloseResource'} != {'261', '267'}):
        raise ValueError('exact individual11 local maps/14 Expiry,exclude two stagefinish catches')
    callback = ROOT/'src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/OwnedTransferDirectory.java'
    if not all(s in callback.read_text() for s in ('public final class OwnedTransferDirectory', 'return operation.execute(capability);')):
        raise ValueError('reviewed final inline callback chain unchanged')
    os.umask(0o077); out = BASE/'PG6064-local-map11-expiry14-v1'; out.mkdir()
    for filename, value in (('reviews.json', result), ('manifest.json', dict(actualExit=0, source=SOURCE, reviewCount=25,
        statuses=dict(Counter(r['status'] for r in result)), rawStaticFindingsRetained=1305, sourceMainFiles=851,
        parseFactsSha256=sha(fp), selectedQualificationSha256=sha(qp), callbackSourceSha256=sha(callback),
        currentWholeJoinPending=True, formalAccepted=False, sourceCodeChanged=False, testsExecuted=0,
        newPtPassesClaimed=0, ptAlternativeCompleted=0, actualCoverageAdded=None))):
        with (out/filename).open('x') as f:
            json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, reviewed=25, currentWholeJoinPending=True, manifestSha256=sha(out/'manifest.json'), reviewsSha256=sha(out/'reviews.json'))))


if __name__ == '__main__':
    main()
