"""Independent proof replacement, original unique counts unchanged, 23 metadata and three summary negatives."""
import copy
import json
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg14562_catalog_two_source_proof_resolution import SOURCE,OLD,OLD_POST,NEW,TARGETS
from pg14548_current_thirty_one_host660_registry_post import contract

OUT=data.BASE/'PG14564-catalog-two-source-proof-resolution-post-v1'
PIN='0eade5a1336d0c4a01bd6a951e1c1310278ee6a3376ee448a95903b904ec68ab'

def main():
    invocation=capture(__file__);assert not OUT.exists()
    value=data.read_checked(data.BASE/'PG14562-catalog-two-source-proof-resolution-v1/manifest.json',PIN)
    old,post,new=[data.read_checked(data.BASE/n/'manifest.json',h) for n,h in (OLD,OLD_POST,NEW)]
    assert all(v['actualExit']==0 and v['source']==SOURCE for v in (value,old,post,new))
    verify(value['invocation']);verify(post['invocation']);verify(new['invocation'])
    assert post['registryManifestSha256']==OLD[1] and post['originalXmlMethods']==660 and post['originalXmlSuites']==86
    assert new['previousUniqueRegistryManifestSha256']==OLD[1] and new['singleSession'] and new['crcMismatch']==0 and new['qualificationReplacementComplete']
    normal=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json',old['normalManifestSha256'])
    assert normal['source']==SOURCE and new['normalManifestSha256']==old['normalManifestSha256']
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert all(data.sha(Path(j['path']).read_bytes())==j['sha256'] for j in normal['jars'].values())
    assert len(new['cases'])==len({(c['classname'],c['name']) for c in new['cases']})==56
    assert {(c['classname'],c['name']) for c in new['cases']}<={(c['classname'],c['name']) for c in old['cases']}
    assert new['uniqueProductMethodDelta']==new['sourceProgramDelta']==0 and new['additionalQualificationProductJvms']==1
    expected=copy.deepcopy(old);units=copy.deepcopy(old['fullSourceUnits']);history={}
    assert set(new['fullSourceUnits'])==TARGETS and all(old['owners'][p]==v for p,v in new['owners'].items())
    for name in TARGETS:
        prior=old['fullSourceUnits'][name];u=new['fullSourceUnits'][name]
        assert prior['counters']['LINE']['missed']==prior['counters']['METHOD']['missed']==1 and not prior['four100']
        assert prior['physical']==u['physical'] and all(c['missed']==0 and c['covered']>0 for c in u['totals'].values())
        history[name]=copy.deepcopy(prior)
        units[name]=dict(post=NEW[0],postSha256=NEW[1],physical=u['physical'],counters=u['totals'],four100=True,execSha256=new['execSha256'],sessionIdentity=new['sessionIdentity'],metadataOnly=False,branchNaturallyZero=False)
    assert all(u['four100'] is all(c['missed']==0 and c['covered']>0 for c in u['counters'].values()) for u in units.values())
    full=[u for u in units.values() if u['four100']]
    pending={n:u for n,u in units.items() if not u['four100'] and not u['branchNaturallyZero'] and not u['metadataOnly']}
    assert len(units)==160 and len(full)==98 and set(pending)=={'dev/codex/schubert/nk/api/messaging/inbound/InboundTransactions'}
    gap=next(iter(pending.values()))['counters'];assert gap['LINE']['missed']==10 and gap['METHOD']['missed']==2
    references=[dict(name=NEW[0],sha256=NEW[1],execSha256=new['execSha256'],sessionIdentity=new['sessionIdentity'],repeatedMethods=56,newMethods=0,newSourcePrograms=0,productJvms=1,purpose=new['qualificationPurpose'])]
    expected.update(invocation=value['invocation'],fullSourceUnits=units,four100SourcePrograms=98,four100Physical=sum(len(u['physical']) for u in full),four100ExecutablePhysical=sum(n not in old['metadataClasses'] for u in full for n in u['physical']),incompleteSourcePrograms=1,previousUniqueRegistryReference=OLD,previousRegistryPostReference=OLD_POST,additionalQualificationReferences=references,qualificationReplacedUnitHistory=history,additionalQualificationExecs=1,totalProductExecs=32,totalMethodExecutions=716,uniqueProductMethodDelta=0,sourceProgramDelta=0,sourceReplacementPreservesOriginalCases=True)
    assert expected['four100Physical']==138 and expected['four100ExecutablePhysical']==133
    contract(value,expected);labels=[]
    vectors=[('source',lambda v:v.update(source='0'*40)),('methods',lambda v:v.update(tests=716)),('first-execs',lambda v:v.update(originalExecs=32)),('duplicate',lambda v:v['cases'].__setitem__(1,copy.deepcopy(v['cases'][0]))),('pending-erased',lambda v:v.update(incompleteSourcePrograms=0)),('four-inflated',lambda v:v.update(four100SourcePrograms=99)),('owner-forged',lambda v:next(u for u in v['owners'].values() if u['canonicalOwner'] is None).update(canonicalOwner='WBS-F03')),('union',lambda v:v.update(coverageExecUnion=True)),('old-transfer',lambda v:v.update(priorSource0061TestsTransferred=True)),('bool-exec',lambda v:v.update(additionalQualificationExecs=True)),('natural-erased',lambda v:v.update(naturalZeroBranchSourcePrograms=0)),('metadata-erased',lambda v:v.update(metadataSourcePrograms=0)),('generated-erased',lambda v:v.update(generatedMetadataPhysical=0)),('code-inflated',lambda v:v.update(executablePhysical=999)),('qualification-erased',lambda v:v.update(additionalQualificationReferences=[])),('formal',lambda v:v.update(formalUpdated=True)),('accepted',lambda v:v.update(newAccepted=1)),('scope-erased',lambda v:v.update(additionalScopeReferences=[])),('scope-counted',lambda v:v['additionalScopeReferences'][0].update(newTests=24)),('context-as-PT',lambda v:v['additionalSourceContractReference'].update(productTestsExecuted=14)),('context-pending-erased',lambda v:v['additionalSourceContractReference'].update(currentWholeJoinPending=False)),('history-erased',lambda v:v.update(qualificationReplacedUnitHistory={})),('old-proof-used',lambda v:v.update(fullSourceUnits=old['fullSourceUnits']))]
    # The context pending field is the actual currentWholeJoinPending role when present;
    # contract also rejects unexpected new fields inside that immutable context object.
    for label,mutate in vectors:
        wrong=copy.deepcopy(value);mutate(wrong)
        try:contract(wrong,expected)
        except ValueError:labels.append(label)
        else:raise ValueError('false replacement accepted: '+label)
    assert len(labels)==23
    summary=dict(actualExit=0,source=SOURCE,invocation=invocation,sourceContextProofCounterNegativeVectors=5,registryManifestSha256=PIN,ownerStatusCounts=value['ownerStatusCounts'],sourceContractContexts=value['additionalSourceContractReference']['sourceContexts'],additionalScopes=len(value['additionalScopeReferences']),originalXmlMethods=value['tests'],originalXmlSuites=value['suites'],originalExecs=value['originalExecs'],four100SourcePrograms=value['four100SourcePrograms'],naturalZeroBranchSourcePrograms=value['naturalZeroBranchSourcePrograms'],generatedMetadataPhysical=value['generatedMetadataPhysical'],four100ExecutablePhysical=value['four100ExecutablePhysical'],metadataSourcePrograms=value['metadataSourcePrograms'],incompleteSourcePrograms=value['incompleteSourcePrograms'],unknownOwnerPaths=value['unknownOwnerPaths'],metadataNegativeVectors=len(labels),nonVacuousLabels=labels,additionalQualificationExecs=1,totalProductExecs=32,totalMethodExecutions=716,uniqueProductMethodDelta=0,sourceProgramDelta=0,oldSourceResultsTransferred=False,coverageExecUnion=False,originalTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False)
    bindings={k:summary[k] for k in ('source','originalXmlMethods','originalXmlSuites','originalExecs','four100SourcePrograms','incompleteSourcePrograms','unknownOwnerPaths','additionalQualificationExecs','totalProductExecs','totalMethodExecutions')}
    checks=0
    for key,bad in [('originalXmlMethods',716),('originalExecs',32),('additionalQualificationExecs',True)]:
        wrong=dict(summary);wrong[key]=bad
        if any(json.dumps(wrong[k])!=json.dumps(v) for k,v in bindings.items()):checks+=1
        else:raise ValueError('inflated summary accepted')
    assert checks==3
    summary.update(postSummaryNegativeVectors=checks,summaryBoundToVerifiedActualFields=True)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',summary)
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
