"""BUG2664 finite owners plus independent unknown-failure wipe/ownership test; no Main change."""
from pathlib import Path
import hashlib,json,re,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';before=json.loads((B/'evidence/PG26518-login-owner-before-v1/manifest.json').read_text());p=R/before['testPath'];old=p.read_text();assert hashlib.sha256(p.read_bytes()).hexdigest()==before['testSha256'];new=old;changes=[]
for expression in ['Executors.newVirtualThreadPerTaskExecutor()','Executors.newFixedThreadPool(8)']:
 a='    try (var workers = '+expression+') {';assert new.count(a)==1;i=new.index(a);openAt=i+len(a)-1;level=1;j=openAt+1
 while level:
  if new[j]=='{':level+=1
  elif new[j]=='}':level-=1
  j+=1
 replacement='    var workers = '+expression+';\n    try {';closing=' finally {\n      workers.shutdownNow();\n      assertTrue(workers.awaitTermination(5, TimeUnit.SECONDS));\n    }';originalBlock=new[i:j];newBlock=replacement+new[openAt+1:j]+closing;new=new[:i]+newBlock+new[j:];changes.append((newBlock,originalBlock))
addition='''
  @Test
  void unknownProviderFailureErasesBothBuffersAndReleasesCapacity() {
    // BUG2664/YKT2344, PT-WEB-LOGIN-UNKNOWN-001; synthetic char/byte inputs only.
    for (Throwable failure : List.of(new NullPointerException("synthetic-provider-fault"),
        new AssertionError("synthetic-provider-fault"))) {
      JmsRequestReplyClient client =
          new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 1);
      AtomicReference<byte[]> handed = new AtomicReference<>();
      AtomicInteger sends = new AtomicInteger();
      JmsRequestSender sender = (id, wire) -> {
        handed.set(wire);
        sends.incrementAndGet();
        if (failure instanceof RuntimeException runtime) throw runtime;
        throw (Error) failure;
      };
      char[] password = {'p'};
      Throwable actual = assertThrows(failure.getClass(), () ->
          service(client, sender).exchange(FIXTURE_ALICE_0A50500B, password, FIXTURE_1_FB15673E));
      assertSame(failure, actual);
      assertArrayEquals(new char[1], password);
      assertArrayEquals(new byte[640], handed.get());
      assertEquals(1, sends.get());
      assertEquals(0, client.pendingCount());
      // A fresh request succeeds through the same one-slot client after the failed owner exits.
      UUID next = new UUID(0, 2);
      char[] nextPassword = {'p'};
      MqLoginClient.Reply reply = new MqLoginClient(client, (id, wire) -> {
        sends.incrementAndGet();
        handed.set(wire);
        assertEquals(next, id);
        assertTrue(client.onReply(id,
            success(id, FIXTURE_ALICE_0A50500B, FIXTURE_USER_2DED8884, "e".repeat(64))));
      }, CLOCK, () -> next, WAIT).exchange(
          FIXTURE_ALICE_0A50500B, nextPassword, FIXTURE_1_FB15673E);
      assertEquals(ResultCode.SUCCESS, reply.code());
      assertEquals(UserRole.USER, reply.data().role().orElseThrow());
      assertEquals(FIXTURE_ALICE_0A50500B, reply.data().username().orElseThrow());
      assertArrayEquals(new char[1], nextPassword);
      assertArrayEquals(new byte[640], handed.get());
      assertEquals(2, sends.get());
      assertEquals(0, client.pendingCount());
    }
  }

''';anchor='  private static void invalid(';assert new.count(anchor)==1;new=new.replace(anchor,addition+anchor);extra='import static org.junit.jupiter.api.Assertions.assertSame;\n';new=new.replace('import static org.junit.jupiter.api.Assertions.assertThrows;',extra+'import static org.junit.jupiter.api.Assertions.assertThrows;');inverse=new.replace(addition,'').replace(extra,'')
for block,prior in reversed(changes):assert inverse.count(block)==1;inverse=inverse.replace(block,prior)
assert inverse==old
fmt=TC/'google-java-format-1.36.1-all-deps.jar'
if not fmt.exists():fmt=next(TC.rglob(fmt.name))
f=subprocess.run([str(TC/'jdk-25.0.4/bin/java'),'-jar',str(fmt),'-'],input=new,text=True,capture_output=True);assert f.returncode==0,f.stderr;p.write_text(f.stdout);assert len(re.findall(r'@Test\b',f.stdout))==7 and 'try (var workers' not in f.stdout and f.stdout.count('workers.awaitTermination(5, TimeUnit.SECONDS)')==2
O=B/'evidence/PG26522-login-test-manufacture-v1';assert not O.exists();O.mkdir();v=dict(actualExit=0,testPath=before['testPath'],beforeSha256=before['testSha256'],afterSha256=hashlib.sha256(p.read_bytes()).hexdigest(),originalSixInverseExactBeforeFormatting=True,newDefinitions=1,newUnknownKinds=2,fixedOwnerSites=2,mainChanged=False,productTestsExecuted=0,actualAuthenticationOrInfrastructureOperations=False);(O/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
