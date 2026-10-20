"""Original JVM ownership/phase order and public ABI inspection,no Production invocation."""
import json
import os
import subprocess
import zipfile
from pg5940_private_lock_compile import W, BASE, TC, sha
from pg6132_api_management_stop_qualification import SOURCE
from pg6056_expiry_read_methods import methods
from pg6116_http_owner_order import prepared_owner
from pg6084_web_factory_order import instructions
from classfile_field_flags import fields

CLASS = 'dev.codex.schubert.nk.api.bootstrap.ApiManagementServer'


def main():
    qp = BASE/'PG6132-api-management-stop-qualification-v1/manifest.json'
    if sha(qp) != 'a3f833f1b349e7d701e1f4e4abd790ce166794e5479a2c88eb39830dcb38488d':
        raise ValueError('genuine current23 original XML/1667/static first')
    q = json.loads(qp.read_bytes())
    if q['actualExit'] != 0 or q['source'] != SOURCE or (q['tests'], q['suites'], q['physicalMain']) != (23, 9, 1667):
        raise ValueError('one exact source/current23 qualification')
    old = W/'pg6112-http-owner-selected-v1/source/src/schubert-nk-api/target/schubert-nk-api-0.1.0-SNAPSHOT.jar'
    jar = W/'pg6130-api-management-stop-green-v1/source/src/schubert-nk-api/target/schubert-nk-api-0.1.0-SNAPSHOT.jar'
    def read(path, flags):
        return subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'), *flags, '-classpath', str(path), CLASS], text=True)
    with zipfile.ZipFile(jar) as z:
        body = z.read(CLASS.replace('.', '/')+'.class')
    flag = fields(body)
    if any(flag[n.encode()]['flags'] != value for n, value in [('server', 0x12), ('stopLock', 0x12), ('stopping', 0x12), ('closed', 2), ('serverStopped', 2)]):
        raise ValueError('private final owner/lock/atomic publication port and lock-only plain phase fields')
    code = methods(read(jar, ['-p', '-c', '-s']))
    proof = prepared_owner(code, CLASS, ['healthy', 'information', 'executor', 'promoted', 'promotionAttempted', 'stopping', 'stopLock'], '$Factory.create:', 'server')
    abi = read(jar, ['-public', '-s'])
    if abi != read(old, ['-public', '-s']):
        raise ValueError('public ABI unchanged')
    prior = methods(read(old, ['-p', '-c', '-s']))
    exported = lambda d: {k for k in d if not k.startswith('  private ') and k != '  static {};'}
    if not exported(prior) <= exported(code) or exported(code)-exported(prior) != {'  void closeWithin(java.time.Duration);'}:
        raise ValueError('all prior package ABI retained;one specified internal remaining-budget method only')
    close = code['  void closeWithin(java.time.Duration);']; ops = instructions(close)
    def one(opcode, token):
        positions = [i for i, (_, op, arg) in enumerate(ops) if op == opcode and token in arg]
        if len(positions) != 1:
            raise ValueError('one actual reviewed phase instruction: '+token)
        return positions[0]
    sequence = [one('invokevirtual', 'ReentrantLock.tryLock:'), one('invokevirtual', 'HttpServer.stop:'),
                one('putfield', '// Field serverStopped:Z'), one('invokevirtual', 'ThreadPoolExecutor.shutdownNow:'),
                one('invokevirtual', 'ThreadPoolExecutor.awaitTermination:'), one('putfield', '// Field closed:Z')]
    if sequence != sorted(sequence) or len(set(sequence)) != 6:
        raise ValueError('lock/confirmed stop/phase marker/shutdown/actual join/closed completion order')
    if [(k, v.count('// Field closed:Z'), v.count('// Field serverStopped:Z')) for k, v in code.items() if '// Field closed:Z' in v or '// Field serverStopped:Z' in v] != [('  void closeWithin(java.time.Duration);', 2, 2)]:
        raise ValueError('phase state accessed only in the private-lock-owned close method')
    if close.count('java/lang/System.nanoTime:') != 3 or 'ReentrantLock.unlock:' not in close:
        raise ValueError('same monotonic budget sampled before lock and actual join;finally unlock retained')
    value = dict(actualExit=0, source=SOURCE, qualificationSha256=sha(qp), preparedOwner=proof,
        phaseOrderInstructionIndices=sequence, publicAbiUnchanged=True, addedPackageMethod='closeWithin(Duration)',
        phaseFieldsOnlyCloseWithin=True, monotonicSamples=3, testsExecuted=0, additionalBuildsIssued=0,
        fullCurrentWholePending=True, formalAccepted=False, nativeQualified=False, ptAlternativeCompleted=0)
    os.umask(0o077); out = BASE/'PG6136-api-management-stop-order-v1'; out.mkdir()
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, source=SOURCE, phaseOrder=sequence, manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
