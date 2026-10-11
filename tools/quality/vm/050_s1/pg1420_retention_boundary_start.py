"""One retention file-set contract, no native/dispatched retention operation."""
from pg998_metrics import append

if __name__=='__main__':
    print(append('V3_RETENTION_UNEXPECTED_ENTRIES','GROUP_START',{
        'source':'769ddb15cd735c25fef581b5f9850ef9d0053c0f','wbsLeafIds':['WBS-P017-05'],'run':'PG1422-next','workCategory':'SELECTED_TEST',
        'estimateAtGroupStartPp':{'low':.05,'base':.1,'high':.25},'remainingEstimatePp':{'low':.05,'base':.1,'high':.25},
        'quotaBefore':{'usedPercent':33,'remainingPercent':67,'resetsAt':1792229056,'windowDurationMins':10080},
        'estimateChangeReason':'Only new actual backup generation with extra regular or directory member. Independent file bytes/all metadata and exact protected reason/no eligible pruning. Same Main and qualified dependency reuse; whole owner budget not repeated.',
        'unaccepted':['new selected/static/sameMain counters','remaining whole owner/fault/restore contracts'],
        'nextCommand':'Add real FD/public golden fixture with extra entries ->format-first ->strict selected10/static/liveMain byte ->latest-only input qualification'}))
