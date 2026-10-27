"""Current GC Fake lifetime gaps and deliberate poison Tag comparison oracle; read-only public facts."""
import copy
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical
from pg11104_web_pure_value_source_post import remove
from pg11320_batch_source_guard_source_post import replace_once
from pg11370_source_constructor_owner_audit import functions
from pg11312_batch_resource_ownership_review import method_tokens

SOURCE='2d733dbd80350c819b732ae3d9b9b0f85ba0172f'
OUT=data.BASE/'PG11434-gc-fake-comparable-review-v1'
POST=data.BASE/'PG11436-gc-fake-comparable-review-post-v1'
PRIMARY_SHA=None


def normalized(text,role):
    tokens=canonical(text)
    for m in re.finditer(r'private static final String (\w+)\s*=\s*("(?:\\.|[^"\\])*")\s*;',text):
        name,value=m.groups()
        remove(tokens,canonical(m.group()))
        tokens=[value if t==name else t for t in tokens]
    replace_once(tokens,canonical('package dev.codex.schubert.nk.'+role+'.monitoring;'),canonical('package dev.codex.schubert.nk.ROLE.monitoring;'))
    # Only the exact application package above changes; org.junit.jupiter.api never changes.
    assert any(tokens[i:i+7]==['org','.','junit','.','jupiter','.','api'] for i in range(len(tokens)-6))
    return [('RoleGcMetricRegistration' if t==role.capitalize()+'GcMetricRegistration' else
        'RoleGcMetricRegistrationTest' if t==role.capitalize()+'GcMetricRegistrationTest' else
        'ROLE'+t[len(role):] if re.fullmatch(role+r'gc[0-9]+\w*',t) else
        '"ROLE"' if t=='"'+role.upper()+'"' else '"CONFIG_INVALID"' if t=='"invalid monitoring mode"' else t) for t in tokens]


