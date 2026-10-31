"""Metadata-only qualification of JLS zero-translation span; no Java execution."""
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pmd_source_span_no_unicode_translation import no_translation,span

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
BASE=('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
COORD=('PG16291-thread-five-gonefd-two-purpose-v2','657a60a441c8a3424422b39f97a54b15326164a5954097c4a51e5ec349de49f1')
OUT=data.BASE/'PG16386-zero-unicode-span-qualification-v1'
PINS={
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question/QuestionSubmissionService.java':'d303f5a79375d69bbc4f45c91d4ab74bd5744c40baafe45f6cbe8beb692ffaa2',
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question/QuestionWorkerService.java':'e3cf7a1056e03ce46380893697cb2d2faefa02a88ea966a14ff99646763b3c83',
 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebRequestLogProducer.java':'f68eb4c356f08234f64c9ab39af6f463933fe0e69fac7cab35feb24875b80b0e'}
HELPER='tools/quality/pmd_source_span_no_unicode_translation.py'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only');bs=chr(92)
    positives=[('',0),('abc',0),(bs+'x',0),(bs*2+'u000a',1),(bs*4+'uu0041',1),
        ('x'+bs*2+'u2028'+bs*2+'u2029',2),(bs+'x'+bs*2+'u005c',1)]
    for text,expected in positives:require(no_translation(text)==expected,'literal zero-translation vector')
    rejects=[None,bs+'u000a',bs*3+'u000a',bs*5+'u005c',bs+'uuuu0041',bs+'u',bs+'u12xz',bs+'u005c'+bs+'u000a']
    rejects += [c for c in ('\r','\0','\v','\f','\x1c','\x1d','\x1e','\x85','\u2028','\u2029','\x1a')]
    rejects += [chr(0xd800)]
    for text in rejects:
        try:no_translation(text)
        except ValueError:pass
        else:raise ValueError('unresolved translation/control accepted')
    attrs=dict(beginline='2',endline='2',begincolumn='8',endcolumn='13')
    byte_vectors=[('// '+bs*2+'u000a\ncatch (Error e) {}\n',(18,23,'Error')),
        ('// §\ncatch (Error e) {}\n',(13,18,'Error')),
        ('// 注釈\ncatch (Error e) {}\n',(17,22,'Error'))]
    for text,expected in byte_vectors:require(span(text,attrs)==expected,'independent byte literal vector')
    coordinate_rejects=[('catch (Error e) {}\n',None),('catch (Error e) {}\n',{}),
        ('catch (Error e) {}\n',dict(beginline=True,endline='1',begincolumn='8',endcolumn='13')),
        ('catch (Error e) {}\n',dict(beginline='1',endline='1',begincolumn='0',endcolumn='13')),
        ('catch (Error e) {}\n',dict(beginline='1',endline='2',begincolumn='8',endcolumn='13')),
        ('catch (Error e) {}\n',dict(beginline='1',endline='1',begincolumn='13',endcolumn='8')),
        ('catch (\tError e) {}\n',dict(beginline='1',endline='1',begincolumn='9',endcolumn='14')),
        ('catch (Error e) {}\n',dict(beginline='1',endline='1',begincolumn='8',endcolumn='99'))]
    for text,a in coordinate_rejects:
        try:span(text,a)
        except ValueError:pass
        else:raise ValueError('ambiguous coordinate accepted')
    baseline,coordinate=[read(v) for v in (BASE,COORD)]
    require(baseline['actualExit']==coordinate['actualExit']==0 and coordinate['source']==SOURCE,'original saved evidence')
    original=data.read_checked(data.BASE/BASE[0]/'findings.json',baseline['findingsSha256'])
    texts={p:(data.ROOT/p).read_text() for p in PINS};proofs={}
    for p,text in texts.items():
        require(data.sha(text.encode())==PINS[p],'whole target Source byte')
        proofs[p]=dict(sourceSha256=PINS[p],ineligibleUnicodeMarkers=no_translation(text),eligibleUnicodeEscapes=0)
    rows=[]
    for row in original:
        p=row['path']
        if p not in PINS or row['rule']!='AvoidCatchingGenericException':continue
        require(row['sourceSha256']==PINS[p],'unchanged original analyzer input')
        a,b,token=span(texts[p],row['attributes']);require(token in {'RuntimeException','Error'},'exact catch type only')
        rows.append(dict(path=p,attributes=row['attributes'],sourceSha256=PINS[p],originalDiagnosticRowSha256=data.sha(wire(row)),
            canonicalSpanStart=a,canonicalSpanEndExclusive=b,canonicalSpanSha256=data.sha(token.encode()),token=token))
    require(len(rows)==22,'all22 target catch warnings, not semantic review')
    helper_hash=data.sha((data.ROOT/HELPER).read_bytes())
    for v in (baseline,coordinate):verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'spans.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,helper=HELPER,helperSha256=helper_hash,
        baselineManifestSha256=BASE[1],coordinateToolManifestSha256=COORD[1],sourceProofs=proofs,spansSha256=data.sha((OUT/'spans.json').read_bytes()),
        zeroTranslationPositiveVectors=len(positives),zeroTranslationNegativeVectors=len(rejects),bytePositiveVectors=len(byte_vectors),coordinateNegativeVectors=len(coordinate_rejects),
        targetWarningRows=len(rows),semanticPurposeReviewsAdded=0,productTestsExecuted=0,sourceChanged=False,ptExecutionExempt=False,
        whole451Accepted=False,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None,
        externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
