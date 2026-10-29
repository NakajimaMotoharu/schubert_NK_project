"""Independent current133 WBS side counts bind real registry and corrected post summary, with historical semantics intact."""
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg9954_pure_query_registry_metadata import INV,SNAP,SECTIONS
from pg9338_wbs_reference_metadata_post import validate
from pg9880_snapshot_nonce_trace import audit
from pg14336_current_ten_host133_wbs import SOURCE,BEFORE,FIELD,REG,POST

OUT=data.BASE/'PG14338-current-ten-host133-wbs-post-v1'
PIN='e5eb2fb43281a3d1729f6575bfa81edd1a3692c9cff515bd382435ce7dafbb32'

def require(ok,message):
    if not ok:raise ValueError(message)

def wire(value):return json.dumps(value,sort_keys=True)

def contract(raw,snap,old,old_snap,expected):
    validate(raw,snap,old,old_snap);parsed=json.loads(raw)
    for name in SECTIONS:require(wire(parsed[name].pop(FIELD))==wire(expected),'exact typed registry/context overlay, no current whole qualification')
    require(wire(parsed)==wire(old),'all old fields/runtime/qualification/budget and types unchanged')

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only independent post')
    m=data.read_checked(data.BASE/'PG14336-current-ten-host133-wbs-v1/manifest.json',PIN)
    r,p=[data.read_checked(data.BASE/name/'manifest.json',pin) for name,pin in (REG,POST)]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in (m,r,p)),'genuine same source references')
    require(p['registryManifestSha256']==REG[1] and p['metadataNegativeVectors']==17 and p['originalXmlMethods']==133 and p['postSummaryNegativeVectors']==3 and p['unknownOwnerPaths']==23,'independent original XML registry binding')
    path=lambda v:str((data.BASE/v[0]/'manifest.json').relative_to(data.ROOT))
    expected=dict(source=SOURCE,registryManifest=path(REG),registrySha256=REG[1],registryPostManifest=path(POST),registryPostSha256=POST[1],record='evidence/01_PT/018_NK-OPS-001/2642_現十host133件・生成metadata区分_限定registry参照結果.md',originalExecs=10,originalMethods=133,originalSuites=21,fullSourceMeasured=39,measuredPhysical=46,executablePhysical=44,metadataPhysical=2,generatedMetadataPhysical=1,four100SourcePrograms=20,four100Physical=26,four100ExecutablePhysical=25,naturalZeroBranchSourcePrograms=17,naturalZeroBranchPhysical=18,metadataSourcePrograms=1,incompleteSourcePrograms=1,unknownOwnerPaths=23,supplementalOwnershipCandidateCount=1,coverageExecUnion=False,oldSource0061RuntimeTransferred=False,old995RuntimeAndQualificationUnchanged=True,previousPG14306Registry71Preserved=True,currentWholeSourceQualification=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None)
    mapping={'originalExecs':'originalExecs','originalMethods':'tests','originalSuites':'suites','fullSourceMeasured':'measuredSourcePrograms','measuredPhysical':'measuredPhysical','executablePhysical':'executablePhysical','metadataPhysical':'metadataPhysical','generatedMetadataPhysical':'generatedMetadataPhysical','four100SourcePrograms':'four100SourcePrograms','four100Physical':'four100Physical','four100ExecutablePhysical':'four100ExecutablePhysical','naturalZeroBranchSourcePrograms':'naturalZeroBranchSourcePrograms','naturalZeroBranchPhysical':'naturalZeroBranchPhysical','metadataSourcePrograms':'metadataSourcePrograms','incompleteSourcePrograms':'incompleteSourcePrograms','unknownOwnerPaths':'unknownOwnerPaths'}
    require(all(wire(expected[k])==wire(r[v]) for k,v in mapping.items()),'every WBS count derives from verified registry, not shared literal mistakes')
    require(expected['supplementalOwnershipCandidateCount']==len(r['supplementalOwnershipCandidates'])==1,'prior candidate only')
    original,snapshot=[subprocess.check_output(['git','show',BEFORE+':'+name],cwd=data.ROOT) for name in (INV,SNAP)]
    old,old_snap=json.loads(original),json.loads(snapshot)
    raw,snap=(data.ROOT/INV).read_bytes(),(data.ROOT/SNAP).read_bytes()
    require(data.sha(raw)==m['inventorySha256'] and data.sha(snap)==m['snapshotSha256'],'exact actual full WBS byte binding')
    contract(raw,snap,old,old_snap,expected);labels=[]
    for label,mutate in [('source',lambda a,b:a[SECTIONS[0]][FIELD].update(source='0'*40)),('methods',lambda a,b:a[SECTIONS[0]][FIELD].update(originalMethods=134)),('four100',lambda a,b:a[SECTIONS[0]][FIELD].update(four100SourcePrograms=21)),('incomplete-erased',lambda a,b:a[SECTIONS[0]][FIELD].update(incompleteSourcePrograms=0)),('unknown-erased',lambda a,b:a[SECTIONS[0]][FIELD].update(unknownOwnerPaths=0)),('natural0-lost',lambda a,b:a[SECTIONS[0]][FIELD].update(naturalZeroBranchSourcePrograms=0)),('metadata-forged',lambda a,b:a[SECTIONS[0]][FIELD].update(metadataSourcePrograms=0)),('stale-unknown12',lambda a,b:a[SECTIONS[0]][FIELD].update(unknownOwnerPaths=12)),('generated-erased',lambda a,b:a[SECTIONS[0]][FIELD].update(generatedMetadataPhysical=0)),('candidate-erased',lambda a,b:a[SECTIONS[0]][FIELD].update(supplementalOwnershipCandidateCount=0)),('old-runtime',lambda a,b:a[SECTIONS[0]].update(currentQualification={'forged':True})),('whole',lambda a,b:a[SECTIONS[1]][FIELD].update(currentWholeSourceQualification=True)),('bool-count',lambda a,b:a[SECTIONS[0]][FIELD].update(newAccepted=False)),('owner',lambda a,b:a['artifacts'][0].update(owner='WBS-F03')),('effort',lambda a,b:b.update(wholeEffortCompletionRate=50))]:
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,writerManifestSha256=PIN,inventorySha256=data.sha(raw),snapshotSha256=data.sha(snap),metadataNegativeVectors=len(labels),nonVacuousLabels=labels,originalMethods=r['tests'],originalSuites=r['suites'],originalExecs=r['originalExecs'],four100SourcePrograms=r['four100SourcePrograms'],naturalZeroBranchSourcePrograms=r['naturalZeroBranchSourcePrograms'],metadataSourcePrograms=r['metadataSourcePrograms'],generatedMetadataPhysical=r['generatedMetadataPhysical'],incompleteSourcePrograms=r['incompleteSourcePrograms'],unknownOwnerPaths=p['unknownOwnerPaths'],onlyTwoMetadataSectionsChanged=True,snapshotOnlyChangedField='inventorySha256',old995RuntimeAndQualificationUnchanged=True,wholeWbsAuditBefore=m['wholeWbsAuditBefore'],wholeWbsAuditAfter=after,productTestsExecuted=0,oldCoverageTransferred=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
