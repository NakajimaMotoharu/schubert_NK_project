"""Three explicit public form/fixture inputs and exact literal-expanded token comparison; no product run."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();main=['src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/form/'+n+'Form.java' for n in ['QuestionSearch','NotificationSearch','UserSearch']];tests=['tools/quality/architecture/'+n+'InputContractTest.java' for n in ['QuestionSearch','NotificationSearch','UserSearch']]
TOKEN=re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\x27(?:\\.|[^\x27\\])*\x27|[A-Za-z_$][\w$]*|\d+[\w.]*|[^\s]')
CONST=re.compile(r'private\s+static\s+final\s+String\s+(\w+)\s*=\s*("(?:\\.|[^"\\])*")\s*;')
def body_tokens(text):
 constants=dict(CONST.findall(text));text=CONST.sub('',text);start=re.search(r'public final class \w+\s*\{',text).end();result=[]
 for token in TOKEN.findall(text[start:]):
  if token.startswith(('//','/*')):continue
  result.append(constants.get(token,token))
 return result
assert TOKEN.findall('x(" a ");')!=TOKEN.findall('x("a");');assert '"a\\\"b"' in TOKEN.findall('x("a\\\"b");');assert [x for x in TOKEN.findall('x /*c*/ ( 1 );') if not x.startswith('/*')]==TOKEN.findall('x(1);')
oldQN=json.loads((b/'evidence/provisional/PG18360-question-notification-search26-pt-v1/manifest.json').read_text());oldU=json.loads((b/'evidence/provisional/PG18340-user-search-form-twelve-pt-v1/manifest.json').read_text());assert oldQN['actualExit']==oldU['actualExit']==0;rows=[];prior=[]
for n in main+tests:
 s=(r/n).read_text();assert not any(w in s for w in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','QuestionListViewModel','QuestionDetailViewModel','NotificationListViewModel','NotificationDetailViewModel','DataSource','DriverManager','ProcessBuilder','Class.forName','setAccessible','java.nio.file','java.net.Socket','@BeforeAll','@TempDir','Executors.']);rows.append(dict(path=n,sha256=sha(r/n),sourceOnlyAdmission=True))
for n in main:assert (r/n).read_bytes()==subprocess.check_output(['git','show','6b53efeec87f3ec36a840dd8e7759656cb4aee5c:'+n])
for n in tests:
 current=(r/n).read_text();origin=oldU if Path(n).name.startswith('UserSearch') else oldQN;key=str(r/n);expected=origin['begin']['testSourceHashes'][key]
 if Path(n).name.startswith('UserSearch'):old=current;commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert sha(r/n)==expected
 else:
  commit='ce284deb86508071d03cf913ce94344f2e49bc9a';old=subprocess.check_output(['git','show',commit+':'+n],text=True);assert hashlib.sha256(old.encode()).hexdigest()==expected;assert body_tokens(old)==body_tokens(current)
 methods=re.findall(r'@Test\s*void (\w+)\(',current);assert len(methods)==(14 if Path(n).name.startswith('Question') else 12);assert methods==re.findall(r'@Test\s*void (\w+)\(',old));prior.append(dict(path=n,currentSha256=sha(r/n),oldSha256=expected,oldFixtureGitCommit=commit,exactBodyAfterLiteralExpansionAndWhitespace=True,tokenCount=len(body_tokens(current)),originalTests=len(methods),oldRun='PG18340' if Path(n).name.startswith('User') else 'PG18360',oldSucceededNotReplayed=True))
out=b/'evidence/PG37938-search-three-source-admission-v3';assert not out.exists();out.mkdir();v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),productionCore='fda03f9f80e13cc81b96ff0da52a43bc83828413',mainSources=main,testSources=[dict(path=n,tests=14 if Path(n).name.startswith('Question') else 12) for n in tests],sourceHashes={n:sha(r/n) for n in main+tests},priorWhole38=prior,literalTokenBoundaryChecks3NotProductTests=True,oldQnN26StyleAndFieldConstantChangesPreserved=True,allThreePureMapListStringDateEnumDto=True,workerOrExternalAuthorityOrKeyResourceOperations=0,prestyle=dict(actualExit=1,onlyFailingSource=tests[2],oldWildcardStaticImport=True),currentProto='PG37688/current176',expectedIndependent='Originalliteral38 and3489/3491; old18344/18364 PythonUTF8-NFC/fixedUTC/daypairs; productionmethodnotusedforexpected',newDefinitions=0,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,sdkHashes={});(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(dict(actualExit=0,Main3=3,original38=38,oldQnNExpandedTokensEqual=True,userStylePending=True,newProductTests=0))
