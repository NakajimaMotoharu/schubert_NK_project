"""Exact whole-source inverse for closed same-registry fixture ownership; no Product invocation."""
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX

SOURCE_BEFORE='639bbc777593cd98d95db1b0316e8113b40b886b'
OUT=data.BASE/'PG12790-api-policy-ownership-plan-v1'
PATH='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiMetricScrapeTest.java'
METHOD='apipol008ClosedSourceNotReopenedOrReadByStandard'


def tokens(text):
    return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]


def require(old,new):
    start=new.index('  void '+METHOD+'() {')
    end=new.index('\n  @Test',start)
    block=new[start:end]
    opening='    try (var source = new Compatible()) {\n'
    assert block.count(opening)==1 and block.endswith('    }\n  }\n')
    block=block.replace(opening,'    var source = new Compatible();\n',1)
    block=block[:-len('    }\n  }\n')]+'  }\n'
    restored=new[:start]+block+new[end:]
    assert tokens(restored)==tokens(old)


def main():
    invocation=capture(__file__);assert not OUT.exists()
    n=data.read_checked(data.BASE/'PG12766-api-duration-six-compile-v1/manifest.json','39678a3c3b3ac634f9ee698f7acc900fa13248522829ce5338752b6bba920072')
    p=data.read_checked(data.BASE/'PG12784-api-approved-closure-plan-v1/manifest.json','46699bde6540959934fc3bdb2d76368b77bb6b6b07b4f1bcade7adf20b4660cb')
    assert n['source']==p['source']==SOURCE_BEFORE and n['actualExit']==n['testsExecuted']==0
    root=Path(n['jars']['api']['path']).parent.parent.parent.parent
    old=(root/PATH).read_text();new=(data.ROOT/PATH).read_text()
    assert data.sha(old.encode())==n['begin']['inputHashes'][PATH]
    require(old,new)
    negatives=[new.replace('try (var source = new Compatible()) {','try (var replacement = new Compatible()) {',1),new.replace('    try (var source = new Compatible()) {','    var source = new Compatible();',1),new.replace('      source.close();\n','',1),new.replace('assertEquals("", policy.scrape(source, STANDARD_MODE))','assertEquals("wrong", policy.scrape(source, STANDARD_MODE))',1),new.replace('assertEquals(0, source.reads.get())','assertEquals(1, source.reads.get())',1),new.replace('assertTrue(source.isClosed())','assertFalse(source.isClosed())',1),new.replace('void '+METHOD,'void disabledClosedSource',1),new.replace('source.reads.set(0)','source.reads.set(1)',1)]
    for bad in negatives:
        assert bad!=new
        try:
            require(old,bad)
        except (AssertionError,ValueError):
            pass
        else:
            raise AssertionError('non-equivalent closed fixture accepted')
    hashes=n['begin']['inputHashes']
    assert all(data.sha((data.ROOT/path).read_bytes())==digest for path,digest in hashes.items() if path!=PATH)
    cases=[];whole={}
    for path in p['wholeTestSourceHashes']:
        text=(data.ROOT/path).read_text();whole[path]=data.sha(text.encode())
        methods=re.findall(r'@Test\s+void\s+(\w+)\s*\(\s*\)',text)
        cases.extend(dict(className=path.split('/java/',1)[1][:-5].replace('/','.'),method=method,path=path,sourceSha256=whole[path]) for method in methods)
    assert [(r['className'],r['method']) for r in cases]==[(r['className'],r['method']) for r in p['cases']]
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2381_ApiPolicy閉鎖fixture所有是正_単体テスト仕様書.md'
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=SOURCE_BEFORE,invocation=invocation,sourceChanges=[dict(path=PATH,beforeSha256=data.sha(old.encode()),sha256=data.sha(new.encode()))],totalCorrections=1,metadataNegativeVectors=len(negatives),eligibilityClosureSourceHashes=p['eligibilityClosureSourceHashes'],wholeTestSourceHashes=whole,cases=cases,originalTests=38,originalSuites=2,newTestIds=0,sameExecRequired=True,oldExecUnion=False,allMainAndOtherInputsUnchanged=True,judgement=p['judgement'],specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),productTestsExecuted=0,newAccepted=0,coverage=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    main()
