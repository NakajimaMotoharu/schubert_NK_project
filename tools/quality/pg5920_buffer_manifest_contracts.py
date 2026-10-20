"""Five exact regular static contracts with actual selected XML; not refused-PT alternatives."""
import copy
import hashlib
import json
import os
import re
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter
from pg5540_snapshot_scratch_selected import ROOT, TC, sha
from static_disposition_overlay import BASE, load, apply_decisions
from pg5918_api_static_rebind import SOURCE, W

PREFIX = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/'
BUFFER = PREFIX + 'idempotency/WipingByteArrayOutputStream.java'
MAP = PREFIX + 'file/AssetChecksumManifest.java'
CODEC = PREFIX + 'idempotency/ResponseSnapshotCodec.java'
FINGERPRINT = PREFIX + 'idempotency/OperationFingerprint.java'


def parent_contract(text):
    declarations = ('void write(int);', 'void write(byte[], int, int);', 'void reset();',
                    'byte[] toByteArray();', 'int size();', 'java.lang.String toString();',
                    'void writeTo(java.io.OutputStream) throws java.io.IOException;')
    if any('public synchronized ' + value not in text for value in declarations):
        raise ValueError('actual JDK parent intrinsic monitor contract required')


def buffer_contract(text, codec, fingerprint):
    if re.search(r'(?m)^class WipingByteArrayOutputStream extends ByteArrayOutputStream \{', text) is None or text.count('public synchronized ') != 4 or 'private static final int MAXIMUM = 1_050_000;' not in text:
        raise ValueError('only existing nonpublic adapter and four matching intrinsic overrides')
    if codec.count('try (var output = new WipingByteArrayOutputStream()) {') != 2 or codec.count('return output.toByteArray();') != 2 or 'private static byte[] compress(' not in codec or 'private static byte[] decompress(' not in codec:
        raise ValueError('two private operation-local owned scopes return copies, never the owner')
    if fingerprint.count('try (var output = new WipingByteArrayOutputStream()) {') != 1 or fingerprint.count('return output.toByteArray();') != 1 or '  byte[] canonicalBytes(CanonicalRequest request) {' not in fingerprint or any('private static void ' + s + '(ByteArrayOutputStream output,' not in fingerprint for s in ('writeText', 'writeValue', 'writeLength')) or 'Arrays.fill(canonical, (byte) 0);' not in fingerprint:
        raise ValueError('one package-private canonical copy scope, private borrow-only helpers, caller erasure')
    if any(value not in text for value in ('Arrays.fill(old, (byte) 0);', 'Arrays.fill(buf, (byte) 0);', 'count = 0;', 'reserve(1);\n    buf[count] = (byte) value;\n    count++;')):
        raise ValueError('bounded reserve and full old/current storage erasure unchanged')


def reference_contract(owners):
    if owners != {BUFFER: 3, CODEC: 2, FINGERPRINT: 1}:
        raise ValueError('all references: declaration/constructor/redacted label, two codec scopes, one canonical scope')


def map_contract(text):
    if any(value not in text for value in ('private final Map<String, String> hashes;', 'this.hashes = Map.copyOf(hashes);', 'Map<String, String> hashes = new HashMap<>();', 'return new AssetChecksumManifest(hashes);', 'require(hashes.putIfAbsent(path, hash) == null);')):
        raise ValueError('local parser map, duplicate rejection and defensive immutable publication')


def selected_refs(snapshot, cls, methods, expected_sha):
    path = snapshot / ('src/schubert-nk-api/target/surefire-reports/TEST-' + cls + '.xml')
    if sha(path) != expected_sha:
        raise ValueError('original selected XML pinned by independent reader')
    result = []
    for case in ET.parse(path).getroot().findall('testcase'):
        method = case.get('name', '').split('(', 1)[0]
        if method not in methods:
            continue
        if any(n.tag in ('failure', 'error', 'skipped', 'flakyFailure', 'flakyError', 'rerunFailure', 'rerunError') for n in case.iter()):
            raise ValueError('actual executed PASS only')
        result.append(dict(klass=cls, method=method, caseNameSha256=hashlib.sha256(case.get('name').encode()).hexdigest(), selectedXmlSha256=sha(path)))
    if {r['method'] for r in result} != set(methods) or len(result) != len(methods):
        raise ValueError('exact ordinary selected methods, never generated expected values')
    return [{'class': r['klass'], 'caseNameSha256': r['caseNameSha256'], 'selectedXmlSha256': r['selectedXmlSha256'], 'selectedMethod': r['method']} for r in result]


