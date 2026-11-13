"""Whole ordinary Test7 + meaningful fatal1; existing Child fixture unchanged except literal origin."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';I=B/'input';TC=R.parent/'toolchain';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));wr=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');start=ld(I/'2198_mpol_feature_whole8_normal_start.json');state=ld(R.parent/'PMO/pgpt-completion-stage-20261102/checkpoint.json');assert state['ordinaryActiveGroup']==start['groupId'] and state['ordinaryGroupNotYetClosed'];t=R/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/MaintenanceUnitStopPolicyTest.java';f=t.parent/'InspectorUnitProbeFixture.java';s=t.parent/'InspectorUnitSnapshotTest.java';old=t.read_text();oldf=f.read_text();snapshotSha=sha(s);assert old==subprocess.check_output(['git','show',start['source']+':'+str(t.relative_to(R))],text=True) and oldf==subprocess.check_output(['git','show',start['source']+':'+str(f.relative_to(R))],text=True);assert len(re.findall(r'@Test\b',old))==7
insert='  private enum NativePoint {\n    START,\n    WAIT\n  }\n\n';addition='''  /** MPOL008/BUG2782: declared query faults never become ordinary sanitized success/failure. */
  @Test
  void mpol008NativePortFatalGraphsPreserveIdentityAndEveryOwnedPostcondition() {
    for (var point : NativePoint.values()) {
      for (int graph = 0; graph < 3; graph++) {
        var marker = new AssertionError("public fatal query marker");
        var failure = new StopGateException(StopGateFailure.TIMEOUT);
        switch (graph) {
          case 0 -> failure.initCause(marker);
          case 1 -> failure.addSuppressed(marker);
          default -> {
            var cycle = new IllegalStateException("public cyclic query fault");
            failure.initCause(cycle);
            cycle.initCause(failure);
            cycle.addSuppressed(marker);
          }
        }
        var child = new InspectorUnitProbeFixture.Child(policy("caddy.service"));
        child.hook =
            (name, count) -> {
              if (point == NativePoint.WAIT && name.equals("wait")) throw failure;
            };
        var starts = new AtomicInteger();
        var reader =
            new InspectorUnitProbe.NativeReader(
                command -> {
                  assertEquals(
                      List.of(
                          "/usr/bin/systemctl",
                          "--system",
                          "--no-pager",
                          "--no-ask-password",
                          "show",
                          "--property=Id,LoadState,KillMode,SendSIGKILL",
                          "caddy.service"),
                      command);
                  starts.incrementAndGet();
                  if (point == NativePoint.START) throw failure;
                  return child;
                });
        assertSame(
            marker,
            assertThrows(
                AssertionError.class,
                () ->
                    new MaintenanceUnitStopPolicy(new MaintenanceUnitStopPolicy.NativeSource(reader))
                        .requireSafe(MaintenanceUnit.CADDY)));
        assertEquals(1, starts.get());
        assertEquals(0, marker.getSuppressed().length);
        if (point == NativePoint.START) {
          assertEquals(List.of(), child.order);
          assertEquals(0, child.destroyed);
          assertEquals(0, child.output.closed);
          assertEquals(0, child.input.closed);
          assertEquals(0, child.error.closed);
        } else {
          child.allClosed();
          child.wiped();
          assertEquals(1, child.destroyed);
          assertEquals(
              List.of(
                  "get.stdout",
                  "get.stdin",
                  "get.stderr",
                  "stdin.close",
                  "stderr.close",
                  "wait",
                  "stdout.close",
                  "alive",
                  "destroy"),
              child.order);
        }
      }
    }
  }

''';anchor='  private static byte[] policy(String name) {';assert old.count(anchor)==1;new=old.replace(anchor,insert+addition+anchor);new=new.replace('import java.util.concurrent.Executors;\n','import java.util.concurrent.Executors;\nimport java.util.concurrent.TimeUnit;\nimport java.util.concurrent.atomic.AtomicInteger;\n');a='    try (var pool = Executors.newFixedThreadPool(8)) {\n';b='    var pool = Executors.newFixedThreadPool(8);\n    try {\n';assert new.count(a)==1;new=new.replace(a,b);a2='      for (var result : pool.invokeAll(tasks)) assertTrue(result.get());\n';b2='      for (var result : pool.invokeAll(tasks, 5, TimeUnit.SECONDS))\n        assertTrue(result.get(5, TimeUnit.SECONDS));\n';assert new.count(a2)==1;new=new.replace(a2,b2);a3='    }\n    // This reader only requests systemctl show.';b3='    } finally {\n      pool.shutdownNow();\n      assertTrue(pool.awaitTermination(5, TimeUnit.SECONDS));\n    }\n    // This reader only requests systemctl show.';assert new.count(a3)==1;new=new.replace(a3,b3);t.write_text(new)
match=re.search(r'  static final String GOLDEN =\n      ("(?:[^"\\]|\\.)*");',s.read_text());assert match;literal=match.group(1);golden=json.loads(literal);assert golden.isascii() and golden.endswith('\n');imp='import static dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshotTest.GOLDEN;\n';assert oldf.count(imp)==1;constant='  private static final String GOLDEN =\n      '+literal+';\n\n';newf=oldf.replace(imp,'').replace('final class InspectorUnitProbeFixture {\n','final class InspectorUnitProbeFixture {\n'+constant,1);f.write_text(newf)
for p in [t,f]:
 q=subprocess.run([str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(p)],capture_output=True,text=True);assert q.returncode==0
reverse=t.read_text();assert reverse.count(insert)==reverse.count(addition)==1;reverse=reverse.replace(insert,'').replace(addition,'').replace('import java.util.concurrent.TimeUnit;\n','').replace('import java.util.concurrent.atomic.AtomicInteger;\n','');assert reverse.count(b)==reverse.count(b2)==reverse.count(b3)==1;reverse=reverse.replace(b,a).replace(b2,a2).replace(b3,a3);assert reverse==old;reverse=f.read_text();assert reverse.count(constant)==1;reverse=reverse.replace(constant,'');reverse=reverse.replace('import static org.junit.jupiter.api.Assertions.assertArrayEquals;',imp+'import static org.junit.jupiter.api.Assertions.assertArrayEquals;',1);assert reverse==oldf;assert sha(s)==snapshotSha;assert len(re.findall(r'@Test\b',t.read_text()))==8
prior=ld(B/'evidence/PG28774-mpol-whole7-pure-main-source-closure-v1/manifest.json');sourcePg=ld(B/'evidence/PG28792-query-two-main-source-static-v1/manifest.json');main=list(prior['mainInputHashes']);changed=[n for n,v in prior['mainInputHashes'].items() if sha(R/n)!=v];assert set(changed)==set(sourcePg['inputHashes']) and sourcePg['originalSourceInverseExact'];O=B/'evidence/PG28804-mpol-whole8-current-source-oracle-closure-v1';assert not O.exists();O.mkdir();v=dict(schema='PGPT_UNSTARTED_PROCESS_SOURCE_V1',actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),productionCoreMain=start['source'],mainInputHashes={n:sha(R/n) for n in main},testInputHashes={str(p.relative_to(R)):sha(p) for p in [t,f]},wholeTestCount=8,newDefinitions=1,oldWhole7AllAssertionsAndBodiesInverseExact=True,oldWholeFixtureAllBodyInverseExact=True,workerLifecycle='invokeAll5s, eachFutureget5s, finallyshutdownNow-awaitTermination5s asserted. Alloriginal64tasks/8literalunits/wipe/assertions retained.',goldenLiteralSource=dict(path=str(s.relative_to(R)),sha256=snapshotSha,field='GOLDEN',valueSha256=hashlib.sha256(golden.encode('ascii')).hexdigest(),wholeTestModifiedOrReplayed=False),literalFixtureFieldExactOriginalValue=True,changedMainQualifiedBySourceOnly=ref(B/'evidence/PG28792-query-two-main-source-static-v1/manifest.json'),allOtherWholeMainSourceReviewReusedByExactHash=ref(B/'evidence/PG28774-mpol-whole7-pure-main-source-closure-v1/manifest.json'),wholeTestAndHelperReviewed=True,noActualCommandInvocation=True,defaultFactoryConstructionOnly=True,noRootOrOtherAuthority=True,forbiddenInitializedClasses=['dev/codex/schubert/nk/batch/platform/SystemctlStateSource$NativeProcess','dev/codex/schubert/nk/batch/platform/InspectorUnitSnapshot','dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle','dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Outcome'],forbiddenExecutedMethods=['InspectorUnitProbe$NativeReader.executeStreaming','InspectorUnitProbe$NativeReader.queryFailure','InspectorUnitProbe$NativeReader.lambda$executeStreaming$*'],independentNewOracle='Two literal providerpoints START/WAIT x cause/suppressed/cycle3; samefatalError identity, markerSupp0, fixed8fieldcommand expectedliteral, startcall1, noownedresourceatSTART, acquiredall3stdio closedexactly1 +destroy1 andliteral9eventorderatWAIT. Production never computesexpected.',classCacheActions=0,productClassesCompiledLoadedInitialized=0,productTestsExecuted=0,newAcceptance=0);wr(O/'manifest.json',v);print(json.dumps(dict(actualExit=0,original7AndWholeHelperInverseExact=True,newDefinitions=1,whole8=True,finiteWorker=True,originalSnapshotTestUntouched=True,ProductPT=0)))
