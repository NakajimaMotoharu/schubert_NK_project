"""Read-only exact74 source constructor sites, actual ownership flows and five confirmed guard gaps."""
from collections import Counter
import copy
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX

SOURCE='d4b5507ba6a76a85c23806e5604a0278f1795f37'
OUT=data.BASE/'PG11370-source-constructor-owner-audit-v1'
POST=data.BASE/'PG11372-source-constructor-owner-audit-post-v1'
PRIMARY_SHA=None
TYPES={'ApiStandardMetricSource','WebStandardMetricSource','BatchStandardMetricSource'}


def close(tokens,start,left,right):
    depth=1
    for i in range(start+1,len(tokens)):
        depth+=(tokens[i][0]==left)-(tokens[i][0]==right)
        if not depth:
            return i
    raise ValueError('complete source delimiter')


def functions(tokens):
    result=[]
    excluded={'if','for','while','switch','catch','synchronized','try','this','super'}
    for i,(v,_) in enumerate(tokens[:-1]):
        if not re.fullmatch(r'[A-Za-z_$][A-Za-z0-9_$]*',v) or v in excluded or tokens[i+1][0]!='(' or i and tokens[i-1][0] in ('.','new'):
            continue
        end=close(tokens,i+1,'(',')')+1
        if end<len(tokens) and tokens[end][0]=='throws':
            while tokens[end][0]!='{':
                end+=1
        if end<len(tokens) and tokens[end][0]=='{':
            result.append((i,close(tokens,end,'{','}'),v))
    return result


