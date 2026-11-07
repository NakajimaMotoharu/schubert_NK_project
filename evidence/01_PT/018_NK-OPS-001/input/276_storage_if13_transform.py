"""Independent named Test constants at13 exact conditions; no expected value or native Test execution."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,re,subprocess,sys
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';F=B/'evidence/PG22850-storage-if13-original-v1/manifest.json';OUT=B/'evidence/PG22852-storage-if13-token-value-guard-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_bytes())
CFG={
'LinuxFileLockTest.java':({'EAGAIN_ERRNO':11},[('if (error == 11)','if (error == EAGAIN_ERRNO)')]),
'LinuxStartupFileLockTest.java':({'EAGAIN_ERRNO':11},[('if (errno == 11)','if (errno == EAGAIN_ERRNO)')]),
'LinuxStartupAdmissionTest.java':({'F_GETFD_COMMAND':1,'F_GET_SEALS_COMMAND':1034,'F_GETFL_COMMAND':3,'CLOSE_ERRNO_VARIANT':1,'CLOSE_RUNTIME_VARIANT':2,'CLOSE_FATAL_VARIANT':3},[('if (cmd == 1)','if (cmd == F_GETFD_COMMAND)'),('if (cmd == 1034)','if (cmd == F_GET_SEALS_COMMAND)'),('if (cmd == 3)','if (cmd == F_GETFL_COMMAND)'),('if (kind == 1)','if (kind == CLOSE_ERRNO_VARIANT)'),('if (kind == 2)','if (kind == CLOSE_RUNTIME_VARIANT)'),('if (kind == 3)','if (kind == CLOSE_FATAL_VARIANT)'),('if (primary >= 2)','if (primary >= CLOSE_RUNTIME_VARIANT)'),('if (secondary >= 2)','if (secondary >= CLOSE_RUNTIME_VARIANT)')]),
'OwnedTransferDirectoryTest.java':({'CLEANUP_ONLY_FAULT_VARIANT':1,'DATE_CHILD_SCOPE':1},[('if (fault != 1)','if (fault != CLEANUP_ONLY_FAULT_VARIANT)'),('if (scope == 1)','if (scope == DATE_CHILD_SCOPE)')]),
'PrivateDirectoryEntryTest.java':({'UNCHECKED_BODY_VARIANT':2},[('if (kind == 2)','if (kind == UNCHECKED_BODY_VARIANT)')])}
def transformed(name,text):
 constants,replacements=CFG[name]
 for symbol in constants:assert not re.search(r'\b'+symbol+r'\b',text)
 for a,z in replacements:assert text.count(a)==1,(name,a,text.count(a));text=text.replace(a,z)
 body='\n'+''.join('  private static final int '+k+' = '+str(v)+';\n' for k,v in constants.items());pattern=r'((?:final )?class '+Path(name).stem+r'\s*\{)';assert len(re.findall(pattern,text))==1;return re.sub(pattern,lambda m:m.group(1)+body,text,count=1)
def main():
 original=load(F);expected={};old={}
 for item in original['inputs']:
  p=R/item['snapshotPath'];assert sha(p)==item['sha256'];old[item['path']]=p.read_text();expected[item['path']]=transformed(p.name,p.read_text())
 if sys.argv[1:]==['edit']:
  assert all(sha(R/i['path'])==i['sha256'] for i in original['inputs'])
  for n,text in expected.items():(R/n).write_text(text)
  print('edited13 conditions/11 compile-time int names in five original sources');return
 assert not sys.argv[1:] and not OUT.exists();lexer=R/'evidence/01_PT/015_NK-WEB-001/input/042_seven_future_independent_post.py';sp=importlib.util.spec_from_file_location('owned_if13_tokens',lexer);lm=importlib.util.module_from_spec(sp);sp.loader.exec_module(lm);negative=0
 for n,text in expected.items():
  current=(R/n).read_text();assert lm.java_tokens(text)==lm.java_tokens(current);symbol,value=next(iter(CFG[Path(n).name][0].items()));bad=current.replace(symbol+' = '+str(value)+';',symbol+' = '+str(value+1)+';',1);assert lm.java_tokens(text)!=lm.java_tokens(bad);negative+=1
 for p,h in original['headers'].items():assert sha(p)==h
 fcntl=Path('/usr/include/asm-generic/fcntl.h').read_text();linux=Path('/usr/include/linux/fcntl.h').read_text();errno=Path('/usr/include/asm-generic/errno-base.h').read_text();number=lambda name,text:int(re.search(r'^#define\s+'+name+r'\s+(\d+)\b',text,re.M).group(1));values=dict(EAGAIN_ERRNO=number('EAGAIN',errno),F_GETFD_COMMAND=number('F_GETFD',fcntl),F_GETFL_COMMAND=number('F_GETFL',fcntl));assert re.search(r'^#define\s+F_GET_SEALS\s+\(F_LINUX_SPECIFIC_BASE\s*\+\s*10\)',linux,re.M);values['F_GET_SEALS_COMMAND']=number('F_LINUX_SPECIFIC_BASE',fcntl)+10;assert values==dict(EAGAIN_ERRNO=11,F_GETFD_COMMAND=1,F_GETFL_COMMAND=3,F_GET_SEALS_COMMAND=1034)
 assert sum(len(v[1]) for v in CFG.values())==13 and sum(len(v[0]) for v in CFG.values())==11
 OUT.mkdir();result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),observerSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),originalManifest=dict(path=str(F.relative_to(R)),sha256=sha(F)),currentHashes={n:sha(R/n) for n in expected},sourceConstantDefinitions={name:const for name,(const,_) in CFG.items()},independentHeaderValues=values,conditionsReplaced=13,constantDefinitions=11,allOtherJavaTokensFixturesAndExpectedValuesUnchanged=True,numericMutationNegatives=negative,productTestsExecuted=0,originalTestsCompiled=False,originalNativeTestsRun=False,staticAlternativeOnly=True,newProductTests=0,newSourceProofs=0,newAcceptance=0,whole451Accepted=False,effortRate=None,producer=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)));(OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,conditions=13,constants=11,metadataNegatives=5,productTests=0)))
if __name__=='__main__':main()
