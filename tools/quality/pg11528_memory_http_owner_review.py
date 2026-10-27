"""All52 existing source-bound warning sites; fifty logical fixture guard gaps and two immediately closed contexts."""
from collections import Counter
import copy
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical
from pg11370_source_constructor_owner_audit import functions
from pg11312_batch_resource_ownership_review import method_tokens
from pg11054_api_request_context import original_match

SOURCE='60d702bf8d83b6c4c8531397a7b770234fd9cf6e'
OUT=data.BASE/'PG11528-memory-http-owner-review-v1'
POST=data.BASE/'PG11530-memory-http-owner-review-post-v1'
PRIMARY_SHA=None

def review():
    normal=data.read_checked(data.BASE/'PG11504-metric-http-literal-six-compile-v1/manifest.json','8a626280621377d27599da1616906f6f1ef2d6f83420e25d495554392b250b11')
    assert normal['source']==SOURCE and normal['actualExit']==0
    hashes=normal['begin']['inputHashes'];assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    sp=data.BASE/'PG11508-metric-http-literal-static-v1/manifest.json'
    static=data.read_checked(sp,'fa8d830558c7799fd70f71104ed49c9cc559e31d3677e73b4a16b12f6072b678')
    raw=(sp.parent/'pmd.xml').read_bytes();assert data.sha(raw)==static['reports']['pmd']['sha256']
    actual=[(str(Path(f.get('name')).relative_to(data.ROOT)),n) for f in ET.fromstring(raw) if f.tag.rpartition('}')[2]=='file' for n in f if n.tag.rpartition('}')[2]=='violation']
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    assert len(actual)==52 and all(n.get('rule')=='CloseResource' for _,n in actual)
    sites=[];declarations=[];main_hashes={}
    for role in ('api','web'):
        path=f'src/schubert-nk-{role}/src/test/java/dev/codex/schubert/nk/{role}/monitoring/{role.capitalize()}MetricHttpHandlerTest.java'
        text=(data.ROOT/path).read_text();compact=''.join(canonical(text))
        assert 'publicvoidclose(){closed=true;closeCalls++;}' in compact
        assert 'privateExchange(Stringmethod,Stringpath){this.method=method;this.uri=URI.create(path);}' in compact
        assert 'privatefinalByteArrayOutputStreamoutput=newByteArrayOutputStream();' in compact
        assert not any(t in text for t in ('HttpServer.create(', 'new Socket(', 'openConnection(', 'getConnection('))
        ts=[(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
        scopes=functions(ts)
        for declaration in re.finditer(r'\bvar (exchange|first|second|missing) = new Exchange\([^;]*\);',text):
            index=next(i for i,(_,pos) in enumerate(ts) if pos==declaration.start())
            a,b,method=min((s for s in scopes if s[0]<=index<=s[1]),key=lambda s:s[1]-s[0])
            assert method.startswith(role+'mhttp') and 'finally' not in [t for t,_ in ts[a:b+1]]
            declarations.append((path,method,declaration[1]))
        main=path.replace('/src/test/','/src/main/').replace('HandlerTest.java','Handler.java')
        main_text=(data.ROOT/main).read_text();main_hashes[main]=hashes[main]
        assert 'try(exchange){write(exchange);}' in ''.join(method_tokens(main_text,'handle'))
        assert 'exchange.close()' not in ''.join(method_tokens(main_text,'write'))
    assert len(declarations)==len(set(declarations))==50
    for path,node in actual:
        old=original_match(path,node,original,actual);method=node.get('method');variable=node.get('variable')
        body=method_tokens((data.ROOT/path).read_text(),method)
        if variable=='context':
            assert method.endswith('mhttp009') and 'varcontext=standard();context.close();' in ''.join(body)
            status='IMMEDIATELY_CLOSED_CONTEXT_CURRENT_WHOLE_PENDING';bug=None
        else:
            assert (path,method,variable) in declarations
            status='LOGICAL_EXCHANGE_PRE_HANDOFF_GUARD_GAP_BUG1921';bug='BUG-1921'
        sites.append(dict(id=old['id'],path=path,source=SOURCE,sourceSha256=hashes[path],attributes=dict(node.attrib),originalRowSha256=old['rowSha256'],
            methodTokenSha256=data.sha('\0'.join(body).encode()),status=status,bug=bug,physicalSocketOrOsResourceLeakObserved=False,
            rawWarningRetained=True,ptExecutionExempt=False,productTestsExecuted=0,coverage=None))
    counts=Counter(r['status'] for r in sites)
    assert counts==Counter(LOGICAL_EXCHANGE_PRE_HANDOFF_GUARD_GAP_BUG1921=50,IMMEDIATELY_CLOSED_CONTEXT_CURRENT_WHOLE_PENDING=2)
    assert {(r['path'],r['attributes']['method'],r['attributes']['variable']) for r in sites if r['bug']}==set(declarations)
    return dict(source=SOURCE,sites=sites,counts=dict(counts),mainHashes=main_hashes,guardGaps=50,immediatelyClosedContexts=2,
        handleOwnsExchange=True,writeBorrowsExchange=True,exchangeCloseIsLogicalOnly=True,relatedBugs=['BUG-1921'],relatedYkt=['YKT-1670'],
        productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,newAccepted=0,effortPercent=None,wholeF03Accepted=False,externalActions=0)

def require(value,expected):
    if value!=expected:
        raise ValueError('all52 exact source-bound sites and concrete ownership facts required')

def main():
    invocation=capture(__file__);assert not OUT.exists()
    value=review();verify(invocation);OUT.mkdir();data.write(OUT/'review.json',value)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),
        reviewed=52,guardGaps=50,immediatelyClosedContexts=2,relatedBugs=['BUG-1921'],relatedYkt=['YKT-1670'],
        productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,newAccepted=0,effortPercent=None,wholeF03Accepted=False,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

def post():
    invocation=capture(__file__);assert not POST.exists()
    primary=data.read_checked(OUT/'manifest.json',PRIMARY_SHA);value=data.read_checked(OUT/'review.json',primary['reviewSha256']);expected=review();require(value,expected)
    bads=[]
    for key,v in [('source','old'),('guardGaps',0),('productTestsExecuted',52),('coverage',100),('rawWarningsRemoved',52),('newAccepted',1),('wholeF03Accepted',True),('handleOwnsExchange',False),('writeBorrowsExchange',False)]:
        bad=copy.deepcopy(value);bad[key]=v;bads.append(bad)
    bad=copy.deepcopy(value);bad['sites'].pop();bads.append(bad)
    for bad in bads:
        try:
            require(bad,expected)
        except ValueError:
            pass
        else:
            raise AssertionError('invented cleanup/runtime proof accepted')
    verify(invocation);POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=PRIMARY_SHA,
        reviewSha256=primary['reviewSha256'],metadataNegativeVectors=len(bads),reviewed=52,guardGaps=50,immediatelyClosedContexts=2,
        productTestsExecuted=0,coverage=None,rawWarningsRemoved=0,newAccepted=0,effortPercent=None,wholeF03Accepted=False,externalActions=0))
    print(data.sha((POST/'manifest.json').read_bytes()))

if __name__=='__main__':
    main()
