"""Owned Servlet CSRF adapter qualification; no real session, generation, database, browser or server."""
from pathlib import Path
import json,hashlib,subprocess,os,re,shutil,zipfile,datetime,sys
import xml.etree.ElementTree as E
import pg9666_pagination_static as c
r=Path.cwd();runs=r.parent/'pgpt-runs/PG379';tc=r.parent/'toolchain';jdk=tc/'jdk-25.0.4/bin';phase=sys.argv[1];assert phase in ['prepare','static','run','post'];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text());write=lambda p,d:Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
normal=runs/'pg20990-outbox-required-six-main-compile-v1/manifest.safe.json';assert sha(normal)=='1db34d8f2ccee9fc90244bea86c3e446be0c0e010c66516a1e25c92df3426618';nm=load(normal);assert nm['actualExit']==0 and nm['source']=='4217e14083c6ecac116216e08d57f4361eb2f12d'
for n,h in nm['begin']['inputHashes'].items():assert sha(r/n)==h
for j in nm['jars'].values():assert sha(j['path'])==j['sha256']
prior=load('evidence/01_PT/018_NK-OPS-001/input/097_login_failure_http.json');deps={nm['jars'][v]['path']:nm['jars'][v]['sha256'] for v in ['protocol','web']};j=tc/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar';deps[str(j)]=sha(j);deps.update(prior['converterDependencies']);deps.update(prior['gsonDependencies']);
auxReference=r/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13218-spotbugs-fresh-aux-plan-recovery-v1/manifest.json';assert sha(auxReference)=='a60a6ff0579588e9a10b5a2de6b2d2f4587f983408645a87e8cd4c7ad6917564';aux=load(auxReference)['auxiliaryClasspathHashes']
crypto=tc/'m2/repository/org/springframework/security/spring-security-crypto/7.1.1/spring-security-crypto-7.1.1.jar';assert sha(crypto)==aux[str(crypto)];deps[str(crypto)]=sha(crypto)
for artifact in ['spring-beans','spring-context','spring-expression']:
 path=tc/'m2/repository/org/springframework'/artifact/'7.0.9'/(artifact+'-7.0.9.jar');assert sha(path)==aux[str(path)];deps[str(path)]=sha(path)
assert all(sha(n)==h for n,h in deps.items());console=tc/'junit-platform-console-standalone-1.13.4.jar';assert sha(console)=='3fdfc37e29744a9a67dd5365e81467e26fbde0b7aa204e6f8bbe79eeaa7ae892'
base='src/schubert-nk-web/';pkg='dev/codex/schubert/nk/web/security/';tests=[base+'src/test/java/'+pkg+'CsrfFilterFactoryPortTest.java'];selected=['dev.codex.schubert.nk.web.security.CsrfFilterFactoryPortTest'];main=base+'src/main/java/'+pkg+'WebCsrfFilterFactory.java';driver=str(Path(__file__).resolve().relative_to(r));inputs={n:sha(n) for n in [*tests,main,driver]};pre=runs/'pg21286-csrf-filter-factory-eight-fixed-compile-v1';sta=runs/'pg21288-csrf-filter-factory-eight-fixed-static-v1';unit=runs/'pg21290-csrf-filter-factory-eight-unit-v1';pub=r/'evidence/01_PT/015_NK-WEB-001/evidence/PG21290-csrf-filter-factory-eight-v1';cp=':'.join([*deps,str(console)])
if phase=='prepare':
 assert not pre.exists();pre.mkdir();c.SLOT=pre;(pre/'classes').mkdir()
 stages={'compile':c.step('compile',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(pre/'classes'),*tests],r)}
 write(pre/'manifest.json',dict(actualExit=stages['compile']['actualExit'],inputHashes=inputs,normalManifestSha256=sha(normal),dependencies=deps,consoleSha256=sha(console),classes={str(p.relative_to(pre/'classes')):sha(p) for p in (pre/'classes').rglob('*.class')},selectedClasses=selected,stages=stages,driverSha256=sha(__file__),testsExecuted=0));print(json.dumps(dict(actualExit=stages['compile']['actualExit'],testsExecuted=0)));sys.exit(stages['compile']['actualExit'])
producerGitArtifact=None;verifierGitArtifact=None
if phase=='post':
 originalSource=sys.argv[2];producerHash=hashlib.sha256(subprocess.check_output(['git','show',originalSource+':'+driver])).hexdigest();inputs[driver]=producerHash;verifierHead=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert hashlib.sha256(subprocess.check_output(['git','show',verifierHead+':'+driver])).hexdigest()==sha(__file__)
 producerGitArtifact=dict(source=originalSource,path=driver,sha256=producerHash);verifierGitArtifact=dict(source=verifierHead,path=driver,sha256=sha(__file__))
