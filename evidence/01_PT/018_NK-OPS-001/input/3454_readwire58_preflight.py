"""Independently admit every exact static site and whole-source input before the one58 run."""
from pathlib import Path
import hashlib
import json
import pgpt_closed_host_profile as policy

root=Path.cwd();base=root/'evidence/01_PT/018_NK-OPS-001';output=base/'evidence/PG33732-readwire58-preflight-v1';assert not output.exists()
load=lambda path:json.loads(path.read_text());sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest();ref=lambda path:dict(path=str(path.relative_to(root)),sha256=sha(path))
prepare_path=base/'evidence/PG33730-readwire58-prepare-v1/manifest.json';prepare=load(prepare_path);assert type(prepare['actualExit']) is int and prepare['actualExit']==0 and prepare['expectedTests']==58
assert prepare['newDefinitions']==1 and prepare['necessaryPriorDefinitions']==57 and len(prepare['mainSources'])==13 and len(prepare['testSources'])==8
assert len(prepare['inputHashes'])==189 and all(sha(root/path)==value for path,value in prepare['inputHashes'].items())
for label,stage in prepare['stages'].items():
    assert type(stage['actualExit']) is int and stage['actualExit']==(4 if label=='pmd' else 0) and stage['timedOut'] is False
    for stream in ['stdout','stderr']:assert sha(prepare_path.parent/(label+'.'+stream))==stage[stream+'Sha256']
assert prepare['processingErrors']==[] and prepare['checkstyleFindings']==0
original=load(root/prepare['originalMainStaticPreflight']['path']);assert original['actualExit']==0 and original['staticApplicable']==original['unclassified']==original['spotbugs']==0
assert sha(root/prepare['originalMainStaticPreflight']['path'])==prepare['originalMainStaticPreflight']['sha256']
assert all(prepare['inputHashes'][path]==value for path,value in original['inputHashes'].items())
legacy={(Path(value['path']).name,value['rule'],value['line']):value for value in original['classified']};assert len(legacy)==27
extra={
    'JmsRequestReplyClientTest.java':{('DoNotUseThreads',str(line)) for line in [133,134,143,171,177,209,210,413]}|{('CloseResource','171')},
    'ReplyCorrelationRegistryTest.java':{('DoNotUseThreads',str(line)) for line in [111,116,130,131]}|{('CloseResource','111')},
}
expected=set(legacy)|{(name,rule,line) for name,values in extra.items() for rule,line in values}
actual={(Path(value['path']).name,value['rule'],value['line']) for value in prepare['rawFindings']};assert actual==expected and len(prepare['rawFindings'])==41
classified=[]
for finding in prepare['rawFindings']:
    key=(Path(finding['path']).name,finding['rule'],finding['line']);path=next(path for path in prepare['mainSources']+prepare['testSources'] if path.endswith('/'+key[0]));text=(root/path).read_text();line=text.splitlines()[int(key[2])-1]
    if key in legacy:
        assert line==legacy[key]['sourceLine'];reason=legacy[key]['reason'];basis='EXACT_OLD27_SOURCE_SITE_AND_QUALIFIED_DISPOSITION'
    else:
        assert key[0] in extra and (key[1],key[2]) in extra[key[0]]
        if key[0]=='JmsRequestReplyClientTest.java':
            assert 'waiting.join(2_000)' in text and 'executor.awaitTermination(5, TimeUnit.SECONDS)' in text and 'release.countDown();' in text
            reason='Standalone whole JUnit owns its waiting thread or pool. Waiting is interrupted/joined2s in finally; release latch in finally, each Future.get2s, pool shutdownNow/assert await5s. Interrupted flag checks/restore are the required contract; no managed application thread or external backend.'
        else:
            assert 'task.get(5, TimeUnit.SECONDS)' in text and 'executor.shutdownNow();' in text and 'executor.awaitTermination(5, TimeUnit.SECONDS)' in text
            reason='Standalone registry100-response JUnit owns fixed16 workers. Latch await5s, every Future.get5s, finally shutdownNow/assert await5s; one literal winning outcome/99late is asserted. Not J2EE application thread creation or unclosed resource.'
        basis='NEW_EXACT14_WHOLE_JUNIT_SOURCE_LIFETIME_REVIEW'
    classified.append(dict(**finding,sourceLine=line,sourceSha256=sha(root/path),disposition='NOT_APPLICABLE_CONCRETE_OWNED_JUNIT_OR_REQUIRED_INTERRUPT_NO_SUPPRESSION',reason=reason,basis=basis))
names=sorted(prepare['physicalClassHashes']);assert len(names)==194
for name in names:policy.relative_name(name)
work=root.parent/'pgpt-runs/PG379/pg33730-readwire58-v1'
assert {name:sha(work/'component'/name) for name in names}==prepare['physicalClassHashes']
for name in prepare['testClassHashes']:policy.relative_name(name)
assert {name:sha(work/'test-classes'/name) for name in prepare['testClassHashes']}==prepare['testClassHashes']
assert all(not any(word in path.lower() for word in ['postgres','artemis','hikari','jna','jnr']) for path in prepare['dependencies'])
assert all(sha(Path(path))==value for path,value in prepare['dependencies'].items())
output.mkdir();manifest=dict(actualExit=0,inputHashes=prepare['inputHashes'],dependencies=prepare['dependencies'],prepare=ref(prepare_path),expectedTests=58,newDefinitions=1,necessaryRequalification=57,sourceMain13=13,fullPhysical194=194,rootCompilerAndMainByteUnchanged=True,originalNullAwaySpotbugsReusedOnlyExact13Source=True,sourceFormat=0,checkstyle=0,pmdRaw41=41,classified=classified,staticApplicable=0,unclassified=0,processingErrors=0,allWholeTestsPreserved=True,heldTestsExtracted=False,manualSuppressionAdded=False,applicationTestsExecuted=0,actualBackendOrHeldClassActions=0,full194CoverageExpectedPartial=True,whole451Accepted=False,newAcceptance=0,formalUpdated=False,verifier=ref(Path(__file__).resolve()))
(output/'manifest.json').open('x').write(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,staticRaw=41,applicable=0,unclassified=0,wholeCases=58,newDefinitions=1,sourceMainRebuild=0)))
