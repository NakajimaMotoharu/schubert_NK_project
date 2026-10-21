"""Source-only normal Backup boundaries; never actual recovery, retirement or admission."""
import inspect
import json
import os
import pg6394_startup_static_reviews as engine
from pg6414_web_frame_pending_qualification import original_source

G = engine.G
SPEC = {
    'BackupArtifactVerifier': {
        (566, 'AvoidInstanceofChecksInCatchClause'): (1, 'The typed StorageIoException reason is retained only in the explicit force-verification mode; every other checked directory or unsupported-operation failure becomes fixed unavailable. The catch never grants admission, repairs storage or consumes a failed-cohort artifact. Both owned byte arrays are zeroed and the lock is released by enclosing finally blocks. This is source applicability, not an actual Backup authenticity proof.')},
    'CleanupBackupAdmission': {
        (68, G): (2, 'Unchecked transaction-observation failures run the bounded rollback recovery and then preserve the primary identity. A failed rollback cannot restore autoCommit and thereby accidentally commit. Successful observation rolls back the read-only FOR UPDATE work; neither this method nor the catch issues DELETE, commit or a permit. Caller disposal of a failed borrowed connection remains a precondition.'),
        (92, G): (2, 'Unchecked rollback/restoration failures are not successful recovery: an unknown primary remains primary with a fresh fixed suppressed marker; known-primary/unknown-cleanup propagates the cleanup; known repository failure is mapped to fixed unavailable. No raw provider message is published and no connection is certified reusable after failure.'),
        (97, 'AvoidInstanceofChecksInCatchClause'): (1, 'Only the typed repository failure is converted to the fixed checked unavailable result; arbitrary RuntimeException/Error is not mislabeled as a known repository outcome. The preceding unknown-primary branch preserves that original identity. Tests explicitly distinguish known and unknown primary/cleanup combinations; actual DB ownership is not proven by this review.')},
    'MorningBackupArtifacts': {
        (548, G): (2, 'The bounded file-read buffer is zeroed on checked or unchecked failure and the same failure is rethrown. The catch neither treats partial bytes as complete nor hides a failed close. Successful return requires all requested bytes plus exact EOF/size; enclosing FileChannel ownership remains try-with-resources.'),
        (563, 'AssignmentInOperand'): (1, 'The single read result is assigned once and compared with EOF before digest update. Zero progress is explicitly rejected, the total read count and final size must match the initial size, and the digest byte buffer is zeroed in finally. This streaming pattern avoids a second consuming read; it does not certify concurrent-file immutability beyond the surrounding verification contract.')},
    'MorningBackupUnitCycle': {
        (393, G): (2, 'Once normal Backup start may have been delivered, IOException/RuntimeException/Error cannot authorize normal parent unwind. Any uncertain receipt, original/request check, quiescence or retirement enters the existing non-returning retain port. Outstanding state is cleared only after all barriers; source review does not prove that a real child stopped or retire an actual intent.'),
        (474, G): (2, 'Within the normal child handoff, receipt/outcome/stop uncertainty invokes retain instead of returning a forged terminal receipt. The one-start CAS, fixed budget and gate checks remain in their original order. This applies to ordinary Backup/Cleanup/Expiry contract source, not failed-cohort recovery or an actual Unit action.'),
        (501, G): (2, 'After advisory reacquisition, completion, repeated same-terminal checks and retirement barriers precede clearing outstanding. Any unchecked/checked uncertainty retains the owner rather than exposing a success or moving to another child. This review executes no retire operation and supplies no native lifetime proof; those dependencies remain held or separately required.')}
}
TESTS = {
    'BackupArtifactVerifier': ['batch.file.BackupArtifactVerifierTest'],
    'CleanupBackupAdmission': ['batch.file.CleanupBackupAdmissionTest'],
    'MorningBackupArtifacts': ['batch.file.MorningBackupPreparationTest', 'batch.file.MorningBackupStageTest'],
    'MorningBackupUnitCycle': ['batch.platform.MorningBackupUnitCycleTest']
}


def calculate():
    scope = {**vars(engine), 'SPEC': SPEC, 'TESTS': TESTS, 'original_source': original_source,
        'PLAN': engine.BASE/'PG6426-api-thread-context-v1/manifest.json',
        'PLAN_SHA': '06001b6f4cfb66e4c1a4cc3f85969dcf1e2f67f78bed9cb31fd538ec3e757a1b'}
    raw = inspect.getsource(engine.calculate)
    for before, after in (
        ('PG6384-web-fatal-callback-retry-qualification-v1', 'PG6414-web-frame-pending-qualification-v1'),
        ('pg6384-web-fatal-callback-retry-qualification-v1', 'pg6414-web-frame-pending-qualification-v1'),
        ('7896c2a6d7d650cf2a67f9270e0ad039360c7a5ba073cf84685adddc578295f7', 'f214986209f003c92248644f55e617042af273ab6b652a2e753dffceda30498f'),
        ('len(decisions) != 19', 'len(decisions) != 15'), ('all19 individually', 'all15 individually'),
        ('reviewed=19', 'reviewed=15'), ('rawFindings=1355', 'rawFindings=1358'),
        ('161 other current', '119 other current'), ('14 prior missing', '12 prior missing'),
        ('current4052 whole', 'current4054 whole')):
        if before not in raw:
            raise ValueError('explicit current1358/fifteen-span binding '+before)
        raw = raw.replace(before, after)
    exec(compile(raw, '<fifteen normal Backup source applicability spans>', 'exec'), scope)
    return scope['calculate']()


def main():
    rows, value = calculate(); os.umask(0o077); out = engine.BASE/'PG6428-backup-normal-static-review-v1'; out.mkdir()
    for name, item in (('decisions.json', rows), ('manifest.json', value)):
        if name == 'manifest.json':
            value['decisionsSha256'] = engine.sha(out/'decisions.json')
        with (out/name).open('x') as f:
            json.dump(item, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, reviewed=15, statusCounts=value['statusCounts'], manifestSha256=engine.sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
