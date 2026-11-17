"""Compile only the changed oracle Test, retaining exact previously compiled fifteen-source closure."""
from pathlib import Path
import hashlib,json,shutil,sys,xml.etree.ElementTree as ET
r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
import pg9666_pagination_static as stage
b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
oldp=b/'evidence/PG37238-monitor-lock4-reused-compile-static-v1/manifest.json';old=ld(oldp);oraclep=b/'evidence/PG37240-monitor-lock-oracle-order-v1/manifest.json';oracle=ld(oraclep);name=oracle['path'];assert old['actualExit']==oracle['actualExit']==0
assert all(n==name or sha(r/n)==h for n,h in old['inputHashes'].items()) and sha(r/name)==oracle['afterSha256']
assert all(sha(r/n)==h for n,h in old['mainInputHashes'].items()) and all(sha(Path(n))==h for n,h in old['toolDependencyHashes'].items())
out=b/'evidence/PG37242-monitor-lock-oracle-current-preflight-v1';work=r.parent/'pgpt-runs/PG379/pg37242-monitor-lock-oracle-current-preflight-v1';assert not out.exists() and not work.exists();out.mkdir();work.mkdir();component=work/'component';classes=work/'test-classes';component.mkdir();classes.mkdir();prior=Path(old['work'])
for n,h in old['physicalClassHashes'].items():
 p=prior/'component'/n;assert sha(p)==h;q=component/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
stem='dev/codex/schubert/nk/batch/monitoring/MonitoringLockContractTest';retained={}
for n,h in old['testPhysicalHashes'].items():
 p=prior/'test-classes'/n;assert sha(p)==h
 if n==stem+'.class' or n.startswith(stem+'$'):continue
 q=classes/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);retained[n]=h
jdk=tc/'jdk-25.0.4/bin';sg=tc/'static-gates-20261015';rules=r/'tools/quality/static';deps=old['toolDependencies'];classpath=':'.join([str(component),*deps]);stage.SLOT=out;stage.ENV=dict(PATH=str(jdk)+':/usr/bin:/bin',JAVA_HOME=str(tc/'jdk-25.0.4'),LANG='C.UTF-8')
import subprocess
fmt=subprocess.run([str(jdk/'java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--assume-filename',Path(name).name,'-'],input=(r/name).read_bytes(),capture_output=True,timeout=60);(out/'format.stdout').write_bytes(fmt.stdout);(out/'format.stderr').write_bytes(fmt.stderr);assert fmt.returncode==0 and fmt.stdout==(r/name).read_bytes()
cmd=[str(jdk/'javac'),'--release','25','-g','-proc:none','-implicit:none','-Xlint:all','-Werror','-cp',str(classes)+':'+classpath,'-d',str(classes),str(r/name)];compile_stage=stage.step('changed-test-compile',cmd,work,timeout=120);assert compile_stage['actualExit']==0 and not compile_stage['timedOut']
assert all(sha(classes/n)==h for n,h in retained.items())
listing=out/'sources.txt';listing.write_text(str(r/name)+'\n');libs=[sg/'record-fix-v1/pmd-record-1298.jar',*sorted((sg/'pmd-bin-7.28.0/lib').glob('*.jar'))]
commands={'checkstyle':[str(jdk/'java'),'-jar',str(sg/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(out/'checkstyle.xml'),'@'+str(listing)],'pmd':[str(jdk/'java'),'-cp',':'.join(map(str,libs)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',str(tc/'jdk-25.0.4/lib/jrt-fs.jar')+':'+str(classes)+':'+classpath,'--no-cache','--format','xml','--report-file',str(out/'pmd.xml')]}
stages={n:stage.step(n,cmd,work,timeout=120) for n,cmd in commands.items()};raw=[];errors=[]
for node in ET.parse(out/'pmd.xml').getroot().iter():
 tag=node.tag.rsplit('}',1)[-1]
 if tag in ['error','configerror']:errors.append(dict(node.attrib))
 if tag=='file':
  for x in node:
   if x.tag.rsplit('}',1)[-1]=='violation':raw.append(dict(path=str(Path(node.get('name')).relative_to(r)),**x.attrib,message=(x.text or '').strip()))
assert not errors and not ET.parse(out/'checkstyle.xml').getroot().findall('.//error') and stages['checkstyle']['actualExit']==0 and stages['pmd']['actualExit'] in [0,4] and not any(x['timedOut'] for x in stages.values())
inputs=dict(old['inputHashes']);inputs[name]=sha(r/name)
value=dict(old,actualExit=0,terminalAtUTC=stages['pmd']['endUTC'],inputHashes=inputs,testSourceHashes=inputs,physicalClassHashes=old['physicalClassHashes'],testPhysicalHashes={str(p.relative_to(classes)):sha(p) for p in classes.rglob('*.class')},work=str(work),classpath=classpath,stage=compile_stage,stages=stages,rawFindings=raw,processingErrors=errors,sourcePatch=ref(oraclep),priorFifteenSourcesCompile=ref(oldp),retainedUnchangedTestPhysical=retained,newStrictlyCompiledTestSources=1,recompiledUnchangedTestSources=0,productTestsExecuted=0,formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,expected113=True,currentStrictCompileSources=1,retainedSources=15,raw=len(raw),productTests=0)))
