"""One necessary grouped full integration: BUG1222 resource and two passed JDBC tests."""
import inspect
import json
import subprocess
import pg1528_filesystem_full_six as transport
import pg2300_jdbc_host_integration_full_six as previous

SOURCE = 'cdbc07cdf'
QUESTION = 'src/schubert-nk-web/src/main/resources/static/js/question-input-validation.js'
NODE_TEST = 'src/schubert-nk-web/src/test/javascript/question-input-validation.test.cjs'
CANDIDATE = '44aa51e79fdcf8bb154f26a51a40d1d087babc32'


def production():
    return subprocess.check_output(['git', 'rev-parse', SOURCE], cwd=transport.prior.ROOT, text=True).strip()


def validate(snapshot):
    root = transport.prior.ROOT
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=root)
    receipt = json.loads((transport.prior.W / 'pg2402-morning-observation-selected-v1/manifest.safe.json').read_bytes())
    if any(receipt.get(k) != v for k, v in {'actualExit':0,'tests':2,'FESAbortedNotRun':0,
            'classByteMismatch':0,'javacWarnings':0,'oldNativeImported':False,
            'source':'3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8'}.items()):
        raise ValueError('actual passed JDBC tests required')
    scope = ['src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization']
    if git('diff', production(), snapshot, '--', *scope):
        raise ValueError('one unchanged current grouped source required')
    changes = git('diff', '--name-only', receipt['testSource'], snapshot, '--', *scope).decode().splitlines()
    if sorted(changes) != sorted([QUESTION, NODE_TEST]):
        raise ValueError('only approved minimal JS candidate delta after selected JDBC test permitted')
    for name in [QUESTION, NODE_TEST]:
        if git('show', snapshot + ':' + name) != git('show', CANDIDATE + ':' + name):
            raise ValueError('approved two candidate files required')


def server_source(head, digest):
    raw = previous.server_source(head, digest).replace('PG2300', 'PG2404').replace('3635', '3637').replace(previous.production(), production())
    compile(raw, '<grouped question JDBC full3637>', 'exec')
    return raw


def main():
    head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=transport.prior.ROOT,text=True).strip()
    validate(head)
    raw = inspect.getsource(transport.main)
    for a, b in [('PG1528','PG2404'),('pg1528','pg2404'),('3582','3637'),('524','540'),('1637','1643')]:
        raw = raw.replace(a, b)
    raw = raw.replace('3578/523/1635 + LinuxFilesystemClassifier4 tests/one suite/two Main classes, other tests retained',
        '3635/540/1643 plus two passed JDBC tests; approved question JS resource with eight existing Node cases; Java Main unchanged')
    raw = raw.replace('SSC269 new production storage/batch dependency and required all-source regression; selected attempts failed before target tests, literal NoTests gates preserved',
        'BUG1222 approved JS resource and two new JDBC tests grouped integration; necessary fresh same-source full six, no repeat for documents/tools')
    namespace = {**transport.__dict__, 'PRODUCTION':production(), 'server_source':server_source}
    exec(compile(raw,'<grouped full current source transport>','exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
