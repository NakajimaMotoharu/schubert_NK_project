"""Host-only unused candidate signing after genuine3712; never deploys or changes VM."""
import hashlib
import inspect
import json
import re

import pg1638_api_signed_candidate as prior
from pg2428_question_signed_candidate import verify_container
import pg3412_outbox_fixed_full as whole

W, P, T = prior.W, prior.P, prior.T
SOURCE = whole.SOURCE
OLD_SOURCE = whole.previous.SOURCE
OLD_BOM = '37bfe01a075449d36cc8b73408dd81fc6d6efc158910a437cbde21b6a0b7f863'
OLD = W / 'pg2802-release-v1'; NEXT = W / 'pg3420-release-v1'
FROZEN = W / 'pg3420-frozen-six-v1'; SIG = P / 'pg3420-manifest-v1.sig'
CHANGED = {'api:dev/codex/schubert/nk/api/messaging/outbound/OutboxJmsSender.class',
           'api:dev/codex/schubert/nk/api/messaging/outbound/OutboxJmsSender$1.class'}


def validate_gate(outer, source):
    expected = {'actualExit': 0, 'productionSource': source, 'tests': 3712, 'suites': 545,
                'mainClasses': 1643, 'FESFlakyNotRun': 0, 'staticSixModules': 0,
                'semanticChangedClasses': 1, 'debugOnlyChangedClasses': 1,
                'oldNativeImported': False, 'candidateNativePending': True, 'formalAccepted': False, 'global100': False}
    if type(outer) is not dict or type(outer.get('actualExit')) is not int or outer['actualExit'] != 0:
        raise ValueError('genuine independent candidate whole0 required')
    gate = outer.get('result')
    if type(gate) is not dict or any(type(gate.get(k)) is not type(v) or gate[k] != v for k, v in expected.items()):
        raise ValueError('exact3712/545/candidate quality boundary required')
    if gate.get('changedClasses') != sorted(CHANGED):
        raise ValueError('both physical API class deltas required')
    if gate.get('allOriginalCaseIdentitiesRetained') is not True or gate.get('newCases') != [list(v) for v in whole.NEW_CASES]:
        raise ValueError('all original3707 identities and five independently named new cases required')
    if gate.get('generatedSwitchDebug') != {'lineEntries': 1, 'oldLine': 154, 'newLine': 158,
                                            'lineOffset': 4, 'allNonLineBytesIdentical': True, 'crcEqualityClaim': False}:
        raise ValueError('exact generated class proof, not old CRC equality')
    hashes = gate.get('jarHashes')
    if type(hashes) is not dict or set(hashes) != set(prior.MODULES) or any(type(v) is not str or not re.fullmatch('[0-9a-f]{64}', v) for v in hashes.values()):
        raise ValueError('six exact actually qualified Jar hashes required')
    if {m: (v['tests'], v['suites'], v['mainClasses']) for m, v in gate['modules'].items()} != whole.EXPECTED:
        raise ValueError('all six independent module cardinalities required')
    return gate


def verify_delta(before, after):
    if set(before) != set(prior.MODULES) or set(after) != set(before):
        raise ValueError('six fixed module inventories required')
    changed = set()
    for module in before:
        if before[module].keys() != after[module].keys():
            raise ValueError('no added or removed Main class')
        changed.update(module + ':' + n for n in before[module] if before[module][n] != after[module][n])
    if changed != CHANGED or sum(len(v) for v in after.values()) != 1643:
        raise ValueError('exact semantic one/debug one among all1643 Main required')
    return 1643


def qualification_matches(outer):
    data = {'candidateSource': SOURCE, 'expected': whole.EXPECTED,
            'newCases': whole.NEW_CASES,
            'priorManifestSha256': json.loads((W / 'pg3400-oracle-boundary-full-qualified-v1/manifest.safe.json').read_bytes())['result']['serverManifestSha256'],
            'priorJarHashes': json.loads((W / 'pg3400-oracle-boundary-full-qualified-v1/manifest.safe.json').read_bytes())['result']['jarHashes']}
    raw = '\n'.join(inspect.getsource(f) for f in [whole.positions, whole.verify_switch_debug, whole.require,
                                                  whole.classify, whole.independent]) + '\nindependent(' + repr(data) + ')\n'
    actual = W / 'pg3414-outbox-full-qualified-v1/qualify.private.py'
    return actual.read_text() == raw and hashlib.sha256(raw.encode()).hexdigest() == outer['qualificationSourceSha256']


def receive(module):
    raw = inspect.getsource(prior.transfer.receive).replace('PG1532', 'PG3412').replace('pg1535', 'pg3420')
    namespace = {**prior.transfer.__dict__, 'FROZEN': FROZEN}
    exec(compile(raw, '<six qualified candidate3712 Jar transfer>', 'exec'), namespace)
    path = namespace['receive'](module)
    old_path = {'api': 'api/api.jar', 'web': 'web/web.jar', 'batch': 'operations/batch.jar'}.get(module)
    if old_path is None:
        rows = json.loads((OLD / 'RELEASE-MANIFEST.json').read_bytes())['artifacts']
        old_path = next(r['path'] for r in rows if r['path'].endswith('/' + path.name))
    verify_container(OLD / old_path, path, {p.split(':', 1)[1] for p in CHANGED if p.startswith(module + ':')})
    return path


def main_source():
    raw = inspect.getsource(prior.main)
    for old, new in [('pg1638', 'pg3420'), ('PG1638', 'PG3420'), ('PG1544', 'PG2802'),
                     ('1683dd9f6de00e71d2317d9af3cd50400a37bf4e', SOURCE),
                     ('pg1636-api-boundary-full-qualified-v1', 'pg3414-outbox-full-qualified-v1'),
                     ("    from pg1636_api_boundary_full_qualification import server\n    require(outer['qualificationSourceSha256'] == hashlib.sha256(server().encode()).hexdigest())", "    require(qualification_matches(outer))"),
                     ("'tests': 3596, 'suites': 532", "'tests': 3712, 'suites': 545"),
                     ("'changedClasses': 3, 'addedClasses': 6", "'changedClasses': 2, 'semanticChangedClasses': 1, 'debugOnlyChangedClasses': 1, 'addedClasses': 0")]:
        if old not in raw:
            raise ValueError('fixed signing template boundary absent')
        raw = raw.replace(old, new)
    return raw


def main():
    whole.validate(prior.subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=T, text=True).strip())
    namespace = {**prior.__dict__, '__file__': __file__, 'PRODUCTION': SOURCE,
                 'OLD_SOURCE': OLD_SOURCE, 'OLD_BOM': OLD_BOM, 'OLD': OLD, 'NEXT': NEXT,
                 'FROZEN': FROZEN, 'SIG': SIG, 'validate_gate': validate_gate,
                 'verify_delta': verify_delta, 'receive': receive, 'qualification_matches': qualification_matches}
    exec(compile(main_source(), '<host-only unused candidate3420>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
