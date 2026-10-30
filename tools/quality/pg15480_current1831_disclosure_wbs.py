"""One mechanical publication: unchanged current1831 plus source-bound effect erratum and two WBS sides."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg9954_pure_query_registry_metadata import INV,SNAP,SECTIONS,replaced
from pg9338_wbs_reference_metadata_post import validate
from pg9880_snapshot_nonce_trace import audit

BEFORE='017ac3db448216f399d934beadf1beed3d7850ee'
REG=('PG15464-current1831-hasher-public-value-registry-v1','a5f265660960abfe3014bb08d7e9ba46b3e2e30ba3d3dbddbf3532a106c4f1a0')
PRIOR=('PG15466-current1831-hasher-public-value-registry-post-v1','d6dd59b559cf4e3a1fc5630100c7b458dc4c14a6ad5dbb5de787691c7189113f')
CORRECTION=('PG15475-nonsecret-digest-disclosure-v2','f88a4e4ae812291db25fbb40084381bfd6dadc349c4bf2e3635597d03f137234')
CORRECTION_POST=('PG15476-nonsecret-digest-disclosure-post-v1','1c0d87141e7c9b3145aa2196db78347f43731f6306e4392dd6285ea3d90efa7b')
R_OUT=data.BASE/'PG15478-current1831-disclosure-registry-v1'
OUT=data.BASE/'PG15480-current1831-disclosure-wbs-v1'
FIELD='typedGuardCurrentHostPG15480DisclosureOverlay'
UNIT='dev/codex/schubert/nk/api/bootstrap/ApiStartupInputs'
RECORD='evidence/01_PT/018_NK-OPS-001/2932_Current1831・digest開示訂正結合_結果.md'
COPY_KEYS=['additionalQualificationReferences','qualificationReplacedUnitHistory','additionalScopeReferences','supplementalOwnershipCandidates','jointQualificationReferences','jointQualificationReplacedUnitHistory','resourceOnlyReferences','javascriptResourceDomain']
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);assert not OUT.exists() and not R_OUT.exists()
    r,prior,c,q=[read(pair) for pair in [REG,PRIOR,CORRECTION,CORRECTION_POST]]
    assert all(v['actualExit']==0 and v['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' for v in [r,prior,c,q])
    assert prior['registryManifestSha256']==REG[1] and prior['metadataNegativeVectors']==34 and q['correctionManifestSha256']==CORRECTION[1] and q['metadataNegativeVectors']==21 and q['all225RegisteredCurrentSuitesIncludedInKnownHelperScan'] is True
    raw,snap=[subprocess.check_output(['git','show',BEFORE+':'+path],cwd=data.ROOT) for path in [INV,SNAP]]
    assert raw==(data.ROOT/INV).read_bytes() and snap==(data.ROOT/SNAP).read_bytes()
    old_pin=c['disclosureCorrection']['originalPost'][1]
    assert old_pin==r['fullSourceUnits'][UNIT]['postSha256'] and 'postDisclosureCorrections' not in r and 'effectDisclosureCorrection' not in r['fullSourceUnits'][UNIT]
    correction=dict(correctionManifest=str((data.BASE/CORRECTION[0]/'manifest.json').relative_to(data.ROOT)),correctionSha256=CORRECTION[1],independentManifest=str((data.BASE/CORRECTION_POST[0]/'manifest.json').relative_to(data.ROOT)),independentSha256=CORRECTION_POST[1],effectiveDisclosure=copy.deepcopy(c['disclosureCorrection']),record=RECORD)
    result=copy.deepcopy(r);result['invocation']=invocation
    result['previousUniqueRegistryReference']=list(REG);result['previousRegistryPostReference']=list(PRIOR)
    result['uniqueProductMethodDelta']=result['newTestIds']=result['sourceProgramDelta']=0
    result['postDisclosureCorrections']={old_pin:copy.deepcopy(correction)}
    result['fullSourceUnits'][UNIT]['effectDisclosureCorrection']=copy.deepcopy(correction)
    result['lastUpdateKind']='DISCLOSURE_METADATA_ONLY_NO_NEW_PRODUCTION_RESULTS'
    restored=copy.deepcopy(result)
    for key in ['invocation','previousUniqueRegistryReference','previousRegistryPostReference','uniqueProductMethodDelta','newTestIds','sourceProgramDelta']:restored[key]=r[key]
    restored.pop('postDisclosureCorrections');restored.pop('lastUpdateKind');restored['fullSourceUnits'][UNIT].pop('effectDisclosureCorrection')
    assert wire(restored)==wire(r)
    summary=copy.deepcopy(prior['summary'])
    for key in ['uniqueProductMethodDelta','newTestIds','sourceProgramDelta']:summary[key]=0
    assert all(wire(v)==wire(result[k]) for k,v in summary.items())
    registry_bytes=(json.dumps(result,sort_keys=True,indent=2)+'\n').encode('utf-8');registry_pin=data.sha(registry_bytes)
    overlay=dict(source=r['source'],registryManifest=str((R_OUT/'manifest.json').relative_to(data.ROOT)),registrySha256=registry_pin,record=RECORD,summary=summary,sourceContractReference=r['additionalSourceContractReference'],postDisclosureCorrections=copy.deepcopy(result['postDisclosureCorrections']),independentDisclosureSha256=CORRECTION_POST[1],metadataOnly=True,coverageExecUnion=False,oldSourceRuntimeTransferred=False,allPreviousSideReferencesPreserved=True,currentWholeSourceQualification=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None)
    for key in COPY_KEYS:overlay[key]=copy.deepcopy(r[key])
    old=json.loads(raw);new_raw=raw
    for name in SECTIONS:
        section=copy.deepcopy(old[name]);assert FIELD not in section
        section[FIELD]=copy.deepcopy(overlay);new_raw,_,_=replaced(new_raw,name,section)
    new_snap,_,_=replaced(snap,'inventorySha256',data.sha(new_raw));validate(new_raw,new_snap,old,json.loads(snap))
    restored=json.loads(new_raw)
    for name in SECTIONS:restored[name].pop(FIELD)
    assert restored==old
    before=audit();assert before['actualExit']==1 and before['lastError']=='ValueError: current physical candidate exact Git/worktree scope'
    for value in [r,prior,c,q]:verify(value['invocation'])
    verify(invocation);R_OUT.mkdir();OUT.mkdir()
    (R_OUT/'manifest.json').write_bytes(registry_bytes)
    # Mechanical metadata rewrite only; no original source/run/acceptance/cost changes.
    (data.ROOT/INV).write_bytes(new_raw);(data.ROOT/SNAP).write_bytes(new_snap)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=r['source'],invocation=invocation,beforeGit=BEFORE,previousRegistry=list(REG),previousRegistryPost=list(PRIOR),correctionReference=list(CORRECTION),correctionPostReference=list(CORRECTION_POST),registryManifestSha256=registry_pin,registryManifest=str((R_OUT/'manifest.json').relative_to(data.ROOT)),summary=summary,inventorySha256=data.sha(new_raw),snapshotSha256=data.sha(new_snap),newOverlay=overlay,wholeWbsAuditBefore=before,wholeWbsAuditAfter='INDEPENDENT_POST_PENDING',productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,registryManifestSha256=registry_pin,writerManifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))
if __name__=='__main__':main()
