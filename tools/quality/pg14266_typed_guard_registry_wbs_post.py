"""Independent fixed current host/context WBS side metadata, historical semantics and genuine audit HOLD."""
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg9954_pure_query_registry_metadata import INV,SNAP,SECTIONS
from pg9338_wbs_reference_metadata_post import validate
from pg9880_snapshot_nonce_trace import audit
from pg14264_typed_guard_registry_wbs import SOURCE,BEFORE,FIELD,REG,POST,CONTEXT,CONTEXT_POST

OUT=data.BASE/'PG14266-typed-guard-current-registry-wbs-post-v1'
PIN='f969a316ecc3929b194c3aedb14510bb98c25acac9a01b5dc5c6e45c42c2ffef'

def require(ok,message):
    if not ok:raise ValueError(message)

def wire(value):return json.dumps(value,sort_keys=True)

def contract(raw,snap,old,old_snap,expected):
    validate(raw,snap,old,old_snap);parsed=json.loads(raw)
    for name in SECTIONS:require(wire(parsed[name].pop(FIELD))==wire(expected),'exact typed registry/context overlay, no current whole qualification')
    require(wire(parsed)==wire(old),'all old fields/runtime/qualification/budget and types unchanged')

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only independent post')
    m=data.read_checked(data.BASE/'PG14264-typed-guard-current-registry-wbs-v1/manifest.json',PIN)
    r,p,c,cp=[data.read_checked(data.BASE/name/'manifest.json',pin) for name,pin in (REG,POST,CONTEXT,CONTEXT_POST)]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in (m,r,p,c,cp)),'genuine same source references')
    require(p['registryManifestSha256']==REG[1] and p['metadataNegativeVectors']==12 and p['originalXmlMethods']==15,'independent original XML registry binding')
    require(cp['reviewManifestSha256']==CONTEXT[1] and cp['sourceContexts']==4 and cp['metadataNegativeVectors']==18,'independent original four-context binding')
    path=lambda v:str((data.BASE/v[0]/'manifest.json').relative_to(data.ROOT))
    expected=dict(source=SOURCE,registryManifest=path(REG),registrySha256=REG[1],registryPostManifest=path(POST),registryPostSha256=POST[1],record='evidence/01_PT/018_NK-OPS-001/2622_現typed修正source三exec・受信四文脈_参照結合結果.md',originalExecs=3,originalMethods=15,originalSuites=4,fullSourceMeasured=4,four100SourcePrograms=3,four100Physical=3,incompleteSourcePrograms=1,unknownOwnerPaths=6,coverageExecUnion=False,oldSource0061RuntimeTransferred=False,contextManifest=path(CONTEXT),contextSha256=CONTEXT[1],contextPostManifest=path(CONTEXT_POST),contextPostSha256=CONTEXT_POST[1],contextOriginalIds=['PMD-00196','PMD-00198','PMD-00255','PMD-00256'],contextSourceRows=4,contextWholeJoinPending=True,historicalRawIds=6247,referenceIdsAcrossRecordedSourceDomains=3682,pendingIdsAcrossRecordedSourceDomains=2821,noReferenceHistoricalIds=2565,old995RuntimeAndQualificationUnchanged=True,currentWholeSourceQualification=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None)
    original,snapshot=[subprocess.check_output(['git','show',BEFORE+':'+name],cwd=data.ROOT) for name in (INV,SNAP)]
    old,old_snap=json.loads(original),json.loads(snapshot)
    raw,snap=(data.ROOT/INV).read_bytes(),(data.ROOT/SNAP).read_bytes()
    require(data.sha(raw)==m['inventorySha256'] and data.sha(snap)==m['snapshotSha256'],'exact actual full WBS byte binding')
    contract(raw,snap,old,old_snap,expected);labels=[]
    for label,mutate in [('source',lambda a,b:a[SECTIONS[0]][FIELD].update(source='0'*40)),('methods',lambda a,b:a[SECTIONS[0]][FIELD].update(originalMethods=16)),('four100',lambda a,b:a[SECTIONS[0]][FIELD].update(four100SourcePrograms=4)),('incomplete-erased',lambda a,b:a[SECTIONS[0]][FIELD].update(incompleteSourcePrograms=0)),('unknown-erased',lambda a,b:a[SECTIONS[0]][FIELD].update(unknownOwnerPaths=0)),('context-lost',lambda a,b:a[SECTIONS[0]][FIELD].update(contextOriginalIds=[])),('old-runtime',lambda a,b:a[SECTIONS[0]].update(currentQualification={'forged':True})),('whole',lambda a,b:a[SECTIONS[1]][FIELD].update(currentWholeSourceQualification=True)),('bool-count',lambda a,b:a[SECTIONS[0]][FIELD].update(newAccepted=False)),('owner',lambda a,b:a['artifacts'][0].update(owner='WBS-F03')),('effort',lambda a,b:b.update(wholeEffortCompletionRate=50))]:
        a,b=json.loads(raw),json.loads(snap);mutate(a,b)
        changed=json.dumps(a,ensure_ascii=False).encode();b['inventorySha256']=data.sha(changed)
        try:contract(changed,json.dumps(b).encode(),old,old_snap,expected)
        except ValueError:labels.append(label)
        else:raise ValueError('incorrect metadata accepted: '+label)
    for name in ('481_PGPT詳細WBS.json','484_WBSコスト枠・細分化.json'):
        pth='documents/400_PGPT/470_PMO/'+name
        require((data.ROOT/pth).read_bytes()==subprocess.check_output(['git','show',BEFORE+':'+pth],cwd=data.ROOT),'original master/budget unchanged')
    after=audit();require(after['actualExit']==m['wholeWbsAuditBefore']['actualExit']==1 and after['lastError']=='ValueError: current physical candidate exact Git/worktree scope','actual whole audit before/after HOLD retained')
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,writerManifestSha256=PIN,inventorySha256=data.sha(raw),snapshotSha256=data.sha(snap),metadataNegativeVectors=len(labels),nonVacuousLabels=labels,originalMethods=15,originalSuites=4,originalExecs=3,four100SourcePrograms=3,incompleteSourcePrograms=1,unknownOwnerPaths=6,newContextRows=4,onlyTwoMetadataSectionsChanged=True,snapshotOnlyChangedField='inventorySha256',old995RuntimeAndQualificationUnchanged=True,wholeWbsAuditBefore=m['wholeWbsAuditBefore'],wholeWbsAuditAfter=after,productTestsExecuted=0,oldCoverageTransferred=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
