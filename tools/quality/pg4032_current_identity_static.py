"""Fresh typed identity facts on all current65 comparisons; old scopes never copied by line."""
import inspect
import pg3864_suppression_identity_review as previous
from pg3966_literal_invariant_full_six import SOURCE

SLOT = 'pg4032-current-identity-static-v1'


def server_source():
    raw = inspect.getsource(previous.server)
    replacements = {'PG3864-suppression-identity-review-v1': 'PG4032-current-identity-static-v1', 'source-full-PG3734': 'source-full-PG3966',
                    'PG3738-hygiene-whole-qualified-v1': 'PG3968-literal-invariant-whole-qualified-v1',
                    'PG3744-pmd-contract-classification-v1': 'PG4030-current-standalone-static-v1', 'PG3734-six-v1': 'PG3966-six-v1',
                    '3714': '3717', '1840': '1653', "previous/'dispositions.safe.json'": "previous/'all1653-dispositions.safe.json'",
                    "prior['dispositionSha256']": "prior['allDispositionsSha256']",
                    "row['disposition']=='UNCLASSIFIED'": "row['disposition']in {'UNCLASSIFIED','REQUIRED_JDK_SELF_SUPPRESSION_IDENTITY_GUARD'}",
                    '0<new<=65': 'new==30', '1592-new': '1394-new', '248+new': '259+new',
                    "'newTechnicalAssessments':new": "'currentTypedGuardsVerified':new,'newSourceRequalifiedScopes':new-28",
                    'exact technical248 authority': 'exact current287 authority'}
    for old, new in replacements.items():
        if old not in raw: raise ValueError('exact current typed-source boundary missing: ' + old)
        raw = raw.replace(old, new)
    compile(raw, '<current all65 exact identity type proof>', 'exec')
    return raw


def main_source():
    raw = inspect.getsource(previous.main).replace('pg3738-hygiene-whole-qualified-v1', 'pg3968-literal-invariant-whole-qualified-v1')
    raw = raw.replace('pg3744-pmd-contract-classification-v1', 'pg4030-current-standalone-static-v1').replace('PG3864-suppression-identity-review-v1', 'PG4032-current-identity-static-v1')
    marker = 'inspect.getsource(x)for x in [require,facts,server]'
    if raw.count(marker) != 1: raise ValueError('one complete typed payload source boundary')
    return raw.replace(marker, '(server_source() if x is server else inspect.getsource(x))for x in [require,facts,server]')


def main():
    values = {**previous.__dict__, 'SOURCE': SOURCE, 'SLOT': SLOT, 'server_source': server_source}
    exec(compile(server_source(), '<current all65 typed extractor and independent JDK>', 'exec'), values)
    exec(compile(main_source(), '<new source-only identity review, no guest management>', 'exec'), values)
    return values['main']()


if __name__ == '__main__': raise SystemExit(main())
