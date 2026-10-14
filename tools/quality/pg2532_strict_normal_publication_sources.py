"""Finite publication source factory; typed candidate BOM, current cdbc kept separate."""
import json
from pyflakes.api import check
import pg2440_question_normal_publication_sources as previous
import pg2516_current_strict_candidate_sources as current_roles
from pg2516_current_strict_candidate_sources import bind as roles, production, W
from pg2524_strict_candidate_ro_sources import sources as ro_sources

TOOLS = 'pg2532-strict-normal-publication-tools-v1'
SAVE = 'pg2535-strict-normal-publication-v1'
CLASS = 'Pg2532OrdinaryPublication'
CURRENT, CURRENT_BOM, BEFORE, BOOT = current_roles.CURRENT, current_roles.CURRENT_BOM, current_roles.BEFORE, current_roles.BOOT


def candidate_bom():
    value = json.loads((W / 'pg2512-candidate-build-v1.safe.json').read_bytes())
    if (type(value.get('actualExit')) is not int or value['actualExit'] != 0
            or value.get('candidateSource') != production() or value.get('signatureVerified') is not True):
        raise ValueError('actual signed candidate required before publication graph freeze')
    return value['manifestSha256']


def bind(raw, bom):
    if type(bom) is not str or len(bom) != 64 or set(bom) - set('0123456789abcdef'):
        raise ValueError('one immutable typed candidate BOM required')
    # Old candidate BOM is the new current BOM; protect before transforming roles.
    raw = roles(raw.replace(previous.BOM, '__STRICT_CANDIDATE_BOM__')).replace('__STRICT_CANDIDATE_BOM__', bom)
    for before, after in [(previous.TOOLS, TOOLS), (previous.SAVE, SAVE),
                          ('pg2440', 'pg2532'), ('Pg2440', 'Pg2532'), ('PG2440', 'PG2532'),
                          ('pg2420', 'pg2524'), ('Pg2420', 'Pg2524'), ('PG2420', 'PG2524'),
                          ('pg2424-question-candidate-host-ro-v1', 'pg2528-strict-candidate-host-ro-v1')]:
        raw = raw.replace(before, after)
    return raw


def sources(bom=None):
    if bom is None:
        bom = candidate_bom()
    # Bind the proven factory as data, then overwrite exact current receipt exports.
    values = {bind(n, bom):bind(raw, bom) for n,raw in previous.sources().items()}
    normal = ro_sources(bom)
    for suffix in ['parent_receipt.py', 'warning_parent_projection.py']:
        values['pg2532_' + suffix] = normal['pg2524_' + suffix]
    for name, raw in values.items():
        if name.endswith('.py'):
            context = "BUNDLE_HASH='pending-real-bundle'\n" if name == 'pg2532_native_refs.py' else ''
            if check(context + raw, '<new finite publication complete namespace>'):
                raise ValueError('whole generated publication globals required')
            compile(raw, '<new candidate finite publication graph>', 'exec')
        if '__STRICT_' in raw or 'REGULAR_MORNING_UNIT_EXCHANGE' in raw or 'NORMAL_DAEMON_RELOAD' in raw:
            raise ValueError('unbound role or duplicate Unit/reload action forbidden')
    return values


if __name__ == '__main__':
    raise SystemExit('source factory only; no guest operation')
