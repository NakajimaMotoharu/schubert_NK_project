"""Tool-only singleton/multiple metadata checks; existing8 post reanalysis, zero Product replay."""
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import reviewed_whole_pure_source_post_v2 as core
import pg14702_backup_manifest_values_eight_pt as original
from pg14704_backup_manifest_values_eight_post import PROFILE as PRIOR_PROFILE

OUT=data.BASE/'PG14706-pure-post-minimum-cardinality-selftest-v1'

def main():
    invocation=capture(__file__);assert not OUT.exists()
    prior=data.read_checked(data.BASE/'PG14704-backup-manifest-values-eight-post-v1/manifest.json','f963fce059a3362592ea62ff1fcdc52b2ce11832dd553bed3defbfd3f93cbb1e')
    raw=data.read_checked(data.BASE/PRIOR_PROFILE['rawFolder']/'manifest.json',PRIOR_PROFILE['rawSha256'])
    old=data.ROOT/'tools/quality/reviewed_whole_pure_source_post_v1.py'
    assert data.sha(old.read_bytes())=='dedda4f153010fa22719a6aefd6406dc90a862e710f9097db90bc4ba38975341'
    text=old.read_text();text=text.replace('"""Shared independently pinned pure whole-Source post; metadata only and unsupported scope fails closed."""','"""Shared pure whole-Source postv2; handles single-method negative data, not expanded runtime permission."""')
    text=text.replace("('duplicate',lambda v:v['cases'].__setitem__(1,copy.deepcopy(v['cases'][0])))","('duplicate',duplicate_case_for_negative)")
    addition='def duplicate_case_for_negative(value):\n    """Alter only copied metadata; a singleton cannot replace a nonexistent index1."""\n    cases=value[\'cases\']\n    if len(cases)>1:cases[1]=copy.deepcopy(cases[0])\n    else:cases.append(copy.deepcopy(cases[0]))\n\n\n'
    text=text.replace('def validate_profile(value):',addition+'def validate_profile(value):')
    assert text==(data.ROOT/'tools/quality/reviewed_whole_pure_source_post_v2.py').read_text()
    checks=[]
    for count in [1,2,8]:
        # Synthetic metadata only, never a claim that this reduced Product selection ran.
        value=copy.deepcopy(raw);name='dev.codex.schubert.nk.batch.backup.BackupManifestValuesTest'
        value['cases']=value['cases'][:count];value['begin']['selectedSuites']={'BackupManifestValuesTest':count};value['begin']['expectedTests']=count
        value['suites']={name:dict(tests=count,failures=0,errors=0,skipped=0)}
        core.validator.common.SOURCE=original.SOURCE;core.validator.COUNTS={'BackupManifestValuesTest':count};core.validator.EXPECTED_FIXTURE_HASHES={}
        core.validator.assess(value);before=json.dumps(value,sort_keys=True);bad=copy.deepcopy(value);core.duplicate_case_for_negative(bad)
        assert json.dumps(value,sort_keys=True)==before and bad['cases'][0]==bad['cases'][1] and bad['cases'][0] is not bad['cases'][1]
        try:core.validator.assess(bad)
        except ValueError:checks.append(count)
        else:raise ValueError('duplicate metadata admitted')
    assert checks==[1,2,8]
    profile=copy.deepcopy(PRIOR_PROFILE);profile['postFolder']='PG14706-pure-v2-existing-backup-eight-post-v1';profile['originalTestsAlreadyCounted']=True
    core.verify_profile(original,profile)
    path=data.BASE/profile['postFolder']/'manifest.json';current=data.read_checked(path,data.sha(path.read_bytes()))
    fields=['source','originalManifestSha256','normalManifestSha256','staticPostManifestSha256','tests','suites','failures','errors','skipped','reruns','targetSourceUnits','completeSourceUnitClosure','sourcePhysicalInventory','fullSourceUnits','strictFour100GateExit','cases','xmlHashes','execSha256','sessionIdentity','crcMismatch','physicalClasses','executable','totals','owners','reportedEnvironment','metadataNegativeVectors','manualCounterExclusions','officialGeneratedFiltersUnchanged','newAccepted','formalUpdated','wholeF03Accepted','whole451Accepted','effortPercent']
    assert all(json.dumps(current[k],sort_keys=True)==json.dumps(prior[k],sort_keys=True) for k in fields)
    assert current['originalTestsCountedElsewhere'] is current['currentSourceExistingExecReanalyzed'] is True and current['newProductExecutions']==0
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,bug='BUG-2109',ykt='YKT-1856',pureMetadataCardinalities=checks,toolMetadataPositiveCases=3,toolMetadataNegativeCases=3,metadataOnlyReducedSelectionsNotProductRuns=True,sourceChangeLimitedToDuplicateNegativeGenerator=True,priorPostSha256='f963fce059a3362592ea62ff1fcdc52b2ce11832dd553bed3defbfd3f93cbb1e',reanalysisPostManifest=str(path.relative_to(data.ROOT)),reanalysisPostSha256=data.sha(path.read_bytes()),equalSemanticFields=fields,existingProductMethodsReferenced=8,newProductMethods=0,newProductExecutions=0,sourceChanged=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
