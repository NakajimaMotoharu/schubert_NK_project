"""Independent full80/24/187 plus PID1 RO mount and genuine returned scopes."""
import json
from pyflakes.api import check
import pg4992_ssc304_unused_post as unused_post
import pg5000_ssc304_ro_sources as role
from pg3786_hygiene_ro_post import EXTRA
from pg4996_resume_connection import execute

SLOT = 'pg5006-ssc304-ro-independent-post-v1'


def payload():
    role.qualify()
    raw = unused_post.payload()
    marker = 'save=base/' + repr(unused_post.SLOT)
    if raw.count(marker) != 1:
        raise ValueError('one new evidence-only RO output')
    raw = raw.replace(marker, 'save=base/' + repr(SLOT), 1)
    extra = EXTRA.replace('PG3748', 'PG4980').replace('pg3784-hygiene-ro-completed-v1', role.SAVE)
    marker = "    proof = {p.name: {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size} for p in root.iterdir() if p.is_file()}"
    if raw.count(marker) != 1:
        raise ValueError('one held tenRef RO proof boundary')
    raw = raw.replace(marker, '\n'.join('    ' + line for line in extra.strip().splitlines()) + '\n' + marker, 1)
    marker = "**candidate_post,'newTenReferencesReturnedNormally':len(refs)==10"
    if raw.count(marker) != 1:
        raise ValueError('one post normal-close result')
    raw = raw.replace(marker, marker + ",'candidateHostReadonlyVerified':True", 1)
    if check(raw, '<independent all80/current04bb PID1RO post>'):
        raise ValueError('complete emitted namespace static0')
    return raw


def main():
    actual = json.loads((role.W / 'pg5004-prepare-ro-v2.safe.json').read_bytes())
    if not (type(actual.get('actualExit')) is int and actual['actualExit'] == 0
            and actual.get('sourceQualified') is True and actual.get('candidateSource') == role.SOURCE
            and actual.get('currentApprovalEpochChanged') is False):
        raise ValueError('actual current04bb/new candidate RO completion first')
    return execute(SLOT, payload(), 180)


if __name__ == '__main__':
    raise SystemExit(main())
