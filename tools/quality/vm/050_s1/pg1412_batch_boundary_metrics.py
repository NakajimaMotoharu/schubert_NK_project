"""Record real selected deltas and quality requalification; shared pp is not token cost."""
from pg998_metrics import append

if __name__=='__main__':
    print(append('V3_BATCH_REPOSITORY_PROFILE_BOUNDARIES','ATTEMPT_END',{
        'source':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','wbsLeafIds':['WBS-P017-02.02','WBS-P017-02.03','WBS-P017-06'],
        'run':'PG1405-1411','workCategory':'SELECTED_TEST','attemptResult':'FRESH24_STATIC0_SAME_MAIN_BYTE_LATEST_CLOSING_ONLY',
        'estimateAtGroupStartPp':{'low':.1,'base':.3,'high':.7},'remainingEstimatePp':{'low':0,'base':0,'high':0},
        'acceptedDelta':{'closedIds':[],'reopenedIds':[],'criteriaSatisfied':['ordinary resume creates real running attempt/no backup skip','invalid finished readback rejects before JDBC with all rows unchanged','DEL127 profile rejects/wipes','latest closing only after actual monotonic proof'],'evidenceRefs':['evidence/01_PT/017_NK-BAT-001/079_NK-BAT-001_PG1405_1411_resume観測profile境界結果.md','evidence/01_PT/018_NK-OPS-001/648_PG1411_latest_closing選択品質是正.md']},
        'technicalMeasurementDelta':{'newClosedIds':[],'reopenedIds':[],'scopeAddedIds':[],'scopeRemovedIds':[],'newTestMethods':3,'freshSelectedTests':24,'newCounterClosedClasses':['BatchRunRepository','BackupProfile'],'qualityInputSelectionReopenedAndRequalified':1,'coverageBySource':[{'source':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','capturedNativeStreams':10,'selectedNativeStreams':9,'sameSessionUnion0':True,'gain':{'LINE':1,'METHOD':0,'CLASS':0,'BRANCH':4},'remaining':{'LINE':896,'METHOD':176,'CLASS':12,'BRANCH':719},'classByteMismatch':0}]},
        'actualPaths':['1409 fresh batch24/static0/allMain byte equality','1411 20 independent vectors and actual monotonic closing/latest-only XML/counter'],
        'attempts':[{'run':'1406','exit':1,'cause':'strict no-test dependency/stale XML','targetNotRun':24},{'run':'1407','exit':1,'cause':'install accidentally enters formal coverage verify','targetNotRun':24},{'run':'1408','exit':1,'cause':'test-format newline','targetNotRun':24},{'run':'1409','exit':0,'targetTests':24},{'run':'1411','exit':0,'cause':'451 selection requalification; no new raw capture'}],
        'failureIds':['BUG1092','BUG1093','BUG1094','BUG1095','YKT861','YKT862','YKT863','YKT864'],
        'retryCause':'Outdated selected lifecycle assumptions and stale report collection; fixed compile-only/live dependency byte reuse/format-first/fresh strict XML. Quality audit corrected inherited same-session union without modifying raw native or specification.',
        'elapsedSeconds':31.781150,'timeOverlapNote':'1409 actual command elapsed; model active/external wait split unknown; dependency not reissued',
        'quotaBefore':{'usedPercent':31,'remainingPercent':69,'resetsAt':1792229056,'windowDurationMins':10080},
        'quotaAfter':{'usedPercent':32,'remainingPercent':68,'resetsAt':1792229056,'windowDurationMins':10080},
        'observedSharedPp':1,'sameQuotaWindow':True,'actualAllocatedPp':None,'tokenTotals':{'N':None,'T':None},
        'tokenMeasurementIds':['07fa4ed2f504c3f4844734d7b4ecc182d49d4c8a49fff0fc872275847e6430cf'],
        'estimateChangeReason':'Selected subset completed; whole v3 forecast unchanged. 1pp shared exceeds frozen .3 base/.7 high but other-chat/mixed quality correction attribution unknown. Future starts check current POM scope/format before dependency work and reuse same-byte evidence.',
        'unaccepted':['whole WBS parents','current Inspector/Log-replay/fault matrix','whole451/QA051/CHR'],
        'nextCommand':'MorningServiceReadiness NUL status and ArtemisRoleReadiness non-object public contract test ->format-first strict selected/static/Main byte ->latest closing only data graph'}))
