"""Four proved source references tracked for later WBS batch; not already written to WBS."""
from f03_api_seven_context_trace_v1 import state_after as prior_state

def new_ids():
    ids,refs,_=prior_state()
    extra={'PMD-00196','PMD-00198','PMD-00255','PMD-00256'}
    assert len(extra)==4 and extra<=ids-refs
    return extra

def state_after():
    ids,refs,pending=prior_state();extra=new_ids()
    return ids,refs|extra,pending|extra
