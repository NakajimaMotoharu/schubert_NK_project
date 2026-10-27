"""Independent original8 token preservation/current four reviewed cases/byte golden metadata and12 negatives."""
import copy
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from public_java_digest_provenance import LEX
from host_tool_invocation import capture,verify
OUT=data.BASE/'PG12014-web-business-record-source-post-v1'
PIN='c550a50234d1798bc97b34a3cee5e3cc5f57b73eead048943d87985170181aba'
FILE='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/WebBusinessWireClientsTest.java'
def raw(s):return [m.group() for m in LEX.finditer(s) if not m.group().startswith(('//','/*'))]
def main():
    invocation=capture(__file__);assert not OUT.exists();p=data.BASE/'PG12012-web-business-record-oracle-plan-v1';plan=data.read_checked(p/'manifest.json',PIN);goldens=data.read_checked(p/'goldens.json',plan['goldenSha256']);normal=data.read_checked(data.BASE/'PG11984-web-business-wire-fixture-six-compile-v1/manifest.json','ba7eb4d008ea6968016bcc4767cdc552d294def6e13f9ac3c0e232bbe34c17f8');snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent;before=(snapshot/FILE).read_text();after=(data.ROOT/FILE).read_text();assert all(data.sha((data.ROOT/k).read_bytes())==h for k,h in normal['begin']['inputHashes'].items() if k!=FILE)
    imports=('dev.codex.schubert.nk.protocol.layout.PayloadRecord','dev.codex.schubert.nk.protocol.layout.common.PagedResponseData','dev.codex.schubert.nk.protocol.layout.question.QuestionSummaryRecord','dev.codex.schubert.nk.protocol.layout.semantic.AnswerState','java.security.MessageDigest','java.util.HexFormat')
    def validate(value,text):
        expected=dict(actualExit=0,sourceBefore=normal['source'],originalMethodsPreserved=8,newMethods=4,totalMethods=12,reviewedAdditionRawTokens=1350,reviewedAdditionRawTokenSha256='02e664106c3b989d2942a26dcf24ee86822f0eaae0a1a5eb2acf6b857e236f1a',productTestsExecuted=0,newAccepted=0,coverage=None,externalActions=0)
        if any(value.get(k)!=v for k,v in expected.items()):raise ValueError('exact original8/four new/source/metadata required')
        change=value['sourceChanges']
        if len(change)!=1 or change[0]!=dict(path=FILE,beforeSha256=data.sha(before.encode()),sha256='5e8ddf531e8ab4145bb25dfc215e1a78ec590e7a52214a77b455dd55167ed8a3') or data.sha(text.encode())!=change[0]['sha256']:raise ValueError('reviewed new source only required')
        a=text.index('  @Test\n  void wire009');b=text.index('  private static int index(',a);block=raw(text[a:b]);original=text[:a]+text[b:]
        for name in imports:
            needle='import '+name+';'
            if original.count(needle)!=1:raise ValueError('six explicit added imports required')
            original=original.replace(needle,'',1)
        if raw(original)!=raw(before) or data.sha('\0'.join(block).encode())!=expected['reviewedAdditionRawTokenSha256']:raise ValueError('original method tokens/addition contract changed')
        names=re.findall(r'@Test\s+void (\w+)\(',text);old=re.findall(r'@Test\s+void (\w+)\(',before)
        if len(names)!=len(set(names))!=12:raise ValueError('unique12 inventory required')
        assert names[:8]==old and len(names)==12 and [r['count'] for r in goldens['vectors']]==[1,2,50] and [r['bodyBytes'] for r in goldens['vectors']]==[976,1648,33904]
        assert all(r['sha256'] in text and r['typedQuestionIds']==list(range(100,100-r['count'],-1)) and r['recordBytes']==672 and r['firstRecord']==304 and r['noProductionEncoderUsed'] for r in goldens['vectors'])
    validate(plan,after);negatives=0
    for key,value in [('sourceBefore','0'*40),('originalMethodsPreserved',0),('newMethods',0),('totalMethods',8),('reviewedAdditionRawTokenSha256','0'*64),('productTestsExecuted',12),('newAccepted',1),('coverage',100)]:
        bad=copy.deepcopy(plan);bad[key]=value
        try:validate(bad,after)
        except ValueError:negatives+=1
        else:raise AssertionError('bad metadata accepted')
    for old,new in [('@Test','@Disabled'),('number(bytes, 193, 6, count)','number(bytes, 193, 6, 0)'),('body[964]','body[965]'),('assertEquals(50, page.pageSize())','assertEquals(49, page.pageSize())')]:
        assert old in after;bad=after.replace(old,new,1)
        try:validate(plan,bad)
        except ValueError:negatives+=1
        else:raise AssertionError('changed original/byte oracle/assertion accepted')
    assert negatives==12;verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,planManifestSha256=PIN,sourceChanges=plan['sourceChanges'],originalMethodsPreserved=8,newMethods=4,totalMethods=12,independentGoldenVectors=3,goldenSha256=plan['goldenSha256'],metadataNegativeVectors=negatives,allMainAndOtherInputsPreserved=True,productTestsExecuted=0,newAccepted=0,coverage=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
