from pg998_metrics import append

if __name__=='__main__':
    print(append('V3_RETENTION_UNEXPECTED_ENTRIES','ATTEMPT_END',{
        'source':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','wbsLeafIds':['WBS-P017-05'],'run':'PG1422/1423','workCategory':'SELECTED_TEST','attempt':1,'attemptResult':'FRESH10_STATIC0_RETENTION_FOUR_COUNTER_ZERO',
        'estimateAtGroupStartPp':{'low':.05,'base':.1,'high':.25},'remainingEstimatePp':{'low':0,'base':0,'high':0},
        'acceptedDelta':{'closedIds':[],'reopenedIds':[],'criteriaSatisfied':['unexpected regular/directory member retained without deletion/all bytes-ninefields preserved'],'evidenceRefs':['evidence/01_PT/017_NK-BAT-001/083_NK-BAT-001_PG1422_1423_Backup余分entry保護結果.md']},
        'technicalMeasurementDelta':{'newClosedIds':[],'reopenedIds':[],'scopeAddedIds':[],'scopeRemovedIds':[],'newTestMethods':1,'freshSelectedTests':10,'newCounterClosedClasses':['MorningBackupRetention'],'coverageBySource':[{'source':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','gain':{'LINE':3,'METHOD':0,'CLASS':0,'BRANCH':1},'remaining':{'LINE':892,'METHOD':176,'CLASS':12,'BRANCH':716},'classByteMismatch':0}]},
        'elapsedSeconds':27.018882,'externalJobWaitSeconds':None,'timeOverlapNote':'Actual selected command elapsed only, active/model split unknown',
        'quotaBefore':{'usedPercent':33,'remainingPercent':67,'resetsAt':1792229056,'windowDurationMins':10080},'quotaAfter':{'usedPercent':33,'remainingPercent':67,'resetsAt':1792229056,'windowDurationMins':10080},
        'observedSharedPp':0,'sameQuotaWindow':True,'actualAllocatedPp':None,'tokenTotals':{'N':None,'T':None},'tokenMeasurementIds':['a58c1bdf531a110d134481334867381e9966b3e126d06e1275092d9761fe4f50'],
        'estimateChangeReason':'Frozen subset complete first attempt. Integer shared zero is not zero actual expense; whole v3 unchanged. Host813MB near805MB start guard; QA052 environment support requested while small independent work continues.',
        'unaccepted':['whole WBS owner','Inspector/replay/fault/QA051/451','larger jobs pending disk capacity'],
        'nextCommand':'Backup request factory wrongRoot/null contract independent boundary; no VM namespace/start replay; recheck host805MB guard before selected run'}))
