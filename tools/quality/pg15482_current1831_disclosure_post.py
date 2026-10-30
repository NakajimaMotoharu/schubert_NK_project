"""Independent zero-credit disclosure registry and two WBS sides, retaining all old counters/costs."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg9954_pure_query_registry_metadata import INV,SNAP,SECTIONS
from pg9338_wbs_reference_metadata_post import validate
from pg9880_snapshot_nonce_trace import audit
from pg15480_current1831_disclosure_wbs import BEFORE,REG,PRIOR,CORRECTION,CORRECTION_POST,FIELD,UNIT,RECORD,COPY_KEYS,read

REGISTRY_PIN='1f43f440ac2346b0a6d85fd615902197408fbeceba6a7cf7e79a2bca6d083c59'
WRITER_PIN='6297f55d96bd568f830f42af6d5162face8bbbd94793ff184b3ca3d30c9f36ec'
OUT=data.BASE/'PG15482-current1831-disclosure-post-v1'
def require(ok,message):
    if not ok:raise ValueError(message)
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,c,q=[read(pair) for pair in [REG,PRIOR,CORRECTION,CORRECTION_POST]]
    r=read(('PG15478-current1831-disclosure-registry-v1',REGISTRY_PIN));writer=read(('PG15480-current1831-disclosure-wbs-v1',WRITER_PIN))
    require(all(v['actualExit']==0 and v['source']==old['source']=='6b53efeec87f3ec36a840dd8e7759656cb4aee5c' for v in [old,prior,c,q,r,writer]) and writer['registryManifestSha256']==REGISTRY_PIN and prior['registryManifestSha256']==REG[1] and q['correctionManifestSha256']==CORRECTION[1] and q['metadataNegativeVectors']==21,'genuine source/prior/disclosure')
    normal=read(('PG14216-typed-marker-guard-six-compile-v1','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'))
    require(all(data.sha((data.ROOT/path).read_bytes())==pin for path,pin in normal['begin']['inputHashes'].items()),'all current frozen source input bytes')
    pin=c['disclosureCorrection']['originalPost'][1]
    expected=dict(correctionManifest=str((data.BASE/CORRECTION[0]/'manifest.json').relative_to(data.ROOT)),correctionSha256=CORRECTION[1],independentManifest=str((data.BASE/CORRECTION_POST[0]/'manifest.json').relative_to(data.ROOT)),independentSha256=CORRECTION_POST[1],effectiveDisclosure=c['disclosureCorrection'],record=RECORD)
    summary=copy.deepcopy(prior['summary'])
    for key in ['uniqueProductMethodDelta','newTestIds','sourceProgramDelta']:summary[key]=0
    def registry_contract(value):
        require(value['postDisclosureCorrections']=={pin:expected} and value['fullSourceUnits'][UNIT]['effectDisclosureCorrection']==expected,'explicit effective digest erratum attached to exact old post/source')
        require(value['lastUpdateKind']=='DISCLOSURE_METADATA_ONLY_NO_NEW_PRODUCTION_RESULTS' and value['previousUniqueRegistryReference']==list(REG) and value['previousRegistryPostReference']==list(PRIOR),'correct append-only ancestry/type')
        require(all(type(value[k]) is int and value[k]==0 for k in ['uniqueProductMethodDelta','newTestIds','sourceProgramDelta']),'zero new product delta, not boolean alias')
        restored=copy.deepcopy(value)
        for key in ['invocation','previousUniqueRegistryReference','previousRegistryPostReference','uniqueProductMethodDelta','newTestIds','sourceProgramDelta']:restored[key]=old[key]
        restored.pop('postDisclosureCorrections');restored.pop('lastUpdateKind');restored['fullSourceUnits'][UNIT].pop('effectDisclosureCorrection')
        require(wire(restored)==wire(old),'all old cases/source/counters/cost/owners/resources/acceptance unchanged')
        require(all(wire(value[k])==wire(v) for k,v in summary.items()),'all exact summary role values')
    registry_contract(r);registry_negative=[]
    vectors=[('source','OLD'),('tests',0),('suites',0),('cases',[]),('fullSourceUnits',{}),('owners',{}),('originalPostReferences',[]),('metadataClasses',{}),('formalUpdated',True),('newAccepted',1),('effortPercent',1),('coverageExecUnion',True),('priorSource0061TestsTransferred',True),('totalProductExecs',0),('originalExecs',0),('totalMethodExecutions',0),('measuredSourcePrograms',0),('measuredPhysical',0),('executablePhysical',0),('four100SourcePrograms',0),('four100Physical',0),('naturalZeroBranchSourcePrograms',0),('metadataSourcePrograms',0),('incompleteSourcePrograms',0),('ownerStatusCounts',{}),('unknownOwnerPaths',0),('javascriptResourceDomain',{}),('resourceOnlyReferences',[]),('uniqueProductMethodDelta',1),('newTestIds',False),('sourceProgramDelta',1),('postDisclosureCorrections',{}),('lastUpdateKind','ACCEPTED'),('previousUniqueRegistryReference',[])]
    for key,value in vectors:
        bad=copy.deepcopy(r);bad[key]=value
        try:registry_contract(bad)
        except (ValueError,KeyError):registry_negative.append(key)
        else:raise ValueError('false registry disclosure '+key)
    require(len(registry_negative)==34,'registry domain34')
    old_raw,old_snap_raw=[subprocess.check_output(['git','show',BEFORE+':'+path],cwd=data.ROOT) for path in [INV,SNAP]]
    old_inventory,old_snap=json.loads(old_raw),json.loads(old_snap_raw);raw,snap=(data.ROOT/INV).read_bytes(),(data.ROOT/SNAP).read_bytes()
    require(data.sha(raw)==writer['inventorySha256'] and data.sha(snap)==writer['snapshotSha256'],'actual WBS bytes')
    overlay=dict(source=r['source'],registryManifest='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG15478-current1831-disclosure-registry-v1/manifest.json',registrySha256=REGISTRY_PIN,record=RECORD,summary=summary,sourceContractReference=old['additionalSourceContractReference'],postDisclosureCorrections={pin:expected},independentDisclosureSha256=CORRECTION_POST[1],metadataOnly=True,coverageExecUnion=False,oldSourceRuntimeTransferred=False,allPreviousSideReferencesPreserved=True,currentWholeSourceQualification=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None)
    for key in COPY_KEYS:overlay[key]=old[key]
    def wbs_contract(a,b):
        validate(a,b,old_inventory,old_snap);value=json.loads(a)
        for section in SECTIONS:require(wire(value[section].pop(FIELD))==wire(overlay),'two exact typed disclosure overlays')
        require(wire(value)==wire(old_inventory),'all old WBS cost/acceptance/sides unchanged')
    wbs_contract(raw,snap);wbs_negative=[]
    fields=[('source','source','OLD'),('correction-erased','postDisclosureCorrections',{}),('correction-proof','independentDisclosureSha256','0'*64),('registry-pin','registrySha256','0'*64),('formal','formalUpdated',True),('acceptance','newAccepted',1),('bool-acceptance','newAccepted',False),('whole','currentWholeSourceQualification',True),('coverage-union','coverageExecUnion',True),('SQL-history','jointQualificationReplacedUnitHistory',{}),('resource','resourceOnlyReferences',[]),('JS','javascriptResourceDomain',{})]
    def reject(label,a,b):
        changed=json.dumps(a,ensure_ascii=False).encode();b['inventorySha256']=data.sha(changed)
        try:wbs_contract(changed,json.dumps(b).encode())
        except ValueError:wbs_negative.append(label)
        else:raise ValueError('false WBS disclosure '+label)
    for label,key,value in fields:
        a,b=json.loads(raw),json.loads(snap);a[SECTIONS[0]][FIELD][key]=value;reject(label,a,b)
    for key,value in [('tests',0),('measuredSourcePrograms',0),('four100SourcePrograms',0),('four100Physical',0),('naturalZeroBranchSourcePrograms',0),('metadataPhysical',0),('incompleteSourcePrograms',0),('nodeChildrenNotAddedToJavaMethods',False),('resourceOnlyJavaMethods',0),('unknownOwnerPaths',0),('ownerStatusCounts',{}),('totalRepeatedOriginalMethods',0),('totalProductExecs',0)]:
        a,b=json.loads(raw),json.loads(snap);a[SECTIONS[1]][FIELD]['summary'][key]=value;reject('summary-'+key,a,b)
    for label,change in [('effort',lambda a,b:b.update(wholeEffortCompletionRate=25)),('old-owner',lambda a,b:a['artifacts'][0].update(owner='WBS-F03')),('old-side',lambda a,b:a[SECTIONS[0]].update(unapprovedAccepted=True))]:
        a,b=json.loads(raw),json.loads(snap);change(a,b);reject(label,a,b)
    require(len(wbs_negative)==28,'WBS domain28')
    for name in ['481_PGPT詳細WBS.json','484_WBSコスト枠・細分化.json']:
        path='documents/400_PGPT/470_PMO/'+name
        require((data.ROOT/path).read_bytes()==subprocess.check_output(['git','show',BEFORE+':'+path],cwd=data.ROOT),'master and cost unchanged')
    after=audit();require(after['actualExit']==writer['wholeWbsAuditBefore']['actualExit']==1 and after['lastError']=='ValueError: current physical candidate exact Git/worktree scope','whole audit still genuine HOLD')
    for value in [old,prior,c,q,r,writer]:verify(value['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=r['source'],invocation=invocation,registryManifestSha256=REGISTRY_PIN,writerManifestSha256=WRITER_PIN,summary=summary,metadataNegativeVectors=len(registry_negative),registryNegativeLabels=registry_negative,wbsMetadataNegativeVectors=len(wbs_negative),wbsNegativeLabels=wbs_negative,correctionManifestSha256=CORRECTION[1],correctionPostSha256=CORRECTION_POST[1],onlyDisclosureAddedToOldSource=True,allOldCasesCountersCostsPreserved=True,inventorySha256=data.sha(raw),snapshotSha256=data.sha(snap),wholeWbsAuditBefore=writer['wholeWbsAuditBefore'],wholeWbsAuditAfter=after,newSourcePrograms=0,newUniqueMethods=0,newProductExecutions=0,protocolMainSourceCount=158,protocolNormalMainSourceInventoryMatched=True,coverageExecUnion=False,productTestsExecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,registryMetadataNegativeVectors=len(registry_negative),wbsMetadataNegativeVectors=len(wbs_negative),productTestsExecuted=0)))
if __name__=='__main__':main()
