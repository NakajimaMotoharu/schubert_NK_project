"""Independent fixed maximum diagnostic through the qualified private compiler engine."""
import inspect
import sys

import pg3340_concurrent_exec_oracle as engine

FILES = ['src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/file/LargeResultRecordCodecTest.java',
         'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/file/LargeResultDescriptor.java',
         'tools/quality/vm/050_s1/ExecOracleCanaryLauncher.java']


def mutate(raw):
    for old, new in [('MAXIMUM_RECORD_COUNT = 10_000;', 'MAXIMUM_RECORD_COUNT = 9_999;'),
                     ('MAXIMUM_BYTE_LENGTH = 48_000_000L;', 'MAXIMUM_BYTE_LENGTH = 47_995_200L;')]:
        engine.require(raw.count(old) == 1 and new not in raw, 'exact approved maximum mutation anchors required')
        raw = raw.replace(old, new)
    return raw


def server():
    raw = engine.SERVER.replace('schubert-nk-storage', 'schubert-nk-protocol')
    raw = raw.replace('dev.codex.schubert.nk.storage.LinuxProcessExecTest', 'dev.codex.schubert.nk.protocol.file.LargeResultRecordCodecTest')
    raw = raw.replace('LinuxProcessExecTest.java', 'LargeResultRecordCodecTest.java').replace('LinuxProcessExec.java', 'LargeResultDescriptor.java')
    anchor = "[('NORMAL_LITERAL','opsExec001LiteralVectorsAndArenaLifetime',False),('NORMAL_CONCURRENT','opsExec007ConcurrentInputsRemainIndependent',False),('COMMON_WRONG_CONCURRENT','opsExec007ConcurrentInputsRemainIndependent',True)]"
    engine.require(raw.count(anchor) == 1, 'exact fixed diagnostic vector table required')
    return raw.replace(anchor, "[('NORMAL_MAXIMUM','largeResultMaximum',False),('LOWERED_MAXIMUM','largeResultMaximum',True)]")


def main(phase):
    raw = inspect.getsource(engine.main).replace("'PG3340-exec-oracle-'", "'PG3346-large-result-oracle-'").replace("['jarHashes']['storage']", "['jarHashes']['protocol']")
    namespace = {**engine.__dict__, 'FILES': FILES, 'SERVER': server(), 'mutate': mutate}
    # The transmitted function must be standalone, not depend on a host module alias.
    mutation = inspect.getsource(mutate).replace('engine.require(', 'require(')
    raw = raw.replace('inspect.getsource(f) for f in [require, mutate, fixed_jdk, launcher_path]',
                      'mutation if f is mutate else inspect.getsource(f) for f in [require, mutate, fixed_jdk, launcher_path]')
    namespace['mutation'] = mutation
    exec(compile(raw, '<fixed maximum private diagnosis transport>', 'exec'), namespace)
    return namespace['main'](phase)


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1] if len(sys.argv) == 2 else ''))
