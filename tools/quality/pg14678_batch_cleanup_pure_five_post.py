"""Independent complete six-Source measurement of original batch cleanup pure5."""
import reviewed_whole_pure_source_post_v1 as core
import pg14676_batch_cleanup_pure_five_pt as original

PROFILE={
    'rawFolder':'PG14676-batch-cleanup-pure-five-pt-v1',
    'rawSha256':'bf82dceab4dd9207bfb6715ca4e0ac64bba46a04b90e930c71acce24dba4af56',
    'postFolder':'PG14678-batch-cleanup-pure-five-post-v1',
    'kind':'REVIEWED_WHOLE_PURE_VALUES_NO_RESOURCE_FIXTURES',
    'originalTestsAlreadyCounted':False,
    'sources':{}
}
for name,pin in [
    ('cleanup/LogCleanupSummary','14c7ddab5f5156bb31f86da057d7460f98c8863ea680bcabdf47505568f3bab1'),
    ('repository/CleanupReason','5a753a16012cee16134b37686d7ee7c26cde29e2a52449fe81bd2bd73a914597'),
    ('repository/CleanupChunk','89a3708504bedbc86eb7bdc7a99e84a61047ccb8fe2a9fad961c0944a687abe8'),
    ('repository/LogCleanupProgress','57cd675756ee9d372388f562ee2242f75df95ce95173f56fe9b861b4723a2833'),
    ('cleanup/CleanupStopReason','948d471fb3d69fd417a3a52a17d46fc2e528814521158f336a0c055fa96b5590'),
    ('cleanup/CleanupStoppedException','65b367602ff1357acd24ec4d7ba30483dd6346a44882105a2e804c168e5f3856')]:
    internal='dev/codex/schubert/nk/batch/'+name
    PROFILE['sources'][internal]=dict(path='src/schubert-nk-batch/src/main/java/'+internal+'.java',sha256=pin,module='batch',closure=[internal],owner='WBS-P017-07')

if __name__=='__main__':core.verify_profile(original,PROFILE)
