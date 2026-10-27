"""Whole two-role source inverse and reviewed closure metadata, never an execution permission tool."""
import difflib
import re
import sys
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX, close
from fixture_scope_advisory import audit, direct_imports
import pg12684_scenario_writer_plan as previous_review

SOURCE_BEFORE='af3f0f86d295ed721f5c1b41670ef224eb1d49e3'
OUT=data.BASE/'PG12743-metric-context-plan-v3'
PATHS=['src/schubert-nk-'+role+'/src/test/java/dev/codex/schubert/nk/'+role+'/monitoring/'+title+'MetricContextTest.java' for role,title in [('api','Api'),('web','Web')]]
STRINGS={'DEBUG_MODE':'"DEBUG"','FIXTURE_BINDING':'"binding"'}
FIELDS={'custom':'customRegistry','standard':'standardRegistry'}
API_NAMES=['ApiCustomMetricPayload','ApiDurationMetricExporter','ApiGcMetricRegistration','ApiJvmMetrics','ApiMetricCatalog','ApiMetricContext','ApiMetricScrape','ApiScalarMetricExporter','ApiStandardMetricSource','ApiStandardMetrics','ApiSystemMetrics','ExactDurationMeterRegistry','ExactDurationSupport']
WEB_NAMES=['HttpMetricContract','OverflowSafeDurationSupport','OverflowSafeHttpMeterRegistry','WebCounterMetricExporter','WebCustomMetricPayload','WebDurationMetricExporter','WebGaugeMetricExporter','WebGcMetricRegistration','WebJvmMetrics','WebMetricCatalog','WebMetricContext','WebMetricScrape','WebMetricText','WebStandardMetricSource','WebStandardMetrics','WebSystemMetrics']


