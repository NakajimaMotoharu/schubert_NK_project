"""Save measured same-source business proof and remaining distinctions."""
from pg998_metrics import append

if __name__=='__main__':
    print(append('V3_CURRENT769_ROOT_BUSINESS','ATTEMPT_END',{
        'source':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','wbsLeafIds':['WBS-N15.06'],'run':'PG1418','workCategory':'NATIVE_CONNECTION',
        'estimateAtGroupStartPp':{'low':.15,'base':.3,'high':.6},'remainingEstimatePp':{'low':0,'base':0,'high':0},
        'attempt':1,'attemptResult':'ACTUAL0_BACKUP_DB_FILES_CONFIG_DUMP_LIST_CAUSAL222_CRYPTO_FULLPOST',
        'elapsedSeconds':7.762823,'externalJobWaitSeconds':None,'timeOverlapNote':'Actual SSH proof elapsed only; model/wait split unknown',
        'acceptedDelta':{'closedIds':[],'reopenedIds':[],'criteriaSatisfied':['Current Backup canonical/file/DB handles','Current causal222 wire/outbox/local/encrypted sessions','full source/raw/resource preservation normal Ref close'],'evidenceRefs':['evidence/01_PT/018_NK-OPS-001/650_PG1418_currentRoot業務原本照合結果.md']},
        'technicalMeasurementDelta':{'newClosedIds':[],'reopenedIds':[],'scopeAddedIds':[],'scopeRemovedIds':[],'newTechnicalStages':2,'actualBackupArchives':3,'causalLogSessionEach':222,'priorRetainedSessions':446,'coverageBySource':[]},
        'actualPaths':['same-current readonly VM normal metadata scopes','independent pg_restore listing/canonical/archive/DB','independent AES-GCM/wire/journal/session'],
        'formalRunDelta':0,'unaccepted':['QA051 final/completeness','native remaining Inspector','replay/fault/restore-prune/timeouts','whole WBS/451'],
        'quotaBefore':{'usedPercent':32,'remainingPercent':68,'resetsAt':1792229056,'windowDurationMins':10080},'quotaAfter':{'usedPercent':33,'remainingPercent':67,'resetsAt':1792229056,'windowDurationMins':10080},
        'observedSharedPp':1,'sameQuotaWindow':True,'actualAllocatedPp':None,'tokenTotals':{'N':None,'T':None},'tokenMeasurementIds':['0eb31fe67895a21824e794ca9c040391eab487867cb7f871c8ccb1e2790327a7'],
        'estimateChangeReason':'Frozen collection/oracle subset complete. Shared1pp spans mixed parent work/other chats, not own exact cost; exceeds .3/.6 diagnostically. Reuse qualified contracts and existing Root; whole v3 forecast unchanged. Consumer N01/N02/P006 references cost0 in this collection group.',
        'nextCommand':'Meaningful Backup publication/retention boundary cases or legal Inspector/replay dependencies; current Root/Backup/ADMIN/stop must not repeat'}))
