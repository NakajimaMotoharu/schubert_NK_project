"""Small subset budget for three independent batch DB/profile boundary tests."""
from pg998_metrics import append

if __name__=='__main__':
    print(append('V3_BATCH_REPOSITORY_PROFILE_BOUNDARIES','GROUP_START',{
        'source':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','wbsLeafIds':['WBS-P017-02.02','WBS-P017-02.03','WBS-P017-06'],
        'run':'PG1405-next','workCategory':'SELECTED_TEST',
        'estimateAtGroupStartPp':{'low':.1,'base':.3,'high':.7},'remainingEstimatePp':{'low':.1,'base':.3,'high':.7},
        'estimateChangeReason':'Subset only: ordinary non-Backup resume, invalid skipped/time finished observation with independent DB no-write oracle, DEL127 profile wipe. Parent leaf budgets are not repeated; no production change planned; no VM/full6 replay.',
        'quotaBefore':{'usedPercent':31,'remainingPercent':69,'resetsAt':1792229056,'windowDurationMins':10080},
        'sourceEvidenceRefs':['PG1402 exact same-source XML gap','SS331/332/341/343','485 cost owners P017-02/P017-06'],
        'unaccepted':['selected test execution/XML/static/byte qualification','other batch fault/replay criteria and wholeleaf/formal451'],
        'nextCommand':'Add independent tests to BatchRunRepositoryTest/BackupProfileTest ->fixed source ->selected batch Maven with isolated DB/static/counters; native/deployed Main unchanged'}))
