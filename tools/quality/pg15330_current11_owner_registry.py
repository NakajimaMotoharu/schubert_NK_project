"""Exact eleven-artifact candidate ownership overlay; public metadata only, no Product execution."""
import copy
from collections import Counter
import json
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical as old_canonical
from trace_owner_current11_v2 import SOURCE,RULES,canonical

OUT=data.BASE/'PG15330-current1760-exact11-owner-registry-v2'
PREV=('PG15312-current1760-api-port-required-registry-v1','4b526f197b393c25f9d77293ad2dad1e7ab91a1724c835aa6bb552385397d080')
POST=('PG15314-current1760-api-port-required-registry-post-v1','5029262deaaafab2fe1b1ff4a6f7472a547941126eef469078262b554fea2c86')
EXPECTED={'ApiNonSecretConfigTest':('WBS-P018-01',7),'WebNonSecretConfigTest':('WBS-P018-01',7),'ApiStopBudget':('WBS-P018-05',0),'ApiStopBudgetTest':('WBS-P018-05',18),'FixedServiceExecArgumentsTest':('WBS-P018-04',5),'FixedNativeCoverageProfileTest':('WBS-P018-08',5),'TerminalNativeCoverageProfileTest':('WBS-P018-08',4),'FixedNativeCoverageTerminalTest':('WBS-P018-08',5),'ApiAdmittedConfigurationTest':('WBS-P018-05',8),'ApiReadinessPredicateTest':('WBS-P018-05',3),'RequiredColumnTest':('WBS-P004-05',1)}
def require(ok,message):
    if not ok:raise ValueError(message)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior=read(PREV),read(POST)
    require(old['actualExit']==prior['actualExit']==0 and old['source']==prior['source']==SOURCE and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34,'qualified exact current1760')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    normal=read(('PG14216-typed-marker-guard-six-compile-v1',old['normalManifestSha256']))
    require(normal['source']==SOURCE,'same source normal inputs')
    hashes=normal['begin']['inputHashes'];snapshot=data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/snapshot'
    require(len(RULES)==len(EXPECTED)==11 and {p.rsplit('/',1)[-1][:-5] for p in RULES}==set(EXPECTED),'exact explicitly reviewed names, not inferred namespace')
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
        for subject in rule['subjects']:source(subject)
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
    require(len(all_cases)==63 and len({a for a,b in all_cases})==10,'original63/10 refs only')
    clock=source(next(p for p in checked if p.endswith('/ApiProcessLifetime.java')))
    require(all(t in clock for t in ['private final ApiStopBudget stopBudget;','stopBudget = new ApiStopBudget(nanos);','stopBudget.begin();','return stopBudget.remainingNanos();']),'real baseline lifetime field/construction/begin/remaining delegation')
    require(all(result['owners'][p]==row and canonical(p,logical)==old_canonical(p,logical) for p,row in old['owners'].items() if p not in RULES),'all outside11 unchanged')
    labels=[]
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
    require(counts=={'BASELINE_LOGICAL_REFERENCE':277,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':215,'UNKNOWN':103},'exact candidate-only delta')
    require(all(result[k]==v for k,v in old.items() if k!='owners'),'all original cases/counters/runtime/fees/old proofs unchanged')
    for p in posts.values():verify(p['invocation'])
    for p in [old,prior]:verify(p['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'owner-proof.json',dict(source=SOURCE,rows=proof,sourceHashes=checked,negativeLabels=labels,originalMethodsReferenced=63,originalSuitesReferenced=10,actualExit=0))
    result.update(invocation=invocation,ownerStatusCounts=counts,unknownOwnerPaths=103,ownershipRuleRevision='PG-D936_EXACT11_V2_CANDIDATE_ONLY',ownershipOverlayPreviousRegistry=list(PREV),ownershipOverlayPreviousPost=list(POST),ownershipProofSha256=data.sha((OUT/'owner-proof.json').read_bytes()),ownershipRuleSha256=data.sha((data.ROOT/'tools/quality/trace_owner_current11_v2.py').read_bytes()),ownershipContractVectors=len(labels),newProductExecutionsForOwnership=0,newTestIdsForOwnership=0,newAcceptedForOwnership=0,historicalCostsReallocated=False)
    data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
