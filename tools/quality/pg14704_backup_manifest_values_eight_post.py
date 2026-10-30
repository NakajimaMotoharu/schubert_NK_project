"""Independent full-Source measurement of immutable manifest claims, never actualBackup."""
import reviewed_whole_pure_source_post_v1 as core
import pg14702_backup_manifest_values_eight_pt as original

PROFILE={
    'rawFolder':'PG14702-backup-manifest-values-eight-pt-v1',
    'rawSha256':'6e608e0030fdef8a20053247acad1ccf60d32ac8054debbbeda8695a5313aa15',
    'postFolder':'PG14704-backup-manifest-values-eight-post-v1',
    'kind':'REVIEWED_WHOLE_PURE_VALUES_NO_RESOURCE_FIXTURES',
    'originalTestsAlreadyCounted':False,
    'sources':{}
}
for name,pin,owner in [
    ('BackupManifest','4edbbd1ad918c5222a534cf6d9330aecd40f9e76118c555a529374cb04bfe6ac','WBS-P017-05'),
    ('BackupVersions','49fc0ea957098ae3f5d0dc40fbbbbf28abfed7353c4e46a0ccea7593951f9dc2','WBS-P017-05'),
    ('BackupFileDigest','5cc172c91118403e73b9b562d8c0286ba6716391b8dd156181ad5e3d0b1bfd65','WBS-P017-03')]:
    internal='dev/codex/schubert/nk/batch/backup/'+name
    PROFILE['sources'][internal]=dict(path='src/schubert-nk-batch/src/main/java/'+internal+'.java',sha256=pin,module='batch',closure=[internal],owner=owner)

if __name__=='__main__':core.verify_profile(original,PROFILE)
