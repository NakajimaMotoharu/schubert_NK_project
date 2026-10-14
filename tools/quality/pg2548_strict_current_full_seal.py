"""Whole fresh Source/run genuine terminal/all24/four ordinary owners; no operation authority."""
import inspect
from pyflakes.api import check
import pg2456_question_current_full_seal as previous
from pg2544_strict_current_terminal import payload as terminal_payload, SLOT as TERM
from pg2546_strict_current_rows import BEFORE
from pg2516_current_strict_candidate_sources import SOURCE
from pg2532_strict_normal_publication_sources import candidate_bom

SLOT = 'pg2548-strict-current-full-seal-v1'


def payload(binding, bom=None):
    if bom is None:
        bom = candidate_bom()
    raw = previous.payload(binding)
    for before, after in [(previous.SLOT, SLOT), ('pg2448-question-current-noargs-once-v1', 'pg2540-strict-current-noargs-once-v1'),
                          (previous.BEFORE, BEFORE), (previous.SOURCE, SOURCE), (previous.BOM, bom),
                          ('PG2428', 'PG2512'), ('pg2428-manifest.sig', 'pg2512-manifest.sig')]:
        raw = raw.replace(before, after)
    guard = terminal_payload(binding, bom)
    marker = "out=pathlib.Path('/var/lib/pgpt-s1-preservation/" + TERM + "')"
    if guard.count(marker) != 1:
        raise ValueError('one actual current terminal boundary required')
    raw = previous.prior.prior.previous.previous.constant(raw, 'GUARD', guard[:guard.index(marker)])
    if check(raw, '<fresh strict whole Source all24 seal>'):
        raise ValueError('complete actual seal globals required')
    compile(raw, '<fresh Source whole seal>', 'exec')
    return raw


def entry():
    raw = inspect.getsource(previous.prior.prior.previous.previous.main)
    for before, after in [('pg2021-fresh-resume-terminal-receipt-v1', TERM),
                          ('pg2023-fresh-resume-rows-oracle-v1', 'pg2546-strict-current-rows-v1'),
                          ('pg2019-fresh-resume-live-binding-complete-v1', 'pg2542-strict-current-live-binding-v1')]:
        raw = raw.replace(before, after)
    raw = raw.replace("payload(live['binding'])", "payload({**live['binding'],'rootPid':live['rootPid']})")
    ns = {**previous.prior.prior.previous.previous.__dict__, 'SLOT':SLOT, 'SOURCE':SOURCE, 'payload':payload}
    exec(compile(raw, '<fresh strict whole acceptance capture>', 'exec'), ns)
    return ns['main']


if __name__ == '__main__':
    raise SystemExit(entry()())
