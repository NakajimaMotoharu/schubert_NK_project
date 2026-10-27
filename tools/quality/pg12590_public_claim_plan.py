"""Four same-value literals in three whole memory-only claim codecs Tests, independent token inverse."""
import difflib
import re
import sys
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX

OUT=data.BASE/'PG12590-public-claim-plan-v1'
PREFIX='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/'
SPECS={
    PREFIX+'file/StartupLaunchRecordTest.java':{'PARENT_PID_ASSIGNMENT':('pid=300',4)},
    PREFIX+'platform/BackupWorkerRequestTest.java':{'VERIFY_DUMP_SIZE_ASSIGNMENT':('dump_size=3',4)},
    PREFIX+'platform/CleanupWorkerRequestTest.java':{'RUN_UUID_TEXT':('31100027-2222-4333-8444-555555555555',4),'CUTOFF_TEXT':('2026-09-27T15:00:00Z',4)}}


def raw(text):return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]


def before():
    n=data.read_checked(data.BASE/'PG12572-public-unit-six-compile-v1/manifest.json','fe361f6c8fb14008feb760c5b0437f7fc68777a776eb39ca7febc8ec49a27c1a')
    assert n['source']=='2efcd4ac8e1b7681fdba0862f7392bbbba5d3f68' and n['actualExit']==n['testsExecuted']==0
    snap=Path(n['jars']['batch']['path']).parent.parent.parent.parent
    old={p:(snap/p).read_text() for p in SPECS};assert all(data.sha(t.encode())==n['begin']['inputHashes'][p] for p,t in old.items())
    return n,old


def intended(old):
    result={}
    for p,definitions in SPECS.items():
        text=old[p]
        for symbol,(value,count) in definitions.items():
            token='"'+value+'"';assert text.count(token)==count;text=text.replace(token,symbol)
        declarations=''.join('  private static final String '+name+' = "'+value+'";\n' for name,(value,_) in definitions.items())
        match=re.search(r'(?:final )?class '+Path(p).stem+r' \{\n',text);assert match
        result[p]=text[:match.end()]+declarations+'\n'+text[match.end():]
    return result


def require_equivalent(old,new):
    assert set(old)==set(new)
    for p,definitions in SPECS.items():
        t=new[p]
        for symbol,(literal,count) in definitions.items():
            declaration='  private static final String '+symbol+' = "'+literal+'";\n'
            assert t.count(declaration)==1;t=t.replace(declaration,'')
            assert len(re.findall(r'\b'+symbol+r'\b',t))==count;t=re.sub(r'\b'+symbol+r'\b','"'+literal+'"',t)
        assert raw(t)==raw(old[p])


def emit():
    _,old=before();new=intended(old);require_equivalent(old,new);patch='*** Begin Patch\n'
    for p in old:
        assert (data.ROOT/p).read_text()==old[p]
        patch+='*** Update File: '+str(data.ROOT/p)+'\n'+'\n'.join('@@' if x.startswith('@@') else x for x in list(difflib.unified_diff(old[p].splitlines(),new[p].splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'


def main():
    invocation=capture(__file__);assert not OUT.exists();n,old=before();new={p:(data.ROOT/p).read_text() for p in old};require_equivalent(old,new)
    assert all(data.sha((data.ROOT/p).read_bytes())==digest for p,digest in n['begin']['inputHashes'].items() if p not in new)
    negatives=[]
    for p,definitions in SPECS.items():
        for symbol,(literal,_) in definitions.items():
            declaration='  private static final String '+symbol+' = "'+literal+'";\n'
            for bad in (new[p].replace(declaration,'',1),new[p].replace(declaration,declaration.replace(' = "',' = "WRONG-',1),1),new[p].replace(symbol,'WRONG_SYMBOL',1)):
                assert bad!=new[p];negatives.append({**new,p:bad})
    p=PREFIX+'file/StartupLaunchRecordTest.java'
    for a,b in [('@Test','@Disabled'),('assertArrayEquals(bytes(literal), record.encode());','assertArrayEquals(new byte[0], record.encode());')]:
        bad=new[p].replace(a,b,1);assert bad!=new[p];negatives.append({**new,p:bad})
    for bad in negatives:
        try:require_equivalent(old,bad)
        except AssertionError:pass
        else:raise AssertionError('changed original independent oracle accepted')
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2356_公開claim三Test四同値是正_単体テスト仕様書.md'
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=n['source'],invocation=invocation,sourceChanges=[dict(path=p,beforeSha256=data.sha(old[p].encode()),sha256=data.sha(new[p].encode())) for p in old],literalCorrections=4,literalReferences=16,metadataNegativeVectors=len(negatives),allMainAndOtherInputsUnchanged=True,originalTests=20,originalSuites=3,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),productTestsExecuted=0,newAccepted=0,coverage=None));print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
    else:assert not sys.argv[1:];main()