def main():
    bp = BASE / 'PG5918-api-dispositions-v1/manifest.json'
    bsha = 'b8874a8ab57f3ba96cf70b3f706114544ebaabb1da13f9ec91ee6c6e17c81725'
    rows = load(bp, bsha, SOURCE)
    pp = BASE / 'PG5916-api35-v1/manifest.json'
    if sha(pp) != '414ebabb5791e2bd142e034f3c82d103053fec1acb3873972908474d97341d4f':
        raise ValueError('independent current35 XML/class/counter proof')
    proof = json.loads(pp.read_bytes())
    if proof['source'] != SOURCE or proof['actualExit'] != 0 or proof['tests'] != 35 or proof['targetFour100'] is not True:
        raise ValueError('actual current normal selected35 qualification')
    snapshot = W / 'pg5912-api-expression-selected35-v1/source'
    texts = {p: (ROOT / p).read_text() for p in (BUFFER, MAP, CODEC, FINGERPRINT)}
    for path in texts:
        if sha(ROOT / path) != sha(snapshot / path):
            raise ValueError('current source immutable')
    buffer_contract(texts[BUFFER], texts[CODEC], texts[FINGERPRINT]); map_contract(texts[MAP])
    owners = [(p.relative_to(ROOT).as_posix(), len(re.findall(r'\bWipingByteArrayOutputStream\b', p.read_text()))) for p in ROOT.glob('src/*/src/main/java/**/*.java')]
    reference_contract({p: n for p, n in owners if n})
    parent = subprocess.check_output([str(TC / 'jdk-25.0.4/bin/javap'), '-p', 'java.io.ByteArrayOutputStream'], text=True)
    parent_contract(parent)
    references = {
        BUFFER: selected_refs(snapshot, 'dev.codex.schubert.nk.api.idempotency.SecretBufferTest', ('supersededAndCurrentStreamStorageAreWipedAtGrowthResetAndClose', 'streamBoundsAndExceptionalExitWipeAllOwnedCapacity', 'requestOwnerClosesEveryFieldWithoutModifyingCallerCopiesOrFingerprint'), proof['xmlHashes']['dev.codex.schubert.nk.api.idempotency.SecretBufferTest']),
        MAP: selected_refs(snapshot, 'dev.codex.schubert.nk.api.file.AssetChecksumManifestTest', ('med041LiteralManifestsPreserveApprovedPathsAndHashes', 'med042MalformedAndMismatchedCountsNeverPublishPartialCatalog', 'med043PartialReadsIoFailuresAndHashMismatchesRemainRedacted', 'med044ConcurrentMatchesOwnImmutableInput'), proof['xmlHashes']['dev.codex.schubert.nk.api.file.AssetChecksumManifestTest'])}
    decisions = []
    for row in rows:
        if (row['sourcePath'], row['rule']) not in ((BUFFER, 'AvoidSynchronizedAtMethodLevel'), (MAP, 'UseConcurrentHashMap')):
            continue
        if row['status'] != 'NOT_REVIEWED_CURRENT_SOURCE' or row['sourceSha256'] != sha(ROOT / row['sourcePath']):
            raise ValueError('one genuinely unreviewed current-source diagnostic')
        reason = ('411/SS324/352: nonpublic operation-local wiping adapter must share the inherited ByteArrayOutputStream intrinsic monitor for protected buf/count with synchronized copy/size/writeTo/reset. Production has two private codec TWR scopes plus one package-private canonical TWR scope with private borrow-only helpers; all return defensive byte copies, never an escaping owner. calculate clears its canonical copy in finally. The buffer type label is not a fourth allocation. Four overrides do bounded array work, not native/blocking I/O. Replacing only these monitors would break parent consistency. Keep raw warnings; no general concurrency/performance waiver.' if row['sourcePath'] == BUFFER else 'SS333/343: this read-local parser map is populated only on its current thread, rejects duplicate paths, then constructor defensively publishes Map.copyOf. It is not a shared concurrent registry; replacing it by a concurrent map would not establish any new required concurrency contract. Explicitly rechecked after loop/index PG; no automatic old-source rationale transfer.')
        value = copy.deepcopy(row)
        value.update(status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING', priorDisposition='CONTEXT_NOT_APPLICABLE', reason=reason,
                     priorReason=reason, rawWarningRetained=True, currentWholeCaseRefs=[], currentWholeJoinPending=True,
                     currentSelectedCaseRefs=references[row['sourcePath']], selectedQualificationSha256=sha(pp), reviewSource=SOURCE,
                     reviewKind='REGULAR_STATIC_CONTRACT_REVIEW_NOT_PT_ALTERNATIVE', parentJdkSignatureSha256=hashlib.sha256(parent.encode()).hexdigest(),
                     sourceContractSha256=sha(ROOT / row['sourcePath']), historicalPtImportedAsCurrent=False)
        decisions.append(value)
    if len(decisions) != 5 or Counter(r['sourcePath'] for r in decisions) != {BUFFER: 4, MAP: 1}:
        raise ValueError('all and only four new parent-monitor and one changed-map rationale')
    result = apply_decisions(rows, decisions)
    out = BASE / 'PG5920-buffer-map-contracts-v2'; os.umask(0o077); out.mkdir()
    target = out / 'decisions.json'
    with target.open('x') as f:
        json.dump(decisions, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    value = dict(actualExit=0, source=SOURCE, baseManifestPath=bp.relative_to(ROOT).as_posix(), baseManifestSha256=bsha,
                 decisionsSha256=sha(target), rawFindings=1544, newIndividualDispositions=4, recheckedChangedPrior=1,
                 statusCounts=dict(Counter(r['status'] for r in result)), selectedQualificationSha256=sha(pp),
                 parentJdkSignatureSha256=hashlib.sha256(parent.encode()).hexdigest(), jdkSourceZipInspected=False,
                 parentEvidenceKind='ACTUAL_PINNED_JDK25_JAVAP_SIGNATURES', sourceCodeChanged=False, testExecutionsIssued=0,
                 actualBufferOwnerScopes=3, sourceReferenceCounts={p: n for p, n in owners if n},
                 executedPtAdded=0, ptAlternativeCompleted=0, wholeReplayed=False, formalAccepted=False, F03Accepted=False, vmActions=0)
    with (out / 'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(value)); print(json.dumps(dict(manifestSha256=sha(out / 'manifest.json'), decisionsSha256=sha(target))))


if __name__ == '__main__':
    main()
