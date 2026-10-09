"""Inspector progress provenance only; other first-run/A01 DB deltas are separate scope."""
def first_progress(old,first,current,run):
 if not all(type(v)is list for v in (old,first,current))or type(run)is not str:return False
 if len(old)!=4 or len(first)!=5 or first!=current:return False
 if any(type(v)is not dict for v in (*old,*first,*current)):return False
 if any(v not in first or v.get('run_id')==run for v in old):return False
 added=[v for v in first if v not in old]
 return len(added)==1 and added[0].get('run_id')==run
