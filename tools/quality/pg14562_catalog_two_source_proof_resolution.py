"""Resolve exactly two incomplete Source proofs, preserving original660 cases and original31 execs."""
import copy
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OLD=('PG14546-current-thirty-one-host660-registry-v1','7887147fa0893ba365e28ccd392a29f6281aa43c02db3e5c33b056162789c232')
OLD_POST=('PG14548-current-thirty-one-host660-registry-post-v1','e8b8721769c930e5ad056d6b397e5c1d7f3d2e7af3ab576a44c5d051d098d437')
NEW=('PG14558-catalog-scrape-single-exec-fifty-six-post-v1','1af12826a6b3e7c39c335a7a00ed6d22bdc8d7dcc151bdff7b61610e3ada6a1b')
OUT=data.BASE/'PG14562-catalog-two-source-proof-resolution-v1'
TARGETS={'dev/codex/schubert/nk/api/monitoring/ApiMetricCatalog','dev/codex/schubert/nk/web/monitoring/WebMetricCatalog'}

def main():
    invocation=capture(__file__);assert not OUT.exists()
    old,checked,new=[data.read_checked(data.BASE/n/'manifest.json',h) for n,h in (OLD,OLD_POST,NEW)]
    assert all(m['actualExit']==0 and m['source']==SOURCE for m in (old,checked,new))
    verify(old['invocation']);verify(checked['invocation']);verify(new['invocation'])
    assert checked['registryManifestSha256']==OLD[1] and checked['summaryBoundToVerifiedActualFields'] and checked['originalXmlMethods']==old['tests']==660
    assert new['previousUniqueRegistryManifestSha256']==OLD[1] and new['qualificationReplacementComplete'] and new['qualificationPurpose']=='SINGLE_EXEC_FULL_SOURCE_GAP_CLOSURE_NOT_CONFIRMATION_ONLY'
    assert new['uniqueProductMethodDelta']==new['sourceProgramDelta']==0 and new['additionalQualificationProductJvms']==1 and new['tests']==new['additionalQualificationRepeatedMethodExecutions']==56
    assert new['singleSession'] and new['crcMismatch']==0 and not new['coverageExecUnion']
    normal=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json',old['normalManifestSha256'])
    assert normal['source']==SOURCE and new['normalManifestSha256']==old['normalManifestSha256']
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items())
    assert all(data.sha(__import__('pathlib').Path(j['path']).read_bytes())==j['sha256'] for j in normal['jars'].values())
    assert {(v['classname'],v['name']) for v in new['cases']}<={(v['classname'],v['name']) for v in old['cases']}
    assert all(old['owners'][p]==v for p,v in new['owners'].items())
    assert set(new['fullSourceUnits'])==set(new['qualificationReplacementCandidates'])==TARGETS
    result=copy.deepcopy(old);history={}
    for name in TARGETS:
        previous=old['fullSourceUnits'][name];unit=new['fullSourceUnits'][name]
        assert previous['counters']['LINE']['missed']==previous['counters']['METHOD']['missed']==1 and not previous['four100']
        assert previous['physical']==unit['physical'] and unit['four100'] and all(v['missed']==0 and v['covered']>0 for v in unit['totals'].values())
        assert new['qualificationReplacementCandidates'][name]['previousCounters']==previous['counters']
        history[name]=copy.deepcopy(previous)
        result['fullSourceUnits'][name]=dict(post=NEW[0],postSha256=NEW[1],physical=unit['physical'],counters=unit['totals'],four100=True,execSha256=new['execSha256'],sessionIdentity=new['sessionIdentity'],metadataOnly=False,branchNaturallyZero=False)
    units=result['fullSourceUnits'];full=[v for v in units.values() if v['four100']]
    pending={n:v for n,v in units.items() if not v['four100'] and not v['branchNaturallyZero'] and not v['metadataOnly']}
    assert len(full)==98 and set(pending)=={'dev/codex/schubert/nk/api/messaging/inbound/InboundTransactions'}
    assert len(units)==160 and sum(len(v['physical']) for v in units.values())==201
    assert sum(v['branchNaturallyZero'] for v in units.values())==60 and sum(v['metadataOnly'] for v in units.values())==1
    references=[dict(name=NEW[0],sha256=NEW[1],execSha256=new['execSha256'],sessionIdentity=new['sessionIdentity'],repeatedMethods=56,newMethods=0,newSourcePrograms=0,productJvms=1,purpose=new['qualificationPurpose'])]
    result.update(invocation=invocation,four100SourcePrograms=len(full),four100Physical=sum(len(v['physical']) for v in full),four100ExecutablePhysical=sum(c not in old['metadataClasses'] for v in full for c in v['physical']),incompleteSourcePrograms=len(pending),previousUniqueRegistryReference=OLD,previousRegistryPostReference=OLD_POST,additionalQualificationReferences=references,qualificationReplacedUnitHistory=history,additionalQualificationExecs=1,totalProductExecs=32,totalMethodExecutions=716,uniqueProductMethodDelta=0,sourceProgramDelta=0,sourceReplacementPreservesOriginalCases=True)
    assert result['four100Physical']==138 and result['four100ExecutablePhysical']==133
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result)
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
