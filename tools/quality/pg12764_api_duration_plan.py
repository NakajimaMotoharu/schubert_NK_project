"""Whole24 literal fixture constants by complete tokens only; preserve all golden text and control."""
import difflib
import sys
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
from fixture_scope_advisory import audit

SOURCE_BEFORE='f75d2fea05a98fe40d731d1a3046a64d20bbbb65'
OUT=data.BASE/'PG12764-api-duration-plan-v1'
PATH='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiDurationMetricExporterTest.java'
VALUES={'OUTCOME_LABEL':'"outcome"','SUCCESS_OUTCOME':'"SUCCESS"'}
COUNTS={'OUTCOME_LABEL':9,'SUCCESS_OUTCOME':10}


def tokens(text):
    return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]


def before():
    n=data.read_checked(data.BASE/'PG12745-metric-context-six-compile-v2/manifest.json','e4830adef59daf5496f23b5fe72f2288757ed3d6785b87077938d29e9626983f')
    assert n['source']==SOURCE_BEFORE and n['actualExit']==n['testsExecuted']==0
    root=Path(n['jars']['api']['path']).parent.parent.parent.parent
    text=(root/PATH).read_text();assert data.sha(text.encode())==n['begin']['inputHashes'][PATH]
    return n,text


def declaration(name,literal):
    return '  private static final String '+name+' = '+literal+';\n'


def intended(old):
    edits=[]
    for name,literal in VALUES.items():
        positions=[m for m in LEX.finditer(old) if m.group()==literal]
        assert len(positions)==COUNTS[name]
        edits.extend((m.start(),m.end(),name) for m in positions)
    text=old
    for start,end,name in sorted(edits,reverse=True):
        text=text[:start]+name+text[end:]
    anchor='  private static final String NAME'
    assert text.count(anchor)==1
    return text.replace(anchor,''.join(declaration(name,literal) for name,literal in VALUES.items())+anchor,1)


def require(old,new):
    text=new
    for name,literal in VALUES.items():
        decl=declaration(name,literal);assert text.count(decl)==1
        text=text.replace(decl,'',1)
    actual=tokens(text)
    for name,literal in VALUES.items():
        assert actual.count(name)==COUNTS[name]
        actual=[literal if value==name else value for value in actual]
    assert actual==tokens(old)


def emit():
    _,old=before();new=intended(old);require(old,new)
    assert (data.ROOT/PATH).read_text()==old
    return '*** Begin Patch\n*** Update File: '+str(data.ROOT/PATH)+'\n'+'\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(old.splitlines(),new.splitlines(),n=3))[2:])+'\n*** End Patch\n'


def main():
    invocation=capture(__file__);assert not OUT.exists()
    n,old=before();new=(data.ROOT/PATH).read_text();require(old,new)
    assert all(data.sha((data.ROOT/path).read_bytes())==digest for path,digest in n['begin']['inputHashes'].items() if path!=PATH)
    previous=data.read_checked(data.BASE/'PG12743-metric-context-plan-v3/manifest.json','8f93b0e7cfe3fdcd9e6dacbd13d936cafcb335645a571815097540574c6b7dd4')
    eligible={path:digest for path,digest in previous['eligibilityClosureSourceHashes'].items() if '/schubert-nk-protocol/' in path or path.endswith(('/ApiDurationMetricExporter.java','/ApiMetricCatalog.java'))}
    assert len(eligible)==11 and all(n['begin']['inputHashes'][path]==digest==data.sha((data.ROOT/path).read_bytes()) for path,digest in eligible.items())
    registry=data.read_checked(data.BASE/'PG12754-metric-context-trace-v1/manifest.json','40a26a0b8151850f78e6cc0025bd8709585bab998bcbac96a94750c75ecb4c7b')
    advisory=audit({**{path:(data.ROOT/path).read_text() for path in eligible},PATH:old},list(eligible),[PATH],n['begin']['inputHashes'],registry['sourceRows'],{'WBS-P018-09'})
    assert advisory['metadataConsistent'] and not advisory['executionQualified'] and advisory['originalOwners']==[dict(path=PATH,canonicalOwner='WBS-P018-09',canonicalCostOwner='WBS-P018-09')]
    negatives=[]
    for name,literal in VALUES.items():
        decl=declaration(name,literal)
        negatives.extend([new.replace(decl,'',1),new.replace(decl,declaration(name,'"wrong"'),1),new.replace(name,'UNKNOWN_CONSTANT',1)])
    negatives.extend([new.replace('le="0.001"} 1','le="0.001"} 2',1),new.replace('summary encoding failed','changed encoding message',1),new.replace('@Test','@Disabled',1),new.replace('assertEquals(1, summary.calls.get())','assertEquals(2, summary.calls.get())',1)])
    for bad in negatives:
        assert bad!=new
        try:
            require(old,bad)
        except AssertionError:
            pass
        else:
            raise AssertionError('changed independent golden/control accepted')
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2377_ApiDurationExporter全24fixture二定数是正_単体テスト仕様書.md'
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=SOURCE_BEFORE,invocation=invocation,sourceChanges=[dict(path=PATH,beforeSha256=data.sha(old.encode()),sha256=data.sha(new.encode()))],totalCorrections=2,completeStringReferences=19,metadataNegativeVectors=len(negatives),eligibilityClosureSourceHashes=eligible,metadataAdvisory=advisory,originalTests=24,originalSuites=1,allMainAndOtherInputsUnchanged=True,judgement='PT_DEFAULT_WHOLE_API_DURATION_MEMORY_SNAPSHOT_JDK_OUTPUTSTREAM_NO_EXTERNAL_IO',specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),productTestsExecuted=0,newAccepted=0,coverage=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
