"""Independent two-side metadata proof; all old costs/acceptance remain unchanged."""
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg9954_pure_query_registry_metadata import INV,SNAP,SECTIONS
from pg9338_wbs_reference_metadata_post import validate
from pg9880_snapshot_nonce_trace import audit
from pg15108_current1511_api_standard_wbs import SOURCE,BEFORE,FIELD,REG,POST

PIN='5c0796cf6b8bf6fdd6d41c5c0509e3380bb30a416d8a09dc00dcd8a2ba403ca4'
OUT=data.BASE/'PG15110-current1511-api-standard-wbs-post-v1'

def require(ok,message):
    if not ok:raise ValueError(message)

def wire(v):return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only independent1511 WBS post')
    writer=data.read_checked(data.BASE/'PG15108-current1511-api-standard-wbs-v1/manifest.json',PIN)
    r,p=[data.read_checked(data.BASE/name/'manifest.json',pin) for name,pin in [REG,POST]]
    require(writer['actualExit']==r['actualExit']==p['actualExit']==0 and writer['source']==r['source']==p['source']==SOURCE and p['registryManifestSha256']==REG[1],'genuine current registry and writer')
    require(p['metadataNegativeVectors']==33 and r['resourceOnlyJavaMethods']==35 and p['protocolMainSourceCount']==158 and p['newSourcePrograms']==3 and r['nodeChildrenNotAddedToJavaMethods'] is True,'independent resource/Source domains')
    require(all(wire(v)==wire(r[k]) for k,v in p['summary'].items()),'independent exact typed summary')
    old_raw,old_snap_raw=[subprocess.check_output(['git','show',BEFORE+':'+name],cwd=data.ROOT) for name in [INV,SNAP]]
    old,old_snap=json.loads(old_raw),json.loads(old_snap_raw);raw,snap=(data.ROOT/INV).read_bytes(),(data.ROOT/SNAP).read_bytes()
    require(data.sha(raw)==writer['inventorySha256'] and data.sha(snap)==writer['snapshotSha256'],'actual whole WBS content hashes')
    path=lambda pair:str((data.BASE/pair[0]/'manifest.json').relative_to(data.ROOT))
    expected=dict(source=SOURCE,registryManifest=path(REG),registrySha256=REG[1],registryPostManifest=path(POST),registryPostSha256=POST[1],record='evidence/01_PT/018_NK-OPS-001/2844_Current1511・API標準三Source結合_結果.md',summary=p['summary'],sourceContractReference=r['additionalSourceContractReference'],coverageExecUnion=False,oldSourceRuntimeTransferred=False,allPreviousSideReferencesPreserved=True,currentWholeSourceQualification=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None)
    for key in ['additionalQualificationReferences','qualificationReplacedUnitHistory','additionalScopeReferences','supplementalOwnershipCandidates','jointQualificationReferences','jointQualificationReplacedUnitHistory','resourceOnlyReferences','javascriptResourceDomain']:expected[key]=r[key]
    def contract(a,b):
        validate(a,b,old,old_snap);value=json.loads(a)
        for section in SECTIONS:require(wire(value[section].pop(FIELD))==wire(expected),'both exact typed side values')
        require(wire(value)==wire(old),'every old scope/owner/acceptance/cost and previous proof unchanged')
    contract(raw,snap);labels=[]
    vectors=[('source','source','OLD'),('coverage-union','coverageExecUnion',True),('formal','formalUpdated',True),('acceptance','newAccepted',1),('bool-acceptance','newAccepted',False),('whole','currentWholeSourceQualification',True),('Catalog-history','qualificationReplacedUnitHistory',{}),('Catalog-proof','additionalQualificationReferences',[]),('SQL-history','jointQualificationReplacedUnitHistory',{}),('SQL-proof','jointQualificationReferences',[]),('resource-erased','resourceOnlyReferences',[]),('JS-erased','javascriptResourceDomain',{})]
    for label,key,value in vectors:
        a,b=json.loads(raw),json.loads(snap);a[SECTIONS[0]][FIELD][key]=value;changed=json.dumps(a,ensure_ascii=False).encode();b['inventorySha256']=data.sha(changed)
        try:contract(changed,json.dumps(b).encode())
        except ValueError:labels.append(label)
        else:raise ValueError('false WBS side accepted '+label)
    for key,value in [('tests',908),('measuredSourcePrograms',215),('four100SourcePrograms',132),('four100Physical',199),('naturalZeroBranchSourcePrograms',74),('metadataPhysical',0),('incompleteSourcePrograms',0),('nodeChildrenNotAddedToJavaMethods',False),('resourceOnlyJavaMethods',0),('unknownOwnerPaths',0),('ownerStatusCounts',{'BASELINE_LOGICAL_REFERENCE':283,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':80,'UNKNOWN':103}),('totalRepeatedOriginalMethods',0),('totalProductExecs',54)]:
        a,b=json.loads(raw),json.loads(snap);a[SECTIONS[1]][FIELD]['summary'][key]=value;changed=json.dumps(a,ensure_ascii=False).encode();b['inventorySha256']=data.sha(changed)
        try:contract(changed,json.dumps(b).encode())
        except ValueError:labels.append('summary-'+key)
        else:raise ValueError('false WBS summary accepted '+key)
    for label,change in [('effort',lambda a,b:b.update(wholeEffortCompletionRate=25)),('old-owner',lambda a,b:a['artifacts'][0].update(owner='WBS-F03')),('old-side',lambda a,b:a[SECTIONS[0]].update(unapprovedAccepted=True))]:
        a,b=json.loads(raw),json.loads(snap);change(a,b);changed=json.dumps(a,ensure_ascii=False).encode();b['inventorySha256']=data.sha(changed)
        try:contract(changed,json.dumps(b).encode())
        except ValueError:labels.append(label)
        else:raise ValueError('false old semantic accepted '+label)
    for name in ['481_PGPT詳細WBS.json','484_WBSコスト枠・細分化.json']:
        path='documents/400_PGPT/470_PMO/'+name
        require((data.ROOT/path).read_bytes()==subprocess.check_output(['git','show',BEFORE+':'+path],cwd=data.ROOT),'master and frozen cost unchanged')
    after=audit();require(after['actualExit']==writer['wholeWbsAuditBefore']['actualExit']==1 and after['lastError']=='ValueError: current physical candidate exact Git/worktree scope','whole audit remains actual HOLD, not local metadata success')
    for v in [writer,r,p]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,writerManifestSha256=PIN,registryManifestSha256=REG[1],registryPostSha256=POST[1],inventorySha256=data.sha(raw),snapshotSha256=data.sha(snap),summary=p['summary'],metadataNegativeVectors=len(labels),negativeLabels=labels,onlyTwoMetadataSectionsChanged=True,snapshotOnlyChangedField='inventorySha256',allOldSemanticsAndCostsPreserved=True,wholeWbsAuditBefore=writer['wholeWbsAuditBefore'],wholeWbsAuditAfter=after,resourcePrograms=4,nodeChildrenNotAddedToJavaMethods=True,productTestsExecuted=0,oldSourceTransferred=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
