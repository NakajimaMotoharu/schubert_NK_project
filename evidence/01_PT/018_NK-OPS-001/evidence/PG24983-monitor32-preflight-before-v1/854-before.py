from pathlib import Path
import json,hashlib,subprocess,re,datetime
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';I=B/'input';E=B/'evidence';RUN=R.parent/'pgpt-runs/PG379';TC=R.parent/'toolchain';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_bytes());write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
before=load(E/'PG24978-monitor-alert-metric-owner-before-v1/manifest.json');app=[]
for row in before['sources']:
 old=subprocess.check_output(['git','show',row['gitBlobObjectIdSHA1']],text=True);assert hashlib.sha256(old.encode()).hexdigest()==row['sha256'];cur=(R/row['path']).read_text();expected=old
 if Path(row['path']).stem=='AlertLifecycleTest':
  start=expected.index('    try (var executor = Executors.newFixedThreadPool(4)) {');end=expected.index('\n  @Test\n  void alert010',start);chunk=expected[start:end];inner=chunk.split('      try {\n',1)[1];inner=inner[:inner.rindex('    }\n  }\n')];replacement='    var executor = Executors.newFixedThreadPool(4);\n    try {\n'+'\n'.join(line[2:] if line.startswith('  ') else line for line in inner.splitlines())+'\n  }\n';expected=expected[:start]+replacement+expected[end:]
  a='''      try (var executor = Executors.newFixedThreadPool(8)) {
        for (var result : executor.invokeAll(tasks, 10, TimeUnit.SECONDS))
          assertSame(first, result.get());
      }''';b='''      var executor = Executors.newFixedThreadPool(8);
      try {
        for (var result : executor.invokeAll(tasks, 10, TimeUnit.SECONDS))
          assertSame(first, result.get());
      } finally {
        executor.shutdownNow();
        assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
      }''';assert expected.count(a)==1;expected=expected.replace(a,b)
 elif Path(row['path']).stem=='MetricContractTest':assert expected.count('executor.invokeAll(tasks)')==1;expected=expected.replace('executor.invokeAll(tasks)','executor.invokeAll(tasks, 10, TimeUnit.SECONDS)')
 # Scoped whitespace comparison paired with an independent exact literal inventory; no Java parser or new fixture.
 assert re.sub(r'\s+','',expected)==re.sub(r'\s+','',cur);assert re.findall(r'"(?:\\.|[^"\\])*"',expected)==re.findall(r'"(?:\\.|[^"\\])*"',cur)
 assert cur.count('@Test')==row['cases'];assert 'try (var executor' not in cur and 'executor.invokeAll(tasks)' not in cur
 app.append(dict(path=row['path'],originalSha256=row['sha256'],currentSha256=sha(R/row['path']),originalWholeBodiesExactlyRestored=True,originalCases=row['cases']))
prepPath=E/'PG24980-monitor-alert-metric-owner-prepare-v1/manifest.json';prep=load(prepPath);assert prep['actualExit']==0 and prep['reports']['pmd']['rawFindings']==16 and prep['reports']['checkstyle']['rawFindings']==0
classifications=[]
allowed={('AlertLifecycleTest','alert009ConcurrentSameTickCountsAndPrivateMonitor'),('AlertLifecycleTest','protectedAlert002ConcurrentNormalSamplesCannotRetireOrChangeProtectedEvent'),('MetricContractTest','metric006ConcurrentCallersObserveOnlyOriginalCatalog')}
for n in prep['reports']['pmd']['findings']:
 assert (n['class'],n['method']) in allowed and n['rule'] in ['DoNotUseThreads','CloseResource','AvoidSynchronizedStatement']
 line=int(n['beginline']);path=next(r['path'] for r in app if Path(r['path']).stem==n['class']);src=(R/path).read_text().splitlines();assert 0<line<=len(src)
 reason={'DoNotUseThreads':'Standalone JUnit own finite worker; not a web runtime thread. Timed invokeAll, terminal Future and finally shutdownNow/await10 reviewed.', 'CloseResource':'Executor lifetime is one explicit finite finally, avoiding unbounded ExecutorService.close; shutdownNow plus await10 assertion. Failure remains test failure.', 'AvoidSynchronizedStatement':'Intentional negative monitor coupling test holds public owner monitor while private internal lock allows all64 workers to finish; removing it would lose the oracle.'}[n['rule']]
 if n['rule']=='AvoidSynchronizedStatement':assert 'synchronized (owner)' in src[line-1]
 classifications.append(dict(test=n['class'],method=n['method'],line=line,rule=n['rule'],applicable=False,basis=reason))
