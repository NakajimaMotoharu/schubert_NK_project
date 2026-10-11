"""Measured dependency closure and next N15 stage budget, no whole-leaf acceptance."""
from pg998_metrics import append

SOURCE='769ddb15cd735c25fef581b5f9850ef9d0053c0f'

if __name__=='__main__':
    print(append('V3_COLD_BOOTSTRAP_ROLE_DEPENDENCY','ATTEMPT_END',{
        'source':SOURCE,'wbsLeafIds':['WBS-N11'],'run':'PG1387-1395','workCategory':'NATIVE_CONNECTION',
        'estimateAtGroupStartPp':{'low':.15,'base':.3,'high':.6},'remainingEstimatePp':{'low':0,'base':0,'high':0},
        'acceptedDelta':{'closedIds':[],'reopenedIds':[],'criteriaSatisfied':['SSC263 one missing role finite filesystem delta; all originals preserved; new read-only management scopes normal closed'],'evidenceRefs':['pg1395-existing-role-normal-post-v1.safe.json']},
        'technicalMeasurementDelta':{'newClosedIds':[],'reopenedIds':[],'scopeAddedIds':[],'scopeRemovedIds':[],'coverageBySource':[],'dependencyStagesClosed':2},
        'actualPaths':['1387 one role created then protocol failed; old143 kept','1390 proven pair once recovery0/fullpost','1394 non-mutating existing-role verification0/all new normal scopes','1395 full independent post0'],
        'failureIds':['BUG1090','BUG1091','YKT859','YKT860'],'retryCause':'closed-message DB contract incorrectly used previous state; corrected state/action matrix and independent current role verification without replaying mkdir',
        'attemptResult':'DEPENDENCY_VERIFIED_NOT_WHOLE_LEAF','elapsedSeconds':14.137409,
        'quotaBefore':{'usedPercent':29,'remainingPercent':71,'resetsAt':1792229056,'windowDurationMins':10080},
        'quotaAfter':{'usedPercent':31,'remainingPercent':69,'resetsAt':1792229056,'windowDurationMins':10080},
        'observedSharedPp':2,'sameQuotaWindow':True,'actualAllocatedPp':None,'tokenTotals':{'N':None,'T':None},
        'unaccepted':['N11 whole cold contract','ADMIN normal20/closing/native','formal451'],'nextCommand':'pg1397_existing_admin_compile.py'}))
    print(append('V3_CURRENT769_EXISTING_ADMIN_NATIVE','GROUP_START',{
        'source':SOURCE,'wbsLeafIds':['WBS-N15.02'],'run':'PG1396-next','workCategory':'NATIVE_CONNECTION',
        'estimateAtGroupStartPp':{'low':.15,'base':.3,'high':.6},'remainingEstimatePp':{'low':.15,'base':.3,'high':.6},
        'estimateChangeReason':'Remaining half of split0387 group; dependency separate, no full-leaf repeated budgeting or source regeneration',
        'quotaBefore':{'usedPercent':31,'remainingPercent':69,'resetsAt':1792229056,'windowDurationMins':10080},
        'unaccepted':['current ADMIN oneshot20 and same Invocation terminal-closing','native/wholeleaf/formal451'],
        'nextCommand':'1397 compiler ->1398 stage/verify/execute once ->independent fullpost ->same-source native'}))
