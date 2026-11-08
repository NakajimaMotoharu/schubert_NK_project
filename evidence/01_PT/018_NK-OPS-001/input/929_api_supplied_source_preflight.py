"""Exact original API whole24 finite-owner delta, SDK memory graph and six physical target classes."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';E=B/'evidence';RUNS=R.parent/'pgpt-runs/PG379';TC=R.parent/'toolchain'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_bytes());write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
before=load(E/'PG25280-api-supplied-owner-before-v1/manifest.json');continuity=[];flat=lambda s:re.sub(r'\s+','',s)
for row in before['sources']:
 old=subprocess.check_output(['git','show',row['gitBlobObjectIdSHA1']],text=True);assert hashlib.sha256(old.encode()).hexdigest()==row['sha256'];cur=(R/row['path']).read_text();name=Path(row['path']).stem;var='executor' if name.startswith('Operation') else 'pool';arg='jobs' if name.startswith('Async') else 'tasks';inverse=flat(cur.replace('import java.util.concurrent.TimeUnit;\n',''))
 suffix='}finally{'+var+'.shutdownNow();assertTrue('+var+'.awaitTermination(10,TimeUnit.SECONDS));}'
 if name.startswith('Mq'):
  new='varpool=Executors.newFixedThreadPool(8);try{';original='try(varpool=Executors.newFixedThreadPool(8)){';tail='}'
 else:
  new='try(varregistry=newRegistry()){var'+var+'=Executors.newFixedThreadPool(8);try{';original='try(varregistry=newRegistry();var'+var+'=Executors.newFixedThreadPool(8)){';tail=''
 assert inverse.count(new)==inverse.count(suffix)==1;inverse=inverse.replace(new,original).replace(suffix,tail).replace(var+'.invokeAll('+arg+',10,TimeUnit.SECONDS)',var+'.invokeAll('+arg+')')
 assert inverse==flat(old) and re.findall(r'"(?:\\.|[^"\\])*"',old)==re.findall(r'"(?:\\.|[^"\\])*"',cur)
 assert cur.count('@Test')==8 and cur.count('.shutdownNow();')==cur.count('.awaitTermination(10, TimeUnit.SECONDS)')==1
 continuity.append(dict(path=row['path'],originalSha256=row['sha256'],currentSha256=sha(R/row['path']),originalWholeBodiesExactlyRestored=True,ownerShape='standalone' if name.startswith('Mq') else 'combined'))
prepPath=E/'PG25282-api-supplied-owner-prepare-v1/manifest.json';prep=load(prepPath);assert prep['actualExit']==0 and prep['testSourceHashes']=={r['path']:r['currentSha256'] for r in continuity};findings=prep['reports']['pmd']['findings'];assert len(findings)==17 and prep['reports']['checkstyle']['rawFindings']==0;classified=[]
for n in findings:
 assert n['class'] in [Path(r['path']).stem for r in continuity] and '007' in n['method'] and n['rule'] in ['DoNotUseThreads','CloseResource','CompareObjectsWithEquals']
 basis='Standalone JUnit-owned8workers/64tasks; invokeAll10 andsinglefinally shutdownNow/await10 before borrowedregistryTWR ends. No container-managed worker.'
 if n['rule']=='CompareObjectsWithEquals':
  assert n['class']=='AsyncJobMetricRecorderTest' and int(n['beginline'])==264;basis='Identity is the independent atomic snapshot cohort oracle: read == first || read == second. Value equals would weaken the required whole-object publication test.'
 classified.append(dict(className=n['class'],method=n['method'],variable=n.get('variable'),line=int(n['beginline']),rule=n['rule'],applicable=False,basis=basis))
normal=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';nm=load(normal);assert type(nm['actualExit']) is int and nm['actualExit']==0 and nm['testsExecuted'] is False and nm['testStatus']=='NOT_RUN_COMPILE_ONLY_NOT_PASS'
pf=load(E/'PG25150-batch-recorders-current-console-preflight-v1/manifest.json');meta=load(R/pf['metadataInventory']['path']);root='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/';targetPaths={root+n+'.java' for n in ['AsyncJobMetricRecorder','MqRedeliveryMetricRecorder','OperationMismatchMetricRecorder']};rows=[r for r in meta if r['sourcePath'] in targetPaths];assert len(rows)==6 and {r['costOwner'] for r in rows}=={'WBS-P018-09'};targets={r['physicalKey'].split(':',1)[1]:r['classSha256'] for r in rows};helper='src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/transport/BrokerTopology.java';inputs={r['path']:r['currentSha256'] for r in continuity}
for path in sorted(targetPaths|{helper,'pom.xml','src/schubert-nk-api/pom.xml','src/schubert-nk-protocol/pom.xml'}):
 assert (R/path).exists() and sha(R/path)==nm['begin']['inputHashes'][path];inputs[path]=sha(R/path)
for path,digest in pf['dependencies'].copy().items():
 if path==nm['jars']['batch']['path']:del pf['dependencies'][path]
for key in ['api','protocol']:pf['dependencies'][nm['jars'][key]['path']]=nm['jars'][key]['sha256']
for path,digest in pf['dependencies'].items():assert sha(Path(path))==digest
main=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip();design='documents/300_SS/320_メッセージング/321_Artemis物理構成・JMS設定設計.md';raw=subprocess.check_output(['git','show',main+':'+design]);pf['approvedDesigns'][design]=dict(approvedMain=main,sha256=hashlib.sha256(raw).hexdigest())
for path,ref in pf['approvedDesigns'].items():assert hashlib.sha256(subprocess.check_output(['git','show',ref['approvedMain']+':'+path])).hexdigest()==ref['sha256']
app=E/'PG25284-api-supplied-source-static-v1';P=E/'PG25284-api-supplied-current-console-preflight-v1';entry=R/'tools/quality/pg25286_api_supplied_original_twenty_four_pt.py';assert not app.exists() and not P.exists() and not entry.exists()
runner=(R/'tools/quality/pg25152_batch_recorders_original_twenty_four_pt.py').read_text();selected=['dev.codex.schubert.nk.api.monitoring.'+Path(r['path']).stem for r in continuity]
for old,new in [('three Batch recorders','three API supplied recorders'),('pg25152-batch-recorders-original-whole24-v1','pg25286-api-supplied-original-whole24-v1'),('PG25152-batch-recorders-original-whole24-v1','PG25286-api-supplied-original-whole24-v1'),('PG25150-batch-recorders-current-console-preflight-v1','PG25284-api-supplied-current-console-preflight-v1'),("nm['jars']['batch']","nm['jars']['api']"),("len(pf['targetClassNames'])==5","len(pf['targetClassNames'])==6"),("['dev.codex.schubert.nk.batch.monitoring.BatchMetricRecorderTest', 'dev.codex.schubert.nk.batch.monitoring.IntegrityFailureMetricRecorderTest', 'dev.codex.schubert.nk.batch.monitoring.ProcessRestartMetricRecorderTest']",repr(selected)),('PG25152-BATCH-RECORDERS-ORIGINAL-WHOLE24','PG25286-API-SUPPLIED-ORIGINAL-WHOLE24')]:
 assert old in runner;runner=runner.replace(old,new)
needle="api=Path(nm['jars']['api']['path']);assert sha(api)==nm['jars']['api']['sha256']";assert runner.count(needle)==1;runner=runner.replace(needle,needle+"\nprotocol=Path(nm['jars']['protocol']['path']);assert sha(protocol)==nm['jars']['protocol']['sha256']")
for old,new in [("[S/'classes',api,*vendor,annotation]","[S/'classes',api,protocol,*vendor,annotation]"),('[api,*vendor,annotation,console]','[api,protocol,*vendor,annotation,console]')]:assert runner.count(old)==1;runner=runner.replace(old,new)
entry.write_text(runner);app.mkdir();write(app/'manifest.json',dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),sourceContinuity=continuity,originalWholeCases=24,rawFindings=17,applicableViolations=0,checkstyleFindings=0,processingErrors=0,suppressionAdded=False,outerExecutorTwrCountAfterFix=0,finiteInvokeAllSitesCorrected=3,finiteOwnerSitesCorrected=3,staticManifest=dict(path=str(prepPath.relative_to(R)),sha256=sha(prepPath)),classifications=classified,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None))
pf.update(atJST=datetime.datetime.now().astimezone().isoformat(),entrypointPath=str(entry.relative_to(R)),entrypointSha256=sha(entry),inputHashes=inputs,testPaths=[r['path'] for r in continuity],targetClassHashes=targets,targetClassNames=sorted(targets),allowedObservedMain=[n.removesuffix('.class') for n in targets]+['dev/codex/schubert/nk/protocol/transport/BrokerTopology'],sourcePrograms=3,targetPhysicalClasses=6,selected=selected,expectedCaseCounts={n:8 for n in selected},expectedTests=24,sourceContinuityAndStatic=dict(path=str((app/'manifest.json').relative_to(R)),sha256=sha(app/'manifest.json')),helperSourcePrograms=1,helperNewQualification=False)
P.mkdir();write(P/'manifest.json',pf);print(json.dumps(dict(actualExit=0,originalWhole24=True,sourcePrograms=3,targetClasses=6,staticRaw=17,applicable=0,preflightSha256=sha(P/'manifest.json'))))
