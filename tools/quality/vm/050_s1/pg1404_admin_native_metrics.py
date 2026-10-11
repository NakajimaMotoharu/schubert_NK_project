"""Completed selected real path, counters separate from whole WBS/formal acceptance."""
from pg998_metrics import append

if __name__=='__main__':
    print(append('V3_CURRENT769_EXISTING_ADMIN_NATIVE','ATTEMPT_END',{
        'source':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','wbsLeafIds':['WBS-N15.02'],'run':'PG1396-1403',
        'workCategory':'NATIVE_CONNECTION','attemptResult':'REAL_NORMAL20_FULLPOST_NATIVE10_0',
        'estimateAtGroupStartPp':{'low':.15,'base':.3,'high':.6},'remainingEstimatePp':{'low':0,'base':0,'high':0},
        'acceptedDelta':{'closedIds':[],'reopenedIds':[],'criteriaSatisfied':['current-source existing ADMIN20 within30s','same Invocation terminal/closing2','independent all24/full32/187/originals/credential retirement/resources0'],'evidenceRefs':['evidence/01_PT/018_NK-OPS-001/647_PG1344_1403_Bootstrap_role正常closing単体仕様結果.md']},
        'technicalMeasurementDelta':{'newClosedIds':[],'reopenedIds':[],'scopeAddedIds':[],'scopeRemovedIds':[],'newRealPathStages':3,'coverageBySource':[{'source':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','nativeBefore':8,'nativeAfter':10,'gain':{'LINE':27,'METHOD':2,'CLASS':0,'BRANCH':1},'remaining':{'LINE':897,'METHOD':176,'CLASS':12,'BRANCH':723},'classByteMismatch':0}]},
        'actualPaths':['1396 verify/execute0, captured ADMIN20 1.489676s','1400 whole protected independentpost0','1401 ten native/frozen six same-source qualification0','1402 exact XMLgap0'],
        'elapsedSeconds':24.367237,'elapsedNote':'verify6.108476+execute14.252596+post4.006165; compiler/counter/runtime wait distinct, model active time unknown',
        'quotaBefore':{'usedPercent':31,'remainingPercent':69,'resetsAt':1792229056,'windowDurationMins':10080},
        'quotaAfter':{'usedPercent':31,'remainingPercent':69,'resetsAt':1792229056,'windowDurationMins':10080},
        'observedSharedPp':0,'sameQuotaWindow':True,'actualAllocatedPp':None,'tokenTotals':{'N':None,'T':None},
        'tokenMeasurementIds':['1ea22824940411ee968cfb4ea50ce7025885646653bfbfcc0889a0678570927d'],
        'estimateChangeReason':'Selected role/ADMIN half-group reached proof; zero integer shared delta is not zero cost; v3 whole forecast unchanged, Inspector/fault/Log-replay remains different stage',
        'unaccepted':['whole WBS leaf/formal451','current-source Inspector native','Log/replay/fault/CHR and QA051'],
        'nextCommand':'SSC263 ledger-only main followup; then current Root business Log/replay oracle or selected batch fault matrix per leaf dependencies'}))
