"""Current74 source owners and31 helper call paths; exact retained evidence, no product replay."""
from collections import Counter
import copy
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions,close,TYPES

SOURCE='4aee5c4b73ffae5426e0cc5d15fc928e06ece7b8'
OUT=data.BASE/'PG11402-source-owner-guard-final-v1'
POST=data.BASE/'PG11404-source-owner-guard-final-post-v1'
PRIMARY_SHA=None


def inventory():
    old_manifest=data.read_checked(data.BASE/'PG11370-source-constructor-owner-audit-v1/manifest.json',
        '2439413972f4aab4204fb2267631528fa72276182cc973075383226caf1c3b8a')
    old=data.read_checked(data.BASE/'PG11370-source-constructor-owner-audit-v1/sites.json',old_manifest['sitesSha256'])
    normal=data.read_checked(data.BASE/'PG11380-full-payload-guard-six-compile-v1/manifest.json',
        'f9691978776defaba64743818d99b493a80ab4f36b1cd30bae3eee542ab55be2')
    inverse=data.read_checked(data.BASE/'PG11378-full-payload-guard-source-post-v1/manifest.json',
        '7e135397d059752d94d46a7475c54a388846a1150a5460600c0528915dd160bc')
    proof=data.read_checked(data.BASE/'PG11386-full-payload-guard-post-v1/manifest.json',
        '11828d8e99e55d282d39b804331e3aff8fb83a4f6c396c4697fb0138d30d75c9')
    host=data.read_checked(data.BASE/'PG11382-full-payload-guard-host-v1/manifest.json',
        'a11545c458aad86980ff035f5b1609bcd62a341ddc0328dc85fd1140e162a080')
    assert normal['source']==host['source']==proof['source']==SOURCE and normal['actualExit']==host['actualExit']==proof['actualExit']==0
    assert host['observedTestExecutions']==89 and proof['originalObservedTestExecutions']==89
    assert inverse['allOriginalOracleTokensRestored'] and inverse['metadataNegativeVectors']==22
    changes={r['path']:r for r in inverse['sourceChanges']}
    assert len(changes)==3 and proof['allMainClassesUnchanged']==1843
    hashes=normal['begin']['inputHashes']
    java={p:h for p,h in hashes.items() if p.startswith('src/') and p.endswith('.java')}
    assert len(java)==1810 and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in java.items())
    assert all(hashes[p]==h for p,h in old['referenceFiles'].items() if p not in changes)
    assert all(hashes[p]==r['sha256'] and old['referenceFiles'][p]==r['beforeSha256'] for p,r in changes.items())
    expected=[(r['path'],r['type'],r['method']) for r in old['constructorSites']]
    sites,helper_calls=[],[]
    current_references={}
    for path in sorted(java):
        text=(data.ROOT/path).read_text()
        if not any(t in text for t in TYPES):
            continue
        current_references[path]=java[path]
        ts=[(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
        scopes=functions(ts)
        for i,(token,offset) in enumerate(ts[:-1]):
            if token in TYPES and ts[i-1][0]=='new' and ts[i+1][0]=='(':
                a,b,method=min((s for s in scopes if s[0]<=i<=s[1]),key=lambda s:s[1]-s[0])
                key=(path,token,method)
                assert key in expected
                body=''.join(t for t,_ in ts[a:b+1])
                old_rows=[r for r in old['constructorSites'] if (r['path'],r['type'],r['method'])==key]
                status=old_rows[0]['status']
                if method=='fullOwner':
                    assert 'booleantransferred=false;try{owner.bind(' in body
                    assert 'transferred=true;returnowner;}finally{if(!transferred)owner.close();}' in body
                    status='HELPER_BIND_GUARDED_UNTIL_SUCCESSFUL_RETURN_TRANSFER'
                else:
                    assert 'GAP' not in status
                sites.append(dict(path=path,type=token,method=method,line=text.count('\n',0,offset)+1,
                    sourceSha256=java[path],methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[a:b+1]).encode()),status=status))
            if token!='fullOwner' or ts[i+1][0]!='(' or any(a==i for a,_,_ in scopes):
                continue
            assert path in changes
            a,b,method=min((s for s in scopes if s[0]<=i<=s[1]),key=lambda s:s[1]-s[0])
            body=''.join(t for t,_ in ts[a:b+1])
            resource_lists=[(j,close(ts,j+1,'(',')')) for j in range(a,b) if ts[j][0]=='try' and ts[j+1][0]=='(']
            if any(j<i<end for j,end in resource_lists):
                status='RETURNED_OWNER_CAPTURED_IN_CALLER_TWR_RESOURCE_INITIALIZER'
            elif 'full012' in method:
                assert 'varstandard=fullOwner(probe);try{try(varexecutor=Executors.newSingleThreadExecutor())' in body
                assert body.endswith('}finally{standard.close();}}')
                status='RETURNED_OWNER_IMMEDIATE_OUTER_FINALLY_BEFORE_EXECUTOR_ACQUISITION'
            else:
                assert method.endswith('full013HelperReleasesRejectedCandidateBeforeReturningOwner')
                assert 'probe.close();assertEquals(1,probe.closes.get());' in body
                assert 'assertThrows(IllegalStateException.class,()->fullOwner(probe))' in body
                assert 'assertEquals(2,probe.closes.get());' in body and 'assertEquals(0,probe.scrapes.get());' in body
                assert any(r['method']==method and r['path']==path for r in host['begin']['cases'])
                status='REJECTED_HELPER_RETURNS_NO_OWNER_CLEANUP_VERIFIED_BY_NEW_INDEPENDENT_CASE'
            helper_calls.append(dict(path=path,method=method,line=text.count('\n',0,offset)+1,
                sourceSha256=java[path],methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[a:b+1]).encode()),status=status))
    assert Counter((r['path'],r['type'],r['method']) for r in sites)==Counter(expected)
    assert len(sites)==74 and set(current_references)==set(old['referenceFiles'])
    assert len(helper_calls)==31 and Counter(r['status'] for r in helper_calls)==Counter(
        RETURNED_OWNER_CAPTURED_IN_CALLER_TWR_RESOURCE_INITIALIZER=26,
        RETURNED_OWNER_IMMEDIATE_OUTER_FINALLY_BEFORE_EXECUTOR_ACQUISITION=2,
        REJECTED_HELPER_RETURNS_NO_OWNER_CLEANUP_VERIFIED_BY_NEW_INDEPENDENT_CASE=3)
    return dict(source=SOURCE,sourceReferenceFiles=current_references,constructorSites=sites,helperCalls=helper_calls,
        counts=dict(directSites=74,helperCalls=31,helperCallerTwr=26,helperCallerFinally=2,helperRejectCases=3),
        originalAuditSha256=data.sha((data.BASE/'PG11370-source-constructor-owner-audit-v1/manifest.json').read_bytes()),
        sameSourceRuntimeProof='11828d8e99e55d282d39b804331e3aff8fb83a4f6c396c4697fb0138d30d75c9',
        sourceOwnerGuardScopeComplete=True,wholeSdkFixtureResourceQualification=False,wholeF03Accepted=False,
        productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,newAccepted=0,effortPercent=None,externalActions=0)


