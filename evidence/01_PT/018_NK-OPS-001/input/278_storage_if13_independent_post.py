"""Independent const-inlining/value/source/static rebinding; no native or original Test execution."""
from pathlib import Path
import collections,datetime,hashlib,importlib.util,json,re,shutil,subprocess,xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';RUNS=R.parent/'pgpt-runs/PG379';PRE=RUNS/'pg22854-storage-if13-prepare-v1';S=RUNS/'pg22856-storage-if13-static-v1';O=B/'evidence/PG22858-storage-if13-independent-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_bytes())
VALUES={'LinuxFileLockTest.java':{'EAGAIN_ERRNO':11},'LinuxStartupFileLockTest.java':{'EAGAIN_ERRNO':11},'LinuxStartupAdmissionTest.java':{'F_GETFD_COMMAND':1,'F_GET_SEALS_COMMAND':1034,'F_GETFL_COMMAND':3,'CLOSE_ERRNO_VARIANT':1,'CLOSE_RUNTIME_VARIANT':2,'CLOSE_FATAL_VARIANT':3},'OwnedTransferDirectoryTest.java':{'CLEANUP_ONLY_FAULT_VARIANT':1,'DATE_CHILD_SCOPE':1},'PrivateDirectoryEntryTest.java':{'UNCHECKED_BODY_VARIANT':2}}
def main():
 assert not O.exists();m=load(S/'manifest.json');pre=load(PRE/'manifest.json');fp=B/'evidence/PG22850-storage-if13-original-v1/manifest.json';f=load(fp);gp=B/'evidence/PG22852-storage-if13-token-value-guard-v1/manifest.json';g=load(gp);assert m['actualExit']==pre['actualExit']==f['actualExit']==g['actualExit']==0 and sha(PRE/'manifest.json')==m['prepareManifestSha256'];assert m['currentHashes']==pre['currentHashes']==g['currentHashes'];assert g['originalManifest']['sha256']==sha(fp) and g['sourceConstantDefinitions']==VALUES
 lexer=R/'evidence/01_PT/015_NK-WEB-001/input/042_seven_future_independent_post.py';sp=importlib.util.spec_from_file_location('owned_if13_inverse',lexer);lm=importlib.util.module_from_spec(sp);sp.loader.exec_module(lm);tok=lm.java_tokens
 def inline(name,tokens):
  tokens=list(tokens);uses=0
  for symbol,value in VALUES[name].items():
   declaration=tok('private static final int '+symbol+' = '+str(value)+';');positions=[i for i in range(len(tokens)-len(declaration)+1) if tokens[i:i+len(declaration)]==declaration];assert len(positions)==1;i=positions[0];tokens=tokens[:i]+tokens[i+len(declaration):];count=tokens.count(symbol);assert count>0;uses+=count;tokens=[str(value) if v==symbol else v for v in tokens]
  return tokens,uses
 negatives=0;uses=0
 for item in f['inputs']:
  n=item['path'];name=Path(n).name;old=R/item['snapshotPath'];assert sha(old)==item['sha256'];assert sha(R/n)==m['currentHashes'][n] and hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+n],cwd=R)).hexdigest()==sha(R/n);actual=(R/n).read_text();restored,count=inline(name,tok(actual));uses+=count;assert restored==tok(old.read_text());assert not set(VALUES[name])&set(tok(old.read_text()));symbol,value=next(iter(VALUES[name].items()));bad=actual.replace(symbol+' = '+str(value)+';',symbol+' = '+str(value+1)+';',1)
  try:valid=inline(name,tok(bad))[0]==tok(old.read_text())
  except AssertionError:valid=False
  assert not valid;negatives+=1
 assert uses==13 and negatives==5 and sum(len(v) for v in VALUES.values())==11
 for p,h in f['headers'].items():assert sha(p)==h
 fcntl=Path('/usr/include/asm-generic/fcntl.h').read_text();linux=Path('/usr/include/linux/fcntl.h').read_text();errno=Path('/usr/include/asm-generic/errno-base.h').read_text();num=lambda name,text:int(re.search(r'^#define\s+'+name+r'\s+(\d+)\b',text,re.M).group(1));assert num('EAGAIN',errno)==11 and num('F_GETFD',fcntl)==1 and num('F_GETFL',fcntl)==3 and num('F_LINUX_SPECIFIC_BASE',fcntl)==1024;assert re.search(r'^#define\s+F_GET_SEALS\s+\(F_LINUX_SPECIFIC_BASE\s*\+\s*10\)',linux,re.M);assert g['independentHeaderValues']==dict(EAGAIN_ERRNO=11,F_GETFD_COMMAND=1,F_GETFL_COMMAND=3,F_GET_SEALS_COMMAND=1034)
 for base,stages in [(PRE,pre['stages']),(S,m['stages'])]:
  for label,s in stages.items():
   assert not s['timedOut'] and s==load(base/(label+'-exit.safe.json'))
   if base==PRE:assert s['actualExit']==0
   for stream in ['stdout','stderr']:assert sha(base/(label+'.'+stream))==s[stream+'Sha256']
 for base,labels in [(PRE,['format','parse']),(S,['pmd','checkstyle'])]:
  for label in labels:
   text=(base/(label+'-class-init.stdout')).read_text();assert "Initializing 'java/lang/Object'" in text and not re.search(r"Initializing '(?:dev/codex/schubert/nk/|dev\.codex\.schubert\.nk\.)",text)
 for n,h in m['dependencies'].items():assert sha(n)==h
 own=pre['ownTool'];assert sha(R/own['path'])==own['sha256']==own['mirrorSha256']==sha(PRE/'source/TestMethodScopeAstCheck.java');assert {p.name:sha(p) for p in (PRE/'classes').iterdir()}==own['classHashes'] and set(own['classHashes'])=={'TestMethodScopeAstCheck.class','TestMethodScopeAstCheck$1.class'};assert 'task.parse()' in (R/own['path']).read_text() and not any(v in (R/own['path']).read_text() for v in ['task.analyze(','task.generate(','Class.forName']);assert pre['stages']['own-tool-javac']['command'][-1]==str(PRE/'source/TestMethodScopeAstCheck.java');parse=pre['stages']['parse']['command'];assert parse[2:6]==['-cp',str(PRE/'classes'),'TestMethodScopeAstCheck',str(R)] and parse[6:]==sorted(m['currentHashes'])
 reports={}
 for label,tag in [('pmd','violation'),('checkstyle','error')]:
  root=E.parse(S/(label+'.xml')).getroot();items=[]
  for parent in root.iter():
   if parent.tag.rsplit('}',1)[-1]=='file':
    n=str(Path(parent.get('name')).relative_to(R));assert n in m['currentHashes'];items += [dict(path=n,**x.attrib,message=' '.join(''.join(x.itertext()).split())[:600]) for x in parent if x.tag.rsplit('}',1)[-1]==tag]
  assert items==m['reports'][label]['items'] and not m['reports'][label]['processingErrors'];reports[label]=items
 assert len(reports['pmd'])==32 and not reports['checkstyle'];assert m['stages']['pmd']['actualExit']==4 and m['stages']['checkstyle']['actualExit']==0
 raw=f['allCurrentRaw'];assert len(raw)==102;paths=set(m['currentHashes']);affected=[v for v in raw if v['path'] in paths];removed=[v for v in affected if v['rule']=='AvoidLiteralsInIfCondition'];retained=[v for v in affected if v['rule']!='AvoidLiteralsInIfCondition'];assert len(affected)==45 and len(removed)==13 and len(retained)==32
 key=lambda v:tuple(v.get(k) for k in ['path','rule','class','method','variable','message']);assert collections.Counter(key(v) for v in retained)==collections.Counter(key(v) for v in reports['pmd']);assert not any(v['rule']=='AvoidLiteralsInIfCondition' for v in reports['pmd']);groups=lambda rows:{k:sorted([v for v in rows if key(v)==k],key=lambda v:(int(v['beginline']),int(v['begincolumn']))) for k in {key(v) for v in rows}};a=groups(retained);z=groups(reports['pmd']);bindings=[dict(original=v,current=w) for k,vs in a.items() for v,w in zip(vs,z[k])];unaffected=[v for v in raw if v['path'] not in paths];current=unaffected+reports['pmd'];assert len(unaffected)==57 and len(current)==89;hashes={n:sha(R/n) for n in f['currentInputHashes']};assert {n for n in hashes if hashes[n]!=f['currentInputHashes'][n]}==paths
 reviewpost=load(R/f['reviewedEight']['path']);assert sha(R/f['reviewedEight']['path'])==f['reviewedEight']['sha256'];rp=reviewpost['reviewManifest'];review=load(R/rp['path']);assert sha(R/rp['path'])==rp['sha256'];reviews=[]
 for oldrow in review['reviewedFindings']:
  matches=[v for v in current if key(v)==key(oldrow['finding'])];assert len(matches)==1;row=dict(oldrow);row['finding']=matches[0];row['currentSourceSha256']=hashes[row['finding']['path']];row['witnesses']=[dict(w,sha256=sha(R/w['path']),line=(R/w['path']).read_text()[:(R/w['path']).read_text().index(w['text'])].count('\n')+1) for w in oldrow['witnesses']];assert row['runtimeValidated'] is False;reviews.append(row)
 assert len(reviews)==8 and all(v['classification']=='NOT_APPLICABLE' for v in reviews)
 assert not m['originalTestsCompiled'] and not pre['originalTestsCompiled'] and m['productTestsExecuted']==pre['productTestsExecuted']==0
 O.mkdir();files={}
 for base,prefix in [(PRE,'prepare-'),(S,'static-')]:
  for p in base.iterdir():
   if p.is_file():name=prefix+p.name;shutil.copyfile(p,O/name);files[name]=sha(O/name)
 value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],sourceFixedTestFiles=5,staticStyleSitesCorrected=13,independentConstantDefinitions=11,allOtherJavaTokensFixturesAndExpectedValuesRestored=True,numericMutationNegatives=5,originalTestCompiled=False,productTestsExecuted=0,originalNativeTestsRun=False,staticAlternativeOnly=True,ptPassCount=None,coverage=None,residualRisk='Original native/filesystem/process/Root runtime tests remain HOLD/not run. Named Test constants/static review do not qualify real platform behavior.',originalManifest=dict(path=str(fp.relative_to(R)),sha256=sha(fp)),guardManifest=dict(path=str(gp.relative_to(R)),sha256=sha(gp)),currentStorage29=dict(checkedSources=29,unchangedSources=24,changedSources=5,currentInputHashes=hashes,allCurrentRaw=current,previousComposedRaw=102,correctedSites=removed,retainedSourceRebindings=bindings,currentComposedRaw=89,reviewedFindings=reviews,individuallyClassified=8,unclassified=81,totalApplicableFindings=None,applicableOnReviewedSubset=0,checkstyle=0,formatDifferences=0,freshAll29EngineRun=False,previousBaseline=f['baseline']),bug='BUG-2454',ykt='YKT-2192',newProductTests=0,newSourceProofs=0,newAcceptance=0,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,files=files,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()));(O/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,correctedSites=13,constants=11,currentStorageRaw=89,classified=8,unclassified=81,productTestsExecuted=0,manifestSha256=sha(O/'manifest.json'))))
if __name__=='__main__':main()
