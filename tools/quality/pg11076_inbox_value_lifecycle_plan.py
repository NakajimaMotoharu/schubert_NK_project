"""Extend fifteen owned Test declarations to TWR, preserve all original assertions and values."""
import difflib
from pathlib import Path
import sys
import g07_host_class_provenance_inputs as data
from public_java_digest_provenance import LEX
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical
from pg10339_result_profile_oracle_post_v2 import folded

OUT=data.BASE/'PG11076-inbox-value-lifecycle-plan-v1'
PREFIX='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/idempotency/'
OPERATIONS={
 'InboxModelTest': [('requestRejectsNullsScopeTokenOwnerAndTimeViolations','CanonicalRequest login =',2)],
 'OperationFingerprintTest': [
  ('goldenCanonicalAndHmacMatchIndependentOpenSslVector','CanonicalRequest request = goldenRequest();',1),
  ('nfcNormalizationAndNullEmptyDistinctionAreStable','CanonicalRequest nfd =',4),
  ('canonicalModelsDefensivelyCopyAndRedact','CanonicalRequest request =',1),
  ('canonicalModelsDefensivelyCopyAndRedact','CanonicalField field =',1),
  ('invalidModelsAndFingerprintArgumentsAreRejected','CanonicalRequest request = goldenRequest();',1)],
 'SecretBufferTest': [
  ('supersededAndCurrentStreamStorageAreWipedAtGrowthResetAndClose','var stream = new Inspectable();',1),
  ('requestOwnerClosesEveryFieldWithoutModifyingCallerCopiesOrFingerprint','var value = new CanonicalField(',4)]}


def body_span(text,method):
    tokens=list(LEX.finditer(text))
    starts=[i for i,t in enumerate(tokens) if t.group()==method and i and tokens[i-1].group()=='void']
    assert len(starts)==1
    start=next(i for i in range(starts[0],len(tokens)) if tokens[i].group()=='{')
    depth=1
    for end in range(start+1,len(tokens)):
        depth+=(tokens[end].group()=='{')-(tokens[end].group()=='}')
        if depth==0:
            return tokens[start].end(),tokens[end].start()
    raise ValueError('bounded complete method body required')


def transformed(stem,before):
    text=before
    wrappers=[]
    for method,first,count in OPERATIONS[stem]:
        begin,end=body_span(text,method)
        body=text[begin:end]
        assert body.count(first)==1
        start=body.index(first)
        tokens=list(LEX.finditer(body[start:]))
        semis=[m for m in tokens if m.group()==';']
        stop=start+semis[count-1].end()
        declarations=body[start:stop]
        header=declarations.rstrip().removesuffix(';')
        text=text[:begin]+body[:start]+'try ('+header+') {\n'+body[stop:]+'\n}'+text[end:]
        wrappers.append(dict(method=method,declarations=declarations,resources=count))
    if stem=='SecretBufferTest':
        assert 'assertDoesNotThrow' not in text
        text=text.replace('import static org.junit.jupiter.api.Assertions.assertArrayEquals;',
            'import static org.junit.jupiter.api.Assertions.assertArrayEquals;\nimport static org.junit.jupiter.api.Assertions.assertDoesNotThrow;')
        assert text.count('stream.close();')==2 and text.count('request.close();')==1
        text=text.replace('stream.close();','assertDoesNotThrow(stream::close);').replace('request.close();','assertDoesNotThrow(request::close);')
        text=text.replace('class SecretBufferTest {','class SecretBufferTest {\n  private static final int MAXIMUM_FIXTURE_CAPACITY = 1_050_000;',1)
        assert text.count('if (length == 1_050_000)')==1
        text=text.replace('if (length == 1_050_000)','if (length == MAXIMUM_FIXTURE_CAPACITY)')
    return text,wrappers


def inputs():
    normal=data.read_checked(data.BASE/'PG11068-inbox-value-six-compile-v1/manifest.json','c0adec1cf3206e0190692c709761803a00f776d3f75c10475294c06e676ea42b')
    assert normal['actualExit']==0 and normal['source']=='c869ff6b7394773e05aee09d0d4390fce1396d9e'
    snapshot=Path(normal['jars']['api']['path']).parent.parent.parent.parent
    return normal,snapshot


def emit():
    _,snapshot=inputs()
    patch='*** Begin Patch\n'
    for stem in OPERATIONS:
        path=PREFIX+stem+'.java'
        before=(snapshot/path).read_text()
        assert (data.ROOT/path).read_text()==before
        after,_=transformed(stem,before)
        patch+='*** Update File: '+str(data.ROOT/path)+'\n'
        patch+='\n'.join('@@' if s.startswith('@@') else s for s in list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:])+'\n'
    return patch+'*** End Patch\n'


def main():
    invocation=capture(Path(__file__))
    assert not OUT.exists()
    normal,snapshot=inputs()
    changed={PREFIX+s+'.java' for s in OPERATIONS}
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in changed)
    rows=[]
    for stem in OPERATIONS:
        path=PREFIX+stem+'.java'
        before,after=(snapshot/path).read_text(),(data.ROOT/path).read_text()
        planned,wrappers=transformed(stem,before)
        assert folded(canonical(after))==folded(canonical(planned))
        rows.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),wrappers=wrappers))
    assert sum(w['resources'] for row in rows for w in row['wrappers'])==15
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=rows,
        twrOwnedDeclarations=15,twrScopes=8,normalCloseAssertionsAdded=3,numericBoundaryReferences=1,
        productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
