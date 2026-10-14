"""Independent actual new Root terminal; no lifecycle authority."""
import inspect
import pg2452_question_current_terminal as previous
from pg2516_current_strict_candidate_sources import SOURCE
from pg2532_strict_normal_publication_sources import candidate_bom

SLOT = 'pg2544-strict-current-terminal-v1'


def payload(binding, bom=None):
    if bom is None:
        bom = candidate_bom()
    raw = previous.payload(binding).replace(previous.SLOT, SLOT).replace('PG2428', 'PG2512').replace(
        previous.SOURCE, SOURCE).replace(previous.BOM, bom)
    marker = "raise ValueError('distinct noargs newrun receipt required')"
    if raw.count(marker) != 1:
        raise ValueError('one actual distinct-generation boundary required')
    raw = raw.replace(marker, marker + "\n    if binding.get('run')=='06236d14-a6f8-4d05-a6ff-49c713cc2647'or binding.get('activation')=='c347b14a-2e59-41e6-993c-a07e537cbd00':raise ValueError('historical cdbc completion is not new source')")
    compile(raw, '<fresh strict-source genuine terminal>', 'exec')
    return raw


def entry():
    raw = inspect.getsource(previous.prior.prior.previous.main).replace(
        'pg2019-fresh-resume-live-binding-complete-v1', 'pg2542-strict-current-live-binding-v1').replace(
        'pg2010-parent-watch-v1', 'pg2538-parent-watch-v1')
    raw = raw.replace("payload(actual['binding'])", "payload({**actual['binding'],'rootPid':actual['rootPid']})")
    ns = {**previous.prior.prior.previous.__dict__, 'SOURCE':SOURCE, 'SLOT':SLOT, 'payload':payload}
    exec(compile(raw, '<new current genuine terminal observer>', 'exec'), ns)
    return ns['main']


if __name__ == '__main__':
    raise SystemExit(entry()())