def lex(text):
    return [(m.group(),m.start(),m.end()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]


def raw(text):
    return [row[0] for row in lex(text)]


def before():
    n=data.read_checked(data.BASE/'PG12718-alert-threshold-six-compile-v1/manifest.json','5433fb79732be52686b99e8ec665a0ebb02752a90004cc777eedb3b4d31ba1c7')
    assert n['source']==SOURCE_BEFORE and n['actualExit']==n['testsExecuted']==0
    snapshot=Path(n['jars']['api']['path']).parent.parent.parent.parent
    texts={p:(snapshot/p).read_text() for p in PATHS}
    assert all(data.sha(text.encode())==n['begin']['inputHashes'][p] for p,text in texts.items())
    return n,texts


def eligibility(normal):
    hashes=normal['begin']['inputHashes']
    allowed=set()
    for role,names in [('api',API_NAMES),('web',WEB_NAMES)]:
        allowed.update('src/schubert-nk-'+role+'/src/main/java/dev/codex/schubert/nk/'+role+'/monitoring/'+name+'.java' for name in names)
    assert len(allowed)==29
    allowed.update(p for p in previous_review.eligibility() if '/schubert-nk-protocol/' in p)
    topology='src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/transport/BrokerTopology.java'
    allowed.add(topology)
    # All source names are fixed input metadata, not a filesystem search or package execution.
    index={p.split('/java/',1)[1][:-5].replace('/','.'):p for p in hashes if '/src/main/java/dev/codex/schubert/nk/' in p and p.endswith('.java')}
    todo=['dev.codex.schubert.nk.'+role+'.monitoring.'+title+'MetricContext' for role,title in [('api','Api'),('web','Web')]]
    found={}
    while todo:
        binary=todo.pop();path=index[binary]
        if path in found:
            continue
        assert path in allowed, 'unreviewed new Main dependency: '+path
        text=(data.ROOT/path).read_text()
        assert data.sha(text.encode())==hashes[path]
        found[path]=hashes[path]
        identifiers=set(raw(text));package=binary.rpartition('.')[0]
        todo.extend(name for name in index if name.rpartition('.')[0]==package and name.rpartition('.')[2] in identifiers and index[name] not in found)
        for row in direct_imports(text):
            name=row['name'];assert not name.endswith('.*')
            while name not in index and '.' in name:
                name=name.rpartition('.')[0]
            assert name in index
            if index[name] not in found:
                todo.append(name)
    return found


def owned(text):
    tokens=lex(text);pairs=[(value,start) for value,start,_ in tokens]
    stack=[];edits=[];count=0
    for index,(value,start,end) in enumerate(tokens):
        if value=='{':
            stack.append(index)
        elif value=='}':
            stack.pop()
        if [row[0] for row in tokens[index:index+2]]!=['var','executor'] and [row[0] for row in tokens[index:index+2]]!=['var','worker']:
            continue
        values=[row[0] for row in tokens[index:index+9]]
        if values[2:]!=['=','Executors','.','newSingleThreadExecutor','(',')',';']:
            continue
        assert stack
        ending=close(pairs,stack[-1],'{','}')
        declaration=text[start:tokens[index+8][2]]
        edits.extend([(start,tokens[index+8][2],'try ('+declaration[:-1]+') {'),(tokens[ending][1],tokens[ending][1],'}\n')])
        count+=1
    assert count==4
    for start,end,replacement in sorted(edits,reverse=True):
        text=text[:start]+replacement+text[end:]
    return text


def intended(old):
    result={}
    for path,text in old.items():
        edits=[];tokens=lex(text)
        for index,(value,start,end) in enumerate(tokens):
            if value in STRINGS.values():
                name=next(k for k,v in STRINGS.items() if v==value)
                edits.append((start,end,name))
            if value in FIELDS:
                previous=tokens[index-1][0] if index else None
                following=tokens[index+1][0] if index+1<len(tokens) else None
                if not (previous==':' and index>=2 and tokens[index-2][0]==':') and following!='(':
                    edits.append((start,end,FIELDS[value]))
        for start,end,replacement in sorted(edits,reverse=True):
            text=text[:start]+replacement+text[end:]
        declaration=''.join('  private static final String '+name+' = '+value+';\n' for name,value in STRINGS.items())
        needle='  private static final String READY_ONE'
        assert text.count(needle)==1
        text=text.replace(needle,declaration+needle,1)
        result[path]=owned(text)
    return result


def require(old,new):
    for path,text in new.items():
        for name,literal in STRINGS.items():
            declaration='  private static final String '+name+' = '+literal+';\n'
            assert text.count(declaration)==1
            text=text.replace(declaration,'',1)
        tokens=raw(text)
        for i,value in enumerate(tokens):
            following=tokens[i+1] if i+1<len(tokens) else None
            if value in FIELDS:
                assert (i>=2 and tokens[i-2:i]==[':',':']) or following=='(', 'old field name outside factory method/ref'
            if value in FIELDS.values():
                assert not (i>=2 and tokens[i-2:i]==[':',':']) and following!='(', 'new field name cannot be a factory method/ref'
            if value in STRINGS:
                tokens[i]=STRINGS[value]
            if value in FIELDS.values():
                tokens[i]=next(k for k,v in FIELDS.items() if v==value)
        count=0
        for index in range(len(tokens)-1,-1,-1):
            if tokens[index:index+3]!=['try','(','var']:
                continue
            name=tokens[index+3]
            if name not in ['worker','executor'] or tokens[index+4:index+12]!=['=','Executors','.','newSingleThreadExecutor','(',')',')','{']:
                continue
            ending=close([(v,0) for v in tokens],index+11,'{','}')
            tokens.pop(ending)
            tokens[index:index+12]=['var',name,'=','Executors','.','newSingleThreadExecutor','(',')',';']
            count+=1
        assert count==4 and tokens==raw(old[path])


def emit():
    _,old=before();new=intended(old);require(old,new)
    patch='*** Begin Patch\n'
    for path in PATHS:
        assert data.sha((data.ROOT/path).read_bytes())=={'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiMetricContextTest.java': '791cadedb5225804a5d5e1450ae98e53960451b52d73534a19c01983cb599ae2', 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/WebMetricContextTest.java': '688fa7e9f6075d47ae77e75c8633056a046690b3b57d1b5847ac6890074b91aa'}[path]
        patch+='*** Update File: '+str(data.ROOT/path)+'\n'+'\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff((data.ROOT/path).read_text().splitlines(),new[path].splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    n,old=before();new={p:(data.ROOT/p).read_text() for p in PATHS};require(old,new)
    mapped=old[PATHS[0]].replace('dev.codex.schubert.nk.api.','dev.codex.schubert.nk.web.').replace('Api','Web').replace('apimctx','webmctx').replace('API','WEB').replace('schubert_nk_api_ready','schubert_nk_web_ready').replace('ExactDurationSupport','OverflowSafeDurationSupport').replace('"CONFIG_INVALID"','"invalid monitoring mode"')
    assert raw(mapped)==raw(old[PATHS[1]]) and len(raw(mapped))==6175
    assert all(data.sha((data.ROOT/p).read_bytes())==digest for p,digest in n['begin']['inputHashes'].items() if p not in new)
    reviewed=eligibility(n)
    registry=data.read_checked(data.BASE/'PG12730-alert-threshold-trace-v1/manifest.json','96a9450934b0b40186c01eae11e90119b1419943b8826e74aa77136da887d270')
    original_texts={p:(data.ROOT/p).read_text() for p in reviewed}
    advisory=audit({**original_texts,**old},list(reviewed),PATHS,n['begin']['inputHashes'],registry['sourceRows'],{'WBS-P018-09'})
    assert advisory['metadataConsistent'] and not advisory['executionQualified'] and not advisory['holdReleased']
    assert all(row['canonicalOwner']==row['canonicalCostOwner']=='WBS-P018-09' for row in advisory['originalOwners'])
    labels=[]
    for path in PATHS:
        replacements=[('DEBUG_MODE = "DEBUG"','DEBUG_MODE = "STANDARD"'),('FIXTURE_BINDING = "binding"','FIXTURE_BINDING = "wrong"'),('this::custom','this::customRegistry'),('this::standard','this::standardRegistry'),('customRegistry = new Custom','unknownRegistry = new Custom'),('standardRegistry = new Standard','unknownRegistry = new Standard'),('awaitTermination(30,','awaitTermination(1,'),('executor.shutdownNow();',''),('release.countDown();',''),('worker.shutdownNow();',''),('future.get(30,','future.get(1,'),('assertEquals(0, h.customCreates.get())','assertEquals(1, h.customCreates.get())'),('@Test','@Disabled'),('customRegistry.onRead','custom.onRead'),('standardRegistry.close','standard.close'),('null : customRegistry','null : custom'),('null : standardRegistry','null : standard')]
        for first,last in replacements:
            bad={**new,path:new[path].replace(first,last,1)};assert bad!=new
            try:
                require(old,bad)
            except AssertionError:
                labels.append(path+':'+first)
            else:
                raise AssertionError('owner/oracle/factory reference mutation accepted')
    assert all(len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==33 for text in new.values())
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2375_MetricContext二role所有fixture是正_単体テスト仕様書.md'
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=SOURCE_BEFORE,invocation=invocation,sourceChanges=[dict(path=p,beforeSha256=data.sha(old[p].encode()),sha256=data.sha(new[p].encode())) for p in PATHS],totalCorrections=16,privateFieldNamesChanged=4,privateStringNamesAdded=4,ownedPools=8,metadataNegativeVectors=len(labels),nonVacuousNegativeLabels=labels,wholeWebRoleCorrespondenceTokens=6175,eligibilityClosureSourceHashes=reviewed,metadataAdvisory=advisory,originalTests=66,originalSuites=2,allMainAndOtherInputsUnchanged=True,judgement='PT_DEFAULT_WHOLE_METRIC_CONTEXT_TWO_ROLE_SELF_JVM_SDK_JMX_OWN_FINITE_WORKERS_NO_EXTERNAL_IO',specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),productTestsExecuted=0,newAccepted=0,coverage=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
