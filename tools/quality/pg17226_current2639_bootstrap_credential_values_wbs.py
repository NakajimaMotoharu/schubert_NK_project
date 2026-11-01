"""Metadata-only two-side binding of original methods and explicitly separate resource domain."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg9954_pure_query_registry_metadata import INV,SNAP,SECTIONS,replaced
from pg9338_wbs_reference_metadata_post import validate

BEFORE='034827e5cedb1eac3df5dc34fbfa0c7bb681446b'
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
FIELD='typedGuardCurrentHostPG17226Overlay'
REG=('PG17222-current2639-bootstrap-credential-values-registry-v1','f66deaf8d49b63b5a132436a582a70aace9674f31ccd16fd039e9c1bce97ec60')
POST=('PG17224-current2639-bootstrap-credential-values-registry-post-v1','3e1f7013848f527e8cf45a1d07034771d82aef6439c67dbccbc4df359d6d97af')
OUT=data.BASE/'PG17226-current2639-bootstrap-credential-values-wbs-v1'
COPY_KEYS=['additionalQualificationReferences','qualificationReplacedUnitHistory','additionalScopeReferences','supplementalOwnershipCandidates','jointQualificationReferences','jointQualificationReplacedUnitHistory','resourceOnlyReferences','javascriptResourceDomain','postDisclosureCorrections','currentOrdinaryTestDeclarationReference','valueFixtureQualificationReferences']
RECORD='evidence/01_PT/018_NK-OPS-001/3357_Current2639・BootstrapCredential値原二十結合_結果.md'

def main():
    invocation=capture(__file__);assert not OUT.exists()
    raw,snap=[subprocess.check_output(['git','show',BEFORE+':'+name],cwd=data.ROOT) for name in [INV,SNAP]]
    assert raw==(data.ROOT/INV).read_bytes() and snap==(data.ROOT/SNAP).read_bytes()
    r,p=[data.read_checked(data.BASE/name/'manifest.json',pin) for name,pin in [REG,POST]]
    assert r['actualExit']==p['actualExit']==0 and r['source']==p['source']==SOURCE and p['registryManifestSha256']==REG[1]
    assert p['metadataNegativeVectors']==34 and p['newSourcePrograms']==r['sourceProgramDelta']==3 and p['previousSourceProofsNotReplaced'] is True and r['resourceOnlyJavaMethods']==67 and r['nodeChildrenNotAddedToJavaMethods'] is True
    assert all(json.dumps(v,sort_keys=True)==json.dumps(r[k],sort_keys=True) for k,v in p['summary'].items())
    for v in [r,p]:verify(v['invocation'])
    path=lambda pair:str((data.BASE/pair[0]/'manifest.json').relative_to(data.ROOT))
    overlay=dict(source=SOURCE,registryManifest=path(REG),registrySha256=REG[1],registryPostManifest=path(POST),registryPostSha256=POST[1],record=RECORD,summary=p['summary'],sourceContractReference=r['additionalSourceContractReference'],coverageExecUnion=False,oldSourceRuntimeTransferred=False,allPreviousSideReferencesPreserved=True,currentWholeSourceQualification=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None)
    overlay.update({key:r[key] for key in COPY_KEYS})
    old=json.loads(raw);result=raw
    for name in SECTIONS:
        section=copy.deepcopy(old[name]);assert FIELD not in section
        section[FIELD]=copy.deepcopy(overlay);result,_,_=replaced(result,name,section)
    new_snap,_,_=replaced(snap,'inventorySha256',data.sha(result));validate(result,new_snap,old,json.loads(snap))
    restored=json.loads(result)
    for name in SECTIONS:restored[name].pop(FIELD)
    assert restored==old
    diagnostic=data.read_checked(data.BASE/'PG15848-g13-physical-scope-diagnosis-v1/manifest.json','c3dc199b0393b4aeccd21ec4dc5bacca23e596b8b55f4dd2977af32d985f1468')
    diagnostic_post=data.read_checked(data.BASE/'PG15850-g13-physical-scope-post-v1/manifest.json','51e3358248219830256033c712189b9a479e63c31353f77322eb825fda79816b')
    assert diagnostic['actualExit']==diagnostic_post['actualExit']==0 and diagnostic['source']==diagnostic_post['source']==SOURCE and diagnostic_post['parentManifestSha256']=='c3dc199b0393b4aeccd21ec4dc5bacca23e596b8b55f4dd2977af32d985f1468'
    assert diagnostic['frozenCandidateArtifacts']==943 and diagnostic['currentProductionArtifacts']==1065 and diagnostic['allCurrentPhysicalBytesMatchProduction'] is True
    assert old['currentPhysicalCandidate']['source']==diagnostic['frozenCandidateSource'] and len(old['currentPhysicalCandidate']['artifacts'])==943
    verify(diagnostic['invocation']);verify(diagnostic_post['invocation'])
    before=dict(status='NOT_REEXECUTED_EXISTING_SCOPE_HOLD_RETAINED',diagnosticSha256='c3dc199b0393b4aeccd21ec4dc5bacca23e596b8b55f4dd2977af32d985f1468',independentSha256='51e3358248219830256033c712189b9a479e63c31353f77322eb825fda79816b',frozenCandidate=943,currentPhysical=1065,wholeWbsAuditExecuted=False)
    verify(invocation);OUT.mkdir();data.write(OUT/'before.safe.json',dict(inventorySha256=data.sha(raw),snapshotSha256=data.sha(snap),wholeWbsAudit=before))
    # Mechanical metadata rewrite; no original acceptance, scope, or cost changes.
    (data.ROOT/INV).write_bytes(result);(data.ROOT/SNAP).write_bytes(new_snap)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,beforeGit=BEFORE,registrySha256=REG[1],registryPostSha256=POST[1],inventorySha256=data.sha(result),snapshotSha256=data.sha(new_snap),wholeWbsAuditBefore=before,wholeWbsAuditAfter='INDEPENDENT_POST_PENDING',productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
