"""Independent finite G13 set/byte/owner diagnostic post; no whole qualification promotion."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import wbs_candidate_trace as trace
import pg15848_g13_physical_scope_diagnosis as original

PIN='c3dc199b0393b4aeccd21ec4dc5bacca23e596b8b55f4dd2977af32d985f1468'
OUT=data.BASE/'PG15850-g13-physical-scope-post-v1'
def require(ok,message):
    if not ok:raise ValueError(message)
def assess(p,rows,changed,current,old):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['beforeGit']==original.BEFORE and p['frozenCandidateSource']=='e7d64fda2453e906ee6ccc5fe718e5c29841e4aa','same exact sources')
    require((p['historicalLogicalArtifacts'],p['frozenCandidateArtifacts'],p['currentProductionArtifacts'],p['currentTrackedArtifacts'],p['addedArtifacts'],p['removedArtifacts'],p['changedCommonArtifacts'])==(941,943,1065,1065,122,0,24),'exact counts, not old whole replay')
    require(p['addedKinds']=={'DEPLOYMENT':8,'JAVA':114} and p['addedCanonicalCandidateOwners']=={'WBS-C07':8,'WBS-P018-05':1,'WBS-P018-09':113} and p['unknownAddedCanonicalOwners']==0,'explicit rules, not engineering group ownership')
    require(p['candidateEqualsItsOwnGit'] is p['currentTrackedEqualsProductionGit'] is p['allCurrentPhysicalBytesMatchProduction'] is True,'three scope/byte domains checked')
    require(all(p[k] is False for k in ['oldInventoryAndCandidateModified','currentWholeSourceQualified','wholeWbsScopeGuardRelaxed','wholeWbsAuditRerun','wholeG13Accepted','formalUpdated','oldNativeTransferred','privateRawRead']) and all(type(p[k]) is int and p[k]==0 for k in ['productTestsExecuted','newAccepted','externalActions']) and p['effortPercent'] is None,'diagnostic not acceptance or execution')
    require(len(rows)==len({r['path'] for r in rows})==122 and {r['path'] for r in rows}==set(current)-set(old),'all exact additions, no duplicates')
    stop='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiStopBudget.java'
    for row in rows:
        path=row['path'];expected='WBS-C07' if path.startswith('src/deployment/monitoring/') else 'WBS-P018-05' if path==stop else 'WBS-P018-09'
        require(row['sha256']==data.sha(current[path]) and row['canonicalOwner']==row['canonicalCostOwner']==expected and row['ownershipStatus']=='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED','exact current byte and pre-existing owner rule')
        require(row['accepted'] is row['currentRuntimeQualification'] is False and type(row['additionalBudgetPp']) is int and row['additionalBudgetPp']==0,'no new cost/acceptance/current runtime')
    expected_changed={path for path in set(current)&set(old) if data.sha(current[path])!=old[path]['sha256']}
    require(len(changed)==len({r['path'] for r in changed})==24 and {r['path'] for r in changed}==expected_changed,'all changed common bytes')
    for row in changed:
        require(row['currentSha256']==data.sha(current[row['path']]) and row['oldSha256']==old[row['path']]['sha256'] and row['oldQualificationTransferred'] is False,'no common byte/source result transfer')
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p=data.read_checked(original.OUT/'manifest.json',PIN)
    rows=data.read_checked(original.OUT/'added-public-artifacts.json',p['addedArtifactsSha256'])
    changed=data.read_checked(original.OUT/'changed-common-artifacts.json',p['changedCommonArtifactsSha256'])
    raw=subprocess.check_output(['git','show',original.BEFORE+':'+original.INV],cwd=data.ROOT)
    require(data.sha(raw)==p['inventorySha256'] and raw==(data.ROOT/original.INV).read_bytes(),'canonical 485 unchanged by diagnostic')
    inv=json.loads(raw);candidate=inv['currentPhysicalCandidate'];old={r['path']:r for r in candidate['artifacts']}
    paths={path for path in trace.git_files(original.SOURCE) if ('/src/main/java/' in path and path.endswith('.java')) or '/src/main/resources/' in path or path.startswith('src/deployment/')}
    current=trace.git_artifacts(original.SOURCE,sorted(paths))
    assess(p,rows,changed,current,old)
    negatives=[]
    for key,value in [('source','0'*40),('currentProductionArtifacts',943),('addedArtifacts',0),('removedArtifacts',1),('changedCommonArtifacts',0),('wholeG13Accepted',True),('wholeWbsScopeGuardRelaxed',True),('currentWholeSourceQualified',True),('newAccepted',False),('effortPercent',0),('oldNativeTransferred',True)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:assess(bad,rows,changed,current,old)
        except ValueError:negatives.append(key)
        else:raise ValueError('false physical closure: '+key)
    for label,mutate in [('owner-promotion',lambda r,c:r[0].update(canonicalOwner='WBS-G13.07')),('baseline-promotion',lambda r,c:r[0].update(ownershipStatus='BASELINE_LOGICAL_REFERENCE')),('missing-addition',lambda r,c:r.pop()),('duplicate-addition',lambda r,c:r.__setitem__(0,r[1])),('common-transfer',lambda r,c:c[0].update(oldQualificationTransferred=True)),('wrong-current-byte',lambda r,c:c[0].update(currentSha256='0'*64))]:
        rr=copy.deepcopy(rows);cc=copy.deepcopy(changed);mutate(rr,cc)
        try:assess(p,rr,cc,current,old)
        except ValueError:negatives.append(label)
        else:raise ValueError('false scope row: '+label)
    verify(p['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,parentManifestSha256=PIN,addedArtifactsSha256=p['addedArtifactsSha256'],changedCommonArtifactsSha256=p['changedCommonArtifactsSha256'],historicalLogicalArtifacts=941,frozenCandidateArtifacts=943,currentProductionArtifacts=1065,addedArtifacts=122,removedArtifacts=0,changedCommonArtifacts=24,independentNegativeVectors=len(negatives),negativeLabels=negatives,oldWholeSourceQualificationTransferred=False,currentWholeSourceQualified=False,wholeG13Accepted=False,wholeWbsScopeGuardRelaxed=False,productTestsExecuted=0,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,independentNegativeVectors=len(negatives),wholeG13Accepted=False)))
if __name__=='__main__':main()