def review():
    normal=data.read_checked(data.BASE/'PG11412-api-web-payload-literal-six-compile-v1/manifest.json',
        'b560ea0179e27b26375d96e7deb6f39deba5e728a2c5d57ed0fee6c46a67933d')
    assert normal['source']==SOURCE and normal['actualExit']==0
    hashes=normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items() if p.startswith('src/') and p.endswith('.java'))
    sdk=data.read_checked(data.BASE/'PG8540-api-gc-owned-six-trace-v1/manifest.json',
        'a50ecec93317318380b9ab6c992ba978d0cc86019563f2ee06405f49d5025150')['sdkActivationMetadata']
    assert sdk['constructorHasNoNotificationRegistration'] and sdk['bindRegisters'] and sdk['closeRemoves']
    assert data.sha(Path(sdk['jarPath']).read_bytes())==sdk['jarSha256']=='9ca47dfa831409b40253c8dc98c17b9d3e050ebbde4d1543c5521dca2b95ad56'
    rows=[];normalized_rows={};files={}
    for role in ('api','web','batch'):
        path=f'src/schubert-nk-{role}/src/test/java/dev/codex/schubert/nk/{role}/monitoring/{role.capitalize()}GcMetricRegistrationTest.java'
        text=(data.ROOT/path).read_text();files[path]=hashes[path]
        normalized_rows[role]=normalized(text,role)
        compact=''.join(canonical(text))
        assert 'publicvoidbindTo(MeterRegistrysource){bindInvocations.incrementAndGet();onBindCallback.accept(source);}' in compact
        assert 'publicvoidclose(){closeInvocations.incrementAndGet();onCloseCallback.run();}' in compact
        ts=[(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
        scopes=functions(ts)
        for i,(v,pos) in enumerate(ts[:-6]):
            if v!='var' or ts[i+1][0] not in ('resource','one','two') or [t for t,_ in ts[i+2:i+7]]!=['=','new','Fake','(',')']:
                continue
            a,b,method=min((s for s in scopes if s[0]<=i<=s[1]),key=lambda s:s[1]-s[0])
            assert any(method.startswith(role+'gc'+number) for number in ('003','009','010','011','012','013','014'))
            body=''.join(t for t,_ in ts[a:b+1])
            assert 'finally' not in body
            rows.append(dict(path=path,line=text.count('\n',0,pos)+1,variable=ts[i+1][0],method=method,sourceSha256=hashes[path],
                methodTokenSha256=data.sha('\0'.join(t for t,_ in ts[a:b+1]).encode()),status='FIXTURE_CANDIDATE_EXCEPTIONAL_GUARD_GAP_BUG1913',
                sdkActivation=False,logicalCleanupRequired=True))
        forbidden=method_tokens(text,role+'gc006ClosedDebugFailsBeforeFactoryAndOwner')
        assert ''.join(forbidden).count('assertEquals(0,calls.get());')==1
        assert 'returnnewFake();' in ''.join(forbidden)
    assert len(rows)==24 and all(len([r for r in rows if '/nk/'+role+'/' in r['path']])==8 for role in ('api','web','batch'))
    assert normalized_rows['api']==normalized_rows['web']==normalized_rows['batch'] and len(normalized_rows['batch'])==2956
    old=data.read_checked(data.BASE/'PG11312-batch-resource-ownership-review-v1/manifest.json','b672a132d30a89a0ef003a181f47aca733d6ceff5d07591736fd11274c52182a')
    old_rows=data.read_checked(data.BASE/'PG11312-batch-resource-ownership-review-v1/sites.json',old['sitesSha256'])
    six=[r for r in old_rows if r['basis']['status']=='FAKE_NO_SDK_ACTIVATION_LOGICAL_LIFETIME_UNCLASSIFIED']
    assert len(six)==6 and all(hashes[r['path']]==r['sourceSha256'] for r in six)
    text_path='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring/BatchMetricTextTest.java'
    text=(data.ROOT/text_path).read_text();compact=''.join(canonical(text))
    assert 'publicintcompareTo(Tagother){thrownewAssertionError("no provider sort");}' in compact
    oracle=method_tokens(text,'batchtext012DuplicateAndNullTagContractsAreNotNormalized')
    assert 'List.of(tag(null,PART_SUFFIX),tag(SUFFIX_LABEL,null))' in ''.join(oracle)
    assert 'assertThrows(NullPointerException.class,()->text(newNoopGauge(raw(G,List.of(invalid)))));' in ''.join(oracle)
    policy='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/BatchMetricLabelPolicy.java'
    policy_text=(data.ROOT/policy).read_text()
    assert 'Objects.requireNonNull(tag.getKey()' in policy_text and 'Objects.requireNonNull(tag.getValue()' in policy_text
    assert 'compareTo' not in policy_text and 'new TreeMap<String, String>()' in policy_text
    return dict(source=SOURCE,sourceHashes={**files,text_path:hashes[text_path],policy:hashes[policy]},candidateSites=rows,
        originalBatchWarningIds=[r['id'] for r in six],normalizedRoleTokens=2956,applicationPackageOnlyNormalization=True,
        comparable=dict(status='DELIBERATE_POISON_NULL_LABEL_PROVIDER_CONTEXT_CURRENT_WHOLE_PENDING',testId='BATCHTEXT012',
            methodTokenSha256=data.sha('\0'.join(oracle).encode()),equalsHashAdded=False,rawWarningRetained=True,
            proof='Only invalid null key/value Tag inputs use poison compareTo; explicit NPE oracle would reject its AssertionError. Main validates/copies Strings before sorting, never provider comparison'),
        sdkCoreSha256=sdk['jarSha256'],sdkConstructorNoListeners=True,fakeBindNeverActivatesSdk=True,
        additionalUnguardedSitesBeyondSixBatchWarnings=18,relatedBugs=['BUG-1913'],relatedYkt=['YKT-1662'],
        productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,newAccepted=0,effortPercent=None,wholeF03Accepted=False,externalActions=0)


def require(value,expected):
    if value!=expected:
        raise ValueError('exact current source,24 candidates, SDK activation and poison oracle facts only')


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    value=review();verify(invocation);OUT.mkdir()
    data.write(OUT/'review.json',value)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),
        candidateSites=24,batchOriginalWarnings=6,comparableContexts=1,relatedBugs=['BUG-1913'],relatedYkt=['YKT-1662'],
        productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,newAccepted=0,effortPercent=None,wholeF03Accepted=False,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


def post():
    invocation=capture(__file__)
    assert not POST.exists()
    primary=data.read_checked(OUT/'manifest.json',PRIMARY_SHA)
    value=data.read_checked(OUT/'review.json',primary['reviewSha256']);expected=review();require(value,expected)
    bads=[]
    for k,v in [('source','old'),('productTestsExecuted',24),('coverage',100),('rawWarningsRemoved',7),('newAccepted',1),('wholeF03Accepted',True)]:
        bad=copy.deepcopy(value);bad[k]=v;bads.append(bad)
    bad=copy.deepcopy(value);bad['candidateSites'].pop();bads.append(bad)
    bad=copy.deepcopy(value);bad['comparable']['rawWarningRetained']=False;bads.append(bad)
    bad=copy.deepcopy(value);bad['fakeBindNeverActivatesSdk']=False;bads.append(bad)
    for bad in bads:
        try:
            require(bad,expected)
        except ValueError:
            pass
        else:
            raise AssertionError('invented resource/oracle/runtime outcome accepted')
    verify(invocation);POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=PRIMARY_SHA,
        reviewSha256=primary['reviewSha256'],metadataNegativeVectors=len(bads),candidateSites=24,batchOriginalWarnings=6,comparableContexts=1,
        productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,newAccepted=0,effortPercent=None,wholeF03Accepted=False,externalActions=0))
    print(data.sha((POST/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
