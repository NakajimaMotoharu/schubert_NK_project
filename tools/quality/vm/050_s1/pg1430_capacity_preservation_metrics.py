from pg998_metrics import append

if __name__=='__main__':
    print(append('V3_ENVIRONMENT_CAPACITY_PRESERVATION','EXECUTION_STOP',{
        'source':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','wbsLeafIds':['WBS-P017-06','WBS-N15.06'],'run':'PG1414-1428-preserved',
        'workCategory':'RECOVERY','attemptResult':'PRESERVED_ENVIRONMENT_CAPACITY_GUARD_NOT_MET','stopReason':'ENVIRONMENT_CAPACITY_QA052_NOT_QUOTA',
        'quotaAfter':{'usedPercent':33,'remainingPercent':67,'resetsAt':1792229056,'windowDurationMins':10080,'secondary':None,'resetCredits':0},
        'actualAllocatedPp':None,'tokenTotals':{'N':None,'T':None},'tokenMeasurementIds':['4f8c2898a44dfac91c84d983a830d00a79b0142319d03c6c3a25d9d7db2e625d'],
        'sourceEvidenceRefs':['017/081','018/650','017/083','017/085','456/460 latest checkpoint'],
        'capacity':{'hostAvailableBytes':802504704,'runnerStartGuardBytes':805306368,'preservationCushionBytes':536870912,'protectedAssetsDeleted':False,'guardLowered':False},
        'actualPaths':['fresh10Unit PID0/jobempty metadata read','QEMU19945/SOCKS401093 preserved','all selected/current-business/counter evidence saved'],
        'currentSource':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','formalRunDelta':0,'pgptAllComplete':False,
        'unaccepted':['legal current Inspector/native','replay-fault/competition','CHR QA051','fresh whole source/scope 451/trace/handoff','QA052 environment capacity'],
        'estimateChangeReason':'Original v3 remainder preserved; no numeric cost attribution, no quota stop or PMO wait. No new implementation until safe capacity for current route is restored.',
        'nextCommand':'QA052 capacity response ->df /dev/shm+freshquota+Git/source/current process reauthentication ->WBS audit ->new frozen remaining group, no successful dispatch replay'}))
