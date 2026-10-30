"""Independent current870 WBS merged joint history and true-noCode mapper counts."""
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg9954_pure_query_registry_metadata import INV,SNAP,SECTIONS
from pg9338_wbs_reference_metadata_post import validate
from pg9880_snapshot_nonce_trace import audit
from pg14772_current870_wbs import SOURCE,BEFORE,FIELD,REG,POST

PIN='fab559a3a63be68bea397d6516aad36391fddc3fbe798e18abc71b05051cc44b'
OUT=data.BASE/'PG14774-current870-wbs-post-v1'

def require(ok,message):
    if not ok:raise ValueError(message)

def wire(v):return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only independent WBS post')
    writer=data.read_checked(data.BASE/'PG14772-current870-wbs-v1/manifest.json',PIN)
    r,p=[data.read_checked(data.BASE/n/'manifest.json',h) for n,h in [REG,POST]]
    require(writer['actualExit']==r['actualExit']==p['actualExit']==0 and r['source']==p['source']==writer['source']==SOURCE,'genuine references')
    require(p['registryManifestSha256']==REG[1] and p['metadataNegativeVectors']==21 and p['singleExecRequestReplacements']==1 and p['newRepositorySourceScopes']==1 and p['necessaryRepeatMethods']==8 and p['newTrueNoCodeMetadata']==1,'independent full registry proof')
    for value in [writer,r,p]:verify(value['invocation'])
    old_raw,old_snap_raw=[subprocess.check_output(['git','show',BEFORE+':'+name],cwd=data.ROOT) for name in [INV,SNAP]]
    old,old_snap=json.loads(old_raw),json.loads(old_snap_raw);raw,snap=(data.ROOT/INV).read_bytes(),(data.ROOT/SNAP).read_bytes()
    require(data.sha(raw)==writer['inventorySha256'] and data.sha(snap)==writer['snapshotSha256'],'actual full WBS hashes')
    path=lambda pair:str((data.BASE/pair[0]/'manifest.json').relative_to(data.ROOT))
    summary_keys=['tests','suites','originalExecs','measuredSourcePrograms','measuredPhysical','executablePhysical','metadataPhysical','generatedMetadataPhysical','four100SourcePrograms','four100Physical','four100ExecutablePhysical','naturalZeroBranchSourcePrograms','naturalZeroBranchPhysical','metadataSourcePrograms','incompleteSourcePrograms','unknownOwnerPaths','ownerStatusCounts','additionalQualificationExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','sourceProgramDelta','necessaryJointRepeatedMethods','totalRepeatedOriginalMethods']
    summary={k:r[k] for k in summary_keys};require(wire(summary)==wire(p['summary']),'typed summary from independently qualified actual fields')
    expected=dict(source=SOURCE,registryManifest=path(REG),registrySha256=REG[1],registryPostManifest=path(POST),registryPostSha256=POST[1],record='evidence/01_PT/018_NK-OPS-001/2766_Current870Question同一exec資格WBS結合_結果.md',summary=summary,additionalQualificationReferences=r['additionalQualificationReferences'],qualificationReplacedUnitHistory=r['qualificationReplacedUnitHistory'],additionalScopeReferences=r['additionalScopeReferences'],sourceContractReference=r['additionalSourceContractReference'],supplementalOwnershipCandidates=r['supplementalOwnershipCandidates'],coverageExecUnion=False,oldSourceRuntimeTransferred=False,allPreviousSideReferencesPreserved=True,currentWholeSourceQualification=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None)
    expected.update(jointQualificationReferences=r['jointQualificationReferences'],jointQualificationReplacedUnitHistory=r['jointQualificationReplacedUnitHistory'])
    def contract(a,b):
        validate(a,b,old,old_snap);value=json.loads(a)
        for section in SECTIONS:require(wire(value[section].pop(FIELD))==wire(expected),'exact typed side scope/count/history/flags')
        require(wire(value)==wire(old),'all prior semantic fields and original side values immutable')
    contract(raw,snap);labels=[]
    vectors=[('source',lambda a,b:a[SECTIONS[0]][FIELD].update(source='OLD')),('methods',lambda a,b:a[SECTIONS[0]][FIELD]['summary'].update(tests=872)),('exec',lambda a,b:a[SECTIONS[0]][FIELD]['summary'].update(originalExecs=44)),('four',lambda a,b:a[SECTIONS[0]][FIELD]['summary'].update(four100SourcePrograms=189)),('natural',lambda a,b:a[SECTIONS[0]][FIELD]['summary'].update(naturalZeroBranchSourcePrograms=0)),('noCode',lambda a,b:a[SECTIONS[0]][FIELD]['summary'].update(metadataSourcePrograms=0)),('synthetic',lambda a,b:a[SECTIONS[0]][FIELD]['summary'].update(generatedMetadataPhysical=0)),('incomplete',lambda a,b:a[SECTIONS[0]][FIELD]['summary'].update(incompleteSourcePrograms=0)),('unknown',lambda a,b:a[SECTIONS[0]][FIELD]['summary'].update(unknownOwnerPaths=0)),('owner-role',lambda a,b:a[SECTIONS[0]][FIELD]['summary']['ownerStatusCounts'].update(UNKNOWN=0)),('history',lambda a,b:a[SECTIONS[0]][FIELD].update(qualificationReplacedUnitHistory={})),('qualification',lambda a,b:a[SECTIONS[0]][FIELD].update(additionalQualificationReferences=[])),('scope',lambda a,b:a[SECTIONS[0]][FIELD].update(additionalScopeReferences=[])),('context',lambda a,b:a[SECTIONS[0]][FIELD].update(sourceContractReference={})),('union',lambda a,b:a[SECTIONS[0]][FIELD].update(coverageExecUnion=True)),('formal',lambda a,b:a[SECTIONS[0]][FIELD].update(formalUpdated=True)),('accepted',lambda a,b:a[SECTIONS[0]][FIELD].update(newAccepted=1)),('bool',lambda a,b:a[SECTIONS[0]][FIELD].update(newAccepted=False)),('effort',lambda a,b:b.update(wholeEffortCompletionRate=50)),('old',lambda a,b:a[SECTIONS[0]].update(unapprovedAccepted=True)),('master',lambda a,b:a['artifacts'][0].update(owner='WBS-F03')),('second-side',lambda a,b:a[SECTIONS[1]][FIELD].update(currentWholeSourceQualification=True))]
    vectors.extend([('physical-minus-one',lambda a,b:a[SECTIONS[0]][FIELD]['summary'].update(four100Physical=194)),('code-minus-one',lambda a,b:a[SECTIONS[0]][FIELD]['summary'].update(four100ExecutablePhysical=184))])
    vectors.extend([('joint-history-erased',lambda a,b:a[SECTIONS[0]][FIELD].update(jointQualificationReplacedUnitHistory={})),('joint-proof-erased',lambda a,b:a[SECTIONS[0]][FIELD].update(jointQualificationReferences=[])),('necessary-repeat-erased',lambda a,b:a[SECTIONS[0]][FIELD]['summary'].update(necessaryJointRepeatedMethods=0)),('repeated-as-new',lambda a,b:a[SECTIONS[0]][FIELD]['summary'].update(tests=876))])
    vectors.extend([('new-noCode-erased',lambda a,b:a[SECTIONS[0]][FIELD]['summary'].update(metadataPhysical=11)),('old-joint-overwritten',lambda a,b:a[SECTIONS[0]][FIELD].update(jointQualificationReferences=[r['jointQualificationReferences'][-1]]))])
    for label,change in vectors:
        a,b=json.loads(raw),json.loads(snap);change(a,b);changed=json.dumps(a,ensure_ascii=False).encode();b['inventorySha256']=data.sha(changed)
        try:contract(changed,json.dumps(b).encode())
        except ValueError:labels.append(label)
        else:raise ValueError('false WBS accepted '+label)
    for name in ['481_PGPT詳細WBS.json','484_WBSコスト枠・細分化.json']:
        path='documents/400_PGPT/470_PMO/'+name
        require((data.ROOT/path).read_bytes()==subprocess.check_output(['git','show',BEFORE+':'+path],cwd=data.ROOT),'original master and cost unchanged')
    after=audit();require(after['actualExit']==writer['wholeWbsAuditBefore']['actualExit']==1 and after['lastError']=='ValueError: current physical candidate exact Git/worktree scope','whole audit actual HOLD, never PASS')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,writerManifestSha256=PIN,registryManifestSha256=REG[1],registryPostSha256=POST[1],inventorySha256=data.sha(raw),snapshotSha256=data.sha(snap),summary=summary,metadataNegativeVectors=len(labels),negativeLabels=labels,onlyTwoMetadataSectionsChanged=True,snapshotOnlyChangedField='inventorySha256',allOldSemanticsAndCostsPreserved=True,wholeWbsAuditBefore=writer['wholeWbsAuditBefore'],wholeWbsAuditAfter=after,productTestsExecuted=0,oldSourceTransferred=False,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
