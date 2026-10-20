"""Original qualified JVM close completion/serialization proof, no production execution."""
import json
import os
import re
import subprocess
import sys
from pg5940_private_lock_compile import W, BASE, TC, sha
from pg6056_expiry_read_methods import methods
from pg6084_web_factory_order import instructions
from pg6146_api_jms_close_qualification_v2 import SOURCE

OWNERS = {
    'inbound.SyncRequestConsumers': ('closeLock', 'jakarta/jms/JMSContext.close:'),
    'inbound.WebLogConsumers': ('closeLock', 'jakarta/jms/JMSContext.close:'),
    'inbound.QuestionWorkConsumers': ('lock', 'jakarta/jms/JMSContext.close:'),
    'inbound.ApiMessagingRuntime': ('closeLock', 'Method closeGroups:'),
    'config.ApiBrokerContexts': ('stateLock', 'java/lang/AutoCloseable.close:')}


def close_proofs(jars):
    def read(jar, cls, *flags):
        return subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'), *flags, '-classpath', str(jar), cls], text=True)
    proof = []
    for name, (lock, operation) in OWNERS.items():
        cls = 'dev.codex.schubert.nk.api.messaging.'+name
        if read(jars[0], cls, '-public', '-s') != read(jars[1], cls, '-public', '-s'):
            raise ValueError('all five existing public ABI unchanged')
        code = methods(read(jars[1], cls, '-p', '-c', '-s'))
        close = code['  public void close();']
        ops = instructions(close)
        def positions(opcode, token):
            return [i for i, (_, op, arg) in enumerate(ops) if op == opcode and token in arg]
        locking = positions('invokevirtual', 'ReentrantLock.lock:')
        completed = positions('putfield', '// Field closed:Z')
        actual = [i for i, (_, _, arg) in enumerate(ops) if operation in arg]
        if len(locking) != 1 or len(actual) != 1 or len(completed) != 1 or not locking[0] < actual[0] < completed[0]:
            raise ValueError('one lock/actual child close/only then closed completion')
        if ('// Field '+lock+':') not in close or 'ReentrantLock.unlock:' not in close:
            raise ValueError('exact private owner lock/finally unlock retained')
        touched = [(k, v.count('// Field closed:Z')) for k, v in code.items() if '// Field closed:Z' in v]
        if touched != [('  public void close();', 2)]:
            raise ValueError('closed phase accessed only in locked close, not publication flag')
        proof.append(dict(className=cls, publicAbiUnchanged=True, lockBeforeActualBeforeCompleted=[locking[0], actual[0], completed[0]], closedOnlyLockedClose=True))
    return proof


def main(expected_sha):
    if not re.fullmatch('[0-9a-f]{64}', expected_sha):
        raise ValueError('exact independent qualification hash required')
    qp = BASE/'PG6146-api-jms-close-qualification-v2/manifest.json'
    if sha(qp) != expected_sha:
        raise ValueError('immutable original v2 qualification required')
    q = json.loads(qp.read_bytes())
    if q['actualExit'] != 0 or q['source'] != SOURCE or (q['tests'], q['suites'], q['physicalMain']) != (1950, 320, 1667):
        raise ValueError('genuine all current1950 original XML/8511667 first')
    jars = [W/(run+'/source/src/schubert-nk-api/target/schubert-nk-api-0.1.0-SNAPSHOT.jar') for run in (
        'pg6130-api-management-stop-green-v1', 'pg6144-api-jms-close-selected-v2')]
    proof = close_proofs(jars)
    value = dict(actualExit=0, source=SOURCE, qualificationSha256=expected_sha, owners=proof,
        testsExecuted=0, buildsIssued=0, brokerFactoryPreparationPending=True,
        nativeRetentionPending=True, fullCurrentWholePending=True, formalAccepted=False,
        nativeQualified=False, ptAlternativeCompleted=0)
    os.umask(0o077); out=BASE/'PG6148-api-jms-close-order-v2'; out.mkdir()
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, source=SOURCE, owners=len(proof), manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__':
    main(sys.argv[1])
