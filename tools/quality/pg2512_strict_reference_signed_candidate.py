"""New Main host-only signed candidate; fresh full required, no guest mutation."""
import inspect
import pg1638_api_signed_candidate as prior
import pg2126_metadata_signed_candidate as contract
from pg2428_question_signed_candidate import verify_container
from pg2510_strict_reference_full_six import SOURCE

W, P, T = prior.W, prior.P, prior.T
OLD = W / 'pg2428-release-v1'
NEXT = W / 'pg2512-release-v1'
FROZEN = W / 'pg2512-frozen-six-v1'
SIG = P / 'pg2512-manifest-v1.sig'
OLD_SOURCE = 'cdbc07cdf77370d521e64de8b327da7f6752139b'
OLD_BOM = '6e069bc89f53b513c719c27fbe71167afbd07b48caa0a31c61bda3e2222f11cf'
DELTA = {
    'batch:dev/codex/schubert/nk/batch/platform/BrokerJournalEvidence.class',
    'batch:dev/codex/schubert/nk/batch/repository/MorningDatabaseSession.class',
    'batch:dev/codex/schubert/nk/batch/repository/MorningDatabaseSession$Session.class'}
PHYSICAL = contract.CHANGED | DELTA


def validate_gate(outer, source):
    raw = inspect.getsource(contract.validate_gate).replace("'tests':3631", "'tests':3650").replace(
        "'semanticChangedClasses':3", "'semanticChangedClasses':6")
    ns = {**contract.__dict__, 'CHANGED': PHYSICAL}
    exec(compile(raw, '<fresh candidate independent full gate>', 'exec'), ns)
    return ns['validate_gate'](outer, source)


def verify_delta(before, after):
    raw = inspect.getsource(contract.verify_delta)
    ns = {**contract.__dict__, 'CHANGED': DELTA}
    exec(compile(raw, '<deployed cdbc candidate exact three-class delta>', 'exec'), ns)
    return ns['verify_delta'](before, after)


def receive(module):
    raw = inspect.getsource(prior.transfer.receive).replace('PG1532', 'PG2510').replace('pg1535', 'pg2512')
    ns = {**prior.transfer.__dict__, 'FROZEN': FROZEN}
    exec(compile(raw, '<fresh qualified candidate Jar transport>', 'exec'), ns)
    path = ns['receive'](module)
    old_path = {'api': 'api/api.jar', 'web': 'web/web.jar', 'batch': 'operations/batch.jar'}.get(module)
    if old_path is None:
        import json
        rows = json.loads((OLD / 'RELEASE-MANIFEST.json').read_bytes())['artifacts']
        old_path = next(r['path'] for r in rows if r['path'].endswith('/' + path.name))
    changed = {name.split(':', 1)[1] for name in DELTA if name.startswith(module + ':')}
    verify_container(OLD / old_path, path, changed)
    return path


def main_source():
    raw = inspect.getsource(prior.main)
    replacements = [('pg1638', 'pg2512'), ('PG1638', 'PG2512'), ('PG1544', 'PG2428'),
        ('1683dd9f6de00e71d2317d9af3cd50400a37bf4e', SOURCE),
        ('pg1636-api-boundary-full-qualified-v1', 'pg2511-strict-reference-full-qualified-v1'),
        ('from pg1636_api_boundary_full_qualification import server', 'from pg2511_strict_reference_full_qualified import server'),
        ("{'VERSION', 'api/api.jar'} <= changed", "{'VERSION', 'operations/batch.jar'} <= changed"),
        ("'tests': 3596, 'suites': 532", "'tests': 3650, 'suites': 540"),
        ("'changedClasses': 3, 'addedClasses': 6", "'changedClasses': 3, 'addedClasses': 0, 'changedResources':0")]
    for before, after in replacements:
        if before not in raw:
            raise ValueError('exact immutable signing boundary required')
        raw = raw.replace(before, after)
    compile(raw, '<new candidate signing only>', 'exec')
    return raw


def main():
    ns = {**prior.__dict__, '__file__': __file__, 'PRODUCTION': SOURCE, 'OLD_SOURCE': OLD_SOURCE,
          'OLD_BOM': OLD_BOM, 'OLD': OLD, 'NEXT': NEXT, 'FROZEN': FROZEN, 'SIG': SIG,
          'receive': receive, 'validate_gate': validate_gate, 'verify_delta': verify_delta}
    exec(compile(main_source(), '<PG2512 signing entry>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
