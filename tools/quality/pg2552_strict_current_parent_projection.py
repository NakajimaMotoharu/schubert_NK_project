"""Actual new-source parent eighteen typed fields; source factory only before whole seal."""
import inspect
import pg2472_question_current_parent_projection as previous
from pg2516_current_strict_candidate_sources import SOURCE
from pg2532_strict_normal_publication_sources import candidate_bom

SLOT = 'pg2552-strict-current-parent-projection-v1'


def payload(sha, bom=None):
    if bom is None:
        bom = candidate_bom()
    raw = previous.payload(sha).replace('pg2456-question-current-full-seal-v1', 'pg2548-strict-current-full-seal-v1').replace(
        previous.SOURCE, SOURCE).replace(previous.BOM, bom)
    compile(raw, '<fresh Source parent18 typed projection>', 'exec')
    return raw


def main():
    raw = inspect.getsource(previous.prior.prior.previous.prior.prior.main).replace(
        'pg2081-current-newrun-full-live-seal-v1', 'pg2548-strict-current-full-seal-v1')
    ns = {**previous.prior.prior.previous.prior.prior.__dict__, 'SOURCE':SOURCE, 'SLOT':SLOT, 'payload':payload}
    exec(compile(raw, '<new Source actual parent18 observer>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
