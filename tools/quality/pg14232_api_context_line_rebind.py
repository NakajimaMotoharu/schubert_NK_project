"""Read-only42 original Main contexts to current Source, preserving original rows and current pending status."""
from collections import Counter
import difflib
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pmd_source_span_ascii import span
from trace_owner_join import canonical
from f03_main_failure_boundary_sixty_two_trace_v1 import state_after

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
BASE='0061d178cda80c2ce3926290619c64db125dbcfc'
OUT=data.BASE/'PG14232-api-seven-forty-two-context-v1'
PREFIX='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/'
TARGETS={
 'admin/UserMutationApplicationService':(1,'WBS-P010-02'),
 'admin/UserQueryApplicationService':(8,'WBS-P010-01'),
 'log/LogQueryApplicationService':(15,'WBS-P010-04'),
 'media/MediaApplicationService':(22,'WBS-P009-01'),
 'question/QuestionMutationApplicationService':(30,'WBS-P014-02'),
 'question/QuestionQueryApplicationService':(37,'WBS-P014-01'),
 'scenario/ScenarioApplicationService':(62,'WBS-P008-02')}
DESIGN={
 'documents/300_SS/310_アプリケーション/312_処理sequence・method・例外・transaction設計.md':'7fc9bb837b9669f301c4c8d1b0b93ea1d680fd6c30e34b7f754e5210beb3765b',
 'documents/300_SS/320_メッセージング/324_Outbox・Inbox・冪等性・再送設計.md':'2bc99fd66ca1121a1ab4ae44e97aab96b52d4cf4c8145f6a425f89c7b07ce774',
 'documents/300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md':'bf35de0b4d24a253eb75808f0280fa92eb3f02f8ba3a988a227f96c7213781a5',
 'documents/300_SS/350_運用・品質/352_Security・credential・監査実装設計.md':'d77617872d91f83af55e12520279d48c7c5385b85b09e4377ef81ed03b1aad03'}
