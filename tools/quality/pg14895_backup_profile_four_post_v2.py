"""Actual baseline owner join before shared post, not an inferred neighbouring codec owner."""
import json
import reviewed_whole_pure_source_post_v2 as core
import g07_host_class_provenance_inputs as data
import pg14892_backup_profile_four_pt as original
from trace_owner_join import canonical

NAME='dev/codex/schubert/nk/batch/backup/BackupProfile'
PATH='src/schubert-nk-batch/src/main/java/'+NAME+'.java'
PROFILE=dict(rawFolder='PG14892-backup-profile-four-pt-v1',rawSha256='a36a4d313f3f6c858a7d89320ef5cc503024b187f03cad855c5255a267b50197',postFolder='PG14895-backup-profile-four-post-v2',kind='REVIEWED_WHOLE_PURE_VALUES_NO_RESOURCE_FIXTURES',originalTestsAlreadyCounted=False,sources={NAME:dict(path=PATH,sha256='4b9b04b202f3cafb60dfd69f420ea5e8e688ecf9db9d795998e55929e21ccdd6',module='batch',closure=[NAME],owner='WBS-P017-06')})

def owner_preflight(candidate,logical):
    actual=canonical(PATH,logical)
    if not (actual['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' and candidate==actual['canonicalOwner']==actual['canonicalCostOwner']):raise ValueError('actual Profile baseline owner required')
    return actual

if __name__=='__main__':
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    assert owner_preflight(PROFILE['sources'][NAME]['owner'],logical)['canonicalOwner']=='WBS-P017-06'
    for bad in ['WBS-P017-05',None,'WBS-UNKNOWN']:
        try:owner_preflight(bad,logical)
        except ValueError:pass
        else:raise AssertionError('inferred/null/unknown owner accepted')
    core.verify_profile(original,PROFILE)