def inventory():
    normal=data.read_checked(data.BASE/'PG11348-api-web-source-guard-six-compile-v1/manifest.json',
        '46569de89d536e303184cd570d83f5138eb3a344abeb64f4e01160622a5482e8')
    hashes=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==0
    java={p:h for p,h in hashes.items() if p.startswith('src/') and p.endswith('.java')}
    assert len(java)==1810 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in java.items())
    rows=[]
    references={}
    for path in sorted(java):
        text=(data.ROOT/path).read_text()
        if not any(t in text for t in TYPES):
            continue
        references[path]=java[path]
        ts=[(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
        scopes=functions(ts)
        for i,(token,offset) in enumerate(ts[:-1]):
            if token not in TYPES:
                continue
            if ts[i+1][0]==':' and ts[i+2][0]==':' and ts[i+3][0]=='new':
                raise ValueError('new method reference requires explicit review')
            if ts[i-1][0]!='new' or ts[i+1][0]!='(':
                continue
            candidates=[(a,b,n) for a,b,n in scopes if a<=i<=b]
            a,b,method=min(candidates,key=lambda x:x[1]-x[0])
            body=''.join(t for t,_ in ts[a:b+1])
            stem=Path(path).stem
            if stem.endswith('StandardMetricSourceTest'):
                if 'host005' in method:
                    assert 'assertThrows(NullPointerException.class' in body
                    status='CONSTRUCTOR_REJECTS_NULL_PORT_NO_OWNER_RETURNED'
                else:
                    assert 'finally{owner.close();}' in body
                    status='CORE_OWNER_FINALLY_GUARDED_PREVIOUS_SCOPE_PROOF'
            elif stem in ('ApiMetricContext','WebMetricContext'):
                assert method==stem and 'this(' in body and 'new'+token+'()' in body
                status='UNBOUND_RESOURCE_FREE_OWNER_CONSTRUCTOR_TRANSFER_TO_CONTEXT'
                assert 'standard.bind(mode);' in ''.join(t for t,_ in ts) and 'standard.close();' in ''.join(t for t,_ in ts)
            elif stem in ('ApiMetricContextTest','WebMetricContextTest'):
                if method=='Harness':
                    assert 'standardOwner' in body and 'context=new' in body
                    assert 'context.close();' in text and 'if (!standard.isClosed()) standard.close();' in text
                    status='UNBOUND_TRANSFER_TO_HARNESS_CONTEXT_CLOSE_WITH_UNUSED_CANDIDATE_CLEANUP'
                else:
                    assert 'mctx005' in method and 'finally{standard.close();}' in body
                    status='CALLER_NULL_PORT_CASE_FINALLY_GUARDED'
            elif stem=='ApiObservationContextTest':
                assert method=='Fixture' and 'metrics=newApiMetricContext' in body and 'newApiObservationContext(' in body
                assert 'metrics.close();' in text
                status='UNBOUND_TRANSFER_TO_RETAINED_METRICS_FIXTURE_NO_RUNTIME_QUALIFICATION_INFERRED'
            elif stem in ('ApiCustomMetricPayloadTest','WebCustomMetricPayloadTest','BatchMetricTextTest'):
                if method=='fullOwner':
                    assert 'owner.bind(' in body and 'returnowner;' in body and 'finally' not in body
                    status='RETURN_BEFORE_TRANSFER_BIND_FAILURE_GUARD_GAP_BUG1910'
                elif 'finally{standard.close();}' in body:
                    status='DIRECT_STANDARD_OWNER_FINALLY_GUARDED'
                elif 'try(' in body and 'varstandard=new'+token+'()' in body:
                    status='DIRECT_STANDARD_OWNER_TWR_BEFORE_BIND'
                else:
                    raise ValueError('unreviewed direct source constructor')
            else:
                raise ValueError('unreviewed source constructor caller')
            rows.append(dict(path=path,line=text.count('\n',0,offset)+1,type=token,method=method,
                source=SOURCE,sourceSha256=java[path],methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[a:b+1]).encode()),
                status=status,productTestsExecuted=0,coverage=None,ptExecutionExempt=False))
    assert len(references)==17 and len(rows)==74 and len({r['path'] for r in rows})==11
    assert Counter(Path(r['path']).stem for r in rows)==Counter(ApiStandardMetricSourceTest=17,WebStandardMetricSourceTest=17,
        BatchStandardMetricSourceTest=17,ApiCustomMetricPayloadTest=5,WebCustomMetricPayloadTest=5,BatchMetricTextTest=4,
        ApiMetricContext=2,WebMetricContext=2,ApiMetricContextTest=2,WebMetricContextTest=2,ApiObservationContextTest=1)
    assert sum(r['status']=='RETURN_BEFORE_TRANSFER_BIND_FAILURE_GUARD_GAP_BUG1910' for r in rows)==3
    additional=[]
    for role in ('api','web'):
        typ=role.capitalize()
        path=f'src/schubert-nk-{role}/src/test/java/dev/codex/schubert/nk/{role}/monitoring/{typ}CustomMetricPayloadTest.java'
        text=(data.ROOT/path).read_text()
        tokens=[(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
        a,b,method=next((a,b,n) for a,b,n in functions(tokens) if n.startswith(role+'full012'))
        body=''.join(t for t,_ in tokens[a:b+1])
        assert 'varstandard=fullOwner(probe);varexecutor=Executors.newSingleThreadExecutor();try(' in body
        assert 'release.countDown();executor.shutdownNow();assertTrue(executor.awaitTermination(30,TimeUnit.SECONDS));standard.close();' in body
        additional.append(dict(path=path,method=method,sourceSha256=java[path],status='RETURNED_OWNER_BEFORE_EXECUTOR_SETUP_GUARD_GAP_BUG1910',
            methodTokenSha256=data.sha('\0'.join(t for t,_ in tokens[a:b+1]).encode())))
    return dict(source=SOURCE,referenceFiles=references,constructorSites=rows,additionalCallerGuardGaps=additional,
        counts=dict(directConstructors=74,callerFiles=11,sourceReferenceFiles=17,helperBindGaps=3,returnedOwnerSetupGaps=2),
        productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,newAccepted=0,effortPercent=None,
        wholeF03Accepted=False,whole451Accepted=False,ykt1659='IN_PROGRESS',externalActions=0)


def require(value,expected):
    if value!=expected:
        raise ValueError('exact source/site/flow inventory; no execution or blanket acceptance')


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    value=inventory()
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'sites.json',value)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,sitesSha256=data.sha((OUT/'sites.json').read_bytes()),
        counts=value['counts'],relatedBugs=['BUG-1910'],relatedYkt=['YKT-1659'],productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,
        newAccepted=0,effortPercent=None,whole451Accepted=False,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def post():
    invocation=capture(__file__)
    assert not POST.exists()
    primary=data.read_checked(OUT/'manifest.json',PRIMARY_SHA)
    value=data.read_checked(OUT/'sites.json',primary['sitesSha256'])
    expected=inventory()
    require(value,expected)
    bads=[]
    for k,v in [('source','old'),('productTestsExecuted',74),('coverage',100),('rawWarningsRemoved',5),('newAccepted',1),('ykt1659','COMPLETE')]:
        bad=copy.deepcopy(value);bad[k]=v;bads.append(bad)
    bad=copy.deepcopy(value);bad['constructorSites'].pop();bads.append(bad)
    bad=copy.deepcopy(value);bad['constructorSites'][0]['sourceSha256']='0'*64;bads.append(bad)
    for bad in bads:
        try:
            require(bad,expected)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid source/site or invented outcome accepted')
    verify(invocation)
    POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=PRIMARY_SHA,
        sitesSha256=primary['sitesSha256'],counts=expected['counts'],metadataNegativeVectors=len(bads),productTestsExecuted=0,coverage=None,
        rawWarningsRemoved=0,newAccepted=0,effortPercent=None,whole451Accepted=False,externalActions=0))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
