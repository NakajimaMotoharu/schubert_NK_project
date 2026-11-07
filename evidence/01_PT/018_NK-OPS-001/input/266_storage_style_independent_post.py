"""Independent inverse-token and diagnostic binding; static alternative is never original PT PASS."""
from pathlib import Path
import collections,datetime,hashlib,importlib.util,json,re,shutil,subprocess,xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';RUNS=R.parent/'pgpt-runs/PG379';PRE=RUNS/'pg22810-storage-style-prepare-v1';S=RUNS/'pg22812-storage-style-static-v1';O=B/'evidence/PG22814-storage-style-independent-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def replace_seq(tokens,old,new):
 at=[i for i in range(len(tokens)-len(old)+1) if tokens[i:i+len(old)]==old];assert len(at)==1,(old,len(at));i=at[0];return tokens[:i]+new+tokens[i+len(old):]
def main():
 assert not O.exists();m=load(S/'manifest.json');pre=load(PRE/'manifest.json');guard=B/'evidence/PG22808-storage-style-token-order-guard-v1/manifest.json';gm=load(guard);assert m['actualExit']==pre['actualExit']==gm['actualExit']==0 and m['prepareManifestSha256']==sha(PRE/'manifest.json');assert m['currentHashes']==pre['currentHashes']==gm['currentHashes'];original=B/'evidence/PG22806-storage-style-original-v1/manifest.json';orig=load(original)
 lexer=R/'evidence/01_PT/015_NK-WEB-001/input/042_seven_future_independent_post.py';sp=importlib.util.spec_from_file_location('owned_storage_inverse_tokens',lexer);lm=importlib.util.module_from_spec(sp);sp.loader.exec_module(lm);tok=lm.java_tokens;oldtexts={};current={}
 def undo(name,t):
  t=list(t)
  if name=='ExistingFileAccessTest.java':
   for a,z in [('int attributeCalls ;','int attributes ;'),('attributeCalls ++ ;','attributes ++ ;'),('"attrs" + attributeCalls','"attrs" + attributes'),('&& attributeCalls == 4','&& attributes == 4')]:t=replace_seq(t,tok(a),tok(z))
  elif name=='OwnedTransferDirectoryTest.java':
   literal='"音源 name.ogg"';t=replace_seq(t,tok('private static final String ASSET_ENTRY_NAME = '+literal+';'),[]);assert t.count('ASSET_ENTRY_NAME')==7;t=[literal if v=='ASSET_ENTRY_NAME' else v for v in t]
   t=replace_seq(t,tok('int sequenceValue = sequence; sequence++; LocalDate date = DATE.plusDays(sequenceValue);'),tok('LocalDate date = DATE.plusDays(sequence++);'))
   t=replace_seq(t,tok('int sequenceValue = sequence; sequence++; String name = "compound-" + sequenceValue;'),tok('String name = "compound-" + sequence++;'))
  else:
   assert name=='ServiceConfigFilesTest.java';literal='"nk.db.pool.api.max: \'8\'\\n"';t=replace_seq(t,tok('private static final String API_POOL_FIXTURE_DOCUMENT = '+literal+';'),[]);assert t.count('API_POOL_FIXTURE_DOCUMENT')==4;t=[literal if v=='API_POOL_FIXTURE_DOCUMENT' else v for v in t]
   for field in ['attributeCalls','readCalls','sizeCalls']:t=replace_seq(t,tok('int call = '+field+' + 1; '+field+' = call;'),tok('int call = ++'+field+';'))
   t=replace_seq(t,tok('int call = channelCalls + 1; channelCalls = call; if (call != 2 ||'),tok('if (++channelCalls != 2 ||'))
   t=replace_seq(t,tok('int call = closed + 1; closed = call; if (call == failAt)'),tok('if (++closed == failAt)'))
  return t
 for item in orig['inputs']:
  n=item['path'];p=original.parent/Path(n).name;assert sha(p)==item['sha256']==gm['originalHashes'][n];assert sha(R/n)==m['currentHashes'][n] and hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+n],cwd=R)).hexdigest()==sha(R/n);oldtexts[n]=p.read_text();current[n]=(R/n).read_text();assert undo(Path(n).name,tok(current[n]))==tok(oldtexts[n]);assert not any(v in tok(oldtexts[n]) for v in ['ASSET_ENTRY_NAME','API_POOL_FIXTURE_DOCUMENT','sequenceValue'])
 for base,stages in [(PRE,pre['stages']),(S,m['stages'])]:
  for label,s in stages.items():
   assert s==load(base/(label+'-exit.safe.json')) and not s['timedOut']
   for stream in ['stdout','stderr']:assert sha(base/(label+'.'+stream))==s[stream+'Sha256']
   if base==PRE:assert s['actualExit']==0
 for n,h in m['dependencies'].items():assert sha(n)==h
 for base,labels in [(PRE,['format','parse']),(S,['pmd','checkstyle'])]:
  for label in labels:
   text=(base/(label+'-class-init.stdout')).read_text();assert "Initializing 'java/lang/Object'" in text and not re.search(r"Initializing '(?:dev/codex/schubert/nk/|dev\.codex\.schubert\.nk\.)",text)
 own=pre['ownTool'];tool=R/own['path'];assert sha(tool)==own['sha256']==own['mirrorSha256']==sha(PRE/'source/TestMethodScopeAstCheck.java');assert {p.name:sha(p) for p in (PRE/'classes').iterdir()}==own['classHashes'];assert set(own['classHashes'])=={'TestMethodScopeAstCheck.class','TestMethodScopeAstCheck$1.class'};assert 'task.parse()' in tool.read_text() and not any(v in tool.read_text() for v in ['task.analyze(','task.generate(','Class.forName'])
 javac=pre['stages']['own-tool-javac']['command'];assert javac[1:7]==['-proc:none','--release','25','-Xlint:all','-Werror','-d'] and javac[-1]==str(PRE/'source/TestMethodScopeAstCheck.java');parse=pre['stages']['parse']['command'];assert parse[2:6]==['-cp',str(PRE/'classes'),'TestMethodScopeAstCheck',str(R)] and parse[6:]==sorted(current)
 assert {x.split('\t')[0] for x in (PRE/'parse.stdout').read_text().splitlines()}==set(current)
 # Check both raw XML and captured diagnostics instead of trusting a claimed reduction.
 reports={}
 for label,tag in [('pmd','violation'),('checkstyle','error')]:
  root=E.parse(S/(label+'.xml')).getroot();items=[]
  for parent in root.iter():
   if parent.tag.rsplit('}',1)[-1]=='file':
    n=str(Path(parent.get('name')).relative_to(R));assert n in current
    items += [dict(path=n,**x.attrib,message=' '.join(''.join(x.itertext()).split())[:600]) for x in parent if x.tag.rsplit('}',1)[-1]==tag]
  errors=[dict(x.attrib) for x in root.iter() if label=='pmd' and x.tag.rsplit('}',1)[-1] in ['error','configerror']];assert items==m['reports'][label]['items'] and not errors and not m['reports'][label]['processingErrors'];reports[label]=items
 assert m['stages']['pmd']['actualExit']==4 and m['stages']['checkstyle']['actualExit']==0 and not reports['checkstyle'];assert len(reports['pmd'])==28
 oldraw=B/'evidence/PG22798-storage-all-test-static-v1/manifest.json';previous=load(oldraw);olditems=previous['reports']['pmd']['rawItems'];fixed={'AvoidFieldNameMatchingMethodName','AvoidDuplicateLiterals','AssignmentInOperand'};removed=[v for v in olditems if v['path'] in current and v['rule'] in fixed];assert len(removed)==10 and collections.Counter(v['rule'] for v in removed)=={'AvoidFieldNameMatchingMethodName':1,'AvoidDuplicateLiterals':2,'AssignmentInOperand':7};retained=[v for v in olditems if v['path'] in current and v['rule'] not in fixed];assert len(retained)==28;assert not any(v['rule'] in fixed for v in reports['pmd'])
 def semantic_key(v):return tuple(v.get(k) for k in ['path','rule','class','method','variable','message'])
 assert collections.Counter(semantic_key(v) for v in retained)==collections.Counter(semantic_key(v) for v in reports['pmd'])
 # Same logical tokens outside the10 corrections establish order-preserving pairing among duplicates.
 group=lambda items:{k:sorted([v for v in items if semantic_key(v)==k],key=lambda v:(int(v['beginline']),int(v['begincolumn']))) for k in {semantic_key(v) for v in items}}
 a=group(retained);z=group(reports['pmd']);bindings=[]
 for k,items in a.items():
  for before,after in zip(items,z[k]):bindings.append(dict(original=before,current=after,meaning='same rule/owner/method/variable/message and order after independent inverse-token equivalence; source positions rebound, not old report replay'))
 hashes={n:sha(R/n) for n in previous['inputHashes']};changed={n for n in hashes if hashes[n]!=previous['inputHashes'][n]};assert changed==set(current);unaffected=[v for v in olditems if v['path'] not in current];assert len(unaffected)==94;assert len(unaffected)+len(reports['pmd'])==122
 # Guard failure examples are independent from editor264's forward transformations.
 negatives=[]
 for n,text in current.items():
  name=Path(n).name
  bad=text.replace('attributeCalls = call;','attributeCalls = call + 1;',1) if name=='ServiceConfigFilesTest.java' else text.replace('sequence++;','sequence += 2;',1) if name=='OwnedTransferDirectoryTest.java' else text.replace('int attributeCalls;','int differentCounter;',1)
  try:valid=undo(name,tok(bad))==tok(oldtexts[n])
  except AssertionError:valid=False
  assert not valid;negatives.append(name)
 assert gm['primitiveEvaluationTraceChecks']==24 and len(gm['negativeGuards'])==5 and gm['allOtherJavaTokensFixturesAndOracleValuesUnchanged'] and gm['productTestsExecuted']==0
 O.mkdir();files={}
 for base,prefix in [(PRE,'prepare-'),(S,'static-')]:
  for p in base.iterdir():
   if p.is_file():name=prefix+p.name;shutil.copyfile(p,O/name);files[name]=sha(O/name)
 value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],sourceFixedTestFiles=3,staticStyleSitesCorrected=10,independentlyRestoredAllOriginalTokens=True,inverseNegativeGuards=negatives,semanticMetadataChecks=24,originalTestCompiled=False,productTestsExecuted=0,originalNativeTestRun=False,staticAlternativeOnly=True,ptPassCount=None,coverage=None,residualRisk='Original native/filesystem/process/Root runtime tests remain HOLD/not run; static/source equivalence is not executed PT or measured coverage. Whole source/program/451 not accepted.',currentStorage29=dict(checkedSources=29,unchangedSources=26,changedSources=3,currentInputHashes=hashes,originalRaw=132,correctedSites=removed,retainedSourceRebindings=bindings,unchangedSourceRaw=94,changedSourceRaw=28,currentComposedRaw=122,applicableFindings=None,unclassified=122,checkstyle=0,formatDifferences=0,freshAll29EngineRun=False),guardManifest=dict(path=str(guard.relative_to(R)),sha256=sha(guard)),rawOriginalManifest=dict(path=str(oldraw.relative_to(R)),sha256=sha(oldraw)),originalHashes=gm['originalHashes'],currentHashes=m['currentHashes'],bug='BUG-2451',ykt='YKT-2190',newProductTests=0,newSourceProofs=0,newAcceptance=0,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,files=files,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()));(O/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,correctedSites=10,remainingUnclassified=122,originalTestCompiled=False,productTestsExecuted=0,manifestSha256=sha(O/'manifest.json'))))
if __name__=='__main__':main()