def require(value,expected):
    if value!=expected:
        raise ValueError('exact complete current guard/transfer proof, not whole resource/F03 qualification')


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    value=inventory()
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'sites.json',value)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,sitesSha256=data.sha((OUT/'sites.json').read_bytes()),
        counts=value['counts'],relatedYkt=['YKT-1659'],sourceOwnerGuardScopeComplete=True,wholeSdkFixtureResourceQualification=False,
        productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,wholeF03Accepted=False,newAccepted=0,effortPercent=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def post():
    invocation=capture(__file__)
    assert not POST.exists()
    primary=data.read_checked(OUT/'manifest.json',PRIMARY_SHA)
    value=data.read_checked(OUT/'sites.json',primary['sitesSha256'])
    expected=inventory()
    require(value,expected)
    bads=[]
    for key,v in [('source','old'),('productTestsExecuted',89),('coverage',100),('rawWarningsRemoved',9),('newAccepted',1),('wholeSdkFixtureResourceQualification',True),('wholeF03Accepted',True)]:
        bad=copy.deepcopy(value);bad[key]=v;bads.append(bad)
    for key in ('constructorSites','helperCalls'):
        bad=copy.deepcopy(value);bad[key].pop();bads.append(bad)
    bad=copy.deepcopy(value);bad['helperCalls'][0]['status']='ASSUMED';bads.append(bad)
    for bad in bads:
        try:
            require(bad,expected)
        except ValueError:
            pass
        else:
            raise AssertionError('invented or incomplete owner guard proof accepted')
    verify(invocation)
    POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=PRIMARY_SHA,
        sitesSha256=primary['sitesSha256'],counts=expected['counts'],metadataNegativeVectors=len(bads),sourceOwnerGuardScopeComplete=True,
        wholeSdkFixtureResourceQualification=False,productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,newAccepted=0,
        effortPercent=None,wholeF03Accepted=False,externalActions=0))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
