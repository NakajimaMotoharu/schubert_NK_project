"""One independent provider-NPE matrix for all18 pure facades; retain whole original12 exactly."""
from pathlib import Path
import hashlib,json,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';p=R/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/WebBusinessWireClientsTest.java';old=p.read_text();before=json.loads((B/'evidence/PG26546-business-facades-contract-v1/manifest.json').read_text());assert hashlib.sha256(p.read_bytes()).hexdigest()==before['inputHashes'][str(p.relative_to(R))]
addition='''
  @Test
  void wire013ProviderNullFailuresEraseCloneAndReleaseEachFacadeCapacity() {
    // PT-WEB-S3WIRE013: independent literal18 request vectors; no backend or grant.
    for (String type : TYPES) {
      var wire = new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 1);
      var sent = new ArrayList<byte[]>();
      var original = new NullPointerException("synthetic-provider-fault");
      JmsRequestSender failing = (id, body) -> {
        assertArrayEquals(request(type, id, CONTEXT.wireValue()), body);
        sent.add(body);
        throw original;
      };
      var client = facade(group(type), wire, failing, CLOCK, () -> ID, WAIT);
      assertSame(original, assertThrows(NullPointerException.class,
          () -> client.apply(input(type), CONTEXT)));
      assertEquals(1, sent.size());
      assertEquals(0, wire.pendingCount());
      assertArrayEquals(new byte[sent.getFirst().length], sent.getFirst());
      // Explicit fresh invocation verifies one-slot capacity recovery; not an automatic retry.
      var next = new UUID(0, 2);
      JmsRequestSender accepted = (id, body) -> {
        assertEquals(next, id);
        assertArrayEquals(request(type, id, CONTEXT.wireValue()), body);
        sent.add(body);
        assertTrue(wire.onReply(id, response(type, ERROR_RESULT_CODE, id, CONTEXT.wireValue())));
      };
      var fresh = facade(group(type), wire, accepted, CLOCK, () -> next, WAIT);
      var reply = fresh.apply(input(type), CONTEXT);
      assertEquals(ERROR_RESULT_CODE, reply.resultCode().wireValue());
      assertTrue(reply.payload().isEmpty());
      assertEquals(2, sent.size());
      assertEquals(0, wire.pendingCount());
      assertEquals(0, wire.lateReplyCount());
      sent.forEach(body -> assertArrayEquals(new byte[body.length], body));
    }
  }

''';anchor='  // UI234 PAGED48 and UI236 section 11.3:';assert old.count(anchor)==1;new=old.replace(anchor,addition+anchor);assert new.replace(addition,'')==old
fmt=TC/'google-java-format-1.36.1-all-deps.jar'
if not fmt.exists():fmt=next(TC.rglob(fmt.name))
f=subprocess.run([str(TC/'jdk-25.0.4/bin/java'),'-jar',str(fmt),'-'],input=new,text=True,capture_output=True);assert f.returncode==0,f.stderr;p.write_text(f.stdout);O=B/'evidence/PG26550-business-npe-manufacture-v1';assert not O.exists();O.mkdir();(O/'original-test-before.java.txt').write_text(old);v=dict(actualExit=0,path=str(p.relative_to(R)),beforeSha256=hashlib.sha256(old.encode()).hexdigest(),afterSha256=hashlib.sha256(p.read_bytes()).hexdigest(),originalWhole12InverseExactBeforeFormatting=True,newDefinitions=1,providerNpeInputs=18,successfulFreshExplicitReuses=18,MainChanged=False,originalFiniteWorkerUnchanged=True,productTestsExecuted=0);(O/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
