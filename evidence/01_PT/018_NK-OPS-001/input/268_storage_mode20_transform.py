"""Mode20 explicit-base conversion, independent public-header values; no native or original Test execution."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,re,subprocess,sys
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';PART=B/'evidence/PG22822-storage-mode20-original-v1';F=B/'evidence/PG22826-storage-mode20-inputs-v1';OUT=B/'evidence/PG22828-storage-mode20-token-value-guard-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def offset(text,line,column):
 lines=text.splitlines(keepends=True);return sum(len(v) for v in lines[:line-1])+len(lines[line-1].encode('utf-16-le')[:(column-1)*2].decode('utf-16-le'))
def main():
 phase=sys.argv[1];assert phase in ['freeze','edit','guard'];m=load(B/'evidence/PG22814-storage-style-independent-v1/manifest.json');old=load(R/m['rawOriginalManifest']['path']);changed=set(m['currentHashes']);items=[v for v in old['reports']['pmd']['rawItems'] if v['path'] not in changed]+[v['current'] for v in m['currentStorage29']['retainedSourceRebindings']];sites=sorted([dict(v) for v in items if v['rule']=='AvoidUsingOctalValues'],key=lambda v:(v['path'],int(v['beginline']),int(v['begincolumn'])));assert len(sites)==20
 if phase=='freeze':
  assert not F.exists();partial=load(PART/'manifest.json');assert partial['actualExit']==1 and not partial['sourceChangesApplied'];names=sorted({v['path'] for v in sites});assert len(names)==8;inputs=[]
  for n in names:
   assert not any(v in n for v in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_']);p=PART/Path(n).name;assert sha(p)==partial['backupFiles'][p.name]==sha(R/n)==m['currentStorage29']['currentInputHashes'][n];inputs.append(dict(path=n,sha256=sha(p),snapshotPath=str(p.relative_to(R))))
  negative=0
  for i,v in enumerate(sites,1):
   text=(R/v['path']).read_text();assert v['beginline']==v['endline'];a=offset(text,int(v['beginline']),int(v['begincolumn']));z=offset(text,int(v['endline']),int(v['endcolumn']));literal=text[a:z];assert re.fullmatch(r'0[0-7]+',literal);assert a==0 or not re.match(r'[A-Za-z0-9_$]',text[a-1]);assert z==len(text) or not re.match(r'[A-Za-z0-9_$]',text[z]);assert not re.fullmatch(r'0[0-7]+',text[a:z+1]);negative+=1;v.update(siteId='MODE'+str(i).zfill(3),octal=literal,decimal=int(literal,8),hex=hex(int(literal,8)),startCodepoint=a,endCodepointExclusive=z)
  headers={p:sha(p) for p in ['/usr/include/linux/stat.h','/usr/include/x86_64-linux-gnu/bits/stat.h']};packages=subprocess.check_output(['dpkg-query','-W','-f=${Package} ${Version}\n','linux-libc-dev','libc6-dev'],text=True).splitlines();F.mkdir();write(F/'manifest.json',dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),inputs=inputs,selected=sites,headers=headers,headerPackages=packages,endColumnAssessment='PMD endcolumn exclusive; UTF16 coordinates converted before slice',endColumnPlusOneNegatives=negative,originalPartial=dict(path=str((PART/'manifest.json').relative_to(R)),sha256=sha(PART/'manifest.json')),currentStorageBaseline=dict(path=str((B/'evidence/PG22814-storage-style-independent-v1/manifest.json').relative_to(R)),sha256=sha(B/'evidence/PG22814-storage-style-independent-v1/manifest.json')),productTestsExecuted=0));print('freeze20/exclusive-end+20 negatives0; partial1 preserved');return
 f=load(F/'manifest.json');expected={}
 for item in f['inputs']:
  p=R/item['snapshotPath'];assert sha(p)==item['sha256'];text=p.read_text()
  for v in sorted([v for v in f['selected'] if v['path']==item['path']],key=lambda v:v['startCodepoint'],reverse=True):
   a=v['startCodepoint'];z=v['endCodepointExclusive'];assert text[a:z]==v['octal'];text=text[:a]+v['hex']+' /* POSIX '+v['octal']+' */'+text[z:]
  expected[item['path']]=text
 if phase=='edit':
  assert all(sha(R/v['path'])==v['sha256'] for v in f['inputs'])
  for n,text in expected.items():(R/n).write_text(text)
  print('edited exactly20 numeric tokens with original-octal comments');return
 assert not OUT.exists();lexer=R/'evidence/01_PT/015_NK-WEB-001/input/042_seven_future_independent_post.py';sp=importlib.util.spec_from_file_location('owned_mode_tokens',lexer);lm=importlib.util.module_from_spec(sp);sp.loader.exec_module(lm)
 for n,text in expected.items():assert lm.java_tokens(text)==lm.java_tokens((R/n).read_text())
 for p,h in f['headers'].items():assert sha(p)==h
 text=Path('/usr/include/linux/stat.h').read_text();macros={n:int(v,8) for n,v in re.findall(r'^#define\s+(S_[A-Z0-9_]+)\s+(0[0-7]+)\b',text,re.M)};formula={'0100640':['S_IFREG','S_IRUSR','S_IWUSR','S_IRGRP'],'0100600':['S_IFREG','S_IRUSR','S_IWUSR'],'0120000':['S_IFLNK'],'0170000':['S_IFMT'],'0700':['S_IRWXU'],'0777':['S_IRWXU','S_IRWXG','S_IRWXO'],'040700':['S_IFDIR','S_IRWXU'],'0100700':['S_IFREG','S_IRWXU'],'040750':['S_IFDIR','S_IRWXU','S_IRGRP','S_IXGRP']};glibc={n:int(v,8) for n,v in re.findall(r'^#define\s+__(S_IF[A-Z]+)\s+(0[0-7]+)\b',Path('/usr/include/x86_64-linux-gnu/bits/stat.h').read_text(),re.M)}
 for n in ['S_IFREG','S_IFDIR','S_IFLNK','S_IFMT']:assert macros[n]==glibc[n]
 rows=[]
 for v in f['selected']:
  value=0
  for name in formula[v['octal']]:value|=macros[name]
  assert value==v['decimal']==int(v['hex'],16) and 0<=value<=2147483647;rows.append(dict(siteId=v['siteId'],path=v['path'],octal=v['octal'],hex=v['hex'],expectedDecimal=value,independentHeaderFormula=formula[v['octal']]))
 negative=0
 for n,text in expected.items():
  first=next(v for v in f['selected'] if v['path']==n);bad=(R/n).read_text().replace(first['hex'],str(first['decimal']+1),1);assert lm.java_tokens(text)!=lm.java_tokens(bad);negative+=1
 OUT.mkdir();value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),observerSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),freeze=dict(path=str((F/'manifest.json').relative_to(R)),sha256=sha(F/'manifest.json')),currentHashes={n:sha(R/n) for n in expected},integerValueWitnesses=rows,independentHeaderMacros=macros,libcFileTypeCrosscheck=glibc,allOtherJavaTokensFixturesAndIntegerExpectedValuesUnchanged=True,numericMutationNegativeGuards=negative,productTestsExecuted=0,originalTestsCompiled=False,originalNativeTestRun=False,staticAlternativeOnly=True,remainingRisk='Real platform native/Root tests remain HOLD; SDK header values are not guest ABI measurements.',newProductTests=0,newSourceProofs=0,newAcceptance=0,whole451Accepted=False,effortRate=None,producer=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)));write(OUT/'manifest.json',value);print(json.dumps(dict(actualExit=0,modeValues=20,numericNegatives=negative,productTests=0)))
if __name__=='__main__':main()
