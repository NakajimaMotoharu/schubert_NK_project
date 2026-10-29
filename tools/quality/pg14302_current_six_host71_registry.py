"""Bind six original completed current-source posts without replay; natural0/noCode are not four100."""
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
NORMAL_PIN='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
POSTS={
 'PG14244-delivery-metadata-whole-two-post-v1':('14f6fb3937435588c58bfa0cdbe7fa6b0ef04b0b3eed7436b4918cd1f15a63bd',2,1),
 'PG14254-inbound-primary-whole-five-post-v1':('d1c31c2b14489e72fe15ab7a72188746a8ec7ce78439c3ebab659dcaad4a08f6',5,1),
 'PG14258-protocol-carrier-whole-eight-post-v1':('2b9ce8ebf4b329a2e36d329bcf7cb91a9396fbe2c40dd6be09fdaa1247ac1e9a',8,2),
 'PG14272-web-three-forms-whole-twenty-four-post-v1':('09fe225e89c4366efb79605456382c56aa4cde8e7392017cb2ae785b19250c0b',24,3),
 'PG14294-web-user-create-whole-eight-post-v1':('0b744221948357f4aadf98a89bddee5fd97988d42ad1c8b4a9e7059da6a3de5b',8,1),
 'PG14298-web-target-mutation-whole-twenty-four-post-v1':('2836720bd34b54355f65fff51f67c6a1f0ccf2a6d4f3791ffcb99260f7803012',24,2)}
OUT=data.BASE/'PG14302-current-six-host71-registry-v1'

def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only source registry')
    normal=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json',NORMAL_PIN)
    require(normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0,'current normal source, no historical PT transfer')
    hashes=normal['begin']['inputHashes'];require(all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items()),'all current input hashes fixed')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    cases=[];suites=set();units={};owners={};entries=[]
    for name,(pin,count,suite_count) in POSTS.items():
        post=data.read_checked(data.BASE/name/'manifest.json',pin)
        require(post['source']==SOURCE and post['normalManifestSha256']==NORMAL_PIN and post['actualExit']==0,'same-source genuine post')
        require(post['tests']==count and post['suites']==suite_count and all(post[k]==0 for k in ('failures','errors','skipped','reruns','newTestIds','newAccepted')),'exact actual original case counts')
        require(post['singleSession'] is True and post['crcMismatch']==0 and post['priorProductResultsReused'] is False and post['oldCoverageTransferred'] is False,'one exec CRC without old result transfer')
        require(post['whole451Accepted'] is post['wholeF03Accepted'] is post['formalUpdated'] is False,'no whole/formal promotion')
        require(post['completeSourceCoverageMeasured'] is True and len(post['cases'])==count and len(post['fullSourceUnits'])==post['targetSourceUnits'],'complete scoped source measurement, not automatically four100')
        local={(r['classname'],r['name']) for r in post['cases']}
        require(len(local)==count and all(r['result']=='PASS' and not r['nonPass'] for r in post['cases']),'unique successful original methods')
        cases.extend(sorted(local));suites.update(r[0] for r in local)
        for p,owned in post['owners'].items():
            require(hashes[p]==owned['sha256'] and all(owned[k]==v for k,v in canonical(p,logical).items()),'preserve exact known/unknown canonical owner')
            if p in owners:require(owners[p]==owned,'consistent shared owner')
            owners[p]=owned
        for source_name,unit in post['fullSourceUnits'].items():
            require(source_name not in units,'source counters belong to a single original exec, never a union')
            counters=unit['totals'];require(set(counters)=={'LINE','METHOD','CLASS','BRANCH'},'four explicit counters')
            require(all(type(v[k]) is int and v[k]>=0 for v in counters.values() for k in ('covered','missed')),'typed measured counters')
            qualified=all(v['missed']==0 and v['covered']>0 for v in counters.values())
            require(unit['four100'] is qualified,'measured four100 including explicit misses')
            metadata=set(unit['physical'])<=set(post.get('metadataClasses',[]))
            natural=not metadata and counters['BRANCH']==dict(missed=0,covered=0)
            require(set(unit['physical'])<=set(post['physicalClasses']) and all(n in post['executable'] or n in post.get('metadataClasses',[]) for n in unit['physical']),'full declared physical closure including metadata')
            if metadata:
                require(all(v==dict(missed=0,covered=0) for v in counters.values()),'noCode has no invented counters')
                require(all(not m['hasCode'] for n in unit['physical'] for m in post['sourcePhysicalInventory'][n]['methods']),'all metadata methods without code')
            if natural:require(all(counters[k]['missed']==0 and counters[k]['covered']>0 for k in ['LINE','METHOD','CLASS']),'natural0 retains full executable coverage')
            units[source_name]=dict(post=name,postSha256=pin,physical=unit['physical'],counters=counters,four100=qualified,execSha256=post['execSha256'],sessionIdentity=post['sessionIdentity'],metadataOnly=metadata,branchNaturallyZero=natural)
        entries.append(dict(name=name,sha256=pin,tests=count,suites=suite_count,execSha256=post['execSha256'],sessionIdentity=post['sessionIdentity'],scope='ORIGINAL_SCOPED_PT_NOT_WHOLE_451'))
    require(len(cases)==len(set(cases))==71 and len(suites)==10 and len(units)==17,'three original executions/15 methods/four suites/four full Source units')
    require(sum(u['four100'] for u in units.values())==9 and sum(len(u['physical']) for u in units.values())==21,'three qualified physical Source units, one unqualified')
    require(sum(u['branchNaturallyZero'] for u in units.values())==6 and sum(u['metadataOnly'] for u in units.values())==1,'separate natural branch0 and noCode')
    pending={n:u for n,u in units.items() if not u['four100'] and not u['branchNaturallyZero'] and not u['metadataOnly']}
    require(len(pending)==1 and next(iter(pending)).endswith('/InboundTransactions'),'retain actual incomplete Source')
    remain=next(iter(pending.values()))['counters']
    require(remain['LINE']['missed']==10 and remain['METHOD']['missed']==2,'incomplete actual ten lines/two methods unchanged')
    require(len(owners)==27 and sum(v['canonicalOwner'] is None for v in owners.values())==12,'two known and six unknown path owners, no invented canonical')
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,normalManifestSha256=NORMAL_PIN,originalPostReferences=entries,cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted(suites),tests=71,suites=10,originalExecs=6,fullSourceUnits=units,measuredSourcePrograms=17,measuredPhysical=21,executablePhysical=20,metadataPhysical=1,four100SourcePrograms=9,four100Physical=13,naturalZeroBranchSourcePrograms=6,metadataSourcePrograms=1,incompleteSourcePrograms=1,owners=owners,unknownOwnerPaths=12,priorSource0061TestsTransferred=False,coverageExecUnion=False,originalTestsReexecutedByRegistry=0,newTestIds=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
