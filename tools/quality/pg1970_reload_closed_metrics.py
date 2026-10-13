"""Record actual stage/failure/recovery/post, no formal acceptance or shared attribution."""
import json
from pg1446_current_cold_stage import W
from pg998_metrics import append


def main():
    post=json.loads((W/'pg1963-reload-ref-scoped-full-post-v1/manifest.safe.json').read_bytes())
    if post['actualExit']!=0 or post['allClientAdvisoryFlock0']is not True:raise ValueError('actual independent normal resource post required')
    return append('SSC283_SAME_OWNER_PUBLICATION_UNIT','CHECKPOINT',{
        'source':'0fd734195b4d5338f6b7e860e087cce561d49562','wbsLeafIds':['WBS-C02','WBS-N15.01'],
        'stage':'NORMAL_UNIT_RELOAD_PARTIAL_RECOVERY_CLOSED','run':'PG1938/1949/1950/1963',
        'estimateAtGroupStartPp':{'low':.5,'base':1.5,'high':4},'estimateFrozenAt':'PGPT-20261008-0539; subset C02 common Unit, N15 reference0; no additive v3 cost',
        'attemptResult':'LIMITED_ACCEPTED_WITH_OLD143_UNKNOWN_PRESERVED','workCategory':'RECOVERY',
        'actualPaths':['canonical currentPG1846 and regularMorning Unit exchange previously published','one normal reload issued; PID1 SuccessExitStatus10; no second reload','fresh101/9FD-peer-OFD all originals proof0','ownedRefThenJava one TERM each, finite reap, sameconnection hostgate normal handoff0','separate fullpost0: all24/32/187, oldUnitinode, OriginalBackup, native26, all10kernel and managementresources0'],
        'acceptedArtifacts':['PG1949 freshproof','PG1950 recovery0','PG1963 separate fullpost0'],
        'failures':[{'run':'PG1938','actualExit':143,'cause':'BUG1193 execution auxiliary reset reclassified as whole-config drift','retryForbidden':True},{'run':'PG1945','actualExit':1,'cause':'BUG1194 emptyExecStop capture missing'},{'run':'PG1953','actualExit':1,'cause':'BUG1195 qualification outside own Ref lifetime'},{'run':'PG1955','actualExit':1,'cause':'BUG1196 NoSuchUnit without live Refs'}],
        'remainingEstimatePp':None,'remainingEstimateNote':'Original approved v3 unchanged; actual N/T and PGPT-exclusive pp unobserved. Finished limited publication/Unit/reload connection; new lawful resume/runtime/native/CHR/451 still pending.',
        'wholeLeafAcceptedDelta':0,'formalAccepted':False,'sharedQuotaUsedPercent':43,'sharedQuotaRemainingPercent':57,
        'sharedQuotaReset':1792299486,'ordinaryUsageAllowed':True,'resetCoupons':0,
        'N':None,'T':None,'actualAllocatedPp':None,'pmoAllocatedPp':None,
        'usageCursor':'329583610c902eed8888b0dd3f717555142eb4447a3d1988462493b9aa50d7bb',
        'evidence':['evidence/01_PT/018_NK-OPS-001/723_通常reload・補助記録分離・現所有回収_仕様結果.md'],
        'nextCommand':'Fresh runtime once-resume source/ownership qualification using current PG1963 before ee13ec; then bounded normal runtime placement/readback/post, fresh observer and one external start; no existing reload/Root/Backup replay.'})


if __name__=='__main__':print(main())
