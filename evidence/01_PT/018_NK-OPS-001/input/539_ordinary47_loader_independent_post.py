"""Different comment/literal masker and anchored grammar; public source only, never target calls."""
from pathlib import Path
from collections import Counter
import datetime,hashlib,json,re,subprocess,xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001'
P=B/'evidence/PG23822-ordinary47-loader-source-review-v1';O=B/'evidence/PG23824-ordinary47-loader-source-independent-v1'
load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def masked(text):
 out=list(text); i=0
 while i<len(text):
  begin=i
  if text.startswith('//',i):
   end=text.find('\n',i+2);i=len(text) if end<0 else end
  elif text.startswith('/*',i):
   end=text.find('*/',i+2);assert end>=0;i=end+2
  elif text.startswith('"""',i):
   end=text.find('"""',i+3);assert end>=0;i=end+3
  elif text[i] in ('"',"'"):
   quote=text[i];i+=1
   while i<len(text):
    if text[i]=='\\':i+=2
    elif text[i]==quote:i+=1;break
    else:i+=1
   else:raise ValueError('unterminated literal')
  else:i+=1;continue
  for n in range(begin,i):
   if out[n]!='\n':out[n]=' '
 return ''.join(out)
grammar=re.compile(r'\bProxy\s*\.\s*newProxyInstance\s*\(\s*(?P<loader>(?P<owner>[A-Za-z_$][\w$]*(?:\s*\.\s*class)?)\s*\.\s*getClassLoader\s*\(\s*\))\s*,\s*(?P<interfaces>new\s+Class(?:\s*<\s*\?\s*>)?\s*\[\s*\]\s*\{[^{}]*\})\s*,')
compact=lambda s:re.sub(r'\s+','',s)
def independent(text):
 clean=masked(text);matches=list(grammar.finditer(clean))
 assert len(re.findall(r'\bgetClassLoader\s*\(',clean))==len(matches)
 return [dict(loader=compact(m['loader']),interfaceDeclaration=compact(m['interfaces']),getterStart=m.start('loader'),getterEnd=m.end('loader'),currentLine=clean.count('\n',0,m.start('loader'))+1) for m in matches]
assert not O.exists();m=load(P/'manifest.json'); assert sha(P/'manifest.json')=='28fb33032070009aed0408e7f0902f98f704e5be16b88ba8d94866d16389b1cf'
assert m['actualExit']==0 and sha(P/'review.json')==m['reviewSha256'];rows=load(P/'review.json')
cfg=load(R/m['config']['path']);assert sha(R/m['config']['path'])==m['config']['sha256']
original=R/cfg['originalManifest']['path'];assert sha(original)==cfg['originalManifest']['sha256'];om=load(original)
assert om['source']==cfg['originalSource'] and om['checkedFiles']==85 and om['reports']['pmd']['raw']==347
p=R/cfg['originalPmd']['path'];assert sha(p)==cfg['originalPmd']['sha256'];raw=[]
for f in E.parse(p).getroot():
 if f.tag.rsplit('}',1)[-1]=='file':raw.extend((str(Path(f.get('name')).relative_to(R)),dict(v.attrib)) for v in f if v.get('rule')=='UseProperClassLoader')
