"""Historical raw-ID tracking plus42 new-source reasons; not a whole current-source qualification."""
from f03_main_failure_boundary_sixty_two_trace_v1 import state_after as prior_state
from pg14232_api_context_line_rebind import TARGETS

def new_ids():
    ids,refs,_=prior_state()
    values={f'PMD-{i:05d}' for first,_ in TARGETS.values() for i in range(first,first+6)}
    assert len(values)==42 and values<=ids-refs
    return values

def state_after():
    ids,refs,pending=prior_state();added=new_ids()
    return ids,refs|added,pending|added
