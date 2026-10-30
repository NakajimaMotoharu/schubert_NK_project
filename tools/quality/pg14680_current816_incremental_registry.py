"""Append four current original scopes to qualified772, retaining every prior proof and gap."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
NORMAL='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREVIOUS=('PG14636-current-thirty-nine-host772-registry-v1','a657d2fead98629001f67b0e842b94adfd86a041b10651f624f7d6cd4c76adfe')
PREVIOUS_POST=('PG14638-current-thirty-nine-host772-registry-post-v1','40331416953e2194f25b66fe5b8876217268c32f1b5aa5a5d68cab339dce42a8')
NEW={
 'PG14648-storage-catalog-whole-five-post-v1':('9d5ed8c6f6c774a973c0bbc1c48e598c36564da71715e9450492d1998e420a2f',5,2),
 'PG14654-storage-resource-whole-twenty-six-post-v1':('64716d82a4588387921fc49a0cdb423c79b661c22429a7a5662ab56edcac5a5f',26,2),
 'PG14660-question-plain-whole-eight-post-v1':('f3db377596bf97bb831e6e538a46e3a62bc383eaad88533e4d14f120f3e9c79f',8,1),
 'PG14678-batch-cleanup-pure-five-post-v1':('b5a30fe1a983ec6dc556b5af6c92c28bf436f528aedfa4e6e22b2e4ae4a1c61c',5,2)}
OUT=data.BASE/'PG14680-current816-incremental-registry-v1'

def require(ok,message):
    if not ok:raise ValueError(message)

def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only incremental registry')
    old,proof=read(PREVIOUS),read(PREVIOUS_POST)
    require(old['actualExit']==proof['actualExit']==0 and old['source']==proof['source']==SOURCE and proof['registryManifestSha256']==PREVIOUS[1],'qualified immediate prior source')
    require(proof['metadataNegativeVectors']==27 and proof['postSummaryNegativeVectors']==3 and proof['summaryBoundToVerifiedActualFields'] is True,'prior independent XML and summary proof')
    verify(old['invocation']);verify(proof['invocation'])
    normal=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json',NORMAL);hashes=normal['begin']['inputHashes']
    require(normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items()),'all normal current inputs unchanged')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    result=copy.deepcopy(old);cases={(r['classname'],r['name']) for r in old['cases']};new_cases=set()
    units=result['fullSourceUnits'];owners=result['owners'];metadata=result['metadataClasses']
    for name,(pin,count,suites) in NEW.items():
        p=read((name,pin));verify(p['invocation'])
        require(p['source']==SOURCE and p['normalManifestSha256']==NORMAL and p['actualExit']==0 and p['tests']==count and p['suites']==suites,'genuine independent new original scope')
        require(all(type(p[k]) is int and p[k]==0 for k in ['failures','errors','skipped','reruns','newTestIds','newAccepted']),'no non-PASS or invented acceptance')
        require(p['singleSession'] is True and p['crcMismatch']==0 and p['priorProductResultsReused'] is p['oldCoverageTransferred'] is p['formalUpdated'] is p['whole451Accepted'] is p['wholeF03Accepted'] is False,'same current source only, no coverage union/formal promotion')
        require(p.get('originalTestsCountedElsewhere',False) is False and p['completeSourceCoverageMeasured'] is True,'new original methods, complete Source closures')
        local={(r['classname'],r['name']) for r in p['cases']}
        require(len(local)==count and not cases&local and all(r['result']=='PASS' and not r['nonPass'] for r in p['cases']),'no duplicate or failed original methods')
        cases.update(local);new_cases.update(local)
        for path,owned in p['owners'].items():
            require(owned['sha256']==hashes[path] and all(owned[k]==v for k,v in canonical(path,logical).items()),'canonical known/candidate/UNKNOWN retained')
            require(path not in owners or owners[path]==owned,'consistent shared path owner');owners[path]=owned
        for meta in p.get('metadataClasses',[]):
            require(meta not in metadata and p['manualCounterExclusions']==[] and p['officialGeneratedFiltersUnchanged'] is True,'no metadata exclusion or overlap')
            info=p['sourcePhysicalInventory'][meta]
            if any(m['hasCode'] for m in info['methods']):
                require(meta=='dev/codex/schubert/nk/storage/ServiceCredentialId$1' and info['flags']==4128 and info['sourceFile']=='ServiceCredentialId.java' and info['methods']==[dict(name='<clinit>',descriptor='()V',flags=8,hasCode=True,codeLength=40)] and p['physicalClasses'][meta]=='ee7584ed10c19ff4b608b4343809a09137d06137957663a657e105f5134799d0','exact code-bearing synthetic, not noCode')
                kind='COMPILER_SYNTHETIC_STANDARD_FILTER'
            else:
                require(info['flags']==1537 and meta.startswith('dev/codex/schubert/nk/storage/ResourceScope$'),'exact abstract ResourceScope port')
                kind='NO_CODE'
            metadata[meta]=dict(kind=kind,sha256=p['physicalClasses'][meta],postSha256=pin)
        for source,unit in p['fullSourceUnits'].items():
            require(source not in units,'never merge coverage execs of one Source')
            counters=unit['totals'];four=all(v['missed']==0 and v['covered']>0 for v in counters.values())
            require(set(counters)=={'LINE','METHOD','CLASS','BRANCH'} and unit['four100'] is four,'measured four counters, misses retained')
            no_code=set(unit['physical'])<=set(p.get('metadataClasses',[]));natural=not no_code and counters['BRANCH']==dict(missed=0,covered=0)
            require(not natural or all(counters[k]['missed']==0 and counters[k]['covered']>0 for k in ['LINE','METHOD','CLASS']),'natural branch0 not untested code')
            require(set(unit['physical'])==set(p['completeSourceUnitClosure'][source]) and set(unit['physical'])<=set(p['physicalClasses']),'full physical closure')
            units[source]=dict(post=name,postSha256=pin,physical=unit['physical'],counters=counters,four100=four,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=no_code,branchNaturallyZero=natural)
        result['originalPostReferences'].append(dict(name=name,sha256=pin,tests=count,suites=suites,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='ORIGINAL_SCOPED_PT_NOT_WHOLE_451'))
    physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};natural={n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']}
    require(sum(len(u['physical']) for u in units.values())==len(physical),'physical closures disjoint')
    generated={n for n,v in metadata.items() if v['kind']=='COMPILER_SYNTHETIC_STANDARD_FILTER'}
    result.update(invocation=invocation,previousUniqueRegistryReference=list(PREVIOUS),previousRegistryPostReference=list(PREVIOUS_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+len(NEW),measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-metadata.keys()),metadataPhysical=len(metadata),generatedMetadataPhysical=len(generated),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-metadata.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len(natural),metadataSourcePrograms=sum(u['metadataOnly'] for u in units.values()),incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in owners.values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in owners.values()),totalProductExecs=old['totalProductExecs']+len(NEW),totalMethodExecutions=old['totalMethodExecutions']+len(new_cases),uniqueProductMethodDelta=len(new_cases),sourceProgramDelta=len(units)-len(old['fullSourceUnits']))
    require((result['tests'],result['suites'],len(units),len(physical),result['originalExecs'],result['four100SourcePrograms'],result['naturalZeroBranchSourcePrograms'],result['metadataSourcePrograms'],result['incompleteSourcePrograms'])==(816,109,189,254,43,117,67,1,4),'actual fixed observation counts')
    require(result['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':147,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':80,'UNKNOWN':72} and len(generated)==5 and len(metadata)-len(generated)==6,'owners and five synthetic/six noCode remain distinct')
    require(all(units[n]==u for n,u in old['fullSourceUnits'].items()) and result['qualificationReplacedUnitHistory']==old['qualificationReplacedUnitHistory'] and result['additionalQualificationReferences']==old['additionalQualificationReferences'],'all old source proofs and Catalog replacement history retained')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
