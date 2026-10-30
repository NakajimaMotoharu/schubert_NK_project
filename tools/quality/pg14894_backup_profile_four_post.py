"""Closed single-Source profile using qualified shared v2, public pure claims only."""
import reviewed_whole_pure_source_post_v2 as core
import pg14892_backup_profile_four_pt as original

NAME='dev/codex/schubert/nk/batch/backup/BackupProfile'
PROFILE=dict(rawFolder='PG14892-backup-profile-four-pt-v1',rawSha256='a36a4d313f3f6c858a7d89320ef5cc503024b187f03cad855c5255a267b50197',postFolder='PG14894-backup-profile-four-post-v1',kind='REVIEWED_WHOLE_PURE_VALUES_NO_RESOURCE_FIXTURES',originalTestsAlreadyCounted=False,sources={NAME:dict(path='src/schubert-nk-batch/src/main/java/'+NAME+'.java',sha256='4b9b04b202f3cafb60dfd69f420ea5e8e688ecf9db9d795998e55929e21ccdd6',module='batch',closure=[NAME],owner='WBS-P017-05')})

if __name__=='__main__':core.verify_profile(original,PROFILE)
