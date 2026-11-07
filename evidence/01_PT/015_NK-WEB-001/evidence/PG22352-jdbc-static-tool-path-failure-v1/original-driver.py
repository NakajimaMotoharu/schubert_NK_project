"""Whole technical JDBC store15: Java SQL proxies, opaque data, no database or cryptography."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as E
import zipfile
import pg9666_pagination_static as c
R=Path.cwd();RUNS=R.parent/'pgpt-runs/PG379';TC=R.parent/'toolchain';JDK=TC/'jdk-25.0.4/bin';phase=sys.argv[1];assert phase in ['prepare','static','run']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
normal=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';nm=load(normal);assert nm['actualExit']==0 and nm['source']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
for name,h in nm['begin']['inputHashes'].items():assert sha(R/name)==h
j=TC/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar';deps={nm['jars']['web']['path']:nm['jars']['web']['sha256'],str(j):sha(j)}
for name,h in deps.items():assert sha(name)==h
console=TC/'junit-platform-console-standalone-1.13.4.jar';assert sha(console)=='3fdfc37e29744a9a67dd5365e81467e26fbde0b7aa204e6f8bbe79eeaa7ae892'
base='src/schubert-nk-web/';pkg='dev/codex/schubert/nk/web/session/';tests=[base+'src/test/java/'+pkg+'JdbcSessionStorePortTest.java'];main=base+'src/main/java/'+pkg+'JdbcWebSessionStore.java';driver=str(Path(__file__).resolve().relative_to(R));inputs={n:sha(R/n) for n in [*tests,main,driver]};pre=RUNS/'pg22346-session-jdbc-store-fifteen-compile-v1';sta=RUNS/'pg22348-session-jdbc-store-fifteen-static-v1';unit=RUNS/'pg22350-session-jdbc-store-fifteen-unit-v1';cp=':'.join([*deps,str(console)])
if phase=='prepare':
 assert not pre.exists();pre.mkdir();(pre/'classes').mkdir();c.SLOT=pre;stage=c.step('javac',[str(JDK/'javac'),'-encoding','UTF-8','-Xlint:all,-requires-automatic,-requires-transitive-automatic','-Werror','-cp',cp,'-d',str(pre/'classes'),*tests],R);write(pre/'manifest.json',dict(actualExit=stage['actualExit'],inputHashes=inputs,dependencies=deps,consoleSha256=sha(console),stage=stage,productTestsExecuted=0));print(json.dumps(dict(actualExit=stage['actualExit'],testsExecuted=0)));sys.exit(stage['actualExit'])
prepared=load(pre/'manifest.json');assert prepared['actualExit']==0 and prepared['inputHashes']==inputs
if phase=='static':
 assert not sta.exists();sta.mkdir();c.SLOT=sta;static=TC/'static-analysis';rules=R/'src/quality';pmd=sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'));listing=sta/'sources.txt';listing.write_text(''.join(str(R/n)+'\n' for n in [main,*tests]));stages={}
 stages['pmd']=c.step('pmd',[str(JDK/'java'),'-cp',':'.join(map(str,pmd)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--aux-classpath',cp,'--no-cache','--format','xml','--report-file',str(sta/'pmd.xml')],R)
 stages['checkstyle']=c.step('checkstyle',[str(JDK/'java'),'-jar',str(static/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(sta/'checkstyle.xml'),'@'+str(listing)],R)
 sbpath=RUNS/'pg22086-api-stop-state-six-static-reactor-v1/manifest.safe.json';assert sha(sbpath)=='0580a14592d3fc00820183034c584208e45b002802d2e3e173b5f752c7cf19f2';sb=load(sbpath);assert sb['actualExit']==0 and sb['normalCompileManifestSha256']==sha(normal);reports={}
 for name,tag in [('pmd','violation'),('checkstyle','error')]:
  tree=E.parse(sta/(name+'.xml')).getroot();items=[dict(x.attrib,message=' '.join(''.join(x.itertext()).split())[:600]) for x in tree.iter() if x.tag.rsplit('}',1)[-1]==tag];errors=[dict(x.attrib) for x in tree.iter() if name=='pmd' and x.tag.rsplit('}',1)[-1] in ['error','configerror']];reports[name]=dict(path=str(sta/(name+'.xml')),sha256=sha(sta/(name+'.xml')),items=items,processingErrors=errors)
 sbfile=Path(sb['reports']['web']['path']);assert sha(sbfile)==sb['reports']['web']['sha256'];reports['spotbugs']=dict(path=str(sbfile),sha256=sha(sbfile),bugs=[dict(x.attrib) for x in E.parse(sbfile).getroot().findall('.//BugInstance')],errors=[dict(x.attrib) for x in E.parse(sbfile).getroot().findall('.//Error')]);write(sta/'manifest.json',dict(inputHashes=inputs,stages=stages,reports=reports,spotbugsReusedOnlyForUnchangedNormalWeb=dict(path=str(sbpath),sha256=sha(sbpath)),normalManifestSha256=sha(normal),testsExecuted=0));print(json.dumps(dict(stages={k:v['actualExit'] for k,v in stages.items()},pmd=len(reports['pmd']['items']),checkstyle=len(reports['checkstyle']['items']),spotbugs=len(reports['spotbugs']['bugs']))));sys.exit(0)
source=sys.argv[2];assert re.fullmatch('[0-9a-f]{40}',source)
for name,h in inputs.items():assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+name],cwd=R)).hexdigest()==h
family={pkg+'JdbcWebSessionStore',pkg+'JdbcWebSessionStore$InvalidStoredRow'}
with zipfile.ZipFile(nm['jars']['web']['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==pkg+'JdbcWebSessionStore.class' or n.startswith(pkg+'JdbcWebSessionStore$')}==family
assert not unit.exists();unit.mkdir();(unit/'tmp').mkdir();(unit/'component').mkdir();c.SLOT=unit;session='PG22350-JDBC-SESSION-STORE15';agent=TC/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar';cli=TC/'org.jacoco.cli-0.8.15-nodeps.jar'
cmd=[str(JDK/'java'),'-Djava.io.tmpdir='+str(unit/'tmp'),'-Dfile.encoding=UTF-8','-Djunit.jupiter.extensions.autodetection.enabled=false','-Djunit.jupiter.execution.parallel.enabled=false','-Duser.timezone=Asia/Tokyo','-javaagent:'+str(agent)+'=destfile='+str(unit/'jacoco.exec')+',sessionid='+session+',append=false','-Xlog:class+init=info:file='+str(unit/'class-init.log'),'-jar',str(console),'execute','--disable-banner','--class-path',str(pre/'classes')+':'+':'.join(deps),'--reports-dir',str(unit/'xml'),'--fail-if-no-tests','--details','summary','--select-class','dev.codex.schubert.nk.web.session.JdbcSessionStorePortTest']
begin=dict(source=source,normalSource=nm['source'],normalManifestSha256=sha(normal),inputHashes=inputs,dependencies=deps,consoleSha256=sha(console),compileManifestSha256=sha(pre/'manifest.json'),selected=['dev.codex.schubert.nk.web.session.JdbcSessionStorePortTest'],expectedTests=15,newMethods=15,session=session,startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),realDbOrCryptoOrAuthOrRootNative=False);write(unit/'begin.json',begin);stages={'unit':c.step('unit',cmd,R,timeout=180)};physical={}
with zipfile.ZipFile(nm['jars']['web']['path']) as jar:
 for name in family:
  p=unit/'component'/(name+'.class');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(jar.read(name+'.class'));physical[name]=sha(p)
for name,args in [('coverage',['report',str(unit/'jacoco.exec'),'--classfiles',str(unit/'component'),'--sourcefiles',str(R/'src/schubert-nk-web/src/main/java'),'--xml',str(unit/'coverage.xml')]),('classinfo',['classinfo',str(unit/'component')]),('execinfo',['execinfo',str(unit/'jacoco.exec')])]:stages[name]=c.step(name,[str(JDK/'java'),'-jar',str(cli),*args],R)
cases=[]
for p in (unit/'xml').glob('TEST-*.xml'):
 for t in E.parse(p).getroot().findall('testcase'):cases.append(dict(classname=t.get('classname'),name=t.get('name'),failure=bool(t.findall('failure')),error=bool(t.findall('error')),skipped=bool(t.findall('skipped'))))
value=dict(actualExit=stages['unit']['actualExit'],begin=begin,stages=stages,cases=cases,tests=len(cases),failures=sum(x['failure'] for x in cases),errors=sum(x['error'] for x in cases),skipped=sum(x['skipped'] for x in cases),physical=physical,formalUpdated=False);write(unit/'manifest.json',value);print(json.dumps({k:value[k] for k in ['actualExit','tests','failures','errors','skipped']}));sys.exit(value['actualExit'])
