"""Independent full Source counters for original cleanup counts/step10, not DB qualification."""
import reviewed_whole_pure_source_post_v1 as core
import pg14696_batch_cleanup_step_ten_pt as original

PROFILE={
    'rawFolder':'PG14696-batch-cleanup-step-ten-pt-v1',
    'rawSha256':'0d030b1a3a9820b12afe753d6fc4ccfe4529daacc4ace8c4761ea98740ee1000',
    'postFolder':'PG14698-batch-cleanup-step-ten-post-v1',
    'kind':'REVIEWED_WHOLE_PURE_VALUES_NO_RESOURCE_FIXTURES',
    'originalTestsAlreadyCounted':False,
    'sources':{}
}
for name,pin in [
    ('repository/CleanupCounts','9a7504e2b266c3de22ce10dfc8b15dadb0ce04f3a5f05bdd86d151c32d341f19'),
    ('repository/CleanupKind','e792d04a7b6409fbfb4696b7b295d242d5958740e084a42bb2f1b3d5592108ea'),
    ('repository/CleanupStepChunk','2da91936cd06c97fa1752906a1385065b6d53737bdc1247619ec1177f5b764c4'),
    ('cleanup/StepCleanupSummary','fe92043709045bb68f2755934a48d70ae7c2c6e81ae87ca016ba2f743d018501')]:
    internal='dev/codex/schubert/nk/batch/'+name
    closure=[internal,internal+'$Reason'] if name=='repository/CleanupStepChunk' else [internal]
    PROFILE['sources'][internal]=dict(path='src/schubert-nk-batch/src/main/java/'+internal+'.java',sha256=pin,module='batch',closure=closure,owner='WBS-P017-07')

if __name__=='__main__':core.verify_profile(original,PROFILE)
