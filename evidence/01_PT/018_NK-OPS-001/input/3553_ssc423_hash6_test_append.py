"""Preserve old whole3 prefix and append meaningful digest/format erasure failure contracts."""
from pathlib import Path
import hashlib,json
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';p=r/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/ContextHashTest.java';old=p.read_text();assert old.count('@Test')==3 and old.endswith('}\n');pub=json.loads((b/'evidence/PG33882-ssc423-design-main-publication-v1/manifest.json').read_text());assert pub['actualExit']==0 and pub['ssc']=='SSC423'
extra=r'''
  @Test
  void hashOwn001DigestAndFormatFailuresEraseOwnedBytesAndReleasePrivateLock() throws Exception {
    String golden = "ffe054fe7ae0cb6dc65c3af9b61d5209f439851db43d0ba5997337df154668eb";
    for (boolean failDigest : new boolean[] {true, false}) {
      for (Throwable fault : new Throwable[] {
        new AssertionError("synthetic hash fault"), new IllegalArgumentException("synthetic hash fault")
      }) {
        byte[][] captured = new byte[2][];
        int[] calls = new int[2];
        var digest = java.security.MessageDigest.getInstance("SHA-256");
        var operations = new ContextHash.DigestOperations() {
          @Override
          public byte[] digest(byte[] raw) {
            captured[0] = raw;
            calls[0]++;
            if (failDigest && calls[0] == 1) throwHashFault(fault);
            captured[1] = digest.digest(raw);
            return captured[1];
          }

          @Override
          public String format(byte[] hashed) {
            calls[1]++;
            if (!failDigest && calls[1] == 1) throwHashFault(fault);
            return java.util.HexFormat.of().formatHex(hashed);
          }
        };
        var hashes = new ContextHash(operations);
        var context = AuthenticationContext.of("a".repeat(64));
        Throwable observed = assertThrows(fault.getClass(), () -> hashes.calculate(context));
        org.junit.jupiter.api.Assertions.assertSame(fault, observed);
        assertArrayEquals(new byte[64], captured[0]);
        if (failDigest) org.junit.jupiter.api.Assertions.assertNull(captured[1]);
        else assertArrayEquals(new byte[32], captured[1]);
        assertEquals("a".repeat(64), context.wireValue());
        byte[] firstRaw = captured[0];
        byte[] firstHash = captured[1];
        var executor = Executors.newSingleThreadExecutor();
        try {
          assertEquals(golden, executor.submit(() -> hashes.calculate(context)).get(5, java.util.concurrent.TimeUnit.SECONDS));
        } finally {
          executor.shutdownNow();
          assertTrue(executor.awaitTermination(10, java.util.concurrent.TimeUnit.SECONDS));
        }
        assertEquals(2, calls[0]);
        assertEquals(failDigest ? 1 : 2, calls[1]);
        org.junit.jupiter.api.Assertions.assertNotSame(firstRaw, captured[0]);
        if (!failDigest) org.junit.jupiter.api.Assertions.assertNotSame(firstHash, captured[1]);
        assertArrayEquals(new byte[64], captured[0]);
        assertArrayEquals(new byte[32], captured[1]);
        assertEquals("a".repeat(64), context.wireValue());
      }
    }
  }

  @Test
  void hashOwn002NullOperationsFailBeforeAnySecretAcquisition() {
    assertThrows(NullPointerException.class, () -> new ContextHash(null));
  }

  @Test
  void hashOwn003AsciiAndDigestBoundariesUseFixedVectorAndDoNotBorrowCallerMonitor() throws Exception {
    String golden = "ffe054fe7ae0cb6dc65c3af9b61d5209f439851db43d0ba5997337df154668eb";
    byte[] expectedAscii = new byte[64];
    java.util.Arrays.fill(expectedAscii, (byte) 'a');
    byte[] expectedHash = java.util.HexFormat.of().parseHex(golden);
    byte[][] captured = new byte[2][];
    int[] calls = new int[2];
    var digest = java.security.MessageDigest.getInstance("SHA-256");
    var operations = new ContextHash.DigestOperations() {
      @Override
      public byte[] digest(byte[] raw) {
        assertArrayEquals(expectedAscii, raw);
        captured[0] = raw;
        calls[0]++;
        return digest.digest(raw);
      }

      @Override
      public String format(byte[] hashed) {
        assertArrayEquals(expectedHash, hashed);
        captured[1] = hashed;
        calls[1]++;
        return java.util.HexFormat.of().formatHex(hashed);
      }
    };
    var hashes = new ContextHash(operations);
    var context = AuthenticationContext.of("a".repeat(64));
    var executor = Executors.newSingleThreadExecutor();
    try {
      synchronized (hashes) {
        assertEquals(golden, executor.submit(() -> hashes.calculate(context)).get(5, java.util.concurrent.TimeUnit.SECONDS));
      }
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, java.util.concurrent.TimeUnit.SECONDS));
    }
    assertArrayEquals(new int[] {1, 1}, calls);
    assertArrayEquals(new byte[64], captured[0]);
    assertArrayEquals(new byte[32], captured[1]);
    assertArrayEquals(expectedAscii, "a".repeat(64).getBytes(java.nio.charset.StandardCharsets.US_ASCII));
    assertEquals("a".repeat(64), context.wireValue());
    assertEquals(32, expectedHash.length);
  }

  private static void throwHashFault(Throwable failure) {
    if (failure instanceof Error fatal) throw fatal;
    throw (RuntimeException) failure;
  }
'''
new=old[:-2]+extra+'}\n';assert new[:new.index('  @Test\n  void hashOwn001')].rstrip()==old[:-2].rstrip();p.write_text(new);e=b/'evidence/PG33883-ssc423-hash6-source-prefix-v1';assert not e.exists();e.mkdir();(e/'manifest.json').open('x').write(json.dumps(dict(actualExit=0,testPath=str(p.relative_to(r)),oldWhole3Sha256=hashlib.sha256(old.encode()).hexdigest(),oldWhole3PrefixExact=True,oldDefinitions=3,newDefinitions=3,expectedWhole6=6,designPublication=pub['mainCommit'],applicationTestsExecuted=0),indent=2)+'\n');print(json.dumps(dict(actualExit=0,old3PrefixExact=True,newDefinitions=3)))
