"""Same-source new cohort genuine terminal→all24→whole seal; no lifecycle mutation."""
import inspect
import json
import sys
import types
import pg4252_current_independent_acceptance as previous
import pg4584_current_admission_image as admission
from pg1446_current_cold_stage import W

TERM='pg4586-current-genuine-terminal-v1'
ROWS='pg4588-current-all24-rows-v1'
SEAL='pg4590-current-whole-seal-v1'


def bind(raw):
    raw=admission.entry.observer.bind(raw)
    for old,new in [(previous.admission.ONCE,admission.ONCE),(previous.admission.LIVE,admission.LIVE),
        ('pg4016-literal-invariant-current-noargs-once-v1',admission.ONCE),('pg4018-literal-invariant-current-live-binding-v1',admission.LIVE),
        ('pg4012-parent-watch-v1','pg4560-parent-watch-v1'),('pg4220-parent-watch-v1','pg4560-parent-watch-v1'),
        (previous.previous.TERM,TERM),(previous.previous.ROWS,ROWS),(previous.previous.SEAL,SEAL),
        (previous.TERM,TERM),(previous.ROWS,ROWS),(previous.SEAL,SEAL)]:raw=raw.replace(old,new)
    return raw


def terminal_payload(observed):return bind(previous.previous.terminal_payload(observed))


def rows_payload(observed,before_hash):
    fn=types.FunctionType(previous.rows_payload.__code__,{**vars(previous),'admission':admission,'ROWS':ROWS})
    return bind(fn(observed,before_hash))


def seal_payload(observed,before_hash):
    # Keep the existing whole-seal oracle/normalization, only bind actual current
    # source, immutable before and static Unit bytes from this publication post.
    ns=previous.previous.namespace()
    fn=types.FunctionType(ns['seal_payload'].__code__,{**ns,'SOURCE':admission.SOURCE,'BOM':admission.BOM,'before':lambda:before_hash})
    raw=bind(fn(observed))
    start=raw.index('def before_shape(before):');end=raw.index('\nOWNED={}',start)
    project_source=inspect.getsource(admission.project)
    view=project_source+'\n'
    view+="publication_raw=(BASE/"+repr(admission.PUBLICATION_PATH)+").read_bytes();require(hashlib.sha256(publication_raw).hexdigest()=="+repr(admission.PUBLICATION)+")\n"
    view+="before=project(before,json.loads(publication_raw))\nold['unitFilesActual']=before['unitFilesActual']\n"
    return raw[:start]+view+raw[end:]


def payload(phase):
    observed=admission.live();before_hash=admission.before()
    if phase=='terminal':return TERM,terminal_payload(observed)
    if phase=='rows':return ROWS,rows_payload(observed,before_hash)
    if phase=='seal':return SEAL,seal_payload(observed,before_hash)
    raise ValueError('terminal/rows/seal only')


def main(phase):
    if phase in {'rows','seal'}:
        term=json.loads((W/TERM/'manifest.safe.json').read_bytes())
        if term['actualExit']!=0 or term['source']!=admission.SOURCE or term['result']['genuineRootDone']is not True:raise ValueError('same-cohort genuine terminal0 first')
    if phase=='seal':
        rows=json.loads((W/ROWS/'manifest.safe.json').read_bytes())
        if rows['actualExit']!=0 or rows['source']!=admission.SOURCE:raise ValueError('same-cohort all24 actual0 first')
    slot,raw=payload(phase);return admission.execute(slot,raw,90)


if __name__=='__main__':raise SystemExit(main(sys.argv[1]))