CATALOG=('PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
REASON='SS312/324/332/352: fixed temporary mapping preserves fatal before classification; owned transaction rolls back failure and attaches rollback secondary before rethrow. Typed business/auth outcomes and source-specific read/write sequencing remain distinct. Full seven bodies reviewed in2607; imported helpers, actual DB/file/graph effects and whole451 remain unqualified; raw warning retained, no NPE-as-success or dynamic PASS claim.'

def require(ok,message):
    if not ok:raise ValueError(message)

def insertion_map(before,after):
    a=before.splitlines(keepends=True);b=after.splitlines(keepends=True);result={}
    for tag,i,j,k,l in difflib.SequenceMatcher(a=a,b=b,autojunk=False).get_opcodes():
        require(tag in ('equal','insert'),'only fixed reviewed insertions, never changed/deleted original line')
        if tag=='equal':
            for u,v in zip(range(i,j),range(k,l)):result[u+1]=v+1
    require(set(result)==set(range(1,len(a)+1)),'all original lines retained exactly once')
    return result

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only public source review')
    normal=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3')
    old=data.read_checked(data.BASE/'PG13832-snapshot-program-six-compile-v1/manifest.json','8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65')
    proof=data.read_checked(data.BASE/'PG14210-typed-marker-guard-after-v1/manifest.json','48f245609e4cb19b754fbcd12a0e92435de5c122c6356269fd1e144483bc18ee')
    historical=data.read_checked(data.BASE/'PG13253-current-all-java-static-v2/manifest.json','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
    current=data.read_checked(data.BASE/'PG14226-typed-marker-guard-three-main-static-v1/manifest.json','0ae9027c8f4819697a6d6926b5b6723dc611c525690d98b0dccfc63259a4c293')
    require(normal['source']==current['source']==SOURCE and old['source']==proof['baselineSource']==BASE,'explicit original/current source domains')
    require(normal['actualExit']==normal['testsExecuted']==old['actualExit']==old['testsExecuted']==historical['actualExit']==current['actualExit']==0,'genuine raw evidence; no PT result transfer')
    require(proof['staticConformance'] is True and proof['metadataNegativeVectors']==16,'four guard-only correction already checked')
    hashes=normal['begin']['inputHashes']
    require(all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items()),'fixed complete current source inputs')
    for p,h in DESIGN.items():
        require(data.sha((data.ROOT/p).read_bytes())==h==data.sha(subprocess.check_output(['git','show','origin/main:'+p],cwd=data.ROOT)),'approved origin/main design equality')
    catalog=data.read_checked(data.BASE/CATALOG[0],CATALOG[1]);by_id={r['id']:r for r in catalog}
    ids,refs,_=state_after();wanted={f'PMD-{i:05d}' for start,_ in TARGETS.values() for i in range(start,start+6)}
    require(len(wanted)==42 and wanted<=ids-refs,'index first: exact previously unreferenced42 only')
    facts_old=data.read_checked(data.BASE/'PG13253-current-all-java-static-v2/findings.json',historical['findingsSha256'])
    facts_new=data.read_checked(data.BASE/'PG14226-typed-marker-guard-three-main-static-v1/findings.json',current['findingsSha256'])
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    rows=[];source_hashes={}
    for name,(first,owner) in TARGETS.items():
        p=PREFIX+name+'.java';text=(data.ROOT/p).read_text();prior=subprocess.check_output(['git','show',BASE+':'+p],cwd=data.ROOT,text=True)
        require(data.sha(prior.encode())==old['begin']['inputHashes'][p] and data.sha(text.encode())==hashes[p],'actual original and current source')
        require(chr(92)+'u' not in prior and chr(92)+'u' not in text,'unchanged ordinary no-Unicode span contract')
        source_hashes[p]=hashes[p];changed=prior!=text;mapping=insertion_map(prior,text)
        require(changed==(p in proof['changedProductionPaths']),'only declared three Source changed')
        required=['TemporaryInfrastructureException.preserveFatal(','TemporaryInfrastructureException.attachSecondary(']
        variable='c' if name=='question/QuestionMutationApplicationService' else 'connection'
        required += [variable+'.commit();',variable+'.rollback();']
        require(all(v in text for v in required),'source-specific transaction/fatal anchor changed')
        owned=canonical(p,logical);require(owned['canonicalOwner']==owned['canonicalCostOwner']==owner,'actual canonical owner not inferred from work group')
        facts=facts_new if changed else facts_old
        observed=[f for f in facts if f['path']==p and f['rule']=='AvoidCatchingGenericException']
        require(len(observed)==6 and all(f['sourceSha256']==hashes[p] for f in observed),'six actual measured warnings/source, not an old runtime result')
        bound=[]
        for identity in [f'PMD-{i:05d}' for i in range(first,first+6)]:
            original=by_id[identity];attrs=dict(original['attributes'])
            require(original['path']==p and original['inputSha256']==old['begin']['inputHashes'][p] and original['rule']=='AvoidCatchingGenericException','exact immutable original row')
            for key in ('beginline','endline'):attrs[key]=str(mapping[int(attrs[key])])
            match=[f for f in observed if f['attributes']==attrs];require(len(match)==1,'current measured coordinate/multiplicity')
            start,end,token=span(text,attrs);old_start,old_end,old_token=span(prior,original['attributes'])
            require(token==old_token and token in ('RuntimeException','Error'),'exact original/current generic type token')
            bound.append(json.dumps(attrs,sort_keys=True))
            rows.append(dict(id=identity,path=p,source=SOURCE,sourceSha256=hashes[p],baselineSource=BASE,originalInputSha256=original['inputSha256'],originalRowSha256=original['rowSha256'],originalAttributes=original['attributes'],attributes=attrs,originalSpan=[old_start,old_end],currentSpan=[start,end],typeToken=token,sourceChanged=changed,coordinateRebind='INSERTION_ONLY_ALL_ORIGINAL_LINES_RETAINED' if changed else 'EXACT_SOURCE_BYTES_UNCHANGED',measurementSource=current['source'] if changed else historical['source'],measurementKind='CURRENT_SOURCE_RAW_XML' if changed else 'EXACT_UNCHANGED_SOURCE_RAW_XML_NO_RUNTIME_TRANSFER',reason=REASON,sourceGuards=required,rawRetained=True,currentWholeJoinPending=True,qualityGatePass=False,productTestsExecuted=0,nativeRuntimeProven=False,**owned))
        require(Counter(bound)==Counter(json.dumps(f['attributes'],sort_keys=True) for f in observed),'all six actual raw occurrences exactly once')
    require(len(rows)==len({r['id'] for r in rows})==42,'no lost/duplicate original raw ID')
    verify(invocation);OUT.mkdir()
    data.write(OUT/'review.json',dict(source=SOURCE,rows=sorted(rows,key=lambda r:r['id']),approvedDesignHashes=DESIGN))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),normalManifestSha256='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3',sourceHashes=source_hashes,sourceContexts=42,sourceFiles=7,currentSourceMeasuredContexts=18,exactUnchangedSourceMeasuredContexts=24,workerHeldIds=[f'PMD-{i:05d}' for i in range(55,61)],wholeCurrentStaticMeasurement=False,rawRetained=42,currentWholeJoinPending=42,productTestsExecuted=0,coverage=None,qualityGatePass=False,formalUpdated=False,newAccepted=0,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
