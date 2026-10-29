"""Independent scoped registry/WBS metadata verification; no execution or coverage replay."""
import copy
import json
import current_host_program_measurements_v1 as registry
from host_tool_invocation import capture,verify
from pg9880_snapshot_nonce_trace import audit

PIN='9c01f2521b537607e818f5cce2d3f20eacce84fe4649053faa41451afef46903'
OUT=registry.data.BASE/'PG14124-current-host-program-measurements-post-v1'

def main():
    invocation=capture(__file__);assert not OUT.exists()
    prior,refs,programs,natural,raw,snap,pin,modules=registry.inputs()
    value=registry.data.read_checked(registry.OUT/'manifest.json',PIN);verify(value['invocation'])
    actual=copy.deepcopy(value)
    for key in ['invocation','wholeWbsAuditBefore']:actual.pop(key,None)
    expected=registry.expected(prior,refs,programs,natural,pin,modules)
    strict=lambda v:json.dumps(v,sort_keys=True)==json.dumps(expected,sort_keys=True)
    assert strict(actual)
    a,b=registry.documents(value,raw,snap)
    assert (registry.data.ROOT/registry.INV).read_bytes()==a and (registry.data.ROOT/registry.SNAP).read_bytes()==b
    registry.validate_docs(a,b,json.loads(raw),json.loads(snap))
    labels=[]
    mutations=[
      ('wrong-source',lambda v:v.update(source='0'*40)),
      ('method-inflation',lambda v:v.update(uniqueMethods=184)),
      ('program-duplicate',lambda v:v['fullSourceProgramMeasurements'].__setitem__(1,copy.deepcopy(v['fullSourceProgramMeasurements'][0]))),
      ('unknown-owner-promoted',lambda v:next(p for p in v['fullSourceProgramMeasurements'] if p['sourceUnit'].endswith('/ApiStopBudget'))['canonicalOwnership'].update(canonicalOwner='WBS-P018-05')),
      ('zero-branch-synthetic100',lambda v:v['naturalZeroBranchSources'][0].update(branchPercent=100)),
      ('exec-union',lambda v:v.update(globalExecUnion=True)),
      ('old995-changed',lambda v:v.update(previous995SourceRowsSha256='0'*64)),
      ('old-current-qualification-changed',lambda v:v.update(previousCurrentQualificationSha256='0'*64)),
      ('new-accepted',lambda v:v.update(newAccepted=1)),
      ('formal-promoted',lambda v:v.update(formalUpdated=True)),
      ('raw-warning-deleted',lambda v:v.update(rawWarningsRemoved=1)),
      ('whole-quality-promoted',lambda v:v.update(whole451Accepted=True))]
    for label,edit in mutations:
        bad=copy.deepcopy(actual);edit(bad)
        assert json.dumps(bad,sort_keys=True)!=json.dumps(actual,sort_keys=True) and not strict(bad)
        labels.append(label)
    old995=registry.data.sha(json.dumps(prior['sourceRows'],sort_keys=True).encode())
    oldqual=registry.data.sha(json.dumps(prior['currentQualification'],sort_keys=True).encode())
    assert old995==value['previous995SourceRowsSha256'] and oldqual==value['previousCurrentQualificationSha256']
    assert len(programs)==15 and sum(v['executablePhysical'] for v in programs)==23
    assert len(natural)==2 and sum(r['methods'] for r in refs)==183 and len(refs)==16
    assert all(r['source']==registry.SOURCE for r in refs)
    observed=audit();assert observed['actualExit']==1 and not observed['passed']
    verify(invocation);OUT.mkdir()
    registry.data.write(OUT/'manifest.json',dict(actualExit=0,source=registry.SOURCE,invocation=invocation,registryManifestSha256=PIN,inventorySha256=registry.data.sha(a),snapshotSha256=registry.data.sha(b),originalExecutions=16,uniqueMethods=183,suiteReferences=31,fullSourceProgramsFour100=15,fullSourceExecutablePhysicalFour100=23,naturalZeroBranchSources=2,partialSourceScopesStillUnaccepted=True,all995HistoricalRowsPreserved=True,oldSnapshotCurrentQualificationPreserved=True,originalBudgetAndAcceptancePreserved=True,metadataNegativeVectors=len(labels),negativeLabels=labels,wholeWbsAudit=observed,applicabilityModulesAreNotWholeQualityAuthority=True,productTestsExecuted=0,coverageExecReanalyzed=False,globalExecUnion=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(registry.data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
