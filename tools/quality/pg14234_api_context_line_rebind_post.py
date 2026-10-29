"""Independent manual coordinate deltas and source/XML binding; metadata negatives only, no Product."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pmd_source_span_ascii import span
from trace_owner_join import canonical
from pg14232_api_context_line_rebind import SOURCE,BASE,TARGETS,DESIGN,CATALOG

PIN='72a764b48dc4a9ad405eec9515123c3ebc1c459968469fd16d769a341e314288'
CURRENT=data.BASE/'PG14232-api-seven-forty-two-context-v1'
OUT=data.BASE/'PG14234-api-seven-forty-two-post-v1'

def require(ok,message):
    if not ok:raise ValueError(message)

def check(rows,catalog,texts,hashes,facts,owners):
    wanted={f'PMD-{i:05d}' for start,_ in TARGETS.values() for i in range(start,start+6)}
    require(len(rows)==42 and {r['id'] for r in rows}==wanted,'exact42 unique raw ids')
    for row in rows:
        original=catalog[row['id']];p=original['path'];text=texts[p]
        require(row['path']==p and row['source']==SOURCE and row['baselineSource']==BASE and row['sourceSha256']==hashes[p],'exact current source/hash')
        require(row['originalInputSha256']==original['inputSha256'] and row['originalRowSha256']==original['rowSha256'] and row['originalAttributes']==original['attributes'],'immutable old row retained')
        attrs=dict(original['attributes']);method=attrs['method']
        require(method in ('process','transaction'),'manual scoped catch roles only')
        # Manual independent delta, not the review tool insertion_map implementation.
        delta=0
        if method=='transaction':
            if p.endswith('/question/QuestionQueryApplicationService.java'):delta=4
            elif p.endswith(('/admin/UserQueryApplicationService.java','/log/LogQueryApplicationService.java')):delta=2
        for field in ('beginline','endline'):attrs[field]=str(int(attrs[field])+delta)
        require(row['attributes']==attrs,'independent exact manual line delta')
        current_start,current_end,token=span(text,attrs)
        require(row['currentSpan']==[current_start,current_end] and row['typeToken']==token and token in ('RuntimeException','Error'),'current raw token/offset identity')
        old_text=subprocess.check_output(['git','show',BASE+':'+p],cwd=data.ROOT,text=True)
        old_start,old_end,old_token=span(old_text,original['attributes'])
        require(row['originalSpan']==[old_start,old_end] and old_token==token,'original token/offset retained')
        require(row['sourceChanged'] is (hashes[p]!=original['inputSha256']),'actual original/current changed flag')
        matches=[f for f in facts[p] if f['attributes']==attrs and f['sourceSha256']==hashes[p]]
        require(len(matches)==1,'one actual measured raw row, not inferred runtime success')
        require(all(row[k]==owners[p][k] for k in owners[p]),'canonical source owner never change group')
        require(row['rawRetained'] is True and row['currentWholeJoinPending'] is True and row['qualityGatePass'] is False and row['nativeRuntimeProven'] is False,'raw/pending/quality/native boundaries')
        require(type(row['productTestsExecuted']) is int and row['productTestsExecuted']==0,'no PT from source review')
        require(isinstance(row['reason'],str) and len(row['reason'])>100 and all(g in text for g in row['sourceGuards']),'source reason anchors remain present')

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only post')
    m=data.read_checked(CURRENT/'manifest.json',PIN);review=data.read_checked(CURRENT/'review.json',m['reviewSha256'])
    require(m['actualExit']==0 and m['source']==review['source']==SOURCE and m['sourceContexts']==42 and m['sourceFiles']==7,'genuine reviewed source scope')
    n=data.read_checked(data.BASE/'PG14216-typed-marker-guard-six-compile-v1/manifest.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3')
    require(n['source']==SOURCE and n['actualExit']==n['testsExecuted']==0,'actual current compiler binding')
    require(all(data.sha((data.ROOT/p).read_bytes())==h for p,h in n['begin']['inputHashes'].items()),'all normal input bytes unchanged')
    raw=data.read_checked(data.BASE/CATALOG[0],CATALOG[1]);catalog={r['id']:r for r in raw}
    measured={}
    for name,pin in [('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf'),('PG14226-typed-marker-guard-three-main-static-v1','0ae9027c8f4819697a6d6926b5b6723dc611c525690d98b0dccfc63259a4c293')]:
        report=data.read_checked(data.BASE/name/'manifest.json',pin)
        measured[name]=data.read_checked(data.BASE/name/'findings.json',report['findingsSha256'])
    texts={p:(data.ROOT/p).read_text() for p in m['sourceHashes']};facts={}
    for p,h in m['sourceHashes'].items():
        require(n['begin']['inputHashes'][p]==h==data.sha(texts[p].encode()),'complete declared source hashes')
        name='PG14226-typed-marker-guard-three-main-static-v1' if p.endswith(('/admin/UserQueryApplicationService.java','/log/LogQueryApplicationService.java','/question/QuestionQueryApplicationService.java')) else 'PG13253-current-all-java-static-v2'
        facts[p]=[r for r in measured[name] if r['path']==p and r['rule']=='AvoidCatchingGenericException']
        require(len(facts[p])==6,'all actual same-scope six measured warnings')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    owners={p:canonical(p,logical) for p in texts}
    require(review['approvedDesignHashes']==DESIGN,'approved complete design scope')
    for p,h in DESIGN.items():require(data.sha((data.ROOT/p).read_bytes())==h==data.sha(subprocess.check_output(['git','show','origin/main:'+p],cwd=data.ROOT)),'origin/main design pins')
    rows=review['rows'];check(rows,catalog,texts,n['begin']['inputHashes'],facts,owners)
    labels=[]
    mutations=[('missing',lambda x:x.pop()),('duplicate',lambda x:x.__setitem__(1,copy.deepcopy(x[0]))),('source',lambda x:x[0].update(source='0'*40)),('hash',lambda x:x[0].update(sourceSha256='0'*64)),('old-hash',lambda x:x[0].update(originalInputSha256='0'*64)),('line',lambda x:x[0]['attributes'].update(beginline='1')),('token',lambda x:x[0].update(typeToken='Throwable')),('owner',lambda x:x[0].update(canonicalOwner='WBS-F03')),('quality',lambda x:x[0].update(qualityGatePass=True)),('raw',lambda x:x[0].update(rawRetained=False)),('pending',lambda x:x[0].update(currentWholeJoinPending=False)),('PT-bool',lambda x:x[0].update(productTestsExecuted=False)),('PT',lambda x:x[0].update(productTestsExecuted=42)),('native',lambda x:x[0].update(nativeRuntimeProven=True))]
    for label,mutate in mutations:
        bad=copy.deepcopy(rows);mutate(bad)
        try:check(bad,catalog,texts,n['begin']['inputHashes'],facts,owners)
        except ValueError:labels.append(label)
        else:raise ValueError('invalid metadata accepted: '+label)
    require(m['workerHeldIds']==[f'PMD-{i:05d}' for i in range(55,61)],'original remaining six not silently removed')
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewManifestSha256=PIN,sourceContexts=42,sourceFiles=7,independentManualTransactionLineDeltas={'UserQuery':2,'LogQuery':2,'QuestionQuery':4,'otherOrProcess':0},metadataNegativeVectors=len(labels),nonVacuousLabels=labels,workerHeldIds=m['workerHeldIds'],rawRetained=42,currentWholeJoinPending=42,productTestsExecuted=0,coverage=None,qualityGatePass=False,wholeF03Accepted=False,whole451Accepted=False,newAccepted=0,formalUpdated=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
