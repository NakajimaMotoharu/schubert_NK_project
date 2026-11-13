"""One catalog guard plus one independent ordinary graph/wipe/slot-reuse Test; no execution."""
from pathlib import Path
import subprocess,hashlib,json
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';o=b/'evidence/PG29452-login-graph-source-manufacture-v1';assert not o.exists();o.mkdir();main=r/'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/security/MqLoginClient.java';test=r/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/security/MqLoginClientTest.java';oldmain=main.read_text();oldtest=test.read_text();(o/'MqLoginClient.before.java.txt').write_text(oldmain);(o/'MqLoginClientTest.before.java.txt').write_text(oldtest)
a='''        | DateTimeException exception) {
      throw new MqLoginExchangeException(MqLoginExchangeException.Reason.UNAVAILABLE);''';z='''        | DateTimeException exception) {
      // BUG2834: retain fatal graph identity; existing finally still wipes every owned buffer.
      JmsRequestReplyException.preserveFatal(exception);
      throw new MqLoginExchangeException(MqLoginExchangeException.Reason.UNAVAILABLE);''';assert oldmain.count(a)==1;newmain=oldmain.replace(a,z)
newtest='''  // LOGIN-GRAPH-001-BEGIN: independent objects, no provider/network or authentication grant.
  @Test
  void knownFailureGraphsRetainFatalIdentityWipeAndReturnTheOneWaitSlot() {
    for (int family = 0; family < 9; family++) {
      Error fatal = new AssertionError(FIXTURE_SYNTHETIC_SENSITIVE_5D06BEDA);
      Exception failure;
      switch (family) {
        case 0 -> {
          JMSException jms = new JMSException(FIXTURE_SYNTHETIC_SENSITIVE_5D06BEDA);
          jms.setLinkedException(new Exception(FIXTURE_SYNTHETIC_SENSITIVE_5D06BEDA, fatal));
          failure = jms;
        }
        case 1 -> failure = new JMSRuntimeException(FIXTURE_SYNTHETIC_SENSITIVE_5D06BEDA, null, fatal);
        case 2 -> failure = new IllegalArgumentException(FIXTURE_SYNTHETIC_SENSITIVE_5D06BEDA, fatal);
        case 3 -> {
          failure = new IllegalStateException(FIXTURE_SYNTHETIC_SENSITIVE_5D06BEDA);
          failure.addSuppressed(fatal);
        }
        case 4 -> failure = new DateTimeException(FIXTURE_SYNTHETIC_SENSITIVE_5D06BEDA, fatal);
        case 5 -> failure = new dev.codex.schubert.nk.protocol.codec.PermanentProtocolException(
            FIXTURE_SYNTHETIC_SENSITIVE_5D06BEDA, fatal);
        case 6 -> {
          var full = new ReplyCorrelationRegistry(1);
          full.register(new UUID(0, 99), NOW.plusSeconds(2), NOW).orElseThrow();
          var bounded = new JmsRequestReplyClient(full, CLOCK, 1);
          failure = assertThrows(dev.codex.schubert.nk.web.messaging.JmsRequestReplyException.class,
              () -> bounded.exchange(ID, new byte[256], WAIT, (id, wire) -> fail(FIXTURE_MUST_NOT_SEND_71FCB2F2)));
          failure.addSuppressed(fatal);
          assertTrue(full.cancel(new UUID(0, 99)));
        }
        case 7 -> {
          var first = new java.sql.SQLException(FIXTURE_SYNTHETIC_SENSITIVE_5D06BEDA);
          var second = new java.sql.SQLException(FIXTURE_SYNTHETIC_SENSITIVE_5D06BEDA, fatal);
          first.setNextException(second);
          second.setNextException(first);
          failure = new IllegalStateException(FIXTURE_SYNTHETIC_SENSITIVE_5D06BEDA, first);
        }
        default -> {
          JMSException jms = new JMSException(FIXTURE_SYNTHETIC_SENSITIVE_5D06BEDA);
          jms.addSuppressed(fatal);
          failure = jms;
        }
      }
      var client = new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 1);
      var handed = new AtomicReference<byte[]>();
      var sends = new AtomicInteger();
      char[] password = {'p'};
      Error actual = assertThrows(Error.class, () -> service(client, (id, wire) -> {
        sends.incrementAndGet();
        handed.set(wire);
        if (failure instanceof JMSException checked) throw checked;
        throw (RuntimeException) failure;
      }).exchange(FIXTURE_ALICE_0A50500B, password, FIXTURE_1_FB15673E));
      assertSame(fatal, actual);
      assertArrayEquals(new char[1], password);
      assertArrayEquals(new byte[640], handed.get());
      assertEquals(1, sends.get());
      assertEquals(0, client.pendingCount());
      UUID next = new UUID(0, 2);
      char[] nextPassword = {'p'};
      var result = new MqLoginClient(client, (id, wire) -> {
        sends.incrementAndGet();
        handed.set(wire);
        assertEquals(next, id);
        assertTrue(client.onReply(id, success(id, FIXTURE_ALICE_0A50500B, FIXTURE_USER_2DED8884, "e".repeat(64))));
      }, CLOCK, () -> next, WAIT).exchange(FIXTURE_ALICE_0A50500B, nextPassword, FIXTURE_1_FB15673E);
      assertEquals(ResultCode.SUCCESS, result.code());
      assertEquals(FIXTURE_ALICE_0A50500B, result.data().username().orElseThrow());
      assertArrayEquals(new char[1], nextPassword);
      assertArrayEquals(new byte[640], handed.get());
      assertEquals(2, sends.get());
      assertEquals(0, client.pendingCount());
    }
    for (int stage = 0; stage < 2; stage++) {
      Error fatal = new AssertionError(FIXTURE_SYNTHETIC_SENSITIVE_5D06BEDA);
      var client = client();
      var sends = new AtomicInteger();
      int selected = stage;
      var service = new MqLoginClient(client, (id, wire) -> sends.incrementAndGet(),
          selected == 0 ? new FaultClock(new DateTimeException(FIXTURE_SYNTHETIC_SENSITIVE_5D06BEDA, fatal)) : CLOCK,
          () -> { if (selected == 1) throw new IllegalStateException(FIXTURE_SYNTHETIC_SENSITIVE_5D06BEDA, fatal); return ID; }, WAIT);
      char[] password = {'p'};
      assertSame(fatal, assertThrows(Error.class, () -> service.exchange(FIXTURE_ALICE_0A50500B, password, FIXTURE_1_FB15673E)));
      assertArrayEquals(new char[1], password);
      assertEquals(0, sends.get());
      assertEquals(0, client.pendingCount());
    }
    var sqlFirst = new java.sql.SQLException(FIXTURE_SYNTHETIC_SENSITIVE_5D06BEDA);
    var sqlSecond = new java.sql.SQLException(FIXTURE_SYNTHETIC_SENSITIVE_5D06BEDA);
    sqlFirst.setNextException(sqlSecond);
    sqlSecond.setNextException(sqlFirst);
    var cycle = new JMSException(FIXTURE_SYNTHETIC_SENSITIVE_5D06BEDA);
    cycle.setLinkedException(sqlFirst);
    cycle.addSuppressed(sqlSecond);
    sqlSecond.addSuppressed(cycle);
    var client = new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 1);
    var handed = new AtomicReference<byte[]>();
    var sends = new AtomicInteger();
    char[] password = {'p'};
    var fixed = assertThrows(MqLoginExchangeException.class, () -> service(client, (id, wire) -> {
      sends.incrementAndGet(); handed.set(wire); throw cycle;
    }).exchange(FIXTURE_ALICE_0A50500B, password, FIXTURE_1_FB15673E));
    fixed(fixed, MqLoginExchangeException.Reason.UNAVAILABLE);
    assertArrayEquals(new char[1], password);
    assertArrayEquals(new byte[640], handed.get());
    assertEquals(1, sends.get());
    assertEquals(0, client.pendingCount());
    assertThrows(NullPointerException.class,
        () -> dev.codex.schubert.nk.web.messaging.JmsRequestReplyException.preserveFatal(null));
  }
  // LOGIN-GRAPH-001-END

'''
anchor='  private static void invalid(';assert oldtest.count(anchor)==1;test.write_text(oldtest.replace(anchor,newtest+anchor));main.write_text(newmain);tc=r.parent/'toolchain';fmt=[str(tc/'jdk-25.0.4/bin/java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings'];subprocess.run(fmt+['--replace',str(main),str(test)],check=True,capture_output=True);norm=lambda s:subprocess.check_output(fmt+['-'],input=s.encode());s=test.read_text();start=s.index('  // LOGIN-GRAPH-001-BEGIN');end=s.index('  // LOGIN-GRAPH-001-END')+len('  // LOGIN-GRAPH-001-END\n\n');assert norm(s[:start]+s[end:])==norm(oldtest) and s.count('@Test')==8 and oldtest.count('@Test')==7;assert norm(newmain.replace(z,a))==norm(oldmain) and main.read_bytes()==norm(newmain)
sources=o/'sources.txt';sources.write_text(str(main)+'\n'+str(test)+'\n');cmd=[str(tc/'jdk-25.0.4/bin/java'),'-jar',str(tc/'static-gates-20261015/checkstyle-14.3.0-all.jar'),'-c',str(r/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(o/'checkstyle.xml'),'@'+str(sources)];p=subprocess.run(cmd,capture_output=True);(o/'checkstyle.stdout').write_bytes(p.stdout);(o/'checkstyle.stderr').write_bytes(p.stderr);assert p.returncode==0
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();v=dict(actualExit=0,MainChanged=1,oldWholeSevenNormalizedInverseEqual=True,newDefinitions=1,newInputCases=dict(knownFamilyFatal=9,earlyCallbackFatal=2,nonfatalCyclicGraph=1,nullClassifierContract=1),expectedWholeTests=155,expectationsFrom='test-owned Error identities andliteralUI232234 goldenoffsets, neverproductionexpectedgenerator',sourceOnly=True,compileExecuted=False,productTestsExecuted=0,checkstyleExit=0,checkstyleCommand=cmd,inputHashes={str(p.relative_to(r)):sha(p) for p in [main,test]},oldMainSha256=hashlib.sha256(oldmain.encode()).hexdigest(),oldTestSha256=hashlib.sha256(oldtest.encode()).hexdigest(),actualHeldRootVmDbNativeJmsOperations=0);(o/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print('one Main guard/one Test13inputcases; original7/golden inverseequal; sourceGJF-CS0, runtime0')
