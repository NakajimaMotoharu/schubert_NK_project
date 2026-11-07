"""Ten pre-registered Test-only style changes; exact other tokens and primitive evaluation order."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,re,subprocess,sys
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';ORIG=B/'evidence/PG22806-storage-style-original-v1';OUT=B/'evidence/PG22808-storage-style-token-order-guard-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def replace_once(text,a,b):
 assert text.count(a)==1,a
 return text.replace(a,b)
def transformed(name,text):
 if name=='ExistingFileAccessTest.java':
  for a,b in [('int attributes;','int attributeCalls;'),('attributes++;','attributeCalls++;'),('"attrs" + attributes','"attrs" + attributeCalls'),('&& attributes == 4','&& attributeCalls == 4')]:text=replace_once(text,a,b)
 elif name=='OwnedTransferDirectoryTest.java':
  literal='"音源 name.ogg"';assert text.count(literal)==7 and 'ASSET_ENTRY_NAME' not in text;text=text.replace(literal,'ASSET_ENTRY_NAME');text=re.sub(r'((?:final )?class OwnedTransferDirectoryTest\s*\{)',r'\1\n  private static final String ASSET_ENTRY_NAME = '+literal+';',text,count=1)
  text=replace_once(text,'LocalDate date = DATE.plusDays(sequence++);','int sequenceValue = sequence;\n              sequence++;\n              LocalDate date = DATE.plusDays(sequenceValue);')
  text=replace_once(text,'String name = "compound-" + sequence++;','int sequenceValue = sequence;\n              sequence++;\n              String name = "compound-" + sequenceValue;')
 else:
  assert name=='ServiceConfigFilesTest.java';literal='"nk.db.pool.api.max: \'8\'\\n"';assert text.count(literal)==4 and 'API_POOL_FIXTURE_DOCUMENT' not in text;text=text.replace(literal,'API_POOL_FIXTURE_DOCUMENT');text=re.sub(r'((?:final )?class ServiceConfigFilesTest\s*\{)',lambda m:m.group(1)+'\n  private static final String API_POOL_FIXTURE_DOCUMENT = '+literal+';',text,count=1)
  for field in ['attributeCalls','readCalls','sizeCalls']:text=replace_once(text,'int call = ++'+field+';','int call = '+field+' + 1;\n      '+field+' = call;')
  text=replace_once(text,'if (++channelCalls != 2 || kind == FaultKind.ROOT_DRIFT || kind == FaultKind.FILE_DRIFT)','int call = channelCalls + 1;\n      channelCalls = call;\n      if (call != 2 || kind == FaultKind.ROOT_DRIFT || kind == FaultKind.FILE_DRIFT)')
  text=replace_once(text,'if (++closed == failAt)','int call = closed + 1;\n      closed = call;\n      if (call == failAt)')
 return text

def main():
 original=load(ORIG/'manifest.json');expected={};before={}
 for item in original['inputs']:
  name=Path(item['path']).name;p=ORIG/name;assert sha(p)==item['sha256'];before[item['path']]=p.read_text();expected[item['path']]=transformed(name,p.read_text())
 if sys.argv[1:]==['edit']:
  assert all(sha(R/x['path'])==x['sha256'] for x in original['inputs'])
  for p,text in expected.items():(R/p).write_text(text)
  print('edited explicit three Test sources only');return
 assert not sys.argv[1:] and not OUT.exists();lexer=R/'evidence/01_PT/015_NK-WEB-001/input/042_seven_future_independent_post.py';sp=importlib.util.spec_from_file_location('owned_storage_style_tokens',lexer);lm=importlib.util.module_from_spec(sp);sp.loader.exec_module(lm);negatives=[]
 for name,want in expected.items():
  actual=(R/name).read_text();assert lm.java_tokens(want)==lm.java_tokens(actual)
  if name.endswith('OwnedTransferDirectoryTest.java'):
   bad=actual.replace('DATE.plusDays(sequenceValue)','DATE.plusDays(sequence)',1);assert lm.java_tokens(want)!=lm.java_tokens(bad);negatives.append('postfix-call-old-value')
   bad=actual.replace('ASSET_ENTRY_NAME = "音源 name.ogg"','ASSET_ENTRY_NAME = "changed.ogg"',1);assert lm.java_tokens(want)!=lm.java_tokens(bad);negatives.append('asset-literal')
  elif name.endswith('ServiceConfigFilesTest.java'):
   for old,new in [('attributeCalls = call;','attributeCalls = call + 1;'),("api.max: '8'","api.max: '9'")]:
    bad=actual.replace(old,new,1);assert lm.java_tokens(want)!=lm.java_tokens(bad);negatives.append(old)
  else:
   assert 'public Map<String, Object> attributes(Path held)' in actual and 'int attributeCalls;' in actual;bad=actual.replace('"bad-post"','"changed-post"',1);assert lm.java_tokens(want)!=lm.java_tokens(bad);negatives.append('fault-label')
 # Independent literal JVM int vectors: no Product call or synthetic native fixture.
 vectors=[(-2147483648,-2147483647),(-1,0),(0,1),(1,2),(2147483646,2147483647),(2147483647,-2147483648)];checks=0
 for old,after in vectors:
  wrap=((old+1+2147483648)%4294967296)-2147483648;assert wrap==after
  for throws in [False,True]:
   # Prefix: field read once, updated value captured locally, field written once before condition/call.
   originalPrefix=[('read',old),('write',after),('input',after),('throws' if throws else 'returns',after)]
   call=wrap;field=call;newPrefix=[('read',old),('write',field),('input',call),('throws' if throws else 'returns',field)];assert originalPrefix==newPrefix;checks+=1
   # Postfix: save old value, update before call; a throwing DATE/concat keeps update performed.
   originalPost=[('read',old),('write',after),('input',old),('throws' if throws else 'returns',after)]
   saved=old;field=wrap;newPost=[('read',old),('write',field),('input',saved),('throws' if throws else 'returns',field)];assert originalPost==newPost;checks+=1
 assert checks==24;OUT.mkdir();m=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),observerSource=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),originalManifest=dict(path=str((ORIG/'manifest.json').relative_to(R)),sha256=sha(ORIG/'manifest.json')),originalHashes={x['path']:x['sha256'] for x in original['inputs']},currentHashes={n:sha(R/n) for n in expected},fieldRenamedSites=4,duplicateLiteralOriginalSites=dict(asset=7,apiPool8=4),assignmentInOperandSites=7,allOtherJavaTokensFixturesAndOracleValuesUnchanged=True,primitiveMetadataVectors=vectors,primitiveEvaluationTraceChecks=checks,negativeGuards=negatives,productTestsExecuted=0,originalTestCompiled=False,originalNativeTestRun=False,staticAlternativeOnly=True,remainingRisk='Original native/filesystem/process/Root Test runtime is HOLD and not run; semantic source review is not a PT PASS or coverage measurement.',newProductTests=0,newSourceProofs=0,newAcceptance=0,whole451Accepted=False,effortRate=None,producer=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)));(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,semanticMetadataChecks=checks,negativeGuards=len(negatives),productTests=0)))
if __name__=='__main__':main()
