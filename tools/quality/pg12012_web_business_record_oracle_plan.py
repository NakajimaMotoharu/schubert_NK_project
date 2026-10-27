"""Independent UI234/236 byte vectors for1/2/50 records and preservation of original8 methods."""
import hashlib
from pathlib import Path
import re
import subprocess
import g07_host_class_provenance_inputs as data
from public_java_digest_provenance import LEX
from host_tool_invocation import capture,verify
OUT=data.BASE/'PG12012-web-business-record-oracle-plan-v1'
FILE='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/WebBusinessWireClientsTest.java'
IMPORTS=['dev.codex.schubert.nk.protocol.layout.PayloadRecord','dev.codex.schubert.nk.protocol.layout.common.PagedResponseData','dev.codex.schubert.nk.protocol.layout.question.QuestionSummaryRecord','dev.codex.schubert.nk.protocol.layout.semantic.AnswerState','java.security.MessageDigest','java.util.HexFormat']
GOLDENS={1:'ad12670840c01563abfa5a3f7bd0236b7a842bd01ecfd996823fbb9dfe81915b',2:'902a963771b805fd8bafe5ffb4dd4e27dc1f83ef35e19cf0129cf18a45699678',50:'73036d0a7f7d78228c414fa889d36d8cc1960167446e2bc4ff2804371d7c3687'}
BLOCK='02e664106c3b989d2942a26dcf24ee86822f0eaae0a1a5eb2acf6b857e236f1a'
def raw(text):return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
def vectors(count):
    b=bytearray(b' '*(304+672*count))
    def text(start,width,value):
        v=value.encode('utf-8');assert len(v)<=width;b[start:start+width]=v+b' '*(width-len(v))
    def num(start,width,value):text(start,width,str(value).zfill(width))
    for start,width,value in [(0,8,'SCHBNK01'),(8,3,'001'),(11,8,'QSSRSP01'),(19,3,'001'),(22,1,'S'),(23,1,'S'),(24,36,'00000000-0000-0001-0000-000000000001'),(60,36,'00000000-0000-0000-0000-000000000001'),(96,17,'20261003040000123'),(113,64,'a'*64),(208,4,'0000')]:text(start,width,value)
    for start,width,value in [(177,4,256),(181,6,48),(187,6,672),(193,6,count),(199,9,len(b)),(256,6,1),(262,3,50),(265,9,count),(274,6,1),(280,9,1),(289,9,count)]:num(start,width,value)
    for row in range(count):
        k=304+672*row;num(k,12,100-row);text(k+12,26,str(row+1).zfill(26));text(k+38,64,'record-user-'+str(row));text(k+102,512,'質問é record-'+str(row));text(k+614,12,('ANSWERED','UNANSWERED','ERROR')[row%3]);text(k+626,17,'20261003040000123');text(k+643,17,'20261003040001123' if row%3==0 else '')
    assert len(b)==304+672*count and b[212:256]==b' '*44 and b[298:304]==b' '*6
    for row in range(count):assert b[304+672*row+660:304+672*(row+1)]==b' '*12
    return bytes(b)
def validate(before,after):
    a=after.index('  @Test\n  void wire009');b=after.index('  private static int index(',a);addition=after[a:b];tokens=raw(addition)
    if data.sha('\0'.join(tokens).encode())!=BLOCK or len(tokens)!=1350:raise ValueError('reviewed four boundary methods and independent helper required')
    old=after[:a]+after[b:]
    for name in IMPORTS:
        needle='import '+name+';';assert old.count(needle)==1;old=old.replace(needle,'',1)
    if raw(old)!=raw(before):raise ValueError('all original8 raw tokens must remain unchanged')
    if len(re.findall(r'@Test\s+void ',after))!=12:raise ValueError('original8 plus4 required')
    assert all(pin in addition for pin in GOLDENS.values()) and not set(tokens)&{'FixedWidthEncoder','HeaderCodec','PayloadCodec','LayoutRegistry','PayloadTypeCatalog'}
    return addition

def main():
    invocation=capture(__file__);assert not OUT.exists();normal=data.read_checked(data.BASE/'PG11984-web-business-wire-fixture-six-compile-v1/manifest.json','ba7eb4d008ea6968016bcc4767cdc552d294def6e13f9ac3c0e232bbe34c17f8');snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent;before=(snapshot/FILE).read_text();after=(data.ROOT/FILE).read_text();assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p!=FILE);validate(before,after);rows=[]
    for count,pin in GOLDENS.items():
        body=vectors(count);assert hashlib.sha256(body).hexdigest()==pin;rows.append(dict(count=count,bodyBytes=len(body),sha256=pin,recordBytes=672,firstRecord=304,typedQuestionIds=list(range(100,100-count,-1)),syntheticContext='FIXED_SYNTHETIC_NOT_SAVED_RAW',noProductionEncoderUsed=True))
    design={}
    for p in ('documents/200_UI/230_インターフェース/234_認証・検索・シナリオ電文仕様.md','documents/200_UI/230_インターフェース/236_管理・質問・通知電文仕様.md','documents/300_SS/320_メッセージング/323_全電文layout・Java・DB対応表.md'):
        design[p]=data.sha(subprocess.check_output(['git','show','origin/main:'+p],cwd=data.ROOT))
    verify(invocation);OUT.mkdir();data.write(OUT/'goldens.json',dict(vectors=rows,expectedSource='origin/main approved UI byte offsets and independent Python construction, never Main/Test generator execution'));data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,sourceChanges=[dict(path=FILE,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()))],originalMethodsPreserved=8,newMethods=4,totalMethods=12,reviewedAdditionRawTokens=1350,reviewedAdditionRawTokenSha256=BLOCK,designHashes=design,goldenSha256=data.sha((OUT/'goldens.json').read_bytes()),productTestsExecuted=0,newAccepted=0,coverage=None,externalActions=0));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
