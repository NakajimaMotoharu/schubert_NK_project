"""Ten explicit private-monitor/volatile/worker-handler reviews joined to original1939; no PT."""
import argparse
import hashlib
import json
import os
import subprocess
import zipfile
from pathlib import Path
from pg5940_private_lock_compile import ROOT, W, BASE, TC, sha
from pg6114_http_owner_qualification import SOURCE
from pg5958_private_lock_reason_review import fragment
from pg5966_api_sql_selected import source_test_names
from pg6056_expiry_read_methods import methods
from classfile_field_flags import fields
from jvm_monitor_release import check_monitor

SITES = {
 ('WebHttpAdmission', 34): 'admit atomically checks stopped/duplicate admission/ownerStopping and publishes accepting under the same private final monitor; STOP005/001002',
 ('WebHttpAdmission', 42): 'accepting observes retained admission and current external stop notification under the same private monitor; STOP005',
 ('WebHttpAdmission', 48): 'acquire combines admission check and active lease increment with refuse/drain exclusion; STOP001002/003',
 ('WebHttpAdmission', 56): 'completed checks minimum active count,decrements once and notifyAll on the identical monitor used by drain; STOP001002/003',
 ('WebHttpAdmission', 65): 'refuse disables new admission without inventing completion of existing leases; STOP001002/003',
 ('WebHttpAdmission', 76): 'drain disables admission then loops on active under same monitor;wait releases it for completed;deadline/interrupt remain unconfirmed,not success; STOP001002/003',
 ('WebLogReplayWorker', 26): 'worker publishes immutable Report reference to snapshot readers using volatile;separate AtomicLong aggregate fields do not promise a multi-field atomic snapshot; W01/temporarySqlAndRuntimeFailuresRecoverWithoutLeakingDetails',
 ('WebLogReplayWorker', 70): 'SQL/Runtime failures traverse fatal graph before failed-cycle accounting;transient retry relies on persisted lease/backoff,no provider diagnostic;hidden Error terminates without cycle credit; rerun008HiddenFatalStopsWithoutFailedCycleAndSelfJoinRejects',
 ('RevocationRetryWorker', 62): 'fixed Runtime dispatch failure traverses fatal graph before failed++;nested/direct Error reaches terminal handler without success/failed credit;row backoff remains retry authority; rerun008bTransientFailureRecoveryAndFatalTerminalNeverExposeProvider',
 ('WebRequestTrace', 63): 'immutable Optional<TopBarViewModel> display snapshot is published across request/async observers by volatile;no principal/session/token retained;REQ007/008;JMM static premise,not native race measurement'
}
CLASSES = {
 'WebHttpAdmission': 'bootstrap.WebHttpAdmission',
 'WebLogReplayWorker': 'logging.WebLogReplayWorker',
 'RevocationRetryWorker': 'revocation.RevocationRetryWorker',
 'WebRequestTrace': 'logging.WebRequestTrace'}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--qualification-sha256', required=True); args = parser.parse_args()
    qp = BASE/'PG6114-http-owner-qualification-v1/manifest.json'
    if sha(qp) != args.qualification_sha256:
        raise ValueError('actual current1939 qualification hash first')
    q = json.loads(qp.read_bytes()); folder = W/'pg6114-http-owner-qualification-v1'
    for name, key in [('manifest.safe.json', 'privateManifestSha256'), ('cases.safe.json', 'casesSha256'), ('findings.safe.json', 'findingsSha256')]:
        if sha(folder/name) != q[key]:
            raise ValueError('original artifacts and unfiltered static bytes')
    proof = json.loads((folder/'manifest.safe.json').read_bytes())
    cases = json.loads((folder/'cases.safe.json').read_bytes())
    if q['actualExit'] != 0 or q['source'] != SOURCE or (q['tests'], q['suites']) != (1939, 318):
        raise ValueError('genuine sourceacb1939/318,never another source result')
    if {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')} != proof['allSourceHashes']:
        raise ValueError('all851 current Main inputs still match original qualification')
    jar = W/'pg6112-http-owner-selected-v1/source/src/schubert-nk-web/target/schubert-nk-web-0.1.0-SNAPSHOT.jar'
    def disassemble(short):
        return methods(subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'), '-p', '-c', '-s', '-classpath', str(jar), 'dev.codex.schubert.nk.web.'+short], text=True))
    with zipfile.ZipFile(jar) as archive:
        if {'web:'+name: hashlib.sha256(archive.read(name)).hexdigest() for name in archive.namelist() if name.endswith('.class')} != {
                k: v for k, v in proof['allPhysicalMainSha256'].items() if k.startswith('web:')}:
            raise ValueError('every actual Web Jar class byte matches qualified original1939')
        field_flags = {name: fields(archive.read('dev/codex/schubert/nk/web/'+short.replace('.', '/')+'.class')) for name, short in CLASSES.items()}
    if (field_flags['WebHttpAdmission'][b'lock']['flags'], field_flags['WebLogReplayWorker'][b'lastReport']['flags'], field_flags['WebRequestTrace'][b'retainedActor']['flags']) != (0x12, 0x42, 0x42):
        raise ValueError('private final monitor and two actual private volatile publication fields')
    admission = disassemble(CLASSES['WebHttpAdmission']); synchronized = []
    for signature, block in admission.items():
        if 'monitorenter' in block:
            check_monitor(block, 3 if ' acquire(' in signature else 2)
            for state in ('retainedAccepting', 'stopping', 'active'):
                if '// Field '+state+':' in block and not block.index('monitorenter') < block.index('// Field '+state+':') < block.rindex('monitorexit'):
                    raise ValueError('state access outside the reviewed monitor')
            synchronized.append(signature)
        elif any('// Field '+s+':' in block for s in ('retainedAccepting', 'stopping', 'active')):
            raise ValueError('no unreviewed state access outside monitor methods')
    if len(synchronized) != 6 or sum('java/lang/Object.wait:' in x for x in admission.values()) != 1 or sum('java/lang/Object.notifyAll:' in x for x in admission.values()) != 1:
        raise ValueError('six monitor scopes with one same-monitor wait/notify pair')
    worker_facts = []
    for name, helper in [('WebLogReplayWorker', 'session.SessionStoreException'), ('RevocationRetryWorker', 'revocation.RevocationRetryCoordinator')]:
        blocks = disassemble(CLASSES[name]); run = next(v for k, v in blocks.items() if ' run(' in k)
        target = 'SessionStoreException.preserveFatal:' if name == 'WebLogReplayWorker' else 'RevocationRetryCoordinator.preserveFatal:'
        failed = '// Field failedCycles:' if name == 'WebLogReplayWorker' else '// Field failed:'
        if not run.index(target) < run.index(failed):
            raise ValueError('fatal detection precedes transient failure credit')
        fatal = next(v for k, v in disassemble(helper).items() if ' preserveFatal(' in k)
        if not all(s in fatal for s in ('java/util/IdentityHashMap', 'java/util/Set.add:', 'java/lang/Error', 'java/lang/Throwable.getCause:', 'java/lang/Throwable.getSuppressed:', 'athrow')):
            raise ValueError('actual identity-cycle guarded cause/suppressed fatal traversal')
        worker_facts.append(dict(className=name, runCodeSha256=hashlib.sha256(run.encode()).hexdigest(), fatalCodeSha256=hashlib.sha256(fatal.encode()).hexdigest()))
    rows = json.loads((folder/'findings.safe.json').read_bytes()); reviews = []; counts = {}; found = set()
    for row in rows:
        key = (Path(row['sourcePath']).stem, int(row['beginline']))
        if key not in SITES:
            continue
        if key in found or row['rule'] not in ('AvoidSynchronizedStatement', 'AvoidUsingVolatile', 'AvoidCatchingGenericException'):
            raise ValueError('one actual specified non-thread warning per reviewed site')
        found.add(key); name = key[0]; path = ROOT/row['sourcePath']
        if sha(path) != row['sourceSha256'] or proof['allSourceHashes'][row['sourcePath']] != sha(path):
            raise ValueError('source/hash matches original compiled1939')
        cls = 'dev.codex.schubert.nk.web.'+CLASSES[name]+'Test'
        test = ROOT/'src/schubert-nk-web/src/test/java'/(cls.replace('.', '/')+'.java')
        expected = source_test_names(test)
        actual = [c for c in cases if c['className'] == cls and c['module'] == 'web']
        if {c['method'] for c in actual} != expected or len(actual) != len(expected) or any(c['source'] != SOURCE or c['result'] != 'PASS_ORIGINAL_XML' for c in actual):
            raise ValueError('every declared independent fixture joins the genuine original XML')
        owner = 'web:dev/codex/schubert/nk/web/'+CLASSES[name].replace('.', '/')
        family = {k: v for k, v in proof['allActualCounters'].items() if k == owner+'.class' or k.startswith(owner+'$')}
        if owner+'.class' not in family or any(v.get('missed', 0) for c in family.values() for v in c.values()):
            raise ValueError('actual reviewed class family has measured coverage gaps;do not invent closed counters')
        counts[name] = family
        reviews.append(dict(row, source=SOURCE, status='REQUIRED_CONTRACT', reason='1289 individual review: '+SITES[key],
            diagnosticFragment=fragment(path.read_text(), row), rawWarningRetained=True,
            declaredIndependentTests=[dict(className=cls, module='web', sourceSha256=sha(test), methods=sorted(expected))],
            original1939CaseRefs=actual, actualClassCounters=family, currentWholeCaseRefs=[], currentWholeJoinPending=True,
            formalAccepted=False, testsExecutedByReview=0, ptAlternativeCompleted=0))
    if found != set(SITES) or len(reviews) != 10:
        raise ValueError('all ten explicit sites present,not a blanket rule exemption')
    value = dict(actualExit=0, source=SOURCE, reviewed=10, newlyReviewed=10, statusCounts={'REQUIRED_CONTRACT': 10},
        qualificationSha256=sha(qp), currentRawFindings=q['pmdRawFindings'], privateMonitorMethods=synchronized,
        workerFacts=worker_facts, actualClassCounters=counts, currentWholeJoinPending=True,
        testsExecuted=0, newPtPassesClaimed=0, dynamicOomExecuted=False, rawWarningsRemoved=0,
        actualRuntimeProven=False, F03Accepted=False, formalAccepted=False, ptAlternativeCompleted=0)
    os.umask(0o077); out = BASE/'PG6122-web-lifecycle-review-v1'; out.mkdir()
    for name, content in [('reviews.json', reviews), ('manifest.json', value)]:
        with (out/name).open('x') as stream:
            json.dump(content, stream, ensure_ascii=False, indent=2); stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    print(json.dumps(dict(actualExit=0, reviewed=10, manifestSha256=sha(out/'manifest.json'), reviewsSha256=sha(out/'reviews.json'))))


if __name__ == '__main__':
    main()
