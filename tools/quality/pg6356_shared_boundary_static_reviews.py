"""35 individually read shared config/JDBC/ownership spans; no credentials or runtime access."""
import inspect
import json
import os
import pg6352_ordinary_boundary_static_reviews as previous

G = previous.G
C = 'CloseResource'
SPEC = {
    'ApiProcessLifetime': {(27, 'AvoidUsingVolatile'): (1, 'installed records hook registration visibility; install and outer resource-close remain the owning lifecycle path, while the hook only notifies and waits. The flag is not a lock/atomic acquisition protocol or proof that actual API resources closed. Existing independent component lifetime cases are associated, not replayed.')},
    'InspectorProcess': {
        (160, C): (1, 'Loaded optional credential material transfers to the operation-local OwnedKeys map before copyKey. Any later failure unwinds the surrounding owner and wipes prior copies/materials; optional absence owns nothing. No actual credential is read in this source review.'),
        (195, C): (1, 'Map-held InspectorAesCredential values are operation-owned, explicitly closed after byte-copy wipe, then both maps cleared. The outer operation TWR owns this aggregate; it is not an exported or unclosed credential resource.')},
    'TransferStartupProbe': {
        (85, G): (1, 'The outer held-directory probe StorageIo/RTE becomes fixed UNAVAILABLE after owned diagnostic cleanup/finally. It cannot certify a ready root from failed write/publish/verify/close. Existing capability and exclusive diagnostic UUID guards remain required.'),
        (119, G): (1, 'Failure deleting an attempt-owned part records failed=true but still attempts other owned cleanup and directory sync, then rejects. No failed delete is treated as normal absence or startup readiness.'),
        (139, G): (1, 'Ready cleanup first verifies the held diagnostic file identity/content; failure preserves changed/unreadable evidence, marks unavailable and still syncs. It never deletes a business ready file or infers cleanup from a missing response.'),
        (145, G): (1, 'Diagnostic directory-sync failure retains unavailable even if prior deletes returned. Aggregation allows remaining owned cleanup attempts but cannot manufacture successful durable startup probe.')},
    'ApiNonSecretConfig': {
        (124, G): (1, 'Untrusted YAML parse/type/value Runtime failures become fixed invalid configuration, not normal fallback. Allowed key/value types and interpolation/newline checks remain explicit; no raw YAML/provider detail or credential becomes output.'),
        (170, G): (1, 'Path Runtime failure rejects configuration after absolute/disjoint asset/transfer checks. It never substitutes a working directory or overlapping path and does not mutate the filesystem.')},
    'WebNonSecretConfig': {
        (117, G): (1, 'YAML parse/type/value Runtime failure rejects the whole nonsecret config with a fixed message after fixed-key/type/interpolation checks. Empty mapping fallback is limited to explicit blank document, not parse failure.'),
        (165, G): (1, 'Configured path Runtime failure rejects rather than selecting fallback assets. Fixed absolute asset-root and preceding numeric wait/stream bounds stay independent; no path or service operation is performed by this review.')},
    'SchemaHistoryAdmission': {
        (87, C): (1, 'Acquired history statement enters direct try/finally immediately, before nonnull/timeout/query. It closes once after the nested ResultSet even on projection failure; the admitted Connection remains borrowed.'),
        (92, C): (1, 'History ResultSet enters its own direct try/finally before required/next/column reads and closes once before statement close. Schema evidence is observed row values, not copied expected success.'),
        (112, G): (2, 'Both unchecked provider row/projection failures retain primary across actual owned ResultSet close, with JdbcAdmissionFailures known/unknown ranking. Full rank/version/type/script/checksum/success and end-of-rows checks precede immutable result publication.'),
        (123, G): (2, 'Both unchecked query/row-close failures retain primary until Statement close, preserving fixed-secret-free secondary policy. Borrowed Connection is never closed/configured and failed history does not admit startup.')},
    'ServiceDatabaseAdmission': {
        (52, C): (1, 'Local identity-query Statement is immediately protected by finally before nonnull/query. Nested row ownership closes before statement; caller still owns Connection on every admission result.'),
        (59, G): (2, 'Both unchecked identity-row failures retain primary before ResultSet finally close under JdbcAdmissionFailures. Exact effective/login role/database, nonrecovery and one-row predicates must all pass before return.'),
        (71, G): (2, 'Both unchecked query/row-close failures retain primary through Statement close; known SQL errors are fixed unavailable, unknown identity is preserved with fixed secondary. No role grant or real DB connection is attempted here.')},
    'ServiceDatabaseSource': {
        (88, G): (2, 'Both unchecked admission failures close the just-acquired unreturned physical connection via discard, then rethrow the original according to SS343 known/unknown policy. Connection transfer occurs only on normal admission; properties clear in finally and source password remains owned until source close.'),
        (107, G): (2, 'Both unchecked discard-close failures follow the specified SQLException-versus-unknown precedence. Unknown primary gets only fixed unavailable secondary, never raw provider/self-suppression; known SQL yields to unknown cleanup. This is not ordinary JMS fatal ranking or proof of physical close.')},
    'ServiceCredentialSet': {(53, G): (2, 'Both unchecked partial-load failures wipe/close all material already owned by the fixed catalog maps before rethrow. Reader/root lifetime remains borrowed. Current synthetic fixtures cover failure/erasure; this source reason does not access or certify actual key files.')},
    'InspectorAesCredential': {(56, 'NullAssignment'): (1, 'decoded=null is an explicit ownership transfer only after constructing the returned credential owner. Finally wipes input/encoded and any still-local decoded bytes on failure, but must not wipe the successfully transferred live key. Nullable local is not a null successful return.')},
    'FixedNativeCoverageCheckpoint': {(116, 'AvoidSynchronizedStatement'): (1, 'Private lock serializes point validation and attempted.add before agent/export I/O. Failed/unknown capture consumes the attempt and cannot be retried as new evidence. A complete real point/session/class stream remains independently qualified; the synchronized source reason is not native coverage proof.')},
    'NativeCoveragePrivateFile': {(436, 'AssignmentInOperand'): (1, 'count+=n is evaluated only after n>0 and immediately checked against the pinned size before digest update. EOF additionally requires exact count and unchanged channel size; zero/oversize/truncated reads fail rather than spin or certify a partial stream. No private file is opened by this review.')},
    'ReleasePayloadVerification': {(381, 'AssignmentInOperand'): (1, 'readLine assignment advances one owned BufferedReader until actual EOF for the pinned Flyway UTF8 CRC32 algorithm. Only the first-line BOM is removed and line endings are deliberately ignored; fixed independent checksum fixtures, not production-generated expectations, are associated below.')},
    'ServiceStartupAdmission': {(190, G): (2, 'Both unchecked readiness delegate failures permanently poison the consumed one-attempt ReadyOnce before rethrow. released=true is published only on normal delegate return; information access is closed after attempt. No readiness token or authority is issued by this source review.')},
    'SystemManagerObservation': {(166, 'NullAssignment'): (1, 'pending=null discards only an observation Session whose own closed() confirms closure. Unknown/unclosed pending handle remains retained for explicit ownership, not overwritten by another observation. This source assignment is not a system manager query or live closure evidence.')}
}
TESTS = {
    'ApiProcessLifetime': ['api.bootstrap.ApiProcessLifetimeTest'],
    'InspectorProcess': ['api.maintenance.InspectorProcessTest'],
    'TransferStartupProbe': ['api.storage.TransferStartupProbeTest'],
    'ApiNonSecretConfig': ['api.bootstrap.ApiNonSecretConfigTest'],
    'WebNonSecretConfig': ['web.bootstrap.WebNonSecretConfigTest'],
    'SchemaHistoryAdmission': ['api.maintenance.SchemaHistoryAdmissionTest'],
    'ServiceDatabaseAdmission': ['api.maintenance.ServiceDatabaseAdmissionTest'],
    'ServiceDatabaseSource': ['api.bootstrap.ServiceDatabaseSourceTest'],
    'ServiceCredentialSet': ['api.file.ServiceCredentialSetTest'],
    'InspectorAesCredential': ['api.maintenance.InspectorAesCredentialTest'],
    'FixedNativeCoverageCheckpoint': ['bootstrap.FixedNativeCoverageCheckpointTest'],
    'NativeCoveragePrivateFile': ['bootstrap.NativeCoveragePrivateFileTest'],
    'ReleasePayloadVerification': ['bootstrap.ReleasePayloadVerificationTest'],
    'ServiceStartupAdmission': ['bootstrap.ServiceStartupAdmissionTest'],
    'SystemManagerObservation': ['bootstrap.SystemManagerObservationTest']
}


