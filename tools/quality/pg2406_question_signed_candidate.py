"""Host-only same-Java, one-approved-resource candidate; never deploys or runs business.

PT-OPS-PG2406-001: SS343 signed187 exact artifact/byte delta; BUG1222.
Historical four Java differences versus 0fd remain independently classified by
the full qualifier. The actual candidate delta versus deployed 3b7f is zero Main.
"""
import hashlib
import inspect
import zipfile
import pg1638_api_signed_candidate as prior
import pg2126_metadata_signed_candidate as historical
from pg2404_question_jdbc_full_six import production

W, P, T = prior.W, prior.P, prior.T
OLD = W / 'pg2126-release-v1'
NEXT = W / 'pg2406-release-v1'
FROZEN = W / 'pg2406-frozen-six-v1'
SIG = P / 'pg2406-manifest-v1.sig'
OLD_SOURCE = '3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8'
OLD_BOM = '62213f357c9dab3b00b557549426b091a03ace6557a62f4410999a02028a332c'
RESOURCE = 'static/js/question-input-validation.js'
BEFORE_JS = 'f181b9920dc95b580764a5266dcdc2294b678181dd20165b6cfde495d0a9709e'
AFTER_JS = '742ebf22201034123b5e96fbb82b9fe25d0f8a5f0260651a42c011389a10cafa'


def validate_gate(outer, source):
    raw = inspect.getsource(historical.validate_gate).replace("'tests':3631", "'tests':3637")
    namespace = {**historical.__dict__}
    exec(compile(raw, '<exact new grouped host gate>', 'exec'), namespace)
    return namespace['validate_gate'](outer, source)


def verify_delta(before, after):
    if type(before) is not dict or type(after) is not dict or set(before) != set(prior.MODULES) or set(after) != set(before):
        raise ValueError('fixed six current Main inventories required')
    if any(before[m] != after[m] for m in before) or sum(len(v) for v in after.values()) != 1643:
        raise ValueError('all1643 actual Java Main bytes unchanged required')
    return 1643


def verify_web_resource(before, after):
    def inventory(path):
        with zipfile.ZipFile(path) as jar:
            names = jar.namelist()
            if len(names) != len(set(names)):
                raise ValueError('duplicate jar member refused')
            return {n: hashlib.sha256(jar.read(n)).hexdigest() for n in names if not n.endswith('/')}
    a, b = inventory(before), inventory(after)
    if set(a) != set(b) or {n for n in a if a[n] != b[n]} != {RESOURCE}:
        raise ValueError('one approved literal resource delta only required')
    if a[RESOURCE] != BEFORE_JS or b[RESOURCE] != AFTER_JS:
        raise ValueError('independent pre-fix and approved JS byte hashes required')


def receive(module):
    raw = inspect.getsource(prior.transfer.receive).replace('PG1532', 'PG2404').replace('pg1535', 'pg2406')
    namespace = {**prior.transfer.__dict__, 'FROZEN': FROZEN}
    exec(compile(raw, '<qualified current six jars>', 'exec'), namespace)
    path = namespace['receive'](module)
    if module == 'web':
        verify_web_resource(OLD / 'web/web.jar', path)
    return path


def main_source():
    raw = inspect.getsource(prior.main)
    for a, b in [('pg1638','pg2406'),('PG1638','PG2406'),('PG1544','PG2126'),
                 ('1683dd9f6de00e71d2317d9af3cd50400a37bf4e',production()),
                 ('pg1636-api-boundary-full-qualified-v1','pg2405-question-jdbc-full-qualified-v1'),
                 ('from pg1636_api_boundary_full_qualification import server','from pg2405_question_jdbc_full_qualified import server'),
                 ("{'VERSION', 'api/api.jar'} <= changed", "{'VERSION', 'web/web.jar'} == changed"),
                 ("'tests': 3596, 'suites': 532", "'tests': 3637, 'suites': 540"),
                 ("'changedClasses': 3, 'addedClasses': 6", "'changedClasses': 0, 'addedClasses': 0, 'changedResources':1")]:
        if a not in raw:
            raise ValueError('one exact immutable candidate generation boundary required')
        raw = raw.replace(a, b)
    compile(raw, '<host-only new question candidate>', 'exec')
    return raw


def main():
    namespace = {**prior.__dict__, '__file__':__file__, 'PRODUCTION':production(),
                 'OLD_SOURCE':OLD_SOURCE,'OLD_BOM':OLD_BOM,'OLD':OLD,'NEXT':NEXT,'FROZEN':FROZEN,
                 'SIG':SIG,'receive':receive,'validate_gate':validate_gate,'verify_delta':verify_delta}
    exec(compile(main_source(), '<host signed resource candidate>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
