"""Reuse genuine strict17 compile for unchanged selected9/helper bytes; no repeat compile or product run."""
from pathlib import Path
import datetime,hashlib,json,re,shutil,sys,xml.etree.ElementTree as ET
r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
import pg9666_pagination_static as stage
b=r/'evidence/01_PT/018_NK-OPS-001';w=r.parent/'pgpt-runs/PG379';tc=r.parent/'toolchain';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
rootp=b/'evidence/PG36956-backup-path-four-main-compile-v1/manifest.json';root=ld(rootp);cp=b/'evidence/PG37164-root-fixture-caller-compile-v2/manifest.json';compiled=ld(cp);source=ld(b/'evidence/PG37156-service-style-and-value-source-v2/manifest.json');assert root['actualExit']==compiled['actualExit']==source['actualExit']==0
assert all(sha(r/n)==h for n,h in root['inputHashes'].items()) and all(sha(r/n)==h for n,h in compiled['inputHashes'].items())
selected='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/MorningServiceReadinessTest.java';shared=selected.replace('MorningServiceReadinessTest.java','RootStartupContextTest.java');sources=[selected,shared];assert len(re.findall(r'@Test\s+void', (r/selected).read_text()))==9
assert all(sha(r/n)==source['inputHashesAfter'][n] and (r/n).read_bytes()==(b/'evidence/PG37156-service-style-and-value-source-v2'/(Path(n).name+'.format.stdout')).read_bytes() for n in sources)
prior=ld(b/'evidence/PG37134-caddy20-prepare-static-v1/manifest.json');component=Path(prior['work'])/'component';oldclasses=w/'pg37164-root-fixture-caller-compile-v2/test-classes';assert all(sha(component/n)==h for n,h in prior['physicalClassHashes'].items()) and all(sha(oldclasses/n)==h for n,h in compiled['testClassHashes'].items())
work=w/'pg37166-service9-prepare-v1';out=b/'evidence/PG37166-service9-reused-compile-static-v1';assert not work.exists() and not out.exists();work.mkdir();out.mkdir();shutil.copytree(component,work/'component');shutil.copytree(oldclasses,work/'test-classes')
deps=[Path(n) for n in compiled['toolDependencies']];assert all(sha(n)==compiled['toolDependencies'][str(n)] for n in deps);classpath=':'.join(map(str,[work/'component',*deps]));jdk=tc/'jdk-25.0.4/bin';sg=tc/'static-gates-20261015';libs=[sg/'record-fix-v1/pmd-record-1298.jar',*sorted((sg/'pmd-bin-7.28.0/lib').glob('*.jar'))];rules=r/'tools/quality/static';listing=out/'sources.txt';listing.write_text(''.join(str(r/n)+'\n' for n in sources));pins={str(n):sha(n) for n in [*deps,*libs,sg/'checkstyle-14.3.0-all.jar',tc/'google-java-format-1.36.1-all-deps.jar',rules/'pmd.xml',rules/'checkstyle.xml']}
commands={'checkstyle':[str(jdk/'java'),'-jar',str(sg/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(out/'checkstyle.xml'),'@'+str(listing)],'pmd':[str(jdk/'java'),'-cp',':'.join(map(str,libs)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',str(tc/'jdk-25.0.4/lib/jrt-fs.jar')+':'+str(work/'test-classes')+':'+classpath,'--no-cache','--format','xml','--report-file',str(out/'pmd.xml')]};stage.SLOT=out;stage.ENV=dict(PATH=str(jdk)+':/usr/bin:/bin',JAVA_HOME=str(tc/'jdk-25.0.4'),LANG='C.UTF-8');stages={}
for n,c in commands.items():
 stages[n]=stage.step(n,c,work,timeout=120);assert not stages[n]['timedOut'] and stages[n]['actualExit'] in ([0,4] if n=='pmd' else [0])
raw=[];errors=[]
for node in ET.parse(out/'pmd.xml').getroot().iter():
 tag=node.tag.rsplit('}',1)[-1]
 if tag in ['error','configerror']:errors.append(dict(node.attrib))
 if tag=='file':
  for x in node:
   if x.tag.rsplit('}',1)[-1]=='violation':raw.append(dict(path=str(Path(node.get('name')).relative_to(r)),**x.attrib,message=(x.text or '').strip()))
assert not errors and not ET.parse(out/'checkstyle.xml').getroot().findall('.//error')
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=root['sourceCore'],rootCompile=ref(rootp),mainInputHashes=root['inputHashes'],testSourceHashes=compiled['inputHashes'],physicalClassHashes=prior['physicalClassHashes'],testPhysicalHashes=compiled['testClassHashes'],work=str(work),classpath=classpath,toolDependencyHashes=pins,stages=stages,rawFindings=raw,processingErrors=errors,wholeTestSourceCounts={selected:9},expectedTests=9,originalWholeTests=8,newValueContractTests=1,sharedTestSources=[n for n in compiled['inputHashes'] if n!=selected],sharedWholeTestsSelected=0,reusedActualStrictCompile=ref(cp),testCompileReruns=0,mainCompileReruns=0,productTestsExecuted=0,heldClassfileActions=0,actualBackendNativeRootOperations=0,sourceFormatProof=ref(b/'evidence/PG37156-service-style-and-value-source-v2/manifest.json'),mainSpotBugsCurrentProof=prior['mainSpotBugsCurrentProof'],formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,expected9=True,raw=len(raw),sharedTestClasses=57,newCompile=0,productTests=0)))
