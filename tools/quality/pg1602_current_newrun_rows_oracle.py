"""Independent same-business-day new-run SQL/HTTP/one-to-one postconditions."""
import inspect
import pg1196_completed_rows_oracle as prior

def source():
    # The observed original cut-off chooses 2026-10-12 in Asia/Tokyo. This is
    # an independent date literal, not an expected value from Production code.
    code=inspect.getsource(prior).replace("row['business_date']=='2026-10-10'","row['business_date']=='2026-10-12'")
    return code+'\n'+TAIL

TAIL='''
def qualify(old,new,lower,upper):
    run='0be226b1-bbb7-43d3-aa9e-59d0bda70f9a';result=after(old,new,run,lower,upper)
    added=[r for r in new[BATCH]if r not in old[BATCH]]
    for row in added:
        baseline=[r for r in old[BATCH]if r['business_date']=='2026-10-12'and r['step']==row['step']]
        if not baseline or sum(r['status']=='SUCCESS'for r in baseline)!=1:raise ValueError('independent same-day successful predecessor required')
        if type(row['attempt'])is not int or row['attempt']!=max(r['attempt']for r in baseline)+1:raise ValueError('independent next attempt required')
        if type(row['id'])is not int or row['id']<=max(r['id']for r in old[BATCH]):raise ValueError('new-run SQL identity monotonicity refused')
    return dict(result,productionGeneratedNewRun=True,oldCompletedRunResumed=False,sameDayAlreadySuccessfulNotNewInspectorExecution=True,formalAccepted=False)
'''

def qualify(old,new,lower,upper):
    ns={};exec(compile(source(),'<current newrun independent SQL rows>','exec'),ns)
    return ns['qualify'](old,new,lower,upper)
