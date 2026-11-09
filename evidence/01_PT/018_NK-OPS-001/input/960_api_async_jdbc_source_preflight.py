"""Original API Async repository and collector whole16 with exact finite-owner and equivalent fixture-style changes."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';E=B/'evidence';RUNS=R.parent/'pgpt-runs/PG379';TC=R.parent/'toolchain'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_bytes());write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
before=load(E/'PG25402-api-async-jdbc-owner-before-v1/manifest.json');continuity=[];flat=lambda s:re.sub(r'\s+','',s)
for row in before['sources']:
 old=subprocess.check_output(['git','show',row['gitBlobObjectIdSHA1']],text=True);assert hashlib.sha256(old.encode()).hexdigest()==row['sha256'];cur=(R/row['path']).read_text();repository=Path(row['path']).stem=='AsyncJobCountRepositoryTest';inverse=flat(cur.replace('import java.util.concurrent.TimeUnit;\n','') if repository else cur)
 if repository:
  new='varpool=Executors.newFixedThreadPool(8);try{';original='try(varpool=Executors.newFixedThreadPool(8)){';suffix='}finally{pool.shutdownNow();assertTrue(pool.awaitTermination(10,TimeUnit.SECONDS));}';assert inverse.count(new)==inverse.count(suffix)==1;inverse=inverse.replace(new,original).replace(suffix,'}').replace('pool.invokeAll(tasks,10,TimeUnit.SECONDS)','pool.invokeAll(tasks)');count=1
  for name,value in [('READ_ONLY_TRANSACTION_VARIANT',1),('ISOLATION_TRANSACTION_VARIANT',2)]:
   declaration='privatestaticfinalint'+name+'='+str(value)+';';assert inverse.count(declaration)==1;inverse=inverse.replace(declaration,'');assert inverse.count('variant=='+name)==1;inverse=inverse.replace('variant=='+name,'variant=='+str(value))
  assert inverse.count('cursor++;returncursor<rows.size();')==1;inverse=inverse.replace('cursor++;returncursor<rows.size();','return++cursor<rows.size();')
 else:
  for workers,other in [(2,''),(8,'varotherRegistry=newRegistry();')]:
   new='try(varregistry=newRegistry()'+(';' + other.removesuffix(';') if other else '')+'){varpool=Executors.newFixedThreadPool('+str(workers)+');try{';original='try(varregistry=newRegistry();'+other+'varpool=Executors.newFixedThreadPool('+str(workers)+')){';assert inverse.count(new)==1;inverse=inverse.replace(new,original)
  suffix='}finally{pool.shutdownNow();assertTrue(pool.awaitTermination(10,TimeUnit.SECONDS));}';assert inverse.count(suffix)==2;inverse=inverse.replace(suffix,'').replace('pool.invokeAll(tasks,10,TimeUnit.SECONDS)','pool.invokeAll(tasks)');count=2
  assert cur.count('.get(5, TimeUnit.SECONDS)')==2 and cur.count('release.countDown();')==2 and 'secondEntered.await(100, TimeUnit.MILLISECONDS)' in cur
 assert inverse==flat(old) and re.findall(r'"(?:\\.|[^"\\])*"',old)==re.findall(r'"(?:\\.|[^"\\])*"',cur);assert cur.count('@Test')==8 and cur.count('.shutdownNow();')==cur.count('.awaitTermination(10, TimeUnit.SECONDS)')==count
 continuity.append(dict(path=row['path'],originalSha256=row['sha256'],currentSha256=sha(R/row['path']),originalWholeBodiesExactlyRestored=True,finiteOwnerSites=count,fixtureStyleSitesCorrected=3 if repository else 0,existingFutureGet5SitesRetained=0 if repository else 2))
prepPath=E/'PG25424-api-async-jdbc-configured-prepare-v1/manifest.json';prep=load(prepPath);assert prep['actualExit']==0 and prep['testSourceHashes']=={r['path']:r['currentSha256'] for r in continuity};findings=prep['reports']['pmd']['findings'];assert len(findings)==21 and prep['reports']['checkstyle']['rawFindings']==0;classified=[]
for n in findings:
 assert n['class'] in ['AsyncJobCountRepositoryTest','AsyncJobCountRepositoryTest.Fixture','AsyncJobMetricCollectorTest'] and n['rule'] in ['DoNotUseThreads','CloseResource','UseConcurrentHashMap','UseProperClassLoader']
 basis='Standalone JUnit owns2/8workers andfakeJDBC observations; existinglatch5/get5/100ms nonentry preserved, twoinvokeAll10/three finallyshutdownNow-await10.'
 if n['rule']=='UseConcurrentHashMap':
  assert n['class']=='AsyncJobCountRepositoryTest.Fixture' and n['variable']=='faults';basis='Each parallel task owns separate Fixture/faults HashMap. Failure maps populated synchronously before calls; no shared mutation across tasks/connection getters.'
 if n['rule']=='UseProperClassLoader':
  assert (n['class']=='AsyncJobCountRepositoryTest.Fixture' and n['method'] in ['connection','statement','result']) or (n['class']=='AsyncJobMetricCollectorTest' and n['method']=='gate');basis='Own JDKProxy uses declaring JDBC interface loader for exact visibility/type identity; no context-loader override, driver lookup or actualconnection.'
 if n['rule']=='UseConcurrentHashMap':assert n.get('method') is None
 else:assert isinstance(n.get('method'),str) and n['method']
 classified.append(dict(className=n['class'],method=n.get('method'),variable=n.get('variable'),line=int(n['beginline']),rule=n['rule'],applicable=False,basis=basis))
normal=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';nm=load(normal);assert type(nm['actualExit']) is int and nm['actualExit']==0 and nm['testsExecuted'] is False and nm['testStatus']=='NOT_RUN_COMPILE_ONLY_NOT_PASS'
pf=load(E/'PG25150-batch-recorders-current-console-preflight-v1/manifest.json');meta=load(R/pf['metadataInventory']['path']);root='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/';targetPaths={root+n+'.java' for n in ['persistence/AsyncJobCountRepository','AsyncJobMetricCollector']};rows=[r for r in meta if r['sourcePath'] in targetPaths];assert len(rows)==2 and {r['costOwner'] for r in rows}=={'WBS-P018-09'};targets={r['physicalKey'].split(':',1)[1]:r['classSha256'] for r in rows};helper='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/AsyncJobMetricRecorder.java';helperRows=[r for r in meta if r['sourcePath']==helper];assert len(helperRows)==3;inputs={r['path']:r['currentSha256'] for r in continuity}
for path in sorted(targetPaths|{helper,'pom.xml','src/schubert-nk-api/pom.xml'}):
 assert (R/path).exists() and sha(R/path)==nm['begin']['inputHashes'][path];inputs[path]=sha(R/path)
for path,digest in pf['dependencies'].copy().items():
 if path==nm['jars']['batch']['path']:del pf['dependencies'][path]
for key in ['api']:pf['dependencies'][nm['jars'][key]['path']]=nm['jars'][key]['sha256']
for path,digest in pf['dependencies'].items():assert sha(Path(path))==digest
main=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip();design='documents/300_SS/320_メッセージング/321_Artemis物理構成・JMS設定設計.md';raw=subprocess.check_output(['git','show',main+':'+design]);pf['approvedDesigns'][design]=dict(approvedMain=main,sha256=hashlib.sha256(raw).hexdigest())
for path,ref in pf['approvedDesigns'].items():assert hashlib.sha256(subprocess.check_output(['git','show',ref['approvedMain']+':'+path])).hexdigest()==ref['sha256']
app=E/'PG25406-api-async-jdbc-source-static-v1';P=E/'PG25406-api-async-jdbc-current-console-preflight-v1';entry=R/'tools/quality/pg25408_api_async_jdbc_original_sixteen_pt.py';assert not app.exists() and not P.exists() and not entry.exists()
runner=(R/'tools/quality/pg25152_batch_recorders_original_twenty_four_pt.py').read_text();selected=['dev.codex.schubert.nk.api.monitoring.'+Path(r['path']).stem for r in continuity]
for old,new in [('three Batch recorders','three API supplied recorders'),('pg25152-batch-recorders-original-whole24-v1','pg25408-api-async-jdbc-original-whole16-v1'),('PG25152-batch-recorders-original-whole24-v1','PG25408-api-async-jdbc-original-whole16-v1'),('PG25150-batch-recorders-current-console-preflight-v1','PG25406-api-async-jdbc-current-console-preflight-v1'),("nm['jars']['batch']","nm['jars']['api']"),("len(pf['targetClassNames'])==5","len(pf['targetClassNames'])==2"),("['dev.codex.schubert.nk.batch.monitoring.BatchMetricRecorderTest', 'dev.codex.schubert.nk.batch.monitoring.IntegrityFailureMetricRecorderTest', 'dev.codex.schubert.nk.batch.monitoring.ProcessRestartMetricRecorderTest']",repr(selected)),('PG25152-BATCH-RECORDERS-ORIGINAL-WHOLE24','PG25408-API-ASYNC-JDBC-ORIGINAL-WHOLE16'),('expectedTests=24','expectedTests=16'),('originalTwentyFourWhole=True','originalSixteenWhole=True')]:
 assert old in runner;runner=runner.replace(old,new)
runner='"""Original API Async repository/collector whole16 using owned JDBC proxies and memory SDK."""\n'+runner.split('\n',1)[1]
formatRef=E/'PG25422-current-selected-configured-format-v1/manifest.json';assert sha(formatRef)=='486e534d9f4912c91518320edf4606d6cd34d7b718d8b29a54399f331bc3382b';fmt=load(formatRef);assert fmt['actualExit']==0 and fmt['sourceCount']==14 and fmt['sourceBytesChanged'] is False and fmt['productTestsExecuted']==0 and fmt['mavenSixModuleGateQualified'] is False
for path,digest in fmt['sourceHashes'].items():assert sha(R/path)==digest
assert '--skip-reflowing-long-strings' in prep['stages']['format']['command']
pf['configuredSelectedFormat']=dict(path=str(formatRef.relative_to(R)),sha256=sha(formatRef));pf['mavenSixModuleFormatQualified']=False
entry.write_text(runner);app.mkdir();write(app/'manifest.json',dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),sourceContinuity=continuity,originalWholeCases=16,rawFindings=21,applicableViolations=0,checkstyleFindings=0,processingErrors=0,suppressionAdded=False,outerExecutorTwrCountAfterFix=0,finiteInvokeAllSitesCorrected=2,finiteOwnerSitesCorrected=3,fixtureStyleSitesCorrected=3,oldStyleRawFindings=24,newStyleRawFindings=21,styleFindingsRemoved=3,staticManifest=dict(path=str(prepPath.relative_to(R)),sha256=sha(prepPath)),classifications=classified,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None))
pf.pop('whole3OriginalRetained',None);pf['whole2OriginalRetained']=True
pf.update(atJST=datetime.datetime.now().astimezone().isoformat(),entrypointPath=str(entry.relative_to(R)),entrypointSha256=sha(entry),inputHashes=inputs,testPaths=[r['path'] for r in continuity],targetClassHashes=targets,targetClassNames=sorted(targets),allowedObservedMain=[n.removesuffix('.class') for n in targets]+[r['physicalKey'].split(':',1)[1].removesuffix('.class') for r in helperRows],sourcePrograms=2,targetPhysicalClasses=2,selected=selected,expectedCaseCounts={n:8 for n in selected},expectedTests=16,sourceContinuityAndStatic=dict(path=str((app/'manifest.json').relative_to(R)),sha256=sha(app/'manifest.json')),helperSourcePrograms=1,helperNewQualification=False)
P.mkdir();write(P/'manifest.json',pf);print(json.dumps(dict(actualExit=0,originalWhole16=True,sourcePrograms=2,targetClasses=2,staticRaw=21,applicable=0,preflightSha256=sha(P/'manifest.json'))))
