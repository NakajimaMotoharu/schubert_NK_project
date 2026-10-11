from pg998_metrics import append

if __name__=='__main__':
    print(append('V3_BACKUP_PUBLICATION_FACTORY_BOUNDARY','ATTEMPT_END',{
        'source':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','wbsLeafIds':['WBS-P017-06'],'run':'PG1426/1428','workCategory':'SELECTED_TEST','attemptResult':'FRESH7_STATIC0_PARTIAL_B1_GAIN',
        'estimateAtGroupStartPp':{'low':.03,'base':.08,'high':.2},'remainingEstimatePp':{'low':0,'base':0,'high':0},
        'acceptedDelta':{'closedIds':[],'reopenedIds':[],'criteriaSatisfied':['nonMorning/default-explicit factory拒否/null proof拒否','partial counters measured without guessed method closure'],'evidenceRefs':['evidence/01_PT/017_NK-BAT-001/085_NK-BAT-001_PG1426_1428_Publication異Root結果.md']},
        'technicalMeasurementDelta':{'newClosedIds':[],'reopenedIds':[],'scopeAddedIds':[],'scopeRemovedIds':[],'newTestMethods':1,'freshSelectedTests':7,'newCounterClosedClasses':[],'qualityPartialObservationReopenedAndRequalified':1,'coverageBySource':[{'source':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','gain':{'LINE':0,'METHOD':0,'CLASS':0,'BRANCH':1},'remaining':{'LINE':892,'METHOD':176,'CLASS':12,'BRANCH':715},'classByteMismatch':0}]},
        'failureIds':['BUG1096','YKT865'],'retryCause':'Counter tool guessed wrapper L/M coverage from exceptional invocation. Bytecode/official JaCoCo FAQ prove subsequent-probe distinction; corrected measurement, not business test expectation.',
        'attempts':[{'run':'1426','actualExit':0,'tests':7},{'run':'1427','actualExit':1,'cause':'guessed partial counter L/M','completedManifest':False},{'run':'1428','actualExit':0}],
        'elapsedSeconds':25.080096,'externalJobWaitSeconds':None,'quotaBefore':{'usedPercent':33,'remainingPercent':67,'resetsAt':1792229056,'windowDurationMins':10080},'quotaAfter':{'usedPercent':33,'remainingPercent':67,'resetsAt':1792229056,'windowDurationMins':10080},
        'observedSharedPp':0,'sameQuotaWindow':True,'actualAllocatedPp':None,'tokenTotals':{'N':None,'T':None},
        'estimateChangeReason':'Frozen subset done; partial tool correction not complete native/default normal return. Integer shared0 not own cost0. Host802MB below805MB runner guard; no fresh Maven/VM write start, QA052 support pending; other bounded independent work continues.',
        'unaccepted':['normal native/default delegates','whole WBS/451/Inspector/replay/QA051','fresh heavier work until capacity support'],
        'nextCommand':'Persist085/ledger/checkpoint; select bounded non-Java/static/contract task or authorized durable capacity response, never weaken805MB guard'}))
