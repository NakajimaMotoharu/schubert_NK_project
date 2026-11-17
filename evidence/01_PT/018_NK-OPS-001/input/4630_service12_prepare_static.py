"""Bind actual new-core Main/Test compiles; analyze changed Main and two whole selected/helper sources only."""
from pathlib import Path
import datetime,hashlib,json,re,sys,xml.etree.ElementTree as ET
r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
import pg9666_pagination_static as stage
b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
cp=b/'evidence/PG37184-service12-test-compile-v1/manifest.json';c=ld(cp);root=ld(r/c['rootCompile']['path']);patch=ld(r/c['sourcePatch']['path']);assert c['actualExit']==root['actualExit']==patch['actualExit']==0
main=patch['mainPath'];selected=patch['testPath'];shared=selected.replace('MorningServiceReadinessTest.java','RootStartupContextTest.java');sources=[main,selected,shared];assert len(re.findall(r'@Test\s+void',(r/selected).read_text()))==12
assert sha(r/main)==patch['mainShaAfter'] and sha(r/selected)==patch['testShaAfter'] and all(sha(r/n)==h for n,h in c['inputHashes'].items()) and all(sha(r/n)==h for n,h in root['inputHashes'].items())
for n in [main,selected]:assert (r/n).read_bytes()==(b/'evidence/PG37178-service-command-port-source-v1'/(Path(n).name+'.format.stdout')).read_bytes()
assert (r/shared).read_bytes()==(b/'evidence/PG37156-service-style-and-value-source-v2'/(Path(shared).name+'.format.stdout')).read_bytes()
work=Path(c['work']);assert all(sha(work/'component'/n)==h for n,h in c['physicalClassHashes'].items()) and all(sha(work/'test-classes'/n)==h for n,h in c['testClassHashes'].items())
deps=[Path(n) for n in c['toolDependencies']];assert all(sha(n)==c['toolDependencies'][str(n)] for n in deps);classpath=':'.join(map(str,[work/'component',*deps]));jdk=tc/'jdk-25.0.4/bin';sg=tc/'static-gates-20261015';libs=[sg/'record-fix-v1/pmd-record-1298.jar',*sorted((sg/'pmd-bin-7.28.0/lib').glob('*.jar'))];rules=r/'tools/quality/static';out=b/'evidence/PG37186-service12-reused-compile-static-v1';assert not out.exists();out.mkdir();listing=out/'sources.txt';listing.write_text(''.join(str(r/n)+'\n' for n in sources));pins={str(n):sha(n) for n in [*deps,*libs,sg/'checkstyle-14.3.0-all.jar',tc/'google-java-format-1.36.1-all-deps.jar',rules/'pmd.xml',rules/'checkstyle.xml']}
commands={'checkstyle':[str(jdk/'java'),'-jar',str(sg/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(out/'checkstyle.xml'),'@'+str(listing)],'pmd':[str(jdk/'java'),'-cp',':'.join(map(str,libs)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',str(tc/'jdk-25.0.4/lib/jrt-fs.jar')+':'+str(work/'test-classes')+':'+classpath,'--no-cache','--format','xml','--report-file',str(out/'pmd.xml')]};stage.SLOT=out;stage.ENV=dict(PATH=str(jdk)+':/usr/bin:/bin',JAVA_HOME=str(tc/'jdk-25.0.4'),LANG='C.UTF-8');stages={}
for n,cmd in commands.items():
 stages[n]=stage.step(n,cmd,work,timeout=120);assert not stages[n]['timedOut'] and stages[n]['actualExit'] in ([0,4] if n=='pmd' else [0])
raw=[];errors=[]
for node in ET.parse(out/'pmd.xml').getroot().iter():
 tag=node.tag.rsplit('}',1)[-1]
 if tag in ['error','configerror']:errors.append(dict(node.attrib))
 if tag=='file':
  for x in node:
   if x.tag.rsplit('}',1)[-1]=='violation':raw.append(dict(path=str(Path(node.get('name')).relative_to(r)),**x.attrib,message=(x.text or '').strip()))
assert not errors and not ET.parse(out/'checkstyle.xml').getroot().findall('.//error')
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=c['sourceCore'],rootCompile=c['rootCompile'],mainInputHashes=root['inputHashes'],testSourceHashes=c['inputHashes'],physicalClassHashes=c['physicalClassHashes'],testPhysicalHashes=c['testClassHashes'],work=str(work),classpath=classpath,toolDependencyHashes=pins,stages=stages,rawFindings=raw,processingErrors=errors,wholeTestSourceCounts={selected:12},expectedTests=12,originalWholeTests=9,newCommandCleanupTests=3,sharedWholeTestsSelected=0,reusedActualStrictCompile=ref(cp),testCompileRerunsAfterSuccess=0,mainCompileRerunsAfterSuccess=0,productTestsExecuted=0,heldClassfileActions=0,actualBackendNativeRootOperations=0,mainSpotBugsCurrentProof=ref(b/'evidence/PG37182-service-command-fresh-sibling-spotbugs-v1/manifest.json'),formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,expected12=True,raw=len(raw),newCompile=0,productTests=0)))
