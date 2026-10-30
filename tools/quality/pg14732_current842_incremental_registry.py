"""Append eight original scopes to qualified816; derive physical counts and preserve prior proofs."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
NORMAL='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREVIOUS=('PG14680-current816-incremental-registry-v1','2060df0aefd44244ce8a944c79d96e800fbcd8abe5ed3bcfbb0c64e4fe8d3b29')
PREVIOUS_POST=('PG14683-current816-incremental-registry-post-v2','ada11a00d7ee4f5aea2c2881dd95dec2fdf086e09a661c4998ec8d9f77f6dbed')
NEW={
 'PG14692-batch-run-diagnostic-three-post-v1':('bae915b076e780950e98f2fbc99f6a086f921a76f42a94b596247cf036fd2c73',3,2),
 'PG14698-batch-cleanup-step-ten-post-v1':('854da25a8435d5be7f31f2704e23597fb18c84e22c863d91099c36998475f4b7',10,2),
 'PG14704-backup-manifest-values-eight-post-v1':('f963fce059a3362592ea62ff1fcdc52b2ce11832dd553bed3defbfd3f93cbb1e',8,1),
 'PG14714-web-security-exception-one-post-v1':('db3573d957a9835d775be15ab16bcad3f13f1b2bdbb2fcaa2b3ee332d2f8eb97',1,1),
 'PG14728-web-logging-exception-one-post-v2':('8db3113828fad40efde6ca9f6b8b349b204349fe274774027405412e4e28bab8',1,1),
 'PG14728-web-revocation-exception-one-post-v2':('f76681c7ca0e418926087390ccefe7b82bf5197722e7c38c0571773ea6badadb',1,1),
 'PG14728-web-media-exception-one-post-v2':('c055a0579f557b763f666efd914ca8220ea57a9f0ef38fcbe45f0578351f4190',1,1),
 'PG14728-web-session-exception-one-post-v2':('fc2d07048ae0912650e42454f5ebd24dd74eba80c16f91968cba25161edddc31',1,1)}
OUT=data.BASE/'PG14732-current842-incremental-registry-v1'

def require(ok,message):
    if not ok:raise ValueError(message)

def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only incremental registry')
    old,proof=read(PREVIOUS),read(PREVIOUS_POST)
    require(old['actualExit']==proof['actualExit']==0 and old['source']==proof['source']==SOURCE and proof['registryManifestSha256']==PREVIOUS[1],'qualified immediate prior source')
    require(proof['metadataNegativeVectors']==20 and proof['independentReturnedXmlAndJarClosure'] is True and all(json.dumps(proof['summary'][k],sort_keys=True)==json.dumps(old[k],sort_keys=True) for k in proof['summary']),'prior independent XML and typed summary proof')
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
    require((result['tests'],result['suites'],len(units),len(physical),result['originalExecs'],result['four100SourcePrograms'],result['naturalZeroBranchSourcePrograms'],result['metadataSourcePrograms'],result['incompleteSourcePrograms'])==(842,119,206,277,51,127,74,1,4),'actual fixed observation counts')
    require(result['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':164,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':80,'UNKNOWN':82} and len(generated)==5 and len(metadata)-len(generated)==6,'owners and five synthetic/six noCode remain distinct')
    require(all(units[n]==u for n,u in old['fullSourceUnits'].items()) and result['qualificationReplacedUnitHistory']==old['qualificationReplacedUnitHistory'] and result['additionalQualificationReferences']==old['additionalQualificationReferences'],'all old source proofs and Catalog replacement history retained')
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