for row in app:assert row['currentSha256']==prep['testSourceHashes'][row['path']]
O=E/'PG24982-monitor-alert-metric-source-static-v1';assert not O.exists();O.mkdir();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),sourceContinuity=app,originalWholeCases=32,rawFindings=16,applicableViolations=0,checkstyleFindings=0,processingErrors=0,suppressionAdded=False,outerExecutorTwrCountAfterFix=0,finiteInvokeAllSitesCorrected=1,finiteOwnerSitesCorrected=2,staticManifest=dict(path=str(prepPath.relative_to(R)),sha256=sha(prepPath)),classifications=classifications,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None);write(O/'manifest.json',v)
# Derive current canonical noarg Console runner by exact scoped replacements.
runner=(R/'tools/quality/pg24962_monitor_window_mode_whole_twenty_three_pt.py').read_text()
runner=runner.replace('Original monitor Window8, Mode7, Retention8','Original Alert12, Metric6, Batch5, Generated7, Continuity2').replace('pg24962-monitor-window-mode-original-whole23-v1','pg24986-monitor-alert-metric-original-whole32-v1').replace('PG24962-monitor-window-mode-original-whole23-v1','PG24986-monitor-alert-metric-original-whole32-v1').replace('PG24960-monitor-window-mode-current-console-preflight-v1','PG24984-monitor-alert-metric-current-console-preflight-v1').replace("len(pf['targetClassNames'])==5","len(pf['targetClassNames'])==11")
old="['dev.codex.schubert.nk.batch.monitoring.ContinuousConditionWindowTest','dev.codex.schubert.nk.batch.monitoring.MonitoringModePolicyTest','dev.codex.schubert.nk.batch.monitoring.MonitoringRetentionConfigurationTest']"
selected=['dev.codex.schubert.nk.batch.monitoring.'+Path(r['path']).stem for r in before['sources']];assert old in runner;runner=runner.replace(old,repr(selected)).replace('PG24962-MONITOR-WINDOW-MODE-ORIGINAL-WHOLE23','PG24986-MONITOR-ALERT-METRIC-ORIGINAL-WHOLE32').replace('expectedTests=23','expectedTests=32').replace('originalTwentyThreeWhole=True','originalThirtyTwoWhole=True')
needle="S.mkdir();(S/'classes').mkdir();(S/'component').mkdir();(S/'tmp').mkdir();stage.SLOT=S";assert needle in runner;runner=runner.replace(needle,needle+"\nresource=R/pf['publicResource']['path'];assert sha(resource)==pf['publicResource']['sha256'];(S/'classes/monitoring').mkdir();(S/'classes/monitoring/metric-catalog.tsv').write_bytes(resource.read_bytes());assert sha(S/'classes/monitoring/metric-catalog.tsv')==sha(resource)")
entry=R/'tools/quality/pg24986_monitor_alert_metric_whole_thirty_two_pt.py';assert not entry.exists();entry.write_text(runner)
normal=RUN/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';nm=load(normal)
oldpf=load(E/'PG24960-monitor-window-mode-current-console-preflight-v1/manifest.json');metaPath=R/oldpf['metadataInventory']['path'];assert sha(metaPath)==oldpf['metadataInventory']['sha256'];meta=load(metaPath)
mainroot='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/'
targetStems=['AlertLifecycle','MetricContract','BatchMetricContract'];helperStems=['MonitoringModePolicy','ContinuousConditionWindow','ObservationContext','TimedFilesystemMonitor','TimedJvmHeapMonitor','TimedDbPoolMonitor','TimedSyncLatencyMonitor','TransferHealthMonitor','TransferMetricRecorder'];targets={r['physicalKey'].split(':',1)[1]:r['classSha256'] for r in meta if r['sourcePath'] in [mainroot+s+'.java' for s in targetStems]};assert len(targets)==11
inputHashes={r['path']:sha(R/r['path']) for r in before['sources']}
for stem in targetStems+helperStems:
 p=mainroot+stem+'.java';assert sha(R/p)==nm['begin']['inputHashes'][p];inputHashes[p]=sha(R/p)
resource='src/schubert-nk-batch/src/test/resources/monitoring/metric-catalog.tsv';assert sha(R/resource)=='1447faabc6f056120561e4356dd75696ace4df613b6379246af29f9837fc43dc';inputHashes[resource]=sha(R/resource);assert len((R/resource).read_bytes().splitlines())==26
prefix='dev/codex/schubert/nk/batch/monitoring/';allow=[n.removesuffix('.class') for n in targets]+[prefix+s for s in ['MonitoringModePolicy','MonitoringModePolicy$DetailService','ContinuousConditionWindow$State','ObservationContext','TimedFilesystemMonitor$Evaluation','TimedJvmHeapMonitor$Evaluation','TimedDbPoolMonitor$Evaluation','TimedSyncLatencyMonitor$Evaluation','TransferHealthMonitor$Evaluation','TransferMetricRecorder$Counts','TransferMetricRecorder$Suffix']]
for path,digest in oldpf['dependencies'].items():assert sha(Path(path))==digest
pf=dict(oldpf);pf.update(atJST=datetime.datetime.now().astimezone().isoformat(),entrypointPath=str(entry.relative_to(R)),entrypointSha256=sha(entry),inputHashes=inputHashes,testPaths=[r['path'] for r in before['sources']],targetClassHashes=targets,targetClassNames=sorted(targets),allowedObservedMain=allow,sourcePrograms=3,targetPhysicalClasses=11,selected=selected,expectedCaseCounts={n:r['cases'] for n,r in zip(selected,before['sources'])},expectedTests=32,sourceContinuityAndStatic=dict(path=str((O/'manifest.json').relative_to(R)),sha256=sha(O/'manifest.json')),whole3OriginalRetained=False,whole5OriginalRetained=True,publicResource=dict(path=resource,sha256=sha(R/resource)))
for path,ref in pf['approvedDesigns'].items():assert hashlib.sha256(subprocess.check_output(['git','show',ref['approvedMain']+':'+path])).hexdigest()==ref['sha256']
P=E/'PG24984-monitor-alert-metric-current-console-preflight-v1';assert not P.exists();P.mkdir();write(P/'manifest.json',pf);print(json.dumps(dict(actualExit=0,sourceContinuity=5,staticRaw=16,sourcePrograms=3,targetClasses=11,resourcePinned=True,entry=str(entry),preflightSha256=sha(P/'manifest.json'))))
