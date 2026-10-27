"""Nine same-value String names in three whole public text Tests; source inverse, PT0."""
import difflib
import re
import sys
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX

OUT=data.BASE/'PG12570-public-unit-plan-v1'
PREFIX='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/'
SPECS={
    'ArtemisServiceUnitTest':{'DIRECTIVE_TRUE':('true',4)},
    'CleanupServiceUnitTest':{'ROOT_ACCOUNT':('root',4)},
    'SupplementaryUnitTemplateTest':{'DIRECTIVE_TRUE':('true',16),'SERVICE_SECTION':('Service',33),'STOP_TIMEOUT_KEY':('TimeoutStopSec',4),'THIRTY_SECONDS':('30s',5),'UNIT_SECTION':('Unit',5),'MINIMUM_HEAP_OPTION':('-Xms',5),'MAXIMUM_HEAP_OPTION':('-Xmx',6)}}


def raw(text):return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]


def before():
    n=data.read_checked(data.BASE/'PG12551-monitoring-main-six-compile-v2/manifest.json','a51e4812b19c20f1ef673b35278a9c4ef75e08100e785360033bbd5c1afdc5e0')
    assert n['source']=='fb1a22da2433c7909ceba05c7eeb07c879e52325' and n['actualExit']==n['testsExecuted']==0
    snap=Path(n['jars']['batch']['path']).parent.parent.parent.parent
    old={PREFIX+name+'.java':(snap/(PREFIX+name+'.java')).read_text() for name in SPECS}
    assert all(data.sha(text.encode())==n['begin']['inputHashes'][p] for p,text in old.items())
    return n,old


def intended(old):
    result={}
    for name,definitions in SPECS.items():
        p=PREFIX+name+'.java';text=old[p]
        for symbol,(literal,count) in definitions.items():
            token='"'+literal+'"';assert text.count(token)==count;text=text.replace(token,symbol)
        declarations=''.join('  private static final String '+s+' = "'+v+'";\n' for s,(v,_) in definitions.items())
        match=re.search(r'(?:final )?class '+name+r' \{\n',text);assert match
        text=text[:match.end()]+declarations+'\n'+text[match.end():];result[p]=text
    return result


def require_equivalent(old,new):
    assert set(old)==set(new)
    for name,definitions in SPECS.items():
        p=PREFIX+name+'.java';text=new[p]
        for symbol,(literal,count) in definitions.items():
            declaration='  private static final String '+symbol+' = "'+literal+'";\n'
            assert text.count(declaration)==1;text=text.replace(declaration,'')
            assert len(re.findall(r'\b'+symbol+r'\b',text))==count
            text=re.sub(r'\b'+symbol+r'\b','"'+literal+'"',text)
        assert raw(text)==raw(old[p])


def emit():
    _,old=before();new=intended(old);require_equivalent(old,new);patch='*** Begin Patch\n'
    for p in old:
        assert (data.ROOT/p).read_text()==old[p]
        patch+='*** Update File: '+str(data.ROOT/p)+'\n'+'\n'.join('@@' if x.startswith('@@') else x for x in list(difflib.unified_diff(old[p].splitlines(),new[p].splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'


def main():
    invocation=capture(__file__);assert not OUT.exists();n,old=before();new={p:(data.ROOT/p).read_text() for p in old};require_equivalent(old,new)
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in n['begin']['inputHashes'].items() if p not in new)
    vectors=[]
    for name,definitions in SPECS.items():
        p=PREFIX+name+'.java'
        for symbol,(literal,_) in definitions.items():
            declaration='  private static final String '+symbol+' = "'+literal+'";\n'
            for bad in (new[p].replace(declaration,'',1),new[p].replace(declaration,declaration.replace(' = "',' = "WRONG-',1),1),new[p].replace(symbol,'WRONG_SYMBOL',1)):
                assert bad!=new[p];vectors.append({**new,p:bad})
    p=PREFIX+'ArtemisServiceUnitTest.java'
    for a,b in [('@Test','@Disabled'),('assertEquals(1,','assertEquals(0,')]:
        bad=new[p].replace(a,b,1);assert bad!=new[p];vectors.append({**new,p:bad})
    for bad in vectors:
        try:require_equivalent(old,bad)
        except AssertionError:pass
        else:raise AssertionError('invalid original text oracle accepted')
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2354_公開Unit三Test九同値是正_単体テスト仕様書.md'
    verify(invocation);OUT.mkdir();value=dict(actualExit=0,sourceBefore=n['source'],invocation=invocation,sourceChanges=[dict(path=p,beforeSha256=data.sha(old[p].encode()),sha256=data.sha(new[p].encode())) for p in old],literalCorrections=9,literalReferences=82,metadataNegativeVectors=len(vectors),allMainAndOtherInputsUnchanged=True,originalTests=13,originalSuites=3,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),productTestsExecuted=0,newAccepted=0,coverage=None)
    data.write(OUT/'manifest.json',value);print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