pm=load(pre/'manifest.json');assert pm['actualExit']==0 and pm['inputHashes']==inputs and pm['dependencies']==deps
for n,h in pm['classes'].items():assert sha(pre/'classes'/n)==h
if phase=='static':
 assert not sta.exists();sta.mkdir();c.SLOT=sta;static=tc/'static-gates-20261015';rules=r/'tools/quality/static';pmd=[static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))];listing=sta/'sources.txt';listing.write_text(''.join(str(r/n)+'\n' for n in [main,*tests]));stages={}
 stages['pmd']=c.step('pmd',[str(jdk/'java'),'-cp',':'.join(map(str,pmd)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--aux-classpath',cp,'--no-cache','--format','xml','--report-file',str(sta/'pmd.xml')],r)
 stages['checkstyle']=c.step('checkstyle',[str(jdk/'java'),'-jar',str(static/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(sta/'checkstyle.xml'),'@'+str(listing)],r)
 sbpath=runs/'pg20992-outbox-required-six-static-reactor-v1/manifest.safe.json';assert sha(sbpath)=='2d3130234ce662ebf2b0bb1f57e74c123ec68e7a307feb10844231bd9822a20a';sbref=load(sbpath);assert sbref['actualExit']==0 and sbref['normalCompileManifestSha256']==sha(normal);reports={}
 for name,tag in [('pmd','violation'),('checkstyle','error')]:
  tree=E.parse(sta/(name+'.xml')).getroot();items=[dict(x.attrib,message=' '.join(''.join(x.itertext()).split())[:600]) for x in tree.iter() if x.tag.rsplit('}',1)[-1]==tag];errors=[dict(x.attrib) for x in tree.iter() if name=='pmd' and x.tag.rsplit('}',1)[-1] in ['error','configerror']];reports[name]=dict(path=str(sta/(name+'.xml')),sha256=sha(sta/(name+'.xml')),items=items,processingErrors=errors)
 sb=Path(sbref['reports']['web']['path']);reports['spotbugs']=dict(path=str(sb),sha256=sha(sb),bugs=[dict(x.attrib) for x in E.parse(sb).getroot().findall('.//BugInstance')],errors=[dict(x.attrib) for x in E.parse(sb).getroot().findall('.//Error')],missing=[x.text for x in E.parse(sb).getroot().findall('.//MissingClass')]);assert reports['spotbugs']['sha256']==sbref['reports']['web']['sha256'];write(sta/'manifest.json',dict(inputHashes=inputs,stages=stages,reports=reports,spotbugsReusedOnlyForUnchangedNormalWeb=dict(path=str(sbpath),sha256=sha(sbpath)),driverSha256=sha(__file__),normalManifestSha256=sha(normal),testsExecuted=0));print(json.dumps(dict(stages={k:v['actualExit'] for k,v in stages.items()},pmd=len(reports['pmd']['items']),checkstyle=len(reports['checkstyle']['items']),spotbugs=len(reports['spotbugs']['bugs']))));sys.exit(0)
source=sys.argv[2];assert re.fullmatch('[0-9a-f]{40}',source)
for n,h in inputs.items():assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+n])).hexdigest()==h
session='PG21290-CSRF-FILTER-FACTORY8';agent=tc/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar';cli=tc/'org.jacoco.cli-0.8.15-nodeps.jar'
if phase=='run':
 assert not unit.exists();unit.mkdir();c.SLOT=unit;(unit/'tmp').mkdir();(unit/'component').mkdir();cmd=[str(jdk/'java'),'-Djava.io.tmpdir='+str(unit/'tmp'),'-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo','-javaagent:'+str(agent)+'=destfile='+str(unit/'jacoco.exec')+',sessionid='+session+',append=false','-Xlog:class+init=info:file='+str(unit/'class-init.log'),'-jar',str(console),'execute','--disable-banner','--class-path',str(pre/'classes')+':'+':'.join(deps),'--reports-dir',str(unit/'xml'),'--fail-if-no-tests','--details','summary']
 for name in selected:cmd.extend(['--select-class',name])
 begin=dict(source=source,normalSource=nm['source'],normalManifestSha256=sha(normal),inputHashes=inputs,dependencies=deps,consoleSha256=sha(console),driverSha256=sha(__file__),compileManifestSha256=sha(pre/'manifest.json'),selected=selected,existingMethodsSourceRequalification=0,newMethods=8,expectedTests=8,realBaselineAccess=False,realChrExecution=False,session=session,startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat());write(unit/'begin.json',begin);stages={'unit':c.step('unit',cmd,r,timeout=180)};physical={}
 with zipfile.ZipFile(nm['jars']['web']['path']) as z:
  names=[n for n in z.namelist() if n in [pkg+'WebCsrfFilterFactory.class']];assert len(names)==1
  for name in names:
   p=unit/'component'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(name));physical[name[:-6]]=sha(p)
 for label,args in [('coverage',['report',str(unit/'jacoco.exec'),'--classfiles',str(unit/'component'),'--sourcefiles',str(r/'src/schubert-nk-web/src/main/java'),'--xml',str(unit/'coverage.xml')]),('classinfo',['classinfo',str(unit/'component')]),('execinfo',['execinfo',str(unit/'jacoco.exec')])]:stages[label]=c.step(label,[str(jdk/'java'),'-jar',str(cli),*args],r)
 cases=[]
 for p in (unit/'xml').glob('TEST-*.xml'):
  for t in E.parse(p).getroot().findall('testcase'):cases.append(dict(classname=t.get('classname'),name=t.get('name'),failure=bool(t.findall('failure')),error=bool(t.findall('error')),skipped=bool(t.findall('skipped'))))
 value=dict(actualExit=stages['unit']['actualExit'],begin=begin,stages=stages,cases=cases,tests=len(cases),failures=sum(x['failure'] for x in cases),errors=sum(x['error'] for x in cases),skipped=sum(x['skipped'] for x in cases),physical=physical,formalUpdated=False);write(unit/'manifest.json',value);print(json.dumps({k:value[k] for k in ['actualExit','tests','failures','errors','skipped']}));sys.exit(value['actualExit'])
assert phase=='post'
raise SystemExit('Post requires original filter factory terminal, no confirmation replay')
