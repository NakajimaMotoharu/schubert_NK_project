"""Single finite current/approval/epoch publication; no Unit exchange or reload."""
import json
import pg2442_question_normal_publication_dispatch as previous
from pg2532_strict_normal_publication_sources import sources, TOOLS, CLASS, candidate_bom, bind, BEFORE, CURRENT, production
from pg2533_strict_normal_publication_compile import TARGET
from pg1446_current_cold_stage import W

GUEST = '/var/lib/pgpt-s1-preservation/' + TOOLS
REMOTE = '/home/ubuntu/pg2534-strict-publication-stage-v1'


def stage(bom):
    return bind(previous.STAGE, bom).replace(previous.REMOTE, REMOTE)


def source(bom):
    raw = bind(previous.source(), bom)
    for before, after in [('pg2441-frozen', 'pg2533-frozen'), ('pg2442-', 'pg2534-'),
        ('pg2426-question-candidate-ro-post-v1', 'pg2530-strict-candidate-ro-post-v1'),
        ('pg2432-current-boot-question-tools-v1', 'pg2516-current-strict-candidate-tools-v1')]:
        raw = raw.replace(before, after)
    compile(raw, '<new finite publication direct body>', 'exec')
    return raw


def main():
    bom = candidate_bom()
    post = json.loads((W / 'pg2530-strict-candidate-ro-post-v1/manifest.safe.json').read_bytes())
    if type(post.get('actualExit')) is not int or post['actualExit'] != 0 or post['guest']['candidateHostReadonlyVerified'] is not True:
        raise ValueError('actual new candidate independent host RO post required')
    ns = {**previous.prior.prior.__dict__, '__file__': __file__, 'TARGET': TARGET, 'TOOLS': TOOLS,
          'CLASS': CLASS, 'GUEST': GUEST, 'REMOTE': REMOTE, 'STAGE': stage(bom), 'sources': sources,
          'CANDIDATE': production(), 'OLD': CURRENT, 'BOM': bom, 'BEFORE': BEFORE}
    exec(compile(source(bom), '<new finite publication transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
