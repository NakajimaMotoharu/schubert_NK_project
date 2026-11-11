"""Two finite owner repairs and pure independent DTO/provider extension; all old8 inverse preserved."""
from pathlib import Path
import datetime,hashlib,json,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG26384-run-reference-manufacture-v1';assert not O.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_bytes());before=B/'evidence/PG26380-run-reference-worker-owner-before-v1';plan=load(before/'manifest.json');p=R/plan['testPath'];old=p.read_text();assert sha(p)==plan['testSha256'];assert old==(before/'original-whole-test.java.txt').read_text();s=old;changes=[]
def replace(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b,1);changes.append((a,b))
replace('import java.time.ZoneOffset;','import java.time.OffsetDateTime;')
replace('Instant.parse("2026-11-05T00:00:00.123456Z").atOffset(ZoneOffset.UTC)','OffsetDateTime.parse("2026-11-05T00:00:00.123456Z")')
replace('      try (var worker = Executors.newSingleThreadExecutor()) {','      var worker = Executors.newSingleThreadExecutor();\n      try {')
replace("""        assertEquals(true, task.get(5, TimeUnit.SECONDS));
      }
      fixture.assertClosed""","""        assertEquals(true, task.get(5, TimeUnit.SECONDS));
      } finally {
        worker.shutdownNow();
        assertTrue(worker.awaitTermination(5, TimeUnit.SECONDS));
      }
      fixture.assertClosed""")
replace('    try (var workers = Executors.newFixedThreadPool(2)) {','    var workers = Executors.newFixedThreadPool(2);\n    try {')
replace("""      assertEquals(true, second.get(5, TimeUnit.SECONDS).hasBatchHistory());
    }
    assertEquals(new UUID(0, 1), one.bindings.get(1));""","""      assertEquals(true, second.get(5, TimeUnit.SECONDS).hasBatchHistory());
    } finally {
      workers.shutdownNow();
      assertTrue(workers.awaitTermination(5, TimeUnit.SECONDS));
    }
    assertEquals(new UUID(0, 1), one.bindings.get(1));""")
replace('for (Throwable original : failures())','for (Throwable original : providerFailures())')
addition="""  // RUNPORT009-BEGIN: pure primitive projection, no database/FS fixture.
  @Test
  void literalProjectionOrAndRedactedDisplayAreIndependentOfDatabaseSetup() {
    for (int bits = 0; bits < 16; bits++) {
      boolean history = (bits & 1) != 0;
      boolean inbox = (bits & 2) != 0;
      boolean log = (bits & 4) != 0;
      boolean consistent = (bits & 8) != 0;
      if (bits == 0) {
        assertThrows(IllegalArgumentException.class,
            () -> new RunReferences(history, inbox, log, consistent));
      } else {
        var value = new RunReferences(history, inbox, log, consistent);
        assertEquals(history, value.hasBatchHistory());
        assertEquals(inbox, value.hasInboxProgress());
        assertEquals(log, value.hasLogProgress());
        assertEquals(consistent, value.identityConsistent());
        assertEquals((bits & 7) != 0, value.anyReference());
        assertEquals("RunReferences[observation=<redacted>]", value.toString());
      }
    }
  }
  // RUNPORT009-END

  private static List<Throwable> providerFailures() {
    var values = new ArrayList<>(failures());
    values.add(new IllegalArgumentException("own provider argument"));
    values.add(new NullPointerException("own provider null"));
    return values;
  }

"""
needle='  private static List<Throwable> failures() {';assert s.count(needle)==1;s=s.replace(needle,addition+needle,1);inverse=s.replace(addition,'',1)
for a,b in reversed(changes):assert inverse.count(b)==1;inverse=inverse.replace(b,a,1)
assert inverse==old
cmd=[str(R.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(R.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'-']
def fmt(txt):
 v=subprocess.run(cmd,input=txt.encode(),capture_output=True,timeout=30);assert v.returncode==0;return v.stdout
fixed=fmt(s);assert fmt(fixed.decode())==fixed
# Reverse exact semantic edits before formatting, and verify old entire fixture canonical format.
assert fmt(inverse)==fmt(old);helper=R/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/BatchRunBoundaryTest.java';helperHash=sha(helper);O.mkdir();p.write_bytes(fixed);assert sha(helper)==helperHash
(O/'changes.json').write_text(json.dumps([dict(old=a,new=b) for a,b in changes],indent=2)+'\n');(O/'addition.java.txt').write_text(addition)
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),beforeManifestSha256=sha(before/'manifest.json'),originalTestSha256=plan['testSha256'],testSha256=sha(p),testPath=plan['testPath'],newUniqueDefinitions=1,expectedWholeRunCases=11,existingPortEightPreservedByExactInverse=True,oldPriorityThreeByThreeAndOriginalFault48Preserved=True,newProviderNegativeInputs=32,newDtoProjectionInputs=16,helperTwoTestSourceUnchangedSha256=helperHash,finiteFinallyOwners=2,ownerJoinDeadlineSeconds=5,independentUtcLiteral=True,formatIdempotent=True,MainChanged=False,productTestsExecuted=0,toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,oldEightInverseExact=True,newDefinitions=1,newProviderNegatives=32,expectedTests=11,manifestSha256=sha(O/'manifest.json'))))