def calculate():
    scope = {**vars(previous), 'SPEC': SPEC, 'TESTS': TESTS,
        'INPUT': previous.BASE/'PG6354-batch-database-static-review-v1/manifest.json',
        'INPUT_SHA': '33d467098f3881a2a92b4de30992f921c51f312eddd572a2bad2c8e2b231805a'}
    raw = inspect.getsource(previous.calculate)
    for before, after in (('len(decisions) != 21', 'len(decisions) != 35'), ('all21 explicitly', 'all35 explicitly'),
                          ('reviewed=21', 'reviewed=35'), ('296 other unreviewed', '226 other unreviewed')):
        if raw.count(before) != 1:
            raise ValueError('explicit35 shared source reader '+before)
        raw = raw.replace(before, after, 1)
    exec(compile(raw, '<35 individually read shared ownership/configuration spans>', 'exec'), scope)
    return scope['calculate']()


def main():
    rows, value = calculate(); os.umask(0o077); out = previous.BASE/'PG6356-shared-boundary-static-review-v1'; out.mkdir()
    for name, item in (('decisions.json', rows), ('manifest.json', value)):
        if name == 'manifest.json':
            value['decisionsSha256'] = previous.sha(out/'decisions.json')
        with (out/name).open('x') as f:
            json.dump(item, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, reviewed=35, statusCounts=value['statusCounts'], manifestSha256=previous.sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
