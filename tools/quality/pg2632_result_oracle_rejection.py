"""Corrected real Header test rejects each synthetic canary; no Production PT credit."""
import inspect
from pyflakes.api import check
import pg2630_result_oracle_canary as previous


def server():
    raw = previous.SERVER.replace('PG2630-canary-v2', 'PG2632-canary-v1')
    old = "require(result.returncode==0 and b'CANARY_STARTED=1 SUCCEEDED=1 FAILED=0'in result.stdout)"
    if raw.count(old) != 1:
        raise ValueError('one exact synthetic expectation boundary required')
    raw = raw.replace(old, """
 if label=='ORIGINAL':
  require(result.returncode==0 and b'CANARY_STARTED=1 SUCCEEDED=1 FAILED=0'in result.stdout)
 else:
  require(result.returncode==1 and b'CANARY_STARTED=1 SUCCEEDED=0 FAILED=1'in result.stdout and b'CANARY_FAILURE_CLASS=org.opentest4j.AssertionFailedError'in result.stdout)""")
    raw = raw.replace("'falseNegativesDemonstrated':3", "'mutationsRejected':3,'baselineRealTestPassed':True")
    if check('INPUT={}\n' + raw, '<corrected synthetic rejection namespace>'):
        raise ValueError('whole namespace required')
    compile(raw, '<corrected canary rejection server>', 'exec')
    return raw


def main():
    raw = inspect.getsource(previous.main).replace('PG2630-canary-v2', 'PG2632-canary-v1')
    raw = raw.replace('*FILES[:2]', 'FILES[1]').replace('original uncorrected code and test required', 'unchanged Production ResultCode required')
    ns = {**previous.__dict__, 'SERVER': server(), 'SLOT': 'pg2632-result-oracle-rejection-v1'}
    exec(compile(raw, '<fixed corrected oracle transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
