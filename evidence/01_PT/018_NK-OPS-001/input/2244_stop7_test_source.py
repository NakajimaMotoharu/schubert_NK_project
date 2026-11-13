from pathlib import Path
import datetime,hashlib,json,re,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';root=R/'src/schubert-nk-web/src';t=root/'test/java/dev/codex/schubert/nk/web/bootstrap/WebRuntimeStopTest.java';old=t.read_text();assert len(re.findall(r'@Test\b',old))==6
new='''
  @Test
  void stop007KnownCatalogFatalGraphsKeepIdentityAndDoNotAdvancePhase() throws Exception {
    for (boolean lifecycle : new boolean[] {false, true}) {
      for (int graph = 0; graph < 3; graph++) {
        var marker = new LinkageError("synthetic fatal graph");
        Throwable catalog = lifecycle
            ? new org.apache.catalina.LifecycleException("synthetic lifecycle")
            : new IllegalStateException("synthetic runtime");
        if (graph == 0) catalog.initCause(marker);
        else if (graph == 1) {
          var cycle = new IllegalStateException("synthetic cycle", catalog);
          catalog.initCause(cycle);
          cycle.addSuppressed(marker);
        } else {
          var sql = new java.sql.SQLException("synthetic SQL graph");
          sql.setNextException(new java.sql.SQLException("synthetic SQL next", marker));
          catalog.initCause(sql);
        }
        var owner = new WebRuntimeStop(() -> 0);
        owner.begin();
        var calls = new ArrayList<String>();
        assertSame(marker, assertThrows(LinkageError.class,
            () -> owner.close(new WebRuntimeStop.Step[] {
              left -> {
                assertEquals(Duration.ofSeconds(30), left);
                calls.add("failed");
                if (catalog instanceof org.apache.catalina.LifecycleException failure)
                  throw failure;
                throw (RuntimeException) catalog;
              },
              left -> {
                throw new AssertionError("fatal retains later phase");
              }
            })));
        assertEquals(List.of("failed"), calls);
        assertNull(marker.getCause());
        assertEquals(0, marker.getSuppressed().length);
        owner.close(new WebRuntimeStop.Step[] {
          left -> {
            assertEquals(Duration.ofSeconds(30), left);
            calls.add("retry");
          },
          left -> {
            assertEquals(Duration.ofSeconds(30), left);
            calls.add("later");
          }
        });
        assertEquals(List.of("failed", "retry", "later"), calls);
      }
    }
  }
'''
assert old.endswith('}\n');t.write_text(old[:-2]+new+'}\n');subprocess.run([str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'-i',str(t)],check=True);nt=t.read_text();idx=nt.index('  @Test\n  void stop007');assert nt[:idx].rstrip()+'\n}\n'==old.rstrip()+'\n'
main=[root/'main/java/dev/codex/schubert/nk/web'/n for n in ['bootstrap/WebRuntimeStop.java','session/SessionStoreException.java','session/InvalidSessionRowException.java']];source='a769422d3bdb936daadccc974ccecbe7c32b3086';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p in main:assert sha(p)==hashlib.sha256(subprocess.check_output(['git','show',source+':'+str(p.relative_to(R))])).hexdigest()
O=B/'evidence/PG29046-stop7-whole-source-closure-v1';assert not O.exists();O.mkdir();(O/'manifest.json').write_text(json.dumps(dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),productionCoreMain=source,MainChanged=False,originalWhole6InverseExact=True,oldWhole6Sha256=hashlib.sha256(old.encode()).hexdigest(),mainInputHashes={str(p.relative_to(R)):sha(p) for p in main},testInputHashes={str(t.relative_to(R)):sha(t)},wholeTestCount=7,newDefinitions=1,wholeSourcesAndTestsReviewed=True,independentOracle='Original6 literal30s and signedwrap/normalphase/retry/UNKNOWN/fixednormalcatalog/IRQ-free fault; new2catalog x3 cause-cycle-SQLnext retains same Error identity, no cause/supp on Error, laterphase not called, retry originalphase and same30s then later. No Production generated expected.',dependency='Ordinary Tomcat LifecycleException data-only Throwable; JDK/sql/real sealed SessionStoreException and InvalidSessionRowException all compile/report, no actual root/native objects. SDK constructors verified PG28986; this test constructs no Connector/network/worker.',actualRootStopHttpDbJmsNativeThreadActions=0,productTestsExecuted=0,newAcceptance=0),ensure_ascii=False,indent=2)+'\n');print('Originalwhole6 byte inverse exact + newcatalogfault1; Main3 unchanged; ProductPT0')
