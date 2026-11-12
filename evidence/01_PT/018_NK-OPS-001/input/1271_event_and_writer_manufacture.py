"""Current event guard integration and independent port/writer boundaries; original9+3 retained."""
from pathlib import Path
import hashlib,json,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';O=B/'evidence/PG26577-event-writer-manufacture-v1';assert not O.exists();O.mkdir();results=[]
event='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/inbound/EventTransactionPortTest.java'
writer='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/outbound/FatalDlqMessageWriterTest.java'
eventAddition='''
  @Test
  void txp010ProviderArgumentAndNullFailuresRollbackRatherThanIsolateWire() {
    // BUG2659 integration; two formerly overcaught getters, both routes and entry points.
    for (boolean question : List.of(true, false)) {
      for (boolean legacy : List.of(true, false)) {
        for (String getter : List.of("getJMSMessageID", "getJMSCorrelationID")) {
          for (RuntimeException failure : List.of(
              new IllegalArgumentException("synthetic provider fault"),
              new NullPointerException("synthetic provider fault"))) {
            var s = new Scenario(question);
            byte[] before = s.body.clone();
            BytesMessage delegate = s.message();
            BytesMessage message = (BytesMessage) Proxy.newProxyInstance(
                BytesMessage.class.getClassLoader(), new Class<?>[] {BytesMessage.class},
                (ignored, method, arguments) -> {
                  if (method.getName().equals(getter)) throw failure;
                  return method.invoke(delegate, arguments);
                });
            var listener = listener(s, ignored -> {
              throw new AssertionError(UNEXPECTED_PROCESSOR);
            }, CLOCK);
            var context = s.context();
            if (legacy) {
              assertSame(failure, assertThrows(failure.getClass(),
                  () -> listener.onMessage(context, message)));
              assertEquals(List.of(MODE, ROLLBACK), s.order);
            } else {
              assertSame(failure, assertThrows(failure.getClass(), () -> listener.onMessage(
                  context, message, () -> s.order.add(ATTEMPTED),
                  () -> s.order.add(CONFIRMED))));
              assertEquals(List.of(MODE, ATTEMPTED, ROLLBACK, CONFIRMED), s.order);
            }
            assertEquals(1, s.bodyReads);
            assertEquals(0, s.clears);
            assertSame(null, s.sent);
            assertArrayEquals(before, s.body);
            assertEquals(0, failure.getSuppressed().length);
          }
        }
      }
    }
  }

  @Test
  void txp011DefaultProcessorNullContractsAndLegacyIdentityAreIndependentOfJms() {
    // Explicit literal object input; expected is SAM count/argument identity, not a codec result.
    var header = new dev.codex.schubert.nk.protocol.header.CommonHeader(
        "SCHBNK01", 1, new dev.codex.schubert.nk.protocol.layout.LayoutId(WORK_LAYOUT), 1,
        dev.codex.schubert.nk.protocol.header.MessageKind.EVENT,
        dev.codex.schubert.nk.protocol.header.InteractionKind.INTERNAL,
        java.util.UUID.fromString(EVENT_ID), java.util.UUID.fromString(CORRELATION_ID), NOW,
        java.util.Optional.empty(), 256, 64, 0, 0, 320, java.util.Optional.empty());
    var event = new dev.codex.schubert.nk.protocol.layout.WireMessage<>(header,
        new dev.codex.schubert.nk.protocol.layout.FixedPayload(
            Arrays.copyOfRange(golden(true), 256, 320), 0, List.of()));
    var delivery = new DeliveryMetadata(3, TRANSPORT_ID, NOW);
    var seen = new ArrayList<Object>();
    InternalEventProcessor processor = seen::add;
    assertThrows(NullPointerException.class, () -> processor.process(null, delivery));
    assertThrows(NullPointerException.class, () -> processor.process(event, null));
    assertThrows(NullPointerException.class, () -> processor.process(null, null));
    assertTrue(seen.isEmpty());
    processor.process(event, delivery);
    assertEquals(1, seen.size());
    assertSame(event, seen.getFirst());
  }

'''
writerAddition='''
  @Test
  void exactPrintable128AndErrorCode32BoundariesAreRetainedWithoutTrimming() throws Exception {
    // SS321 section11: independently authored exact maxima, including ASCII space and tilde.
    for (String transport : new String[] {"!" + " ".repeat(126) + "~", "~".repeat(128)}) {
      for (String code : new String[] {"A", "A" + "Z".repeat(31)}) {
        Capture capture = new Capture();
        byte[] body = {0, 32, (byte) 0xff};
        FatalDlqMetadata metadata =
            new FatalDlqMetadata(code, FatalDlqMetadata.DetectedBy.WEB_REPLY, DETECTED_AT);
        FatalDlqMessageWriter.INSTANCE.create(context(capture), rejected(body, transport), metadata);
        assertArrayEquals(new byte[] {0, 32, (byte) 0xff}, capture.body);
        assertEquals(128, transport.length());
        assertEquals(transport, capture.stringProperties.get("NKOriginalTransportID"));
        assertEquals(code, capture.stringProperties.get("NKErrorCode"));
      }
    }
    FatalDlqMetadata metadata =
        new FatalDlqMetadata("A", FatalDlqMetadata.DetectedBy.WEB_REPLY, DETECTED_AT);
    for (String bad : new String[] {"X\\u001f", "X\\u007f"}) {
      Capture capture = new Capture();
      assertThrows(IllegalArgumentException.class, () -> FatalDlqMessageWriter.INSTANCE.create(
          context(capture), rejected(new byte[0], bad), metadata));
      assertEquals(0, capture.stringProperties.size());
    }
  }

'''
fmt=TC/'google-java-format-1.36.1-all-deps.jar'
if not fmt.exists():fmt=next(TC.rglob(fmt.name))
for index,path,addition,anchor,originalCases in [(1,event,eventAddition,'  private static TransactedEventListener listener(',9),(2,writer,writerAddition,'  private static GuardedJmsMessage rejected(',3)]:
 p=R/path;old=p.read_text();assert old.count(anchor)==1;new=old.replace(anchor,addition+anchor);assert new.replace(addition,'')==old;(O/(str(index)+'-original.java.txt')).write_text(old)
 f=subprocess.run([str(TC/'jdk-25.0.4/bin/java'),'-jar',str(fmt),'-'],input=new,text=True,capture_output=True);assert f.returncode==0,f.stderr;p.write_text(f.stdout);results.append(dict(path=path,beforeSha256=hashlib.sha256(old.encode()).hexdigest(),afterSha256=hashlib.sha256(p.read_bytes()).hexdigest(),originalCases=originalCases,originalAllTokensInverseExact=True,newDefinitions=2 if index==1 else 1))
v=dict(actualExit=0,results=results,MainChanged=False,newDefinitions=3,providerIntegrationInputs=16,defaultNullInputs=3,defaultPositiveIdentity=1,writerValidBoundaryInputs=4,writerInvalidNearBoundaryInputs=2,oldDlgWhole8ReusedNotDuplicated=True,productTestsExecuted=0);(O/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(actualExit=0,newDefinitions=3,originalCasesRetained=12,productTestsExecuted=0)))
