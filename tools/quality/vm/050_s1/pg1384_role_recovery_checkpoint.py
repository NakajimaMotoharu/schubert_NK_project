"""One completed checkpoint, no acceptance inflation or shared quota allocation."""
from pg998_metrics import append

if __name__=='__main__':
    print(append('V3_COLD_BOOTSTRAP_ROLE_DEPENDENCY','CHECKPOINT',{
        'source':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','wbsLeafIds':['WBS-N11'],
        'run':'PG1377-1382','workCategory':'RECOVERY','attemptResult':'FAILED_143_THEN_OWNED_RECOVERY_0',
        'failureIds':['BUG1090','YKT859'],'retryCause':'actual helper SQL lacked whitespace after numeric backend; old role mutation not reached',
        'actualPaths':['1381 exact current parent/child/private bus proof0','1382 child then Java durable once TERM0/full24-full32/187/originals/native stable/resources0'],
        'acceptedDelta':{'closedIds':[],'reopenedIds':[],'criteriaSatisfied':[],'evidenceRefs':[]},
        'technicalMeasurementDelta':{'newClosedIds':[],'reopenedIds':[],'scopeAddedIds':[],'scopeRemovedIds':[],'coverageBySource':[]},
        'estimateAtGroupStartPp':{'low':.15,'base':.3,'high':.6},
        'remainingEstimatePp':{'low':.3,'base':.6,'high':1.2},
        'estimateChangeReason':'Retain remaining working forecast pending real role prepare and post; 2pp shared observation exceeds .3 baseline, tool failures not accepted production work. No full-leaf repeated charging; v3 aggregate unchanged.',
        'quotaBefore':{'usedPercent':29,'remainingPercent':71,'resetsAt':1792229056,'windowDurationMins':10080},
        'quotaAfter':{'usedPercent':31,'remainingPercent':69,'resetsAt':1792229056,'windowDurationMins':10080,'fetchedAtJST':'2026-10-11T10:20+09:00'},
        'observedSharedPp':2,'sameQuotaWindow':True,'actualAllocatedPp':None,
        'tokenMeasurementIds':['1b18599e4a29252536b536c4a522bca8bdbf9cd5c8f315ef078ab16122b51942'],
        'tokenTotals':{'N':None,'T':None},'elapsedSeconds':4.910875,
        'unaccepted':['role preparation','normal20/closing/native','whole leaf/formal451'],
        'nextCommand':'pg1383_role_sql_readonly_parse.py -> fresh compiler/fullcurrent guard -> one new role preparation'}))
