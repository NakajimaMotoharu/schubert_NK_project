"""Three whole step value Sources only; private History/parent Repository never qualified from partial coverage."""
import json
import reviewed_whole_pure_source_post_v2 as core
import g07_host_class_provenance_inputs as data
import pg14911_batch_step_values_eight_pt_v2 as original
from trace_owner_join import canonical

PREFIX='dev/codex/schubert/nk/batch/repository/'
PROFILE=dict(rawFolder='PG14911-batch-step-values-eight-pt-v2',rawSha256='9736adfd97804fa8daddb7ba8286b9450b25895f0bc2fd24240d8b04b428d39a',postFolder='PG14912-batch-step-values-eight-post-v1',kind='REVIEWED_WHOLE_PURE_VALUES_NO_RESOURCE_FIXTURES',originalTestsAlreadyCounted=False,sources={})
for simple,pin,owner in [('BatchStep','f736e4cf0f251df6b0d0579996b0353e6a757b0def2777a4528ee976c8384285','WBS-P017-02'),('BatchStepAttempt','a37a929c6f7f01ccdd2facf7b6f74a72eea2f8927739b38c0ff998f3ec1015fe','WBS-P017-12'),('BatchStepResult','d4d8f244943923c428596dd5629c942fe207fb9d51a6a7872c3fa7190a71e319','WBS-P017-02')]:
    name=PREFIX+simple;PROFILE['sources'][name]=dict(path='src/schubert-nk-batch/src/main/java/'+name+'.java',sha256=pin,module='batch',closure=[name,*([name+'$Reason',name+'$Status'] if simple=='BatchStepResult' else [])],owner=owner)

if __name__=='__main__':
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for info in PROFILE['sources'].values():
        actual=canonical(info['path'],logical);assert actual['canonicalOwner']==actual['canonicalCostOwner']==info['owner'] and actual['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE'
    core.verify_profile(original,PROFILE)
