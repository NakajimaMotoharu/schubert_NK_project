"""Qualify shared-v2 minimum-case canaries and one existing exec reanalysis; Product executions0."""
import copy
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import reviewed_whole_pure_source_post_v2 as core
import pg15307_required_column_one_pt_v2 as original

OUT=data.BASE/'PG15324-shared-pure-single-case-tool-v2'
PROFILE={'rawFolder':'PG15307-required-column-one-pt-v2','rawSha256':'caafa8ae9909b8cd0f3ff7a7e2293c8a07260d1cab79505486e6b053f6b4f189','postFolder':'PG15324-shared-pure-required-one-post-v2','sources':{'dev/codex/schubert/nk/api/database/RequiredColumn':{'path':'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/database/RequiredColumn.java','sha256':'1a2121d84e092a0fae4a973452370cf9ea0aa5d9fb56d023ae7015b0061fae7d','module':'api','closure':['dev/codex/schubert/nk/api/database/RequiredColumn'],'owner':'WBS-P004-05'}},'kind':'REVIEWED_WHOLE_PURE_VALUES_NO_RESOURCE_FIXTURES','originalTestsAlreadyCounted':True}
RAW_INPUTS=[
('PG15307-required-column-one-pt-v2','caafa8ae9909b8cd0f3ff7a7e2293c8a07260d1cab79505486e6b053f6b4f189',1),
('PG15300-api-config-readiness-eleven-pt-v1','de9cb79a296838fd5112450d14ac6531dbb510eed64860853a807108fdbd58d4',11),
('PG15150-api-service-binding-sixteen-pt-v1','e5ad03985cbf9fa278cba902b1d2343bfcecf6554827bbf6cf1885627cbc017f',16)]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    library=data.ROOT/'tools/quality/reviewed_whole_pure_source_post_v2.py'
    old_library=data.ROOT/'tools/quality/reviewed_whole_pure_source_post_v1.py'
    assert data.sha(old_library.read_bytes())=='dedda4f153010fa22719a6aefd6406dc90a862e710f9097db90bc4ba38975341'
    old=old_library.read_text();new=library.read_text()
    expected=old.replace('Shared independently pinned pure whole-Source post; metadata only and unsupported scope fails closed.','Shared v2 pure whole-Source post; single-case duplicate canary fixed, no scope broadening.').replace("v['cases'].__setitem__(1,copy.deepcopy(v['cases'][0]))","v['cases'].append(copy.deepcopy(v['cases'][0]))")
    assert new.rstrip()==expected.rstrip() and "__setitem__(1" not in new and ".append(copy.deepcopy(v['cases'][0]))" in new
    legacy=data.read_checked(data.BASE/'PG14672-shared-pure-post-independent-v1/manifest.json','5bbb497529d1b9767fba1ce7a3c2a19e98b12e686f627e742cf9f7da42b57e08')
    assert legacy['actualExit']==0 and legacy['profileNegativeVectors']==18 and legacy['semanticNegativeVectors']==12
    labels=[];refs=[]
    for folder,pin,count in RAW_INPUTS:
        raw=data.read_checked(data.BASE/folder/'manifest.json',pin);assert raw['actualExit']==0 and raw['source']==original.SOURCE and len(raw['cases'])==count
        core.validator.common.SOURCE=original.SOURCE;core.validator.COUNTS=raw['begin']['selectedSuites'];core.validator.EXPECTED_FIXTURE_HASHES={}
        core.validator.assess(raw)
        for action in ['duplicate-append','missing-case']:
            bad=copy.deepcopy(raw)
            if action=='duplicate-append':bad['cases'].append(copy.deepcopy(bad['cases'][0]));assert len(bad['cases'])==count+1
            else:bad['cases'].pop();assert len(bad['cases'])==count-1
            try:core.validator.assess(bad)
            except ValueError:labels.append(action+'-'+str(count))
            else:raise AssertionError('minimum/multi case false qualification')
        verify(raw['begin']['invocation']);refs.append(dict(path=str((data.BASE/folder/'manifest.json').relative_to(data.ROOT)),sha256=pin,actualCases=count))
    assert len(labels)==6
    core.validate_profile(PROFILE)
    core.verify_profile(original,PROFILE)
    post_path=data.BASE/PROFILE['postFolder']/'manifest.json';post=data.read_checked(post_path,data.sha(post_path.read_bytes()))
    assert post['actualExit']==0 and post['tests']==post['suites']==1 and post['strictFour100GateExit']==0 and post['originalTestsCountedElsewhere'] is post['currentSourceExistingExecReanalyzed'] is True and post['newProductExecutions']==post['productTestsReexecutedByPost']==0
    verify(legacy['invocation']);verify(post['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,profile=PROFILE,libraryPath=str(library.relative_to(data.ROOT)),librarySha256=data.sha(library.read_bytes()),legacyLibrarySha256='dedda4f153010fa22719a6aefd6406dc90a862e710f9097db90bc4ba38975341',legacyQualificationSha256='5bbb497529d1b9767fba1ce7a3c2a19e98b12e686f627e742cf9f7da42b57e08',priorProfileNegativeVectorsReused=18,priorSemanticNegativeVectorsReused=12,caseCardinalityNegativeVectors=len(labels),negativeLabels=labels,originalInputReferences=refs,reanalysisPostManifest=str(post_path.relative_to(data.ROOT)),reanalysisPostSha256=data.sha(post_path.read_bytes()),originalMethodsAlreadyCounted=1,newProductMethods=0,newProductExecutions=0,productionSourceChanged=False,toolOnly=True,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
