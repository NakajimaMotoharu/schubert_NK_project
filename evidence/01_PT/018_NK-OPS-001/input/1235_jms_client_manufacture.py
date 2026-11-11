"""Finite client Test ownership and independent failure-isolation boundary cases; preserve whole old8."""
from pathlib import Path
import datetime,hashlib,json,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG26446-jms-client-manufacture-v1';assert not O.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_bytes());before=B/'evidence/PG26442-jms-client-worker-owner-before-v1';plan=load(before/'manifest.json');p=R/plan['testPath'];old=p.read_text();assert sha(p)==plan['testSha256'] and old==(before/'original-whole-test.java.txt').read_text();s=old;changes=[]
def replace(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b,1);changes.append((a,b))
replace('import static org.junit.jupiter.api.Assertions.assertThrows;','import static org.junit.jupiter.api.Assertions.assertSame;\nimport static org.junit.jupiter.api.Assertions.assertThrows;')
replace('      try (ExecutorService executor = Executors.newFixedThreadPool(maximum)) {','      ExecutorService executor = Executors.newFixedThreadPool(maximum);\n      try {')
replace("""        } finally {
          release.countDown();
        }
      }
      assertEquals(maximum, sends.get());""","""        } finally {
          release.countDown();
        }
      } finally {
        executor.shutdownNow();
        assertTrue(executor.awaitTermination(5, TimeUnit.SECONDS));
      }
      assertEquals(maximum, sends.get());""")
replace("""    } finally {
      waiting.interrupt();
      waiting.join(2_000);
    }
  }""","""    } finally {
      waiting.interrupt();
      waiting.join(2_000);
      assertFalse(waiting.isAlive());
    }
  }""")
addition="""  // JMSCLIENT009010-BEGIN: independent provider and local ownership negatives.
  @Test
  void uncheckedSenderTypesPreserveIdentityCopyAndReusableCapacity() throws Exception {
    for (Throwable original : List.of(new IllegalArgumentException("synthetic sender argument"),
        new NullPointerException("synthetic sender null"), new AssertionError("synthetic sender error"))) {
      JmsRequestReplyClient client = client(new MutableClock(NOW), 1);
      AtomicInteger sends = new AtomicInteger();
      byte[] encoded = request();
      Throwable observed = assertThrows(original.getClass(), () -> client.exchange(
          ID_1, encoded, Duration.ofSeconds(2), (id, body) -> {
            sends.incrementAndGet();
            body[0] = 9;
            if (original instanceof RuntimeException runtime) throw runtime;
            throw (Error) original;
          }));
      assertSame(original, observed);
      assertEquals(0, encoded[0]);
      assertEquals(1, sends.get());
      assertEquals(0, client.pendingCount());
      assertArrayEquals(new byte[] {4, 5, 6}, client.exchange(ID_1, request(), Duration.ofSeconds(2),
          (id, body) -> {
            sends.incrementAndGet();
            assertTrue(client.onReply(id, new byte[] {4, 5, 6}));
          }));
      assertEquals(2, sends.get());
      assertEquals(0, client.pendingCount());
    }
  }

  @Test
  void duplicateAndClockOverflowDoNotSendOrCancelOtherOwnershipAndReleasePermit() throws Exception {
    MutableClock clock = new MutableClock(NOW);
    ReplyCorrelationRegistry registry = new ReplyCorrelationRegistry(2);
    PendingReply existing = registry.register(ID_1, NOW.plusSeconds(2), NOW).orElseThrow();
    JmsRequestReplyClient client = new JmsRequestReplyClient(registry, clock, 1);
    AtomicInteger sends = new AtomicInteger();
    assertThrows(IllegalStateException.class, () -> client.exchange(ID_1, request(),
        Duration.ofSeconds(2), (id, body) -> sends.incrementAndGet()));
    assertEquals(0, sends.get());
    assertEquals(1, registry.pendingCount());
    assertFalse(existing.completion().toCompletableFuture().isDone());
    assertArrayEquals(new byte[] {7}, client.exchange(new UUID(0, 2), request(), Duration.ofSeconds(2),
        (id, body) -> {
          sends.incrementAndGet();
          assertTrue(client.onReply(id, new byte[] {7}));
        }));
    assertEquals(1, registry.pendingCount());
    assertFalse(existing.completion().toCompletableFuture().isDone());
    assertTrue(registry.cancel(ID_1));
    clock.set(Instant.MAX);
    assertThrows(java.time.DateTimeException.class, () -> client.exchange(ID_1, request(),
        Duration.ofSeconds(2), (id, body) -> sends.incrementAndGet()));
    assertEquals(1, sends.get());
    assertEquals(0, registry.pendingCount());
    clock.set(NOW);
    assertArrayEquals(new byte[] {8}, client.exchange(ID_1, request(), Duration.ofSeconds(2),
        (id, body) -> {
          sends.incrementAndGet();
          assertTrue(client.onReply(id, new byte[] {8}));
        }));
    assertEquals(2, sends.get());
    assertEquals(0, registry.pendingCount());
  }
  // JMSCLIENT009010-END

""";needle='  private static JmsRequestReplyClient client(';assert s.count(needle)==1;s=s.replace(needle,addition+needle,1);inverse=s.replace(addition,'',1)
for a,b in reversed(changes):assert inverse.count(b)==1;inverse=inverse.replace(b,a,1)
assert inverse==old
cmd=[str(R.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(R.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'-']
def fmt(txt):
 v=subprocess.run(cmd,input=txt.encode(),capture_output=True,timeout=30);assert v.returncode==0;return v.stdout
fixed=fmt(s);assert fmt(fixed.decode())==fixed and fmt(inverse)==fmt(old);helper='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/ReplyCorrelationRegistryTest.java';catalog='src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/transport/BrokerTopologyTest.java';pins={q:sha(R/q) for q in [helper,catalog]};O.mkdir();(O/'addition.java.txt').write_text(addition.rstrip()+'\n');p.write_bytes(fixed);assert all(sha(R/q)==h for q,h in pins.items());d=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),beforeManifestSha256=sha(before/'manifest.json'),testPath=plan['testPath'],testSha256=sha(p),oldTestSha256=plan['testSha256'],originalEightInverseExactBeforeFormatting=True,originalEightCanonicalInverseExact=True,formatIdempotent=True,finiteExecutorOwners=1,executorFinallyJoinSeconds=5,ThreadFinallyJoinMillis=2000,ThreadFinallyAssertTerminal=True,newDefinitions=2,newProviderUnknownKinds=3,newDuplicateAndClockNegativeCases=2,connectedExpectedTests=19,unchangedHelperTestHashes=pins,MainChanged=False,timingOracleChanged=False,productTestsExecuted=0,files={q.name:sha(q) for q in O.iterdir()},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,old8InverseExact=True,newDefinitions=2,expectedConnectedCases=19,MainChanged=False,manifestSha256=sha(O/'manifest.json'))))
