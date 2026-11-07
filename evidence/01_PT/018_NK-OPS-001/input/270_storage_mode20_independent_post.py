"""Independent explicit-base inversion/header/boundary/static binding; original native PT stays not run."""
from pathlib import Path
import collections,datetime,hashlib,importlib.util,json,re,shutil,subprocess,xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';RUNS=R.parent/'pgpt-runs/PG379';PRE=RUNS/'pg22830-storage-mode20-prepare-v1';S=RUNS/'pg22832-storage-mode20-static-v1';O=B/'evidence/PG22834-storage-mode20-independent-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def main():
 assert not O.exists();m=load(S/'manifest.json');pre=load(PRE/'manifest.json');fp=B/'evidence/PG22826-storage-mode20-inputs-v1/manifest.json';f=load(fp);gp=B/'evidence/PG22828-storage-mode20-token-value-guard-v1/manifest.json';g=load(gp);assert m['actualExit']==pre['actualExit']==f['actualExit']==g['actualExit']==0 and sha(PRE/'manifest.json')==m['prepareManifestSha256'];assert m['currentHashes']==pre['currentHashes']==g['currentHashes'];assert g['freeze']['sha256']==sha(fp)
 lexer=R/'evidence/01_PT/015_NK-WEB-001/input/042_seven_future_independent_post.py';sp=importlib.util.spec_from_file_location('owned_mode_inverse_tokens',lexer);lm=importlib.util.module_from_spec(sp);sp.loader.exec_module(lm)
 pattern=re.compile(r'(?<![A-Za-z0-9_$])(0x[0-9a-f]+)\s*/\* POSIX (0[0-7]+) \*/');negative=0;restored=0
 def revert(text):
  def sub(match):
   assert int(match.group(1),16)==int(match.group(2),8) and 0<=int(match.group(1),16)<=2147483647
   return match.group(2)
  return pattern.sub(sub,text)
 for item in f['inputs']:
  n=item['path'];old=R/item['snapshotPath'];assert sha(old)==item['sha256'];assert sha(R/n)==m['currentHashes'][n] and hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+n],cwd=R)).hexdigest()==sha(R/n);text=(R/n).read_text();original=old.read_text();assert not pattern.search(original);hits=list(pattern.finditer(text));sites=[v for v in f['selected'] if v['path']==n];assert len(hits)==len(sites);restored+=len(hits);assert [(v.group(1),v.group(2)) for v in hits]==[(v['hex'],v['octal']) for v in sites];assert lm.java_tokens(revert(text))==lm.java_tokens(original)
  bad=text[:hits[0].start()]+text[hits[0].start():].replace(hits[0].group(1),hex(int(hits[0].group(1),16)+1),1)
  try:valid=lm.java_tokens(revert(bad))==lm.java_tokens(original)
  except AssertionError:valid=False
  assert not valid;negative+=1
 assert restored==20 and negative==8
 for path,h in f['headers'].items():assert sha(path)==h
 kernel=Path('/usr/include/linux/stat.h').read_text();libc=Path('/usr/include/x86_64-linux-gnu/bits/stat.h').read_text();ks={n:int(v,8) for n,v in re.findall(r'^#define\s+(S_[A-Z0-9_]+)\s+(0[0-7]+)\b',kernel,re.M)};ls={n:int(v,8) for n,v in re.findall(r'^#define\s+__(S_IF[A-Z]+)\s+(0[0-7]+)\b',libc,re.M)}
 assert all(ks[n]==ls[n] for n in ['S_IFMT','S_IFREG','S_IFDIR','S_IFLNK']);assert ks['S_IRWXU']==ks['S_IRUSR']|ks['S_IWUSR']|ks['S_IXUSR'];assert ks['S_IRWXG']==ks['S_IRGRP']|ks['S_IWGRP']|ks['S_IXGRP']
 # Fixed formulas are public ABI/type/permission combinations, independent of Production methods.
 forms={'0100640':ks['S_IFREG']|ks['S_IRUSR']|ks['S_IWUSR']|ks['S_IRGRP'],'0100600':ks['S_IFREG']|ks['S_IRUSR']|ks['S_IWUSR'],'0120000':ks['S_IFLNK'],'0170000':ks['S_IFMT'],'0700':ks['S_IRWXU'],'0777':ks['S_IRWXU']|ks['S_IRWXG']|ks['S_IRWXO'],'040700':ks['S_IFDIR']|ks['S_IRWXU'],'0100700':ks['S_IFREG']|ks['S_IRWXU'],'040750':ks['S_IFDIR']|ks['S_IRWXU']|ks['S_IRGRP']|ks['S_IXGRP']}
 boundaryNegative=0
 for v in f['selected']:
  assert forms[v['octal']]==v['decimal']==int(v['hex'],16);text=(R/next(i['snapshotPath'] for i in f['inputs'] if i['path']==v['path'])).read_text();a=v['startCodepoint'];z=v['endCodepointExclusive'];assert text[a:z]==v['octal'];assert not re.match(r'[A-Za-z0-9_$]',text[z:z+1]);assert re.match(r'[0-9]',text[z-1:z]);assert not re.fullmatch(r'0[0-7]+',text[a:z+1]);boundaryNegative+=1
 assert boundaryNegative==f['endColumnPlusOneNegatives']==20;assert load(R/f['originalPartial']['path'])['actualExit']==1 and sha(R/f['originalPartial']['path'])==f['originalPartial']['sha256']
 for base,stages in [(PRE,pre['stages']),(S,m['stages'])]:
  for label,s in stages.items():
   assert not s['timedOut'] and s==load(base/(label+'-exit.safe.json'))
   if base==PRE:assert s['actualExit']==0
   for stream in ['stdout','stderr']:assert sha(base/(label+'.'+stream))==s[stream+'Sha256']
 for base,labels in [(PRE,['format','parse']),(S,['pmd','checkstyle'])]:
  for label in labels:
   text=(base/(label+'-class-init.stdout')).read_text();assert "Initializing 'java/lang/Object'" in text and not re.search(r"Initializing '(?:dev/codex/schubert/nk/|dev\.codex\.schubert\.nk\.)",text)
 for n,h in m['dependencies'].items():assert sha(n)==h
 own=pre['ownTool'];assert sha(R/own['path'])==own['sha256']==own['mirrorSha256']==sha(PRE/'source/TestMethodScopeAstCheck.java');assert {p.name:sha(p) for p in (PRE/'classes').iterdir()}==own['classHashes'] and set(own['classHashes'])=={'TestMethodScopeAstCheck.class','TestMethodScopeAstCheck$1.class'};assert 'task.parse()' in (R/own['path']).read_text() and not any(v in (R/own['path']).read_text() for v in ['task.analyze(','task.generate(','Class.forName']);javac=pre['stages']['own-tool-javac']['command'];assert javac[-1]==str(PRE/'source/TestMethodScopeAstCheck.java') and '-proc:none' in javac;parse=pre['stages']['parse']['command'];assert parse[2:6]==['-cp',str(PRE/'classes'),'TestMethodScopeAstCheck',str(R)] and parse[6:]==sorted(m['currentHashes'])
 reports={}
 for label,tag in [('pmd','violation'),('checkstyle','error')]:
  root=E.parse(S/(label+'.xml')).getroot();items=[]
  for parent in root.iter():
   if parent.tag.rsplit('}',1)[-1]=='file':
    n=str(Path(parent.get('name')).relative_to(R));assert n in m['currentHashes'];items += [dict(path=n,**x.attrib,message=' '.join(''.join(x.itertext()).split())[:600]) for x in parent if x.tag.rsplit('}',1)[-1]==tag]
  assert items==m['reports'][label]['items'] and not m['reports'][label]['processingErrors'];reports[label]=items
 assert len(reports['pmd'])==59 and not reports['checkstyle'];assert m['stages']['pmd']['actualExit']==4 and m['stages']['checkstyle']['actualExit']==0
 previous=load(R/f['currentStorageBaseline']['path']);assert sha(R/f['currentStorageBaseline']['path'])==f['currentStorageBaseline']['sha256'];raw=load(R/previous['rawOriginalManifest']['path']);changed=set(previous['currentHashes']);olditems=[v for v in raw['reports']['pmd']['rawItems'] if v['path'] not in changed]+[v['current'] for v in previous['currentStorage29']['retainedSourceRebindings']];assert len(olditems)==122;paths=set(m['currentHashes']);affected=[v for v in olditems if v['path'] in paths];removed=[v for v in affected if v['rule']=='AvoidUsingOctalValues'];retained=[v for v in affected if v['rule']!='AvoidUsingOctalValues'];assert len(affected)==79 and len(removed)==20 and len(retained)==59
 key=lambda v:tuple(v.get(k) for k in ['path','rule','class','method','variable','message']);assert collections.Counter(key(v) for v in retained)==collections.Counter(key(v) for v in reports['pmd']);assert not any(v['rule']=='AvoidUsingOctalValues' for v in reports['pmd']);groups=lambda rows:{k:sorted([v for v in rows if key(v)==k],key=lambda v:(int(v['beginline']),int(v['begincolumn']))) for k in {key(v) for v in rows}};a=groups(retained);z=groups(reports['pmd']);bindings=[dict(original=v,current=w,reason='same rule/owner/message and source order after independent complete integer/comment inverse') for k,vs in a.items() for v,w in zip(vs,z[k])];unaffected=[v for v in olditems if v['path'] not in paths];assert len(unaffected)==43
 hashes={n:sha(R/n) for n in previous['currentStorage29']['currentInputHashes']};assert {n for n in hashes if hashes[n]!=previous['currentStorage29']['currentInputHashes'][n]}==paths;assert len(unaffected)+len(bindings)==102
 assert not m['originalTestsCompiled'] and not pre['originalTestsCompiled'] and m['productTestsExecuted']==pre['productTestsExecuted']==0
 O.mkdir();files={}
 for base,prefix in [(PRE,'prepare-'),(S,'static-')]:
  for p in base.iterdir():
   if p.is_file():name=prefix+p.name;shutil.copyfile(p,O/name);files[name]=sha(O/name)
 value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],sourceFixedTestFiles=8,staticStyleSitesCorrected=20,integerExpectedValuesUnchanged=True,allOtherJavaTokensRestored=True,independentHeaderCrosscheck=True,numericMutationNegatives=8,endColumnNegatives=20,originalTestCompiled=False,productTestsExecuted=0,originalNativeTestRun=False,staticAlternativeOnly=True,ptPassCount=None,coverage=None,residualRisk='Original native/filesystem/process/Root runtime tests remain HOLD/not run. Host SDK headers are independent numeric ABI sources, not fresh guest ABI/native execution evidence.',freeze=dict(path=str(fp.relative_to(R)),sha256=sha(fp)),guardManifest=dict(path=str(gp.relative_to(R)),sha256=sha(gp)),currentStorage29=dict(checkedSources=29,unchangedSources=21,changedSources=8,currentInputHashes=hashes,previousComposedRaw=122,correctedSites=removed,retainedSourceRebindings=bindings,unaffectedSourceRaw=43,currentComposedRaw=102,applicableFindings=None,unclassified=102,checkstyle=0,formatDifferences=0,freshAll29EngineRun=False,previousBinding=dict(path=f['currentStorageBaseline']['path'],sha256=f['currentStorageBaseline']['sha256'])),bugs=['BUG-2452','BUG-2453'],ykt='YKT-2191',newProductTests=0,newSourceProofs=0,newAcceptance=0,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,files=files,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()));(O/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,correctedSites=20,currentStorageUnclassified=102,productTestsExecuted=0,manifestSha256=sha(O/'manifest.json'))))
if __name__=='__main__':main()
