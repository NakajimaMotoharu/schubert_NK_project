"""Exact eleven-artifact candidate ownership overlay; public metadata only, no Product execution."""
import copy
from collections import Counter
import json
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_current11_v2 import canonical as old_canonical
from trace_owner_current12_v3 import SOURCE,RULES,canonical

OUT=data.BASE/'PG15408-current1800-exact12-owner-registry-v3'
PREV=('PG15396-current1800-auth-wire-policy-registry-v1','84e8cb25872c6b063a596e66ef45c631b6befc20769de36fbe06343ff40223c5')
POST=('PG15398-current1800-auth-wire-policy-registry-post-v1','0688cb78770d148a8472f8b4820fc0d556edfd01ecf4cbbb995545f39a9e4e47')
EXPECTED={"ApiStartupInputsTest":("WBS-P018-05",4),"OutboxPolicyTest":("WBS-P006-02",4),"OutboxModelTest":("WBS-P006-02",4),"OutboxDlqMetadataTest":("WBS-P006-02",2),"OutboxDispatchReportBoundaryTest":("WBS-P006-02",3),"QuestionCommandTimeBoundaryTest":("WBS-P011-03",3),"LoginUsernameTest":("WBS-P018-09",3),"PasswordPolicyTest":("WBS-P007-01",3),"LoginAttemptStateTest":("WBS-P007-01",5),"LoginAttemptSequenceTest":("WBS-P007-01",4),"AuthenticationResponseMapperTest":("WBS-P007-04",3),"AuthorizationServiceTest":("WBS-P007-03",2)}
def require(ok,message):
    if not ok:raise ValueError(message)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def outcome(fn,path,logical):
    try:return dict(kind='VALUE',value=fn(path,logical))
    except ValueError as exc:return dict(kind='REJECTED',error=str(exc))
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior=read(PREV),read(POST)
    require(old['actualExit']==prior['actualExit']==0 and old['source']==prior['source']==SOURCE and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34,'qualified exact current1760')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    normal=read(('PG14216-typed-marker-guard-six-compile-v1',old['normalManifestSha256']))
    require(normal['source']==SOURCE,'same source normal inputs')
    hashes=normal['begin']['inputHashes'];snapshot=data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/snapshot'
    require(len(RULES)==len(EXPECTED)==12 and {p.rsplit('/',1)[-1][:-5] for p in RULES}==set(EXPECTED),'exact explicitly reviewed names, not inferred namespace')
    checked={}
    def source(path):
        digest=hashes[path]
        require(data.sha((data.ROOT/path).read_bytes())==data.sha((snapshot/path).read_bytes())==digest,'unchanged source/snapshot/normal byte identity')
        checked[path]=digest
        return (data.ROOT/path).read_text()
    result=copy.deepcopy(old);proof=[];all_cases=set();posts={}
    for path,rule in RULES.items():
        name=path.rsplit('/',1)[-1][:-5];owner,count=EXPECTED[name]
        require(rule['owner']==owner and type(rule['originalTests']) is int and rule['originalTests']==count and rule['sha256']==hashes[path],'explicit owner/count/source')
        text=source(path);require(all(t in text for t in rule['tokens']),'reviewed body anchors, not substitute for manual review')
        anchor=rule['anchor'];source(anchor)
        require(anchor in logical and logical[anchor]['owner']==logical[anchor]['costOwner']==owner,'original baseline subject ownership')
        for subject in rule['subjects']:
            source(subject);require(logical[subject]['owner']==logical[subject]['costOwner']==owner,'multiple explicit subjects keep same baseline owner/cost')
        require(path not in logical and old['owners'][path]['ownershipStatus']=='UNKNOWN' and old['owners'][path]['canonicalOwner'] is None and old['owners'][path]['canonicalCostOwner'] is None,'exact old UNKNOWN, never overwrite baseline')
        pair=(rule['post'],rule['postSha256']);post=posts.setdefault(pair,read(pair))
        require(post['actualExit']==post['failures']==post['errors']==post['skipped']==0 and post['source']==SOURCE and post['normalManifestSha256']==old['normalManifestSha256'] and post['owners'][path]['sha256']==hashes[path],'original actual source post retained')
        cases=[]
        if count:
            cls=re.search(r'package\s+([^;]+);',text)[1]+'.'+name
            cases=[c for c in post['cases'] if c['classname']==cls]
            require(len(cases)==len({c['name'] for c in cases})==len(re.findall(r'@Test\b',text))==count,'whole original suite declarations and unique cases')
            for case in cases:
                require(case['result']=='PASS' and case['nonPass']==[] and re.search(r'\bvoid\s+'+re.escape(case['name'])+r'\s*\(',text),'original TestID/source method')
                require((case['classname'],case['name']) in {(v['classname'],v['name']) for v in old['cases']},'already counted, never new PT')
                all_cases.add((case['classname'],case['name']))
        resolved=canonical(path,logical)
        require(resolved['canonicalOwner']==resolved['canonicalCostOwner']==owner and resolved['ownershipStatus']=='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED','candidate only')
        result['owners'][path]={**old['owners'][path],**resolved}
        proof.append(dict(path=path,sha256=hashes[path],before=old['owners'][path],after=result['owners'][path],anchor=anchor,anchorSha256=hashes[anchor],subjectPaths=rule['subjects'],originalCases=cases,originalPost=list(pair),reason=rule['reason']))
    require(len(all_cases)==40 and len({a for a,b in all_cases})==12,'original63/10 refs only')
    require(all(result['owners'][p]==row and outcome(canonical,p,logical)==outcome(old_canonical,p,logical) for p,row in old['owners'].items() if p not in RULES),'all outside11 unchanged')
    labels=[]
    external=[p for p in old['owners'] if not p.startswith('src/')]
    require(external==['tools/quality/architecture/ProtocolCarrierBoundaryTest.java'],'exact existing non-src metadata reference')
    expected=outcome(old_canonical,external[0],logical)
    require(expected==dict(kind='REJECTED',error='bounded source namespace') and outcome(canonical,external[0],logical)==expected,'both scoped resolvers reject, row preserved')
    for bad in [dict(kind='VALUE',value=None),dict(kind='REJECTED',error='different'),dict(kind='VALUE',value=old['owners'][external[0]])]:
        require(bad!=expected,'outside namespace asymmetry rejected');labels.append('outside-outcome:'+str(len(labels)))
    for path,rule in RULES.items():
        synthetic=copy.deepcopy(logical);synthetic[path]=dict(path=path,owner='WBS-G01',costOwner='WBS-G03')
        require(canonical(path,synthetic)==old_canonical(path,synthetic),'baseline always wins');labels.append('baseline-wins:'+path)
        for label,field,value in [('missing',None,None),('owner','owner','WBS-G01'),('cost','costOwner','WBS-G01'),('path','path','src/not-the-anchor.java')]:
            bad=copy.deepcopy(logical)
            if field is None:del bad[rule['anchor']]
            else:bad[rule['anchor']][field]=value
            try:canonical(path,bad)
            except ValueError:labels.append(label+':'+path)
            else:raise ValueError('invalid anchor accepted')
    counts=dict(Counter(v['ownershipStatus'] for v in result['owners'].values()))
    require(counts=={'BASELINE_LOGICAL_REFERENCE':295,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':227,'UNKNOWN':103},'exact candidate-only delta')
    require(all(result[k]==v for k,v in old.items() if k!='owners'),'all original cases/counters/runtime/fees/old proofs unchanged')
    for p in posts.values():verify(p['invocation'])
    for p in [old,prior]:verify(p['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'owner-proof.json',dict(source=SOURCE,rows=proof,sourceHashes=checked,negativeLabels=labels,originalMethodsReferenced=40,originalSuitesReferenced=12,actualExit=0))
    result.update(invocation=invocation,ownerStatusCounts=counts,unknownOwnerPaths=103,ownershipRuleRevision='PG-D937_EXACT12_V3_CANDIDATE_ONLY',ownershipOverlayPreviousRegistry=list(PREV),ownershipOverlayPreviousPost=list(POST),ownershipProofSha256=data.sha((OUT/'owner-proof.json').read_bytes()),ownershipRuleSha256=data.sha((data.ROOT/'tools/quality/trace_owner_current12_v3.py').read_bytes()),ownershipContractVectors=len(labels),newProductExecutionsForOwnership=0,newTestIdsForOwnership=0,newAcceptedForOwnership=0,historicalCostsReallocated=False)
    data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