wire=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'))
assert Counter((n,wire(v)) for n,v in raw)==Counter((v['path'],wire(v['rawDiagnostic'])) for v in rows)
assert len(rows)==93 and len(m['sourceInventory'])==47 and set(m['sourceInventory'])==set(cfg['currentSourcePins'])
changed=0;out=[]
for name,v in m['sourceInventory'].items():
 assert name in cfg['currentSourcePins'] and '/src/test/java/' in name and not any(x in name for x in ('RootFailedStart','SnapshotKeyCloseWitness','pg9892_snapshot_key_close_witness'))
 current=(R/name).read_bytes();assert hashlib.sha256(current).hexdigest()==v['currentSha256']==cfg['currentSourcePins'][name]
 old=subprocess.check_output(['git','show',cfg['originalSource']+':'+name],cwd=R);assert hashlib.sha256(old).hexdigest()==v['originalSha256']==cfg['originalSourcePins'][name]
 changed+=current!=old;a=old.decode();z=current.decode();before=independent(a);after=independent(z)
 assert [(v['loader'],v['interfaceDeclaration']) for v in before]==[(v['loader'],v['interfaceDeclaration']) for v in after]
 own=[v for v in rows if v['path']==name];assert len(own)==len(before)==len(after)==v['loaderCalls']
 expected=[]
 for i,(previous,present) in enumerate(zip(before,after)):
  matches=[v for v in own if v['originalInvocation']['loaderBegin']==previous['getterStart']]
  assert len(matches)==1;row=matches[0];rawv=row['rawDiagnostic'];lines=a.splitlines(keepends=True)
  start=sum(len(x) for x in lines[:int(rawv['beginline'])-1])+int(rawv['begincolumn'])-1
  end=sum(len(x) for x in lines[:int(rawv['endline'])-1])+int(rawv['endcolumn'])
  assert start<=previous['getterStart']<previous['getterEnd']<=end
  assert row['currentInvocation']['loaderBegin']==present['getterStart'] and row['currentInvocation']['loaderEnd']==present['getterEnd']
  assert row['currentLine']==present['currentLine'] and row['currentInvocation']['loader']==present['loader'] and row['currentInvocation']['interfaceDeclaration']==present['interfaceDeclaration']
  assert row['originalSourceSha256']==v['originalSha256'] and row['currentSourceSha256']==v['currentSha256']
  expected.append(row['rawDiagnosticOrdinalInSource'])
 assert Counter(expected)==Counter(range(len(own)))
 out.append(dict(path=name,sourceBytesEqual=old==current,siteCount=len(own),independentPositionAndSignatureBinding=True))
assert changed==m['currentChangedSources']==9
sample='Proxy.newProxyInstance(Connection.class.getClassLoader(), new Class<?>[] {Connection.class}, handler)'
assert len(independent(sample))==1
negatives=[]
for label,altered in [('context-loader',sample.replace('Connection.class.getClassLoader()','Thread.currentThread().getContextClassLoader()')),('null-loader',sample.replace('Connection.class.getClassLoader()','null')),('different-factory',sample.replace('newProxyInstance','newSomething')),('wrong-array',sample.replace('new Class<?>[]','new Object[]')),('extra-loader-expression',sample.replace('getClassLoader()','getClassLoader() + other')),('missing-interfaces',sample.replace('new Class<?>[] {Connection.class}','null'))]:
 try:found=independent(altered)
 except AssertionError:found=[]
 assert not found;negatives.append(label)
for label,altered in [('string',json.dumps(sample)),('line-comment','//'+sample),('block-comment','/*'+sample+'*/')]:
 assert independent(altered)==[];negatives.append(label)
assert m['currentWholeUnknownCount'] is None and m['priorTwentyFixtureOverlapCredit'] is None and m['currentWholeStaticMeasurement'] is False
assert m['rawRuleSuppressed'] is False and all(m[k]==0 for k in ('newCompilerOrJvmExecutions','productTestsExecuted','productClassesInitialized','actualBackendActions','heldFourInitializations','newAcceptance'))
O.mkdir();p=O/'source-bindings.json';p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),originalSource=cfg['originalSource'],source=cfg['originalSource'],producer=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),sourceFiles=47,originalRawSitesIndependentlyBound=93,currentChangedSources=9,currentOrderedCallSignaturesIdentical=True,sourceBindingsSha256=sha(p),sourceContextDispositionCounts=m['sourceContextDispositionCounts'],metadataNegativeChecks=len(negatives),metadataNegativeLabels=negatives,currentWholeStaticMeasurement=False,currentWholeUnknownCount=None,priorTwentyFixtureOverlapCredit=None,sourceChanged=False,productTestsExecuted=0,compilerOrJvmExecuted=False,originalProducerOrScannerExecuted=False,actualBackendActions=0,heldFourInitializations=0,ptPassCount=None,coverage=None,newAcceptance=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,sites=93,files=47,changed=9,negatives=len(negatives),manifestSha256=sha(O/'manifest.json'))))
