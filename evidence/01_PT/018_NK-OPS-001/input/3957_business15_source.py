"""Preserve thirteen independent wire oracles; add original-object fatal and cyclic-graph cleanup."""
from pathlib import Path
import hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
base='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/'
names=['QuestionWireClient','NotificationWireClient','UserAdministrationWireClient','LogoutWireClient','MediaDescriptorWireClient','ProtectedReadWireClient','ProtectedReadWireException','JmsRequestReplyException','JmsRequestReplyClient','JmsRequestSender','ReplyCorrelationRegistry','PendingReply','package-info'];main=[base+n+'.java' for n in names]
assert all((r/n).read_bytes()==subprocess.check_output(['git','show','HEAD:'+n]) for n in main)
p=r/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/WebBusinessWireClientsTest.java';original=p.read_text();old=ld(b/'evidence/PG27904-business-wire13-independent-v1/manifest.json');assert sha(p)==old['inputHashes'][str(p.relative_to(r))]
new='''  @Test
  @org.junit.jupiter.api.Timeout(30)
  void wire014AllEighteenFacadesPreserveFatalIdentityWipeAndReleaseWithoutAutomaticRetry() {
    for (String type : TYPES) {
      var fatal = new AssertionError(PUBLIC_FAILURE);
      var wrapped = new IllegalStateException(PUBLIC_FAILURE, fatal);
      var sql = new java.sql.SQLException(PUBLIC_FAILURE);
      var next = new java.sql.SQLException(PUBLIC_FAILURE, fatal);
      sql.setNextException(next);
      var linked = new JMSException(PUBLIC_FAILURE);
      linked.setLinkedException(sql);
      for (Throwable failure : List.of(fatal, wrapped, linked)) {
        var wire = new JmsRequestReplyClient(new ReplyCorrelationRegistry(1), CLOCK, 1);
        var sent = new ArrayList<byte[]>();
        JmsRequestSender sender =
            (id, body) -> {
              assertArrayEquals(request(type, id, CONTEXT.wireValue()), body);
              sent.add(body);
              if (failure instanceof Error error) throw error;
              if (failure instanceof JMSException checked) throw checked;
              throw (IllegalStateException) failure;
            };
        var client = facade(group(type), wire, sender, CLOCK, () -> ID, WAIT);
        for (int attempt = 1; attempt <= 2; attempt++) {
          assertSame(fatal, assertThrows(AssertionError.class, () -> client.apply(input(type), CONTEXT)));
          assertEquals(attempt, sent.size());
          assertArrayEquals(new byte[sent.getLast().length], sent.getLast());
          assertEquals(0, wire.pendingCount());
          assertEquals(0, wire.lateReplyCount());
        }
        assertSame(fatal, wrapped.getCause());
        assertSame(sql, linked.getLinkedException());
        assertSame(next, sql.getNextException());
        assertSame(fatal, next.getCause());
        assertEquals(0, fatal.getSuppressed().length);
      }
    }
  }

  @Test
  @org.junit.jupiter.api.Timeout(30)
  void wire015AllEighteenFacadesTerminateMixedCyclesAndKeepFixedCatalogAndCapacity() {
    for (String type : TYPES) {
      var failure = new JMSException(PUBLIC_FAILURE);
      var linked = new JMSException(PUBLIC_FAILURE);
      var sql = new java.sql.SQLException(PUBLIC_FAILURE);
      var next = new java.sql.SQLException(PUBLIC_FAILURE);
      failure.setLinkedException(linked);
      linked.setLinkedException(failure);
      sql.setNextException(next);
      next.setNextException(sql);
      linked.addSuppressed(sql);
      next.addSuppressed(failure);
      var wire = new JmsRequestReplyClient(new ReplyCorrelationRegistry(1), CLOCK, 1);
      var sent = new ArrayList<byte[]>();
      JmsRequestSender sender =
          (id, body) -> {
            assertArrayEquals(request(type, id, CONTEXT.wireValue()), body);
            sent.add(body);
            throw failure;
          };
      var client = facade(group(type), wire, sender, CLOCK, () -> ID, WAIT);
      for (int attempt = 1; attempt <= 2; attempt++) {
        var actual = assertThrows(ProtectedReadWireException.class, () -> client.apply(input(type), CONTEXT));
        assertSame(ProtectedReadWireException.Reason.UNAVAILABLE, actual.reason());
        assertEquals("protected read exchange rejected", actual.getMessage());
        assertNull(actual.getCause());
        assertEquals(0, actual.getSuppressed().length);
        assertEquals(attempt, sent.size());
        assertArrayEquals(new byte[sent.getLast().length], sent.getLast());
        assertEquals(0, wire.pendingCount());
        assertEquals(0, wire.lateReplyCount());
      }
      assertSame(linked, failure.getLinkedException());
      assertSame(failure, linked.getLinkedException());
      assertSame(next, sql.getNextException());
      assertSame(sql, next.getNextException());
      assertArrayEquals(new Throwable[] {sql}, linked.getSuppressed());
      assertArrayEquals(new Throwable[] {failure}, next.getSuppressed());
    }
  }

'''
marker='  // UI234 PAGED48 and UI236 section 11.3:';assert original.count(marker)==1;constant='  private static final String PUBLIC_FAILURE = \"public unissued failure\";\n';p.write_text(original.replace('  private static final String QSB_TYPE',constant+'  private static final String QSB_TYPE').replace(marker,new+marker));subprocess.run([str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(p)],check=True,timeout=30)
now=p.read_text();start=now.index('  @Test\n  @org.junit.jupiter.api.Timeout(30)\n  void wire014');end=now.index(marker,start);assert (now[:start]+now[end:]).replace(constant,'')==original
sdk=ld(b/'evidence/PG34940-reply-values-source-v1/manifest.json')['sdkHashes'];assert all(sha(Path(n))==h for n,h in sdk.items())
oldp=b/'evidence/PG33750-ssc418-context64-independent-v1/manifest.json';oldrawp=b/'evidence/PG33752-ssc418-context64-unfiltered-same-exec-v1/manifest.json';prior=ld(oldp);priorraw=ld(oldrawp);assert priorraw['own13Source20Physical17CodeRawFour100'];reference=[]
for n in ['ProtectedReadWireException','ScenarioWireException']:
 path=base+n+'.java';assert sha(r/path)==prior['inputHashes'][path];reference.append(dict(path=path,sha256=sha(r/path),oldSource=prior['source'],oldProductionCore=prior['productionCoreMain'],oldRaw={k:priorraw['classes']['dev/codex/schubert/nk/web/messaging/'+n+k]['counters'] for k in ['', '$Reason']},sourceComponentReferenceOnly=True,currentCoreExecutionTransferred=False))
o=b/'evidence/PG34980-business15-source-v1';o.mkdir();v=dict(actualExit=0,mainSources=main,testSources=[dict(path=str(p.relative_to(r)),tests=15)],inputHashes={n:sha(r/n) for n in main+[str(p.relative_to(r))]},sdkHashes=sdk,mainSourcesUnchanged=True,original13InverseByteExact=True,original13Sha256=hashlib.sha256(original.encode()).hexdigest(),newDefinitions=2,necessaryPriorDefinitions=13,expectedTests=15,targets=['dev/codex/schubert/nk/web/messaging/'+n for n in names[:5]],prior13=ref(b/'evidence/PG27904-business-wire13-independent-v1/manifest.json'),changedDependencySincePrior13=base+'ProtectedReadWireClient.java',unchangedExceptionsReference=reference,old64Post=ref(oldp),old64Raw=ref(oldrawp),wholeOld64OrOld13Transferred=False,applicationTestsExecuted=0,newAcceptance=0)
(o/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,main=len(main),original13InverseByteExact=True,whole=15,newDefinitions=2,priorExceptionsNoReplay=2)))
