"""Fourteen source-only collector contexts; old state and pending/raw truth remain preserved."""
from f03_api_inbound_four_trace_v1 import state_after as prior_state
from pg14370_monitor_seven_failure_fourteen_context import PLAN

def new_ids():
    values={i for row in PLAN['targets'].values() for i in row['ids']}
    assert len(values)==14
    return values

def state_after():
    ids,refs,pending=prior_state()
    extra=new_ids()
    assert (len(ids),len(refs),len(pending))==(6247,3682,2821)
    assert extra<=ids-refs
    return ids,refs|extra,pending|extra
